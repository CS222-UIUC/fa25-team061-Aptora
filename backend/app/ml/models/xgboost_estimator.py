"""
XGBoost-based study time estimator - Real ML model
"""
import numpy as np
import xgboost as xgb
import logging
import joblib
from pathlib import Path
from typing import Dict, Optional, Tuple
from sqlalchemy.orm import Session

from ...models import Assignment
from ..feature_engineering import FeatureEngineer

logger = logging.getLogger(__name__)


class XGBoostTimeEstimator:
    """
    XGBoost-based time estimator that learns from historical feedback data
    """

    def __init__(self, db: Session, model_path: Optional[str] = None):
        self.db = db
        self.feature_engineer = FeatureEngineer(db)
        self.model = None
        self.model_version = "v1.0"
        self.is_trained = False

        # Default model path
        if model_path is None:
            model_path = Path(__file__).resolve().parent.parent.parent.parent / "models" / "xgboost_time_estimator.pkl"

        self.model_path = Path(model_path)

        # Try to load existing model
        self._load_model()

        # If no model exists, create untrained model
        if self.model is None:
            self._initialize_model()

    def _initialize_model(self):
        """Initialize a new XGBoost model with default hyperparameters"""
        self.model = xgb.XGBRegressor(
            objective='reg:squarederror',
            n_estimators=100,
            max_depth=5,
            learning_rate=0.1,
            subsample=0.8,
            colsample_bytree=0.8,
            random_state=42,
            n_jobs=-1
        )
        self.is_trained = False
        logger.info("Initialized new XGBoost model (untrained)")

    def _load_model(self):
        """Load trained model from disk"""
        try:
            if self.model_path.exists():
                saved_data = joblib.load(self.model_path)
                self.model = saved_data['model']
                self.model_version = saved_data.get('version', 'unknown')
                self.is_trained = saved_data.get('is_trained', False)
                logger.info(f"Loaded XGBoost model {self.model_version} from {self.model_path}")
            else:
                logger.info(f"No saved model found at {self.model_path}")
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            self.model = None

    def save_model(self):
        """Save trained model to disk"""
        try:
            # Create models directory if it doesn't exist
            self.model_path.parent.mkdir(parents=True, exist_ok=True)

            # Save model with metadata
            save_data = {
                'model': self.model,
                'version': self.model_version,
                'is_trained': self.is_trained,
                'feature_names': self._get_feature_names()
            }

            joblib.dump(save_data, self.model_path)
            logger.info(f"Saved model {self.model_version} to {self.model_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to save model: {e}")
            return False

    def _get_feature_names(self) -> list:
        """Get list of feature names in order"""
        return [
            'task_type_assignment', 'task_type_exam', 'task_type_project',
            'difficulty_easy', 'difficulty_medium', 'difficulty_hard',
            'estimated_hours', 'priority_low', 'priority_medium', 'priority_high',
            'days_until_due', 'course_difficulty_score', 'avg_weekly_hours',
            'course_level', 'avg_session_duration', 'total_completed_sessions',
            'completion_rate', 'concurrent_assignments', 'week_of_semester'
        ]

    def _features_dict_to_array(self, features: Dict) -> np.ndarray:
        """Convert feature dictionary to numpy array in correct order"""
        feature_names = self._get_feature_names()
        feature_values = []

        for name in feature_names:
            value = features.get(name, 0.0)
            # Handle None values
            if value is None:
                value = 0.0
            feature_values.append(float(value))

        return np.array(feature_values).reshape(1, -1)

    def predict(self, assignment: Assignment, user_id: int) -> Dict:
        """
        Predict study time required for an assignment using XGBoost

        Args:
            assignment: Assignment object
            user_id: User ID for personalization

        Returns:
            Dictionary with prediction, confidence, and explanation
        """
        try:
            # Extract features
            features = self.feature_engineer.extract_features(assignment, user_id)

            # If model is not trained, fall back to simple prediction
            if not self.is_trained:
                logger.warning("XGBoost model not trained, using baseline estimate")
                return self._fallback_prediction(assignment, features)

            # Convert features to array
            X = self._features_dict_to_array(features)

            # Make prediction
            predicted_hours = self.model.predict(X)[0]

            # Ensure prediction is reasonable (between 0.5 and 100 hours)
            predicted_hours = max(0.5, min(100.0, predicted_hours))

            # Calculate confidence based on model and data quality
            confidence = self._calculate_confidence(features, predicted_hours, assignment)

            # Calculate confidence interval using model's uncertainty
            # For now, use ±25% as std dev
            std_dev = predicted_hours * 0.25
            confidence_interval = (
                max(0.5, predicted_hours - std_dev),
                predicted_hours + std_dev
            )

            # Get feature importance from the model
            feature_importance = self._get_feature_importance()

            return {
                'predicted_hours': round(predicted_hours, 2),
                'confidence': round(confidence, 2),
                'confidence_interval': (
                    round(confidence_interval[0], 2),
                    round(confidence_interval[1], 2)
                ),
                'feature_importance': feature_importance,
                'model_version': self.model_version,
                'model_type': 'xgboost'
            }

        except Exception as e:
            logger.error(f"XGBoost prediction failed: {e}", exc_info=True)
            # Fallback to baseline
            return self._fallback_prediction(assignment, features)

    def _fallback_prediction(self, assignment: Assignment, features: Dict) -> Dict:
        """Fallback prediction when model is not available"""
        # Simple rule-based fallback
        base_hours = assignment.estimated_hours

        # Apply basic adjustments
        difficulty_mult = {'easy': 0.8, 'medium': 1.0, 'hard': 1.3}.get(
            assignment.difficulty.value, 1.0
        )

        predicted_hours = base_hours * difficulty_mult

        return {
            'predicted_hours': round(predicted_hours, 2),
            'confidence': 0.4,
            'confidence_interval': (
                round(predicted_hours * 0.7, 2),
                round(predicted_hours * 1.3, 2)
            ),
            'feature_importance': {'note': 'Model not trained - using fallback'},
            'model_version': 'fallback',
            'model_type': 'rule-based'
        }

    def _calculate_confidence(self, features: Dict, predicted_hours: float,
                            assignment: Assignment) -> float:
        """
        Calculate prediction confidence score

        Higher confidence when:
        - More historical data available
        - Course insights available
        - Prediction is close to user estimate (not too extreme)
        """
        confidence = 0.6  # Base confidence for trained model

        # Increase confidence if we have course difficulty data
        if features.get('course_difficulty_score', 5.0) != 5.0:
            confidence += 0.15

        # Increase confidence if user has history
        completed_sessions = features.get('total_completed_sessions', 0)
        if completed_sessions > 10:
            confidence += 0.15
        elif completed_sessions > 5:
            confidence += 0.1

        # Increase confidence if prediction is reasonable relative to estimate
        user_estimate = assignment.estimated_hours
        if user_estimate > 0:
            ratio = predicted_hours / user_estimate
            if 0.5 <= ratio <= 2.0:  # Within 2x of user estimate
                confidence += 0.1

        # Decrease confidence for extreme concurrent workload
        if features.get('concurrent_assignments', 0) > 7:
            confidence -= 0.1

        return max(0.3, min(0.95, confidence))

    def _get_feature_importance(self) -> Dict:
        """Get feature importance from trained model"""
        if not self.is_trained or self.model is None:
            return {'note': 'Model not trained'}

        try:
            # Get feature importance scores
            importance_scores = self.model.feature_importances_
            feature_names = self._get_feature_names()

            # Get top 5 most important features
            top_indices = np.argsort(importance_scores)[-5:][::-1]

            importance_dict = {}
            for idx in top_indices:
                feature_name = feature_names[idx]
                score = float(importance_scores[idx])
                importance_dict[feature_name] = round(score, 3)

            return importance_dict
        except Exception as e:
            logger.error(f"Failed to get feature importance: {e}")
            return {'error': str(e)}
