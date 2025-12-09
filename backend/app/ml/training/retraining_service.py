"""
Automatic model retraining service
Monitors feedback data and triggers retraining when needed
"""
import logging
from typing import Dict, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from pathlib import Path

from ...models import StudySessionFeedback, StudySession
from .model_trainer import ModelTrainer
from ..models.xgboost_estimator import XGBoostTimeEstimator

logger = logging.getLogger(__name__)


class RetrainingService:
    """
    Service for automatic model retraining based on new feedback data
    """

    def __init__(
        self,
        db: Session,
        min_new_samples: int = 50,
        min_improvement_pct: float = 5.0
    ):
        """
        Initialize retraining service

        Args:
            db: Database session
            min_new_samples: Minimum new feedback samples before retraining
            min_improvement_pct: Minimum improvement required to replace model
        """
        self.db = db
        self.min_new_samples = min_new_samples
        self.min_improvement_pct = min_improvement_pct
        self.trainer = ModelTrainer(db)

    def check_retraining_needed(self) -> Dict:
        """
        Check if model retraining is needed

        Returns:
            Dictionary with retraining status and statistics
        """
        try:
            # Get current model info
            current_model = XGBoostTimeEstimator(self.db)

            if not current_model.is_trained:
                return {
                    'retraining_needed': True,
                    'reason': 'No trained model exists',
                    'current_model_version': None,
                    'total_feedback': self._count_total_feedback(),
                    'new_feedback_since_training': 0
                }

            # Count total feedback
            total_feedback = self._count_total_feedback()

            # Estimate feedback used in current model (based on model age)
            # If we had model training metadata, we'd use that
            # For now, assume all current feedback is "new"
            new_feedback = total_feedback

            # Check if we have enough new samples
            needs_retraining = new_feedback >= self.min_new_samples

            return {
                'retraining_needed': needs_retraining,
                'reason': f'{new_feedback} feedback samples available' if needs_retraining else 'Insufficient new feedback',
                'current_model_version': current_model.model_version,
                'total_feedback': total_feedback,
                'new_feedback_since_training': new_feedback,
                'threshold': self.min_new_samples
            }

        except Exception as e:
            logger.error(f"Error checking retraining status: {e}", exc_info=True)
            return {
                'retraining_needed': False,
                'error': str(e)
            }

    def retrain_model(self, force: bool = False) -> Dict:
        """
        Retrain the model if conditions are met

        Args:
            force: Force retraining even if conditions not met

        Returns:
            Dictionary with retraining results
        """
        try:
            # Check if retraining needed
            if not force:
                status = self.check_retraining_needed()
                if not status['retraining_needed']:
                    return {
                        'success': False,
                        'reason': status['reason'],
                        'retraining_needed': False
                    }

            logger.info("Starting automatic model retraining...")

            # Get current model performance for comparison
            old_performance = self._get_current_model_performance()

            # Train new model
            training_results = self.trainer.train_model()

            if not training_results['success']:
                return {
                    'success': False,
                    'error': training_results.get('error', 'Training failed')
                }

            # Compare performance
            new_mae = training_results['test_metrics']['mae']
            old_mae = old_performance.get('test_mae', float('inf'))

            improvement_pct = ((old_mae - new_mae) / old_mae * 100) if old_mae > 0 else 0

            # Decide whether to keep new model
            should_keep = (
                old_mae == float('inf') or  # No previous model
                improvement_pct >= -self.min_improvement_pct  # Not significantly worse
            )

            if should_keep:
                logger.info(f"New model accepted (improvement: {improvement_pct:.1f}%)")
                action = 'promoted'
            else:
                logger.warning(f"New model rejected (worse by {abs(improvement_pct):.1f}%)")
                # In production, we'd restore the old model here
                action = 'rejected'

            return {
                'success': True,
                'action': action,
                'new_model_version': training_results['model_version'],
                'old_performance': old_performance,
                'new_performance': {
                    'test_mae': new_mae,
                    'test_rmse': training_results['test_metrics']['rmse'],
                    'test_r2': training_results['test_metrics']['r2']
                },
                'improvement_pct': round(improvement_pct, 2),
                'training_samples': training_results['training_samples'],
                'test_samples': training_results['test_samples']
            }

        except Exception as e:
            logger.error(f"Retraining failed: {e}", exc_info=True)
            return {
                'success': False,
                'error': str(e)
            }

    def _count_total_feedback(self) -> int:
        """Count total valid feedback entries"""
        return self.db.query(StudySessionFeedback).join(
            StudySession
        ).filter(
            StudySession.is_completed == True,
            StudySessionFeedback.actual_duration_hours.isnot(None)
        ).count()

    def _get_current_model_performance(self) -> Dict:
        """Get performance metrics of current model"""
        try:
            current_model = XGBoostTimeEstimator(self.db)

            if not current_model.is_trained:
                return {
                    'model_version': None,
                    'test_mae': float('inf')
                }

            # Evaluate current model
            evaluation = self.trainer.evaluate_against_baseline()

            if 'error' in evaluation:
                return {
                    'model_version': current_model.model_version,
                    'test_mae': float('inf')
                }

            return {
                'model_version': current_model.model_version,
                'test_mae': evaluation['ml_mae']
            }

        except Exception as e:
            logger.error(f"Error getting current model performance: {e}")
            return {
                'model_version': 'unknown',
                'test_mae': float('inf')
            }

    def schedule_periodic_retraining(self, interval_days: int = 7) -> Dict:
        """
        Schedule periodic retraining checks

        Args:
            interval_days: Check interval in days

        Returns:
            Dictionary with scheduling info

        Note: In production, this would integrate with Celery/APScheduler
        """
        return {
            'scheduled': False,
            'message': 'Automatic scheduling requires Celery integration',
            'recommendation': f'Manually check retraining every {interval_days} days',
            'endpoint': 'POST /schedules/ml/retrain'
        }
