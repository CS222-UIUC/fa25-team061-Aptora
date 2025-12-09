#!/usr/bin/env python3
"""
Test ML scheduler with different course combinations
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from app.database import SessionLocal
from app.models import Course, Assignment, DifficultyLevel, TaskType, PriorityLevel, User, AvailabilitySlot
from app.ml.models.xgboost_estimator import XGBoostTimeEstimator
from app.schedule_generator import ScheduleGenerator
from app.schemas import ScheduleRequest
from datetime import datetime, timedelta
import logging

logging.basicConfig(level=logging.WARNING)

def create_test_courses_and_assignments(db, user_id, scenario_name):
    """Create test courses and assignments for different scenarios"""

    # Clear existing test data for this user
    existing_courses = db.query(Course).filter(Course.user_id == user_id).all()
    for course in existing_courses:
        db.query(Assignment).filter(Assignment.course_id == course.id).delete()
    db.query(Course).filter(Course.user_id == user_id).delete()
    db.commit()

    scenarios = {
        "light_load": {
            "name": "Light Load (2 easy courses)",
            "courses": [
                {"code": "CS 101", "name": "Intro to Programming", "assignments": [
                    {"title": "Homework 1", "hours": 2, "difficulty": DifficultyLevel.EASY, "type": TaskType.ASSIGNMENT, "priority": PriorityLevel.MEDIUM, "days": 5},
                    {"title": "Quiz Prep", "hours": 1.5, "difficulty": DifficultyLevel.EASY, "type": TaskType.EXAM, "priority": PriorityLevel.HIGH, "days": 7},
                ]},
                {"code": "MATH 115", "name": "Calculus I", "assignments": [
                    {"title": "Problem Set 3", "hours": 3, "difficulty": DifficultyLevel.EASY, "type": TaskType.ASSIGNMENT, "priority": PriorityLevel.MEDIUM, "days": 6},
                ]}
            ]
        },

        "medium_load": {
            "name": "Medium Load (3 mixed courses)",
            "courses": [
                {"code": "CS 225", "name": "Data Structures", "assignments": [
                    {"title": "MP3: Maze Solver", "hours": 8, "difficulty": DifficultyLevel.HARD, "type": TaskType.ASSIGNMENT, "priority": PriorityLevel.HIGH, "days": 10},
                    {"title": "Lab 4", "hours": 2, "difficulty": DifficultyLevel.MEDIUM, "type": TaskType.ASSIGNMENT, "priority": PriorityLevel.LOW, "days": 3},
                ]},
                {"code": "MATH 241", "name": "Calculus III", "assignments": [
                    {"title": "Homework 5", "hours": 4, "difficulty": DifficultyLevel.MEDIUM, "type": TaskType.ASSIGNMENT, "priority": PriorityLevel.MEDIUM, "days": 5},
                    {"title": "Midterm Prep", "hours": 6, "difficulty": DifficultyLevel.HARD, "type": TaskType.EXAM, "priority": PriorityLevel.HIGH, "days": 8},
                ]},
                {"code": "PHYS 211", "name": "Physics I", "assignments": [
                    {"title": "Lab Report", "hours": 3, "difficulty": DifficultyLevel.MEDIUM, "type": TaskType.ASSIGNMENT, "priority": PriorityLevel.MEDIUM, "days": 4},
                ]}
            ]
        },

        "heavy_load": {
            "name": "Heavy Load (4 hard courses - crunch time!)",
            "courses": [
                {"code": "CS 374", "name": "Algorithms", "assignments": [
                    {"title": "Homework 6", "hours": 10, "difficulty": DifficultyLevel.HARD, "type": TaskType.ASSIGNMENT, "priority": PriorityLevel.HIGH, "days": 7},
                    {"title": "Final Exam Prep", "hours": 15, "difficulty": DifficultyLevel.HARD, "type": TaskType.EXAM, "priority": PriorityLevel.HIGH, "days": 12},
                ]},
                {"code": "CS 421", "name": "Programming Languages", "assignments": [
                    {"title": "ML Interpreter Project", "hours": 12, "difficulty": DifficultyLevel.HARD, "type": TaskType.PROJECT, "priority": PriorityLevel.HIGH, "days": 14},
                ]},
                {"code": "CS 425", "name": "Distributed Systems", "assignments": [
                    {"title": "MP4: Consensus", "hours": 10, "difficulty": DifficultyLevel.HARD, "type": TaskType.ASSIGNMENT, "priority": PriorityLevel.HIGH, "days": 9},
                    {"title": "Paper Review", "hours": 3, "difficulty": DifficultyLevel.MEDIUM, "type": TaskType.ASSIGNMENT, "priority": PriorityLevel.LOW, "days": 5},
                ]},
                {"code": "STAT 400", "name": "Statistics", "assignments": [
                    {"title": "Problem Set 8", "hours": 5, "difficulty": DifficultyLevel.MEDIUM, "type": TaskType.ASSIGNMENT, "priority": PriorityLevel.MEDIUM, "days": 6},
                ]}
            ]
        },

        "finals_week": {
            "name": "Finals Week (All exams, tight deadlines!)",
            "courses": [
                {"code": "CS 225", "name": "Data Structures", "assignments": [
                    {"title": "Final Exam Prep", "hours": 12, "difficulty": DifficultyLevel.HARD, "type": TaskType.EXAM, "priority": PriorityLevel.HIGH, "days": 5},
                ]},
                {"code": "CS 233", "name": "Computer Architecture", "assignments": [
                    {"title": "Final Exam Prep", "hours": 10, "difficulty": DifficultyLevel.HARD, "type": TaskType.EXAM, "priority": PriorityLevel.HIGH, "days": 4},
                ]},
                {"code": "MATH 241", "name": "Calculus III", "assignments": [
                    {"title": "Final Exam Prep", "hours": 8, "difficulty": DifficultyLevel.MEDIUM, "type": TaskType.EXAM, "priority": PriorityLevel.HIGH, "days": 6},
                ]},
                {"code": "PHYS 211", "name": "Physics I", "assignments": [
                    {"title": "Final Exam Prep", "hours": 9, "difficulty": DifficultyLevel.HARD, "type": TaskType.EXAM, "priority": PriorityLevel.HIGH, "days": 3},
                ]}
            ]
        }
    }

    scenario = scenarios[scenario_name]
    created_assignments = []

    for course_data in scenario["courses"]:
        # Create course
        course = Course(
            user_id=user_id,
            code=course_data["code"],
            name=course_data["name"]
        )
        db.add(course)
        db.flush()

        # Create assignments
        for assign_data in course_data["assignments"]:
            assignment = Assignment(
                course_id=course.id,
                title=assign_data["title"],
                description=f"{course_data['code']}: {assign_data['title']}",
                estimated_hours=assign_data["hours"],
                difficulty=assign_data["difficulty"],
                task_type=assign_data["type"],
                priority=assign_data["priority"],
                due_date=datetime.now() + timedelta(days=assign_data["days"]),
                is_completed=False
            )
            db.add(assignment)
            db.flush()
            created_assignments.append(assignment)

    db.commit()
    return scenario, created_assignments

def create_availability_slots(db, user_id):
    """Create typical student availability"""
    # Clear existing
    db.query(AvailabilitySlot).filter(AvailabilitySlot.user_id == user_id).delete()

    # Monday-Friday: 9am-12pm, 2pm-5pm, 7pm-10pm
    # Saturday-Sunday: 10am-2pm, 3pm-7pm

    weekday_slots = [
        ("09:00", "12:00"),  # Morning
        ("14:00", "17:00"),  # Afternoon
        ("19:00", "22:00"),  # Evening
    ]

    weekend_slots = [
        ("10:00", "14:00"),  # Morning
        ("15:00", "19:00"),  # Afternoon
    ]

    for day in range(5):  # Monday-Friday
        for start, end in weekday_slots:
            slot = AvailabilitySlot(
                user_id=user_id,
                day_of_week=day,
                start_time=start,
                end_time=end
            )
            db.add(slot)

    for day in [5, 6]:  # Saturday-Sunday
        for start, end in weekend_slots:
            slot = AvailabilitySlot(
                user_id=user_id,
                day_of_week=day,
                start_time=start,
                end_time=end
            )
            db.add(slot)

    db.commit()

def test_scenario(db, user_id, scenario_name):
    """Test a specific course load scenario"""
    print("\n" + "="*80)

    # Create courses and assignments
    scenario, assignments = create_test_courses_and_assignments(db, user_id, scenario_name)
    print(f"Scenario: {scenario['name']}")
    print("="*80)

    # Show courses and assignments
    print(f"\nCourses and Assignments:")
    total_hours = 0
    for course_data in scenario["courses"]:
        print(f"\n📚 {course_data['code']} - {course_data['name']}")
        for assign_data in course_data["assignments"]:
            days_until = assign_data["days"]
            print(f"   • {assign_data['title']}")
            print(f"     Estimated: {assign_data['hours']}h | "
                  f"Difficulty: {assign_data['difficulty'].value} | "
                  f"Type: {assign_data['type'].value} | "
                  f"Due: in {days_until} days")
            total_hours += assign_data["hours"]

    print(f"\n📊 Total estimated hours: {total_hours}h")

    # Get ML predictions
    print("\n" + "-"*80)
    print("ML Time Predictions (XGBoost)")
    print("-"*80)

    estimator = XGBoostTimeEstimator(db)
    if not estimator.is_trained:
        print("⚠️  XGBoost model not trained - using fallback estimates")

    total_predicted = 0
    for assignment in assignments:
        prediction = estimator.predict(assignment, user_id)

        user_estimate = assignment.estimated_hours
        ml_estimate = prediction['predicted_hours']
        confidence = prediction['confidence']

        diff = ml_estimate - user_estimate
        diff_pct = (diff / user_estimate * 100) if user_estimate > 0 else 0

        print(f"\n{assignment.course.code} - {assignment.title}")
        print(f"  User estimate: {user_estimate:.1f}h")
        print(f"  ML prediction: {ml_estimate:.1f}h (confidence: {confidence:.0%})")
        print(f"  Difference: {diff:+.1f}h ({diff_pct:+.1f}%)")
        print(f"  Model: {prediction.get('model_type', 'unknown')}")

        total_predicted += ml_estimate

    print(f"\n📊 Total predicted hours: {total_predicted:.1f}h (vs {total_hours:.1f}h estimated)")
    print(f"   ML adjustment: {total_predicted - total_hours:+.1f}h ({(total_predicted - total_hours) / total_hours * 100:+.1f}%)")

    # Generate schedule
    print("\n" + "-"*80)
    print("Generating Study Schedule")
    print("-"*80)

    # Create availability
    create_availability_slots(db, user_id)

    # Try greedy scheduler
    print("\nUsing Greedy Scheduler...")
    generator = ScheduleGenerator(db, use_rl=False)

    start_date = datetime.now()
    end_date = start_date + timedelta(days=21)  # 3 weeks

    request = ScheduleRequest(start_date=start_date, end_date=end_date)
    schedule = generator.generate_schedule(user_id, request)

    print(f"\n✓ Schedule generated!")
    print(f"   Sessions created: {len(schedule.study_sessions)}")
    print(f"   Total hours: {schedule.total_hours_scheduled:.1f}h")
    print(f"   Assignments covered: {len(schedule.assignments_covered)}/{len(assignments)}")

    # Show sample sessions
    if schedule.study_sessions:
        print(f"\n📅 Sample Sessions (first 5):")
        for i, session in enumerate(schedule.study_sessions[:5]):
            duration = (session.end_time - session.start_time).total_seconds() / 3600
            # Find assignment
            assignment = next((a for a in assignments if a.id == session.assignment_id), None)
            if assignment:
                print(f"   {i+1}. {assignment.course.code} - {assignment.title}")
                print(f"      {session.start_time.strftime('%a %m/%d %I:%M%p')} - "
                      f"{session.end_time.strftime('%I:%M%p')} ({duration:.1f}h)")

        if len(schedule.study_sessions) > 5:
            print(f"   ... and {len(schedule.study_sessions) - 5} more sessions")

    # Analysis
    print("\n" + "-"*80)
    print("Schedule Analysis")
    print("-"*80)

    coverage_pct = len(schedule.assignments_covered) / len(assignments) * 100 if assignments else 0
    hours_pct = (schedule.total_hours_scheduled / total_predicted * 100) if total_predicted > 0 else 0

    print(f"\nCoverage: {coverage_pct:.0f}%")
    print(f"Hours scheduled: {hours_pct:.0f}% of predicted time")

    if coverage_pct < 100:
        print(f"\n⚠️  Warning: Not all assignments covered!")
        print(f"   Need more availability or reduce workload")

    if hours_pct < 80:
        print(f"\n⚠️  Warning: Insufficient time scheduled!")
        print(f"   May need to extend schedule period or add more study time")

    if scenario_name == "heavy_load" or scenario_name == "finals_week":
        avg_hours_per_week = schedule.total_hours_scheduled / 3
        print(f"\n📈 Average hours per week: {avg_hours_per_week:.1f}h")
        if avg_hours_per_week > 40:
            print(f"   ⚠️  Very heavy workload! Consider reducing course load.")
        elif avg_hours_per_week > 30:
            print(f"   ⚠️  Heavy workload. Make sure to take breaks!")

    return {
        'scenario': scenario_name,
        'total_estimated': total_hours,
        'total_predicted': total_predicted,
        'sessions': len(schedule.study_sessions),
        'hours_scheduled': schedule.total_hours_scheduled,
        'coverage': coverage_pct
    }

def main():
    print("\n" + "="*80)
    print("ML Scheduler - Course Combination Testing")
    print("="*80)

    db = SessionLocal()

    try:
        # Get test user
        user = db.query(User).first()
        if not user:
            print("\n❌ No user found. Please create a user first.")
            return 1

        print(f"\nUsing user: {user.email}")

        # Test all scenarios
        scenarios = ["light_load", "medium_load", "heavy_load", "finals_week"]
        results = []

        for scenario in scenarios:
            result = test_scenario(db, user.id, scenario)
            results.append(result)

        # Summary
        print("\n" + "="*80)
        print("Summary - All Scenarios")
        print("="*80)

        print(f"\n{'Scenario':<20} {'Est.Hours':<12} {'ML Pred.':<12} {'Sessions':<10} {'Coverage':<10}")
        print("-" * 80)

        for r in results:
            print(f"{r['scenario']:<20} {r['total_estimated']:<12.1f} "
                  f"{r['total_predicted']:<12.1f} {r['sessions']:<10} {r['coverage']:<10.0f}%")

        print("\n" + "="*80)
        print("\nKey Insights:")
        print("• Light load: Easy to schedule, plenty of time")
        print("• Medium load: Typical semester, manageable")
        print("• Heavy load: Requires careful planning, tight schedule")
        print("• Finals week: High stress, may need to prioritize")
        print("="*80 + "\n")

        return 0

    finally:
        db.close()

if __name__ == "__main__":
    sys.exit(main())
