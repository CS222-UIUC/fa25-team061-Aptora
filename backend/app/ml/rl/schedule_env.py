"""
Gym environment for study schedule optimization using Reinforcement Learning
"""
import gym
from gym import spaces
import numpy as np
from datetime import datetime, timedelta
from typing import List, Dict, Tuple, Optional
import logging

logger = logging.getLogger(__name__)


class StudyScheduleEnv(gym.Env):
    """
    Custom Gym environment for study schedule optimization

    State: Current schedule state (assignments, time slots, current progress)
    Action: Select which assignment to schedule in which time slot
    Reward: Based on deadline adherence, workload balance, completion
    """

    metadata = {'render.modes': ['human']}

    def __init__(
        self,
        assignments: List[Dict],
        time_slots: List[Dict],
        max_assignments: int = 20,
        max_time_slots: int = 50
    ):
        """
        Initialize the scheduling environment

        Args:
            assignments: List of assignment dictionaries with:
                - id, estimated_hours, due_date, priority, difficulty
            time_slots: List of time slot dictionaries with:
                - start_time, end_time, duration_hours
            max_assignments: Maximum number of assignments to handle
            max_time_slots: Maximum number of time slots
        """
        super(StudyScheduleEnv, self).__init__()

        self.max_assignments = max_assignments
        self.max_time_slots = max_time_slots

        # Store original data
        self.original_assignments = assignments[:max_assignments]
        self.original_time_slots = time_slots[:max_time_slots]

        # Number of actual assignments and slots
        self.n_assignments = min(len(assignments), max_assignments)
        self.n_time_slots = min(len(time_slots), max_time_slots)

        # Action space: Choose (assignment_idx, time_slot_idx) or SKIP
        # We use a discrete action space with flattened (assignment, slot) pairs + 1 for SKIP
        self.action_space = spaces.Discrete(
            (self.max_assignments * self.max_time_slots) + 1
        )

        # Observation space: State of assignments and time slots
        # For each assignment: [hours_remaining, days_until_due, priority, difficulty, is_scheduled]
        # For each time slot: [available_hours, is_used]
        # Plus global state: [total_scheduled_hours, num_assignments_complete]
        obs_dim = (
            self.max_assignments * 5 +  # Assignment features
            self.max_time_slots * 2 +    # Time slot features
            2                             # Global state
        )

        self.observation_space = spaces.Box(
            low=-10.0,
            high=10.0,
            shape=(obs_dim,),
            dtype=np.float32
        )

        # Initialize state
        self.reset()

    def reset(self) -> np.ndarray:
        """Reset the environment to initial state"""
        # Track remaining hours for each assignment
        self.assignment_hours_remaining = np.array([
            a.get('estimated_hours', 0.0)
            for a in self.original_assignments
        ] + [0.0] * (self.max_assignments - self.n_assignments))

        # Track which assignments are complete
        self.assignment_scheduled = np.zeros(self.max_assignments, dtype=bool)

        # Track available hours in each time slot
        self.slot_available_hours = np.array([
            s.get('duration_hours', 0.0)
            for s in self.original_time_slots
        ] + [0.0] * (self.max_time_slots - self.n_time_slots))

        # Track which slots are used
        self.slot_used = np.zeros(self.max_time_slots, dtype=bool)

        # Global state
        self.total_scheduled_hours = 0.0
        self.num_assignments_complete = 0

        # Schedule history (for reconstruction)
        self.schedule = []

        # Current step
        self.current_step = 0
        self.max_steps = self.n_assignments * 3  # Allow multiple sessions per assignment

        return self._get_observation()

    def _get_observation(self) -> np.ndarray:
        """Get current observation/state"""
        obs = []

        # Assignment features
        current_time = datetime.now()
        for i in range(self.max_assignments):
            if i < self.n_assignments:
                assignment = self.original_assignments[i]

                # Normalize features
                hours_remaining = self.assignment_hours_remaining[i] / 20.0  # Normalize by max ~20 hours

                # Days until due (can be negative if overdue)
                due_date = assignment.get('due_date', current_time + timedelta(days=7))
                days_until_due = (due_date - current_time).total_seconds() / (24 * 3600)
                days_until_due = days_until_due / 14.0  # Normalize by 2 weeks

                # Priority (1-3, normalize to 0-1)
                priority = assignment.get('priority', 2) / 3.0

                # Difficulty (1-3, normalize to 0-1)
                difficulty = assignment.get('difficulty', 2) / 3.0

                # Is scheduled (boolean)
                is_scheduled = 1.0 if self.assignment_scheduled[i] else 0.0

                obs.extend([hours_remaining, days_until_due, priority, difficulty, is_scheduled])
            else:
                # Padding for unused assignment slots
                obs.extend([0.0, 0.0, 0.0, 0.0, 0.0])

        # Time slot features
        for i in range(self.max_time_slots):
            if i < self.n_time_slots:
                available_hours = self.slot_available_hours[i] / 4.0  # Normalize by max ~4 hour slots
                is_used = 1.0 if self.slot_used[i] else 0.0
                obs.extend([available_hours, is_used])
            else:
                obs.extend([0.0, 0.0])

        # Global state
        total_hours_norm = self.total_scheduled_hours / 100.0  # Normalize
        completion_rate = self.num_assignments_complete / max(self.n_assignments, 1)
        obs.extend([total_hours_norm, completion_rate])

        return np.array(obs, dtype=np.float32)

    def _decode_action(self, action: int) -> Tuple[Optional[int], Optional[int]]:
        """
        Decode action into (assignment_idx, slot_idx) or None for SKIP

        Returns:
            (assignment_idx, slot_idx) or (None, None) for SKIP
        """
        # Last action is SKIP
        if action >= self.max_assignments * self.max_time_slots:
            return None, None

        # Decode flattened action
        assignment_idx = action // self.max_time_slots
        slot_idx = action % self.max_time_slots

        return assignment_idx, slot_idx

    def step(self, action: int) -> Tuple[np.ndarray, float, bool, Dict]:
        """
        Execute one step in the environment

        Args:
            action: Action to take

        Returns:
            observation, reward, done, info
        """
        self.current_step += 1

        # Decode action
        assignment_idx, slot_idx = self._decode_action(action)

        # Initialize reward
        reward = 0.0
        info = {'action': 'skip'}

        # Handle SKIP action
        if assignment_idx is None:
            # Small penalty for skipping to encourage action
            reward = -0.1
            info = {'action': 'skip'}

        # Validate action
        elif (assignment_idx >= self.n_assignments or
              slot_idx >= self.n_time_slots or
              self.assignment_hours_remaining[assignment_idx] <= 0 or
              self.slot_available_hours[slot_idx] <= 0):
            # Invalid action - strong penalty
            reward = -1.0
            info = {'action': 'invalid'}

        else:
            # Valid action - schedule the assignment in the slot
            assignment = self.original_assignments[assignment_idx]
            time_slot = self.original_time_slots[slot_idx]

            # Calculate session duration (up to 3 hours max per session)
            session_duration = min(
                self.assignment_hours_remaining[assignment_idx],
                self.slot_available_hours[slot_idx],
                3.0
            )

            # Update state
            self.assignment_hours_remaining[assignment_idx] -= session_duration
            self.slot_available_hours[slot_idx] -= session_duration
            self.total_scheduled_hours += session_duration

            # Mark assignment as complete if all hours scheduled
            if self.assignment_hours_remaining[assignment_idx] <= 0.1:
                self.assignment_scheduled[assignment_idx] = True
                self.num_assignments_complete += 1

            # Mark slot as used
            if self.slot_available_hours[slot_idx] <= 0.1:
                self.slot_used[slot_idx] = True

            # Store in schedule
            self.schedule.append({
                'assignment_idx': assignment_idx,
                'assignment_id': assignment.get('id'),
                'slot_idx': slot_idx,
                'start_time': time_slot.get('start_time'),
                'duration': session_duration
            })

            # Calculate reward
            reward = self._calculate_reward(assignment_idx, slot_idx, session_duration, assignment)

            info = {
                'action': 'schedule',
                'assignment_idx': assignment_idx,
                'slot_idx': slot_idx,
                'duration': session_duration
            }

        # Check if done
        done = (
            self.current_step >= self.max_steps or
            self.num_assignments_complete >= self.n_assignments or
            np.all(self.slot_available_hours <= 0.1)
        )

        # Get new observation
        obs = self._get_observation()

        return obs, reward, done, info

    def _calculate_reward(
        self,
        assignment_idx: int,
        slot_idx: int,
        session_duration: float,
        assignment: Dict
    ) -> float:
        """
        Calculate reward for scheduling an assignment

        Reward components:
        1. Completion bonus (finished assignment)
        2. Deadline adherence (earlier is better)
        3. Workload balance (avoid cramming)
        4. Session length (prefer reasonable sessions)
        """
        reward = 0.0

        # 1. Completion bonus
        if self.assignment_hours_remaining[assignment_idx] <= 0.1:
            reward += 10.0  # Big bonus for completing assignment

        # 2. Deadline adherence
        current_time = datetime.now()
        due_date = assignment.get('due_date', current_time + timedelta(days=7))
        slot_time = self.original_time_slots[slot_idx].get('start_time', current_time)

        days_before_deadline = (due_date - slot_time).total_seconds() / (24 * 3600)

        if days_before_deadline < 0:
            # Scheduling after deadline - bad!
            reward -= 10.0
        elif days_before_deadline < 1:
            # Very close to deadline - risky
            reward += 2.0
        elif days_before_deadline < 3:
            # Close to deadline - good
            reward += 5.0
        else:
            # Early - excellent
            reward += 3.0

        # 3. Priority bonus
        priority = assignment.get('priority', 2)
        if priority == 3:  # High priority
            reward += 2.0
        elif priority == 2:  # Medium
            reward += 1.0

        # 4. Session length reward (prefer 1-3 hour sessions)
        if 1.0 <= session_duration <= 3.0:
            reward += 1.0
        elif session_duration < 0.5:
            reward -= 0.5  # Too short

        # 5. Efficiency bonus (using time slot well)
        slot_capacity = self.original_time_slots[slot_idx].get('duration_hours', 1.0)
        utilization = session_duration / slot_capacity
        if utilization > 0.7:  # Using >70% of slot
            reward += 1.0

        return reward

    def render(self, mode='human'):
        """Render the current state (for debugging)"""
        print("\n" + "="*60)
        print(f"Step: {self.current_step}/{self.max_steps}")
        print(f"Scheduled Hours: {self.total_scheduled_hours:.1f}")
        print(f"Assignments Complete: {self.num_assignments_complete}/{self.n_assignments}")
        print(f"Schedule Items: {len(self.schedule)}")
        print("="*60)

    def get_schedule(self) -> List[Dict]:
        """Get the final schedule"""
        return self.schedule
