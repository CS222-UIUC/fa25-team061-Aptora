#!/usr/bin/env python3
"""
Train the RL-based scheduler on synthetic scheduling problems
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from app.database import SessionLocal
from app.ml.rl.rl_scheduler import RLScheduler
from datetime import datetime, timedelta
import random
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def generate_training_scenarios(num_scenarios: int = 10) -> list:
    """
    Generate synthetic scheduling scenarios for training

    Each scenario has:
    - Multiple assignments with varying priorities, difficulties, due dates
    - Multiple time slots with varying durations
    """
    scenarios = []

    for scenario_idx in range(num_scenarios):
        # Random number of assignments (3-10)
        n_assignments = random.randint(3, 10)

        # Random number of time slots (10-30)
        n_time_slots = random.randint(10, 30)

        # Generate assignments
        assignments = []
        base_date = datetime.now()

        for i in range(n_assignments):
            assignments.append({
                'id': scenario_idx * 100 + i,
                'estimated_hours': random.uniform(2, 15),
                'due_date': base_date + timedelta(days=random.randint(1, 21)),
                'priority': random.randint(1, 3),
                'difficulty': random.randint(1, 3)
            })

        # Generate time slots
        time_slots = []
        current_date = base_date

        for day in range(21):  # 3 weeks of slots
            # 2-4 slots per day
            slots_per_day = random.randint(2, 4)

            for slot in range(slots_per_day):
                # Random start hour (8am - 8pm)
                start_hour = random.randint(8, 20)

                # Random duration (1-4 hours)
                duration = random.uniform(1, 4)

                start_time = current_date + timedelta(days=day, hours=start_hour)

                time_slots.append({
                    'start_time': start_time,
                    'end_time': start_time + timedelta(hours=duration),
                    'duration_hours': duration
                })

            current_date += timedelta(days=1)

        scenarios.append({
            'assignments': assignments,
            'time_slots': time_slots
        })

    return scenarios


def main():
    print("\n" + "="*80)
    print("RL Scheduler Training")
    print("="*80)

    db = SessionLocal()

    try:
        # Generate training data
        print("\nGenerating synthetic training scenarios...")
        training_scenarios = generate_training_scenarios(num_scenarios=20)
        print(f"Generated {len(training_scenarios)} training scenarios")

        # Show sample scenario
        sample = training_scenarios[0]
        print(f"\nSample scenario:")
        print(f"  Assignments: {len(sample['assignments'])}")
        print(f"  Time slots: {len(sample['time_slots'])}")
        print(f"  Total hours to schedule: {sum(a['estimated_hours'] for a in sample['assignments']):.1f}")
        print(f"  Total available hours: {sum(s['duration_hours'] for s in sample['time_slots']):.1f}")

        # Create RL scheduler
        print("\nInitializing RL scheduler...")
        rl_scheduler = RLScheduler(db)

        # Train the model
        print("\nTraining PPO agent...")
        print("This will take several minutes...")
        print("(Training on 100,000 timesteps)")

        results = rl_scheduler.train(
            training_data=training_scenarios,
            total_timesteps=100000,  # Can increase for better performance
            verbose=1
        )

        if not results['success']:
            print(f"\n❌ Training failed: {results.get('error', 'Unknown error')}")
            return 1

        # Display results
        print("\n" + "="*80)
        print("✓ TRAINING COMPLETE!")
        print("="*80)
        print(f"\nTotal Timesteps: {results['total_timesteps']}")
        print(f"Model Saved: {results['model_saved']}")
        print(f"Model Path: {results['model_path']}")

        # Test the trained model
        print("\n" + "="*80)
        print("Testing Trained Model")
        print("="*80)

        test_scenario = training_scenarios[0]
        print(f"\nTest scenario:")
        print(f"  Assignments: {len(test_scenario['assignments'])}")
        print(f"  Time slots: {len(test_scenario['time_slots'])}")

        # Mock Assignment objects for testing
        class MockAssignment:
            def __init__(self, data):
                self.id = data['id']
                self.estimated_hours = data['estimated_hours']
                self.due_date = data['due_date']
                self.priority = MockEnum(data['priority'])
                self.difficulty = MockEnum(data['difficulty'])

        class MockEnum:
            def __init__(self, value):
                self.value = {1: 'low', 2: 'medium', 3: 'high'}[value]

        test_assignments = [MockAssignment(a) for a in test_scenario['assignments']]

        # Generate schedule using RL
        print("\nGenerating schedule with RL agent...")
        rl_schedule = rl_scheduler.generate_schedule(
            assignments=test_assignments,
            time_slots=test_scenario['time_slots'],
            use_rl=True
        )

        print(f"\n✓ Generated {len(rl_schedule)} study sessions")

        # Calculate metrics
        total_scheduled = sum(
            (s['end_time'] - s['start_time']).total_seconds() / 3600
            for s in rl_schedule
        )

        print(f"  Total scheduled hours: {total_scheduled:.1f}")
        print(f"  Average session length: {total_scheduled / len(rl_schedule):.1f}h" if rl_schedule else "N/A")

        # Show sample sessions
        print("\nSample sessions:")
        for i, session in enumerate(rl_schedule[:5]):
            duration = (session['end_time'] - session['start_time']).total_seconds() / 3600
            print(f"  {i+1}. Assignment {session['assignment_id']}: "
                  f"{session['start_time'].strftime('%Y-%m-%d %H:%M')} ({duration:.1f}h)")

        if len(rl_schedule) > 5:
            print(f"  ... and {len(rl_schedule) - 5} more sessions")

        # Compare with greedy
        print("\nComparing with greedy algorithm...")
        greedy_schedule = rl_scheduler.generate_schedule(
            assignments=test_assignments,
            time_slots=test_scenario['time_slots'],
            use_rl=False
        )

        greedy_hours = sum(
            (s['end_time'] - s['start_time']).total_seconds() / 3600
            for s in greedy_schedule
        )

        print(f"\nGreedy scheduler:")
        print(f"  Sessions: {len(greedy_schedule)}")
        print(f"  Total hours: {greedy_hours:.1f}")

        print(f"\nRL scheduler:")
        print(f"  Sessions: {len(rl_schedule)}")
        print(f"  Total hours: {total_scheduled:.1f}")

        print("\n" + "="*80)
        print("\nThe RL model is now ready to use!")
        print("It will be automatically used when generating schedules.")
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
