"""
RL-based schedule optimizer using Stable Baselines3 PPO
"""
import numpy as np
import logging
from typing import List, Dict, Optional
from datetime import datetime, timedelta
from pathlib import Path
from sqlalchemy.orm import Session

from stable_baselines3 import PPO
from stable_baselines3.common.env_checker import check_env

from ...models import Assignment, AvailabilitySlot
from .schedule_env import StudyScheduleEnv

logger = logging.getLogger(__name__)


class RLScheduler:
    """
    Reinforcement Learning-based scheduler using PPO
    """

    def __init__(self, db: Session, model_path: Optional[str] = None):
        """
        Initialize RL scheduler

        Args:
            db: Database session
            model_path: Path to saved model (optional)
        """
        self.db = db
        self.model = None
        self.is_trained = False

        # Default model path
        if model_path is None:
            model_path = Path(__file__).resolve().parent.parent.parent.parent / "models" / "rl_scheduler.zip"

        self.model_path = Path(model_path)

        # Try to load existing model
        self._load_model()

    def _load_model(self):
        """Load trained RL model from disk"""
        try:
            if self.model_path.exists():
                self.model = PPO.load(self.model_path)
                self.is_trained = True
                logger.info(f"Loaded RL scheduler model from {self.model_path}")
            else:
                logger.info(f"No saved RL model found at {self.model_path}")
                self.is_trained = False
        except Exception as e:
            logger.error(f"Failed to load RL model: {e}")
            self.model = None
            self.is_trained = False

    def save_model(self):
        """Save trained model to disk"""
        try:
            if self.model is None:
                logger.warning("No model to save")
                return False

            # Create models directory if it doesn't exist
            self.model_path.parent.mkdir(parents=True, exist_ok=True)

            # Save model
            self.model.save(self.model_path)
            logger.info(f"Saved RL model to {self.model_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to save RL model: {e}")
            return False

    def train(
        self,
        training_data: List[Dict],
        total_timesteps: int = 100000,
        verbose: int = 1
    ) -> Dict:
        """
        Train the RL agent on sample scheduling problems

        Args:
            training_data: List of training scenarios with assignments and slots
            total_timesteps: Number of training steps
            verbose: Verbosity level

        Returns:
            Training results dictionary
        """
        try:
            logger.info(f"Training RL scheduler for {total_timesteps} timesteps...")

            # Create a sample environment for training
            if not training_data:
                return {'success': False, 'error': 'No training data provided'}

            sample_scenario = training_data[0]
            env = StudyScheduleEnv(
                assignments=sample_scenario['assignments'],
                time_slots=sample_scenario['time_slots']
            )

            # Check environment
            logger.info("Validating environment...")
            try:
                check_env(env, warn=True)
            except Exception as e:
                logger.warning(f"Environment check warning: {e}")

            # Create PPO model
            logger.info("Creating PPO model...")
            self.model = PPO(
                "MlpPolicy",
                env,
                verbose=verbose,
                learning_rate=0.0003,
                n_steps=2048,
                batch_size=64,
                n_epochs=10,
                gamma=0.99,
                gae_lambda=0.95,
                clip_range=0.2,
                ent_coef=0.01
            )

            # Train
            logger.info("Starting training...")
            self.model.learn(total_timesteps=total_timesteps)
            self.is_trained = True

            # Save model
            saved = self.save_model()

            return {
                'success': True,
                'total_timesteps': total_timesteps,
                'model_saved': saved,
                'model_path': str(self.model_path)
            }

        except Exception as e:
            logger.error(f"Training failed: {e}", exc_info=True)
            return {'success': False, 'error': str(e)}

    def generate_schedule(
        self,
        assignments: List[Assignment],
        time_slots: List[Dict],
        use_rl: bool = True
    ) -> List[Dict]:
        """
        Generate schedule using RL agent

        Args:
            assignments: List of Assignment objects
            time_slots: List of time slot dictionaries
            use_rl: Whether to use RL (True) or fallback to greedy (False)

        Returns:
            List of scheduled sessions
        """
        if not use_rl or not self.is_trained or self.model is None:
            logger.warning("RL model not available, using greedy fallback")
            return self._greedy_schedule(assignments, time_slots)

        try:
            # Convert assignments to environment format
            assignment_dicts = []
            for a in assignments:
                assignment_dicts.append({
                    'id': a.id,
                    'estimated_hours': a.estimated_hours,
                    'due_date': a.due_date,
                    'priority': self._convert_priority(a.priority),
                    'difficulty': self._convert_difficulty(a.difficulty)
                })

            # Create environment
            env = StudyScheduleEnv(
                assignments=assignment_dicts,
                time_slots=time_slots
            )

            # Run RL agent
            obs = env.reset()
            done = False
            step = 0
            max_steps = len(assignments) * len(time_slots)

            while not done and step < max_steps:
                # Predict action
                action, _states = self.model.predict(obs, deterministic=True)

                # Take action
                obs, reward, done, info = env.step(action)
                step += 1

            # Get final schedule
            schedule = env.get_schedule()

            # Convert to session format
            sessions = []
            for item in schedule:
                slot = time_slots[item['slot_idx']]
                start_time = slot['start_time']
                end_time = start_time + timedelta(hours=item['duration'])

                sessions.append({
                    'assignment_id': item['assignment_id'],
                    'start_time': start_time,
                    'end_time': end_time,
                    'notes': f"RL-optimized study session ({item['duration']:.1f}h)"
                })

            logger.info(f"RL scheduler generated {len(sessions)} sessions in {step} steps")
            return sessions

        except Exception as e:
            logger.error(f"RL scheduling failed: {e}", exc_info=True)
            logger.warning("Falling back to greedy scheduler")
            return self._greedy_schedule(assignments, time_slots)

    def _greedy_schedule(
        self,
        assignments: List[Assignment],
        time_slots: List[Dict]
    ) -> List[Dict]:
        """
        Fallback greedy scheduling algorithm

        This is a simple greedy approach:
        1. Sort assignments by priority and due date
        2. Fill earliest available time slots first
        """
        sessions = []

        # Sort assignments by priority (high first) and due date (earliest first)
        sorted_assignments = sorted(
            assignments,
            key=lambda a: (
                -self._convert_priority(a.priority),
                a.due_date
            )
        )

        # Sort time slots by start time
        sorted_slots = sorted(time_slots, key=lambda s: s['start_time'])

        # Track remaining hours for each assignment
        remaining_hours = {a.id: a.estimated_hours for a in sorted_assignments}

        # Track available hours in each slot
        slot_available = [s['duration_hours'] for s in sorted_slots]

        # Greedy assignment
        for assignment in sorted_assignments:
            assignment_hours = remaining_hours[assignment.id]

            for slot_idx, slot in enumerate(sorted_slots):
                if assignment_hours <= 0:
                    break

                if slot_available[slot_idx] <= 0:
                    continue

                # Schedule session
                session_duration = min(
                    assignment_hours,
                    slot_available[slot_idx],
                    3.0  # Max 3 hours per session
                )

                if session_duration >= 0.5:  # Minimum 30 minutes
                    start_time = slot['start_time']
                    end_time = start_time + timedelta(hours=session_duration)

                    sessions.append({
                        'assignment_id': assignment.id,
                        'start_time': start_time,
                        'end_time': end_time,
                        'notes': f"Greedy scheduled study session ({session_duration:.1f}h)"
                    })

                    # Update remaining
                    assignment_hours -= session_duration
                    slot_available[slot_idx] -= session_duration

        return sessions

    def _convert_priority(self, priority) -> int:
        """Convert priority enum to integer (1-3)"""
        priority_map = {
            'low': 1,
            'medium': 2,
            'high': 3
        }
        if hasattr(priority, 'value'):
            return priority_map.get(priority.value, 2)
        return priority_map.get(priority, 2)

    def _convert_difficulty(self, difficulty) -> int:
        """Convert difficulty enum to integer (1-3)"""
        difficulty_map = {
            'easy': 1,
            'medium': 2,
            'hard': 3
        }
        if hasattr(difficulty, 'value'):
            return difficulty_map.get(difficulty.value, 2)
        return difficulty_map.get(difficulty, 2)
