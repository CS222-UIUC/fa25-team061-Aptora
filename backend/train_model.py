#!/usr/bin/env python3
"""
CLI script to train the XGBoost time estimation model
Usage: python train_model.py
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from app.database import SessionLocal, engine, Base
from app.ml.training.model_trainer import ModelTrainer
from app.models import StudySessionFeedback, StudySession
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    """Train the XGBoost model on feedback data"""
    print("\n" + "="*80)
    print("XGBoost Time Estimator Training")
    print("="*80)

    # Create database session
    db = SessionLocal()

    try:
        # Check available training data
        print("\nChecking training data availability...")
        total_feedback = db.query(StudySessionFeedback).count()
        valid_feedback = db.query(StudySessionFeedback).join(
            StudySession
        ).filter(
            StudySession.is_completed == True,
            StudySessionFeedback.actual_duration_hours.isnot(None)
        ).count()

        print(f"Total feedback entries: {total_feedback}")
        print(f"Valid training samples: {valid_feedback}")
        print(f"Minimum required: 20")

        if valid_feedback < 20:
            print("\n❌ Insufficient training data!")
            print(f"Need at least 20 samples, have {valid_feedback}")
            print("\nTo get training data:")
            print("1. Create study sessions via the scheduler")
            print("2. Mark sessions as completed")
            print("3. Submit feedback with actual hours spent")
            return 1

        print(f"\n✓ Sufficient training data available ({valid_feedback} samples)")

        # Create trainer and train model
        print("\nInitializing model trainer...")
        trainer = ModelTrainer(db)

        print("\nTraining XGBoost model...")
        print("This may take a few moments...\n")

        results = trainer.train_model()

        if not results['success']:
            print(f"\n❌ Training failed: {results.get('error', 'Unknown error')}")
            return 1

        # Display results
        print("\n" + "="*80)
        print("✓ TRAINING COMPLETE!")
        print("="*80)
        print(f"\nModel Version: {results['model_version']}")
        print(f"Training Samples: {results['training_samples']}")
        print(f"Test Samples: {results['test_samples']}")
        print(f"Model Saved: {results['model_saved']}")

        print("\nTraining Metrics:")
        print(f"  MAE:  {results['train_metrics']['mae']:.3f} hours")
        print(f"  RMSE: {results['train_metrics']['rmse']:.3f} hours")
        print(f"  R²:   {results['train_metrics']['r2']:.3f}")

        print("\nTest Metrics:")
        print(f"  MAE:  {results['test_metrics']['mae']:.3f} hours")
        print(f"  RMSE: {results['test_metrics']['rmse']:.3f} hours")
        print(f"  R²:   {results['test_metrics']['r2']:.3f}")

        if results.get('cv_mae'):
            print(f"\nCross-Validation MAE: {results['cv_mae']:.3f} hours")

        # Evaluate against baseline
        print("\n" + "="*80)
        print("Model vs Baseline Comparison")
        print("="*80)

        baseline_results = trainer.evaluate_against_baseline()

        if 'error' not in baseline_results:
            print(f"\nBaseline (user estimates) MAE: {baseline_results['baseline_mae']:.3f} hours")
            print(f"XGBoost Model MAE:             {baseline_results['ml_mae']:.3f} hours")
            print(f"Improvement:                   {baseline_results['mae_improvement_pct']:.1f}%")
            print(f"\nSamples Evaluated: {baseline_results['samples_evaluated']}")

        print("\n" + "="*80)
        print("\nThe trained model will be automatically used for predictions.")
        print("API endpoint: POST /schedules/generate-ml")
        print("="*80 + "\n")

        return 0

    except Exception as e:
        logger.error(f"Training failed with error: {e}", exc_info=True)
        print(f"\n❌ Error: {str(e)}")
        return 1

    finally:
        db.close()


if __name__ == "__main__":
    sys.exit(main())
