#!/usr/bin/env python3
"""
Check if model retraining is needed and retrain if necessary
This script can be run periodically (e.g., daily cron job)
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from app.database import SessionLocal
from app.ml.training.retraining_service import RetrainingService
import logging
import argparse

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    parser = argparse.ArgumentParser(description='Check and retrain ML model if needed')
    parser.add_argument(
        '--force',
        action='store_true',
        help='Force retraining even if conditions not met'
    )
    parser.add_argument(
        '--min-samples',
        type=int,
        default=50,
        help='Minimum new samples before retraining (default: 50)'
    )
    parser.add_argument(
        '--check-only',
        action='store_true',
        help='Only check status, do not retrain'
    )

    args = parser.parse_args()

    print("\n" + "="*80)
    print("Automatic Model Retraining Service")
    print("="*80)

    db = SessionLocal()

    try:
        # Create retraining service
        service = RetrainingService(
            db,
            min_new_samples=args.min_samples,
            min_improvement_pct=5.0
        )

        # Check status
        print("\nChecking retraining status...")
        status = service.check_retraining_needed()

        print(f"\nCurrent Status:")
        print(f"  Model Version: {status.get('current_model_version', 'None')}")
        print(f"  Total Feedback: {status['total_feedback']}")
        print(f"  New Samples: {status.get('new_feedback_since_training', 0)}")
        print(f"  Threshold: {status['threshold']}")
        print(f"  Retraining Needed: {status['retraining_needed']}")
        print(f"  Reason: {status['reason']}")

        # Check-only mode
        if args.check_only:
            print("\n✓ Check complete (--check-only mode)")
            return 0

        # Retrain if needed (or forced)
        if status['retraining_needed'] or args.force:
            if args.force:
                print("\n⚠ Force retraining requested (--force)")
            else:
                print("\n✓ Conditions met, starting retraining...")

            print("\nRetraining model...")
            results = service.retrain_model(force=args.force)

            if not results['success']:
                print(f"\n❌ Retraining failed: {results.get('error', 'Unknown error')}")
                return 1

            # Display results
            print("\n" + "="*80)
            print(f"✓ Model {results['action'].upper()}!")
            print("="*80)

            print(f"\nNew Model: {results['new_model_version']}")
            print(f"Training Samples: {results['training_samples']}")
            print(f"Test Samples: {results['test_samples']}")

            print("\nOld Performance:")
            old_perf = results['old_performance']
            print(f"  Model: {old_perf.get('model_version', 'N/A')}")
            print(f"  Test MAE: {old_perf.get('test_mae', 'N/A'):.3f} hours")

            print("\nNew Performance:")
            new_perf = results['new_performance']
            print(f"  Test MAE:  {new_perf['test_mae']:.3f} hours")
            print(f"  Test RMSE: {new_perf['test_rmse']:.3f} hours")
            print(f"  Test R²:   {new_perf['test_r2']:.3f}")

            improvement = results['improvement_pct']
            if improvement > 0:
                print(f"\nImprovement: +{improvement:.1f}% (better)")
            elif improvement < 0:
                print(f"\nChange: {improvement:.1f}% (worse)")
            else:
                print(f"\nChange: No significant change")

            print("\n" + "="*80)

            if results['action'] == 'promoted':
                print("✓ New model is now active for predictions")
            else:
                print("⚠ New model was not promoted (performance not better)")

            print("="*80 + "\n")

        else:
            print(f"\n✓ No retraining needed")
            print(f"   Current feedback count: {status['total_feedback']}")
            print(f"   Threshold: {status['threshold']}")
            print(f"   Need {status['threshold'] - status['total_feedback']} more samples")

        return 0

    except Exception as e:
        logger.error(f"Retraining check failed: {e}", exc_info=True)
        print(f"\n❌ Error: {str(e)}")
        return 1

    finally:
        db.close()


if __name__ == "__main__":
    sys.exit(main())
