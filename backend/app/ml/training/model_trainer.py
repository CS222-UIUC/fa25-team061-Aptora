"""
Model training pipeline for XGBoost time estimator
Trains on historical study session feedback data
"""
import numpy as np
import pandas as pd
import logging
from typing import Dict, List, Tuple, Optional
from sqlalchemy.orm import Session
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from datetime import datetime

from ...models import StudySessionFeedback, StudySession, Assignment
from ..feature_engineering import FeatureEngineer
from ..models.xgboost_estimator import XGBoostTimeEstimator

logger = logging.getLogger(__name__)


class ModelTrainer:
    """
    Trains XGBoost model on historical feedback data
    """

    def __init__(self, db: Session):
        self.db = db
        self.feature_engineer = FeatureEngineer(db)

    def collect_training_data(self, min_samples: int = 20) -> Optional[Tuple[np.ndarray, np.ndarray, List[Dict]]]:
        """
        Collect training data from study session feedback

        Args:
            min_samples: Minimum number of samples required for training

        Returns:
            Tuple of (X_features, y_actual_hours, metadata) or None if insufficient data
        """
        logger.info("Collecting training data from study session feedback...")

        # Query all feedback with completed study sessions
        feedbacks = self.db.query(StudySessionFeedback).join(
            StudySession
        ).filter(
            StudySession.is_completed == True,
            StudySessionFeedback.actual_duration_hours.isnot(None)
        ).all()

        if len(feedbacks) < min_samples:
            logger.warning(f"Insufficient training data: {len(feedbacks)} samples (minimum: {min_samples})")
            return None

        logger.info(f"Found {len(feedbacks)} training samples")

        X_data = []
        y_data = []
        metadata = []

        for feedback in feedbacks:
            try:
                study_session = feedback.study_session
                assignment = study_session.assignment

                if not assignment:
                    continue

                # Extract features for this assignment
                features = self.feature_engineer.extract_features(
                    assignment,
                    study_session.user_id
                )

                # Convert features to array
                feature_array = self._features_dict_to_array(features)

                # Target: actual duration from feedback
                actual_hours = feedback.actual_duration_hours

                # Skip invalid data
                if actual_hours <= 0 or actual_hours > 100:
                    continue

                X_data.append(feature_array)
                y_data.append(actual_hours)

                # Store metadata for analysis
                metadata.append({
                    'feedback_id': feedback.id,
                    'assignment_id': assignment.id,
                    'user_id': study_session.user_id,
                    'estimated_hours': assignment.estimated_hours,
                    'actual_hours': actual_hours,
                    'productivity_rating': feedback.productivity_rating,
                    'difficulty_rating': feedback.difficulty_rating
                })

            except Exception as e:
                logger.error(f"Error processing feedback {feedback.id}: {e}")
                continue

        if len(X_data) == 0:
            logger.warning("No valid training samples after processing")
            return None

        X = np.vstack(X_data)
        y = np.array(y_data)

        logger.info(f"Prepared {len(X)} valid training samples")
        logger.info(f"Target hours - Mean: {y.mean():.2f}, Std: {y.std():.2f}, Min: {y.min():.2f}, Max: {y.max():.2f}")

        return X, y, metadata

    def train_model(self, test_size: float = 0.2, random_state: int = 42) -> Dict:
        """
        Train XGBoost model on collected feedback data

        Args:
            test_size: Proportion of data to use for testing
            random_state: Random seed for reproducibility

        Returns:
            Dictionary with training results and metrics
        """
        logger.info("Starting model training...")

        # Collect training data
        training_data = self.collect_training_data()

        if training_data is None:
            return {
                'success': False,
                'error': 'Insufficient training data',
                'samples_required': 20
            }

        X, y, metadata = training_data

        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=random_state
        )

        logger.info(f"Training set: {len(X_train)} samples")
        logger.info(f"Test set: {len(X_test)} samples")

        # Initialize and train model
        estimator = XGBoostTimeEstimator(self.db)
        estimator.model.fit(X_train, y_train)
        estimator.is_trained = True

        # Evaluate on training set
        train_predictions = estimator.model.predict(X_train)
        train_mae = mean_absolute_error(y_train, train_predictions)
        train_rmse = np.sqrt(mean_squared_error(y_train, train_predictions))
        train_r2 = r2_score(y_train, train_predictions)

        # Evaluate on test set
        test_predictions = estimator.model.predict(X_test)
        test_mae = mean_absolute_error(y_test, test_predictions)
        test_rmse = np.sqrt(mean_squared_error(y_test, test_predictions))
        test_r2 = r2_score(y_test, test_predictions)

        # Cross-validation (if enough data)
        cv_scores = None
        if len(X) >= 50:
            cv_scores = cross_val_score(
                estimator.model, X, y, cv=5,
                scoring='neg_mean_absolute_error'
            )
            cv_mae = -cv_scores.mean()
        else:
            cv_mae = None

        # Save model
        estimator.model_version = f"v1.0_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        save_success = estimator.save_model()

        results = {
            'success': True,
            'model_version': estimator.model_version,
            'training_samples': len(X_train),
            'test_samples': len(X_test),
            'train_metrics': {
                'mae': round(train_mae, 3),
                'rmse': round(train_rmse, 3),
                'r2': round(train_r2, 3)
            },
            'test_metrics': {
                'mae': round(test_mae, 3),
                'rmse': round(test_rmse, 3),
                'r2': round(test_r2, 3)
            },
            'cv_mae': round(cv_mae, 3) if cv_mae else None,
            'model_saved': save_success,
            'trained_at': datetime.now().isoformat()
        }

        logger.info(f"Training complete!")
        logger.info(f"Test MAE: {test_mae:.3f} hours")
        logger.info(f"Test RMSE: {test_rmse:.3f} hours")
        logger.info(f"Test R²: {test_r2:.3f}")

        return results

    def evaluate_against_baseline(self) -> Dict:
        """
        Compare XGBoost model against simple baseline (user estimates)

        Returns:
            Dictionary comparing model vs baseline performance
        """
        training_data = self.collect_training_data()

        if training_data is None:
            return {'error': 'Insufficient data for evaluation'}

        X, y_actual, metadata = training_data

        # Get user estimates
        user_estimates = np.array([m['estimated_hours'] for m in metadata])

        # Get XGBoost predictions
        estimator = XGBoostTimeEstimator(self.db)
        if not estimator.is_trained:
            return {'error': 'Model not trained'}

        ml_predictions = estimator.model.predict(X)

        # Calculate metrics for both
        baseline_mae = mean_absolute_error(y_actual, user_estimates)
        ml_mae = mean_absolute_error(y_actual, ml_predictions)

        baseline_rmse = np.sqrt(mean_squared_error(y_actual, user_estimates))
        ml_rmse = np.sqrt(mean_squared_error(y_actual, ml_predictions))

        # Improvement percentage
        mae_improvement = ((baseline_mae - ml_mae) / baseline_mae) * 100
        rmse_improvement = ((baseline_rmse - ml_rmse) / baseline_rmse) * 100

        return {
            'baseline_mae': round(baseline_mae, 3),
            'ml_mae': round(ml_mae, 3),
            'mae_improvement_pct': round(mae_improvement, 2),
            'baseline_rmse': round(baseline_rmse, 3),
            'ml_rmse': round(ml_rmse, 3),
            'rmse_improvement_pct': round(rmse_improvement, 2),
            'samples_evaluated': len(y_actual)
        }

    def _features_dict_to_array(self, features: Dict) -> np.ndarray:
        """Convert feature dictionary to numpy array in correct order"""
        feature_names = [
            'task_type_assignment', 'task_type_exam', 'task_type_project',
            'difficulty_easy', 'difficulty_medium', 'difficulty_hard',
            'estimated_hours', 'priority_low', 'priority_medium', 'priority_high',
            'days_until_due', 'course_difficulty_score', 'avg_weekly_hours',
            'course_level', 'avg_session_duration', 'total_completed_sessions',
            'completion_rate', 'concurrent_assignments', 'week_of_semester'
        ]

        feature_values = []
        for name in feature_names:
            value = features.get(name, 0.0)
            if value is None:
                value = 0.0
            feature_values.append(float(value))

        return np.array(feature_values)
