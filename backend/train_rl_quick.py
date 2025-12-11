#!/usr/bin/env python3
"""
Quick RL training script (10K timesteps for testing)
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

# Run the full training with reduced timesteps
from train_rl_scheduler import *

if __name__ == "__main__":
    print("\n" + "="*80)
    print("RL Scheduler Quick Training (10K timesteps)")
    print("="*80)

    db = SessionLocal()

    try:
        # Generate smaller training set
        print("\nGenerating training scenarios...")
        training_scenarios = generate_training_scenarios(num_scenarios=5)
        print(f"Generated {len(training_scenarios)} training scenarios")

        # Create RL scheduler
        print("\nInitializing RL scheduler...")
        rl_scheduler = RLScheduler(db)

        # Quick training
        print("\nTraining PPO agent (quick mode - 10,000 timesteps)...")
        results = rl_scheduler.train(
            training_data=training_scenarios,
            total_timesteps=10000,  # Reduced for quick testing
            verbose=1
        )

        if results['success']:
            print("\n✓ Training complete!")
            print(f"  Model saved: {results['model_saved']}")
            print(f"  Path: {results['model_path']}")
        else:
            print(f"\n❌ Training failed: {results.get('error')}")

    finally:
        db.close()
