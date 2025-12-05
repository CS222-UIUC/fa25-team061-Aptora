"""
ML-based study time estimator (simplified MVP version)
"""
import numpy as np
import logging
from typing import Dict, Optional
from sqlalchemy.orm import Session

from ...models import Assignment, DifficultyLevel, TaskType
from ..feature_engineering import FeatureEngineer

logger = logging.getLogger(__name__)


class StudyTimeEstimator:
    """
    Rule-based time estimator with ML-inspired features
    (Simplified version - full ML model training can be added later)
    """

    def __init__(self, db: Session):
        self.db = db
        self.feature_engineer = FeatureEngineer(db)

        # Baseline multipliers (these would be learned from data in full ML version)
        self.difficulty_multipliers = {
            'easy': 0.7,
            'medium': 1.0,
            'hard': 1.5
        }

        self.task_type_multipliers = {
            'assignment': 1.0,
            'exam': 2.0,  # Exams need more prep time
            'project': 1.8
        }

    def predict(self, assignment: Assignment, user_id: int) -> Dict:
        """
        Predict study time required for an assignment

        Args:
            assignment: Assignment object
            user_id: User ID for personalization

        Returns:
            Dictionary with prediction, confidence, and explanation
        """
        try:
            # Extract features
            features = self.feature_engineer.extract_features(assignment, user_id)

            # Base prediction from user's estimate
            base_hours = assignment.estimated_hours

            # Apply difficulty multiplier
            difficulty_mult = self.difficulty_multipliers.get(
                assignment.difficulty.value,
                1.0
            )

            # Apply task type multiplier
            task_mult = self.task_type_multipliers.get(
                assignment.task_type.value,
                1.0
            )

            # Course difficulty adjustment (from scraped data)
            course_difficulty = features.get('course_difficulty_score', 5.0)
            course_mult = 0.8 + (course_difficulty / 10.0) * 0.4  # Range: 0.8 to 1.2

            # Workload adjustment
            concurrent = features.get('concurrent_assignments', 0)
            concurrent_mult = 1.0 + (concurrent * 0.05)  # +5% per concurrent assignment

            # Combined prediction
            predicted_hours = (
                base_hours *
                difficulty_mult *
                task_mult *
                course_mult *
                concurrent_mult
            )

            # Calculate confidence (higher for more data)
            confidence = self._calculate_confidence(features)

            # Confidence interval (±20%)
            std_dev = predicted_hours * 0.2
            confidence_interval = (
                max(0.5, predicted_hours - std_dev),
                predicted_hours + std_dev
            )

            # Feature importance (for explainability)
            feature_importance = {
                'base_estimate': base_hours,
                'difficulty_adjustment': f"{difficulty_mult:.2f}x",
                'task_type_adjustment': f"{task_mult:.2f}x",
                'course_difficulty': f"{course_mult:.2f}x",
                'workload_factor': f"{concurrent_mult:.2f}x"
            }

            return {
                'predicted_hours': round(predicted_hours, 2),
                'confidence': round(confidence, 2),
                'confidence_interval': (
                    round(confidence_interval[0], 2),
                    round(confidence_interval[1], 2)
                ),
                'feature_importance': feature_importance
            }

        except Exception as e:
            logger.error(f"Prediction failed: {e}", exc_info=True)
            # Fallback to user estimate
            return {
                'predicted_hours': assignment.estimated_hours,
                'confidence': 0.5,
                'confidence_interval': (
                    assignment.estimated_hours * 0.8,
                    assignment.estimated_hours * 1.2
                ),
                'feature_importance': {'error': 'Using fallback estimate'}
            }

    def _calculate_confidence(self, features: Dict) -> float:
        """
        Calculate prediction confidence based on available data

        Args:
            features: Feature dictionary

        Returns:
            Confidence score (0-1)
        """
        confidence = 0.5  # Base confidence

        # Increase confidence if we have course difficulty data
        if features.get('course_difficulty_score', 5.0) != 5.0:
            confidence += 0.2

        # Increase confidence if user has history
        if features.get('total_completed_sessions', 0) > 5:
            confidence += 0.2

        # Decrease confidence for extreme workload
        if features.get('concurrent_assignments', 0) > 5:
            confidence -= 0.1

        return max(0.3, min(0.95, confidence))
