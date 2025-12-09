#!/usr/bin/env python3
"""
Compare RL scheduler vs Greedy scheduler performance
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from app.database import SessionLocal
from app.ml.rl.rl_scheduler import RLScheduler
from datetime import datetime, timedelta
import random

def generate_test_scenario():
    """Generate a test scheduling scenario"""
    # Mock Assignment class
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

    # Generate assignments
    base_date = datetime.now()
    n_assignments = 8

    assignments_data = [
        {
            'id': i,
            'estimated_hours': random.uniform(3, 12),
            'due_date': base_date + timedelta(days=random.randint(2, 14)),
            'priority': random.randint(1, 3),
            'difficulty': random.randint(1, 3)
        }
        for i in range(n_assignments)
    ]

    assignments = [MockAssignment(a) for a in assignments_data]

    # Generate time slots (3 weeks, 2-3 slots per day)
    time_slots = []
    for day in range(21):
        for slot in range(random.randint(2, 3)):
            start_hour = random.randint(9, 18)
            duration = random.uniform(1.5, 3.5)

            start_time = base_date + timedelta(days=day, hours=start_hour)
            time_slots.append({
                'start_time': start_time,
                'end_time': start_time + timedelta(hours=duration),
                'duration_hours': duration
            })

    return assignments, time_slots, assignments_data

def main():
    print("\n" + "="*80)
    print("RL vs Greedy Scheduler Comparison")
    print("="*80)

    db = SessionLocal()

    try:
        # Generate test scenario
        assignments, time_slots, assignments_data = generate_test_scenario()

        print(f"\nTest Scenario:")
        print(f"  Assignments: {len(assignments)}")
        print(f"  Total hours to schedule: {sum(a.estimated_hours for a in assignments):.1f}h")
        print(f"  Time slots available: {len(time_slots)}")
        print(f"  Total available hours: {sum(s['duration_hours'] for s in time_slots):.1f}h")

        # Create RL scheduler
        rl_scheduler = RLScheduler(db)

        if not rl_scheduler.is_trained:
            print("\n❌ RL model not trained. Run 'python train_rl_quick.py' first.")
            return 1

        print("\n" + "-"*80)
        print("Generating schedules...")
        print("-"*80)

        # Generate with RL
        print("\n1. RL-Based Scheduler:")
        rl_schedule = rl_scheduler.generate_schedule(
            assignments=assignments,
            time_slots=time_slots,
            use_rl=True
        )

        rl_hours = sum((s['end_time'] - s['start_time']).total_seconds() / 3600 for s in rl_schedule)
        rl_assignments_covered = len(set(s['assignment_id'] for s in rl_schedule))

        print(f"   Sessions created: {len(rl_schedule)}")
        print(f"   Total hours scheduled: {rl_hours:.1f}h")
        print(f"   Assignments covered: {rl_assignments_covered}/{len(assignments)}")
        print(f"   Avg session length: {rl_hours / len(rl_schedule):.1f}h" if rl_schedule else "   N/A")

        # Generate with Greedy
        print("\n2. Greedy Scheduler:")
        greedy_schedule = rl_scheduler.generate_schedule(
            assignments=assignments,
            time_slots=time_slots,
            use_rl=False
        )

        greedy_hours = sum((s['end_time'] - s['start_time']).total_seconds() / 3600 for s in greedy_schedule)
        greedy_assignments_covered = len(set(s['assignment_id'] for s in greedy_schedule))

        print(f"   Sessions created: {len(greedy_schedule)}")
        print(f"   Total hours scheduled: {greedy_hours:.1f}h")
        print(f"   Assignments covered: {greedy_assignments_covered}/{len(assignments)}")
        print(f"   Avg session length: {greedy_hours / len(greedy_schedule):.1f}h" if greedy_schedule else "   N/A")

        # Comparison
        print("\n" + "="*80)
        print("Comparison Summary")
        print("="*80)

        print(f"\nTotal Hours Scheduled:")
        print(f"  RL:     {rl_hours:.1f}h")
        print(f"  Greedy: {greedy_hours:.1f}h")
        print(f"  Difference: {abs(rl_hours - greedy_hours):.1f}h ({'+' if rl_hours > greedy_hours else '-'}{abs(rl_hours - greedy_hours) / greedy_hours * 100:.1f}%)")

        print(f"\nNumber of Sessions:")
        print(f"  RL:     {len(rl_schedule)}")
        print(f"  Greedy: {len(greedy_schedule)}")

        print(f"\nAssignments Covered:")
        print(f"  RL:     {rl_assignments_covered}/{len(assignments)}")
        print(f"  Greedy: {greedy_assignments_covered}/{len(assignments)}")

        # Detailed comparison
        print("\n" + "-"*80)
        print("Sample Sessions (First 5):")
        print("-"*80)

        print("\nRL Scheduler:")
        for i, session in enumerate(rl_schedule[:5]):
            duration = (session['end_time'] - session['start_time']).total_seconds() / 3600
            print(f"  {i+1}. Assignment {session['assignment_id']}: "
                  f"{session['start_time'].strftime('%Y-%m-%d %H:%M')} ({duration:.1f}h)")

        print("\nGreedy Scheduler:")
        for i, session in enumerate(greedy_schedule[:5]):
            duration = (session['end_time'] - session['start_time']).total_seconds() / 3600
            print(f"  {i+1}. Assignment {session['assignment_id']}: "
                  f"{session['start_time'].strftime('%Y-%m-%d %H:%M')} ({duration:.1f}h)")

        print("\n" + "="*80)
        print("\nBoth schedulers successfully generated schedules.")
        print("RL scheduler learns optimal patterns through reinforcement learning.")
        print("Greedy scheduler uses a simpler priority-based approach.")
        print("="*80 + "\n")

        return 0

    finally:
        db.close()


if __name__ == "__main__":
    sys.exit(main())
