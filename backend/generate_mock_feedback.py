#!/usr/bin/env python3
"""
Generate mock feedback data for testing ML model training
This creates realistic study session feedback based on assignments
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from app.database import SessionLocal
from app.models import (
    StudySession, StudySessionFeedback, Assignment, Course, User,
    DifficultyLevel, TaskType, PriorityLevel
)
from datetime import datetime, timedelta
import random
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def generate_mock_feedback(db, num_samples: int = 50):
    """Generate mock feedback data for training"""

    print(f"\nGenerating {num_samples} mock feedback samples...")

    # Get or create a test user
    user = db.query(User).first()
    if not user:
        print("❌ No users found. Please create a user first.")
        return 0

    print(f"Using user: {user.email}")

    # Get or create courses
    courses = db.query(Course).filter(Course.user_id == user.id).all()
    if not courses:
        print("Creating mock courses...")
        course_data = [
            ("CS 225", "Data Structures"),
            ("CS 374", "Algorithms"),
            ("MATH 241", "Calculus III"),
            ("PHYS 211", "Classical Mechanics")
        ]

        courses = []
        for code, name in course_data:
            course = Course(
                user_id=user.id,
                code=code,
                name=name
            )
            db.add(course)
            courses.append(course)
        db.commit()

    print(f"Using {len(courses)} courses")

    # Generate assignments and feedback
    created_count = 0
    difficulties = [DifficultyLevel.EASY, DifficultyLevel.MEDIUM, DifficultyLevel.HARD]
    task_types = [TaskType.ASSIGNMENT, TaskType.PROJECT, TaskType.EXAM]
    priorities = [PriorityLevel.LOW, PriorityLevel.MEDIUM, PriorityLevel.HIGH]

    for i in range(num_samples):
        # Create assignment
        course = random.choice(courses)
        difficulty = random.choice(difficulties)
        task_type = random.choice(task_types)
        priority = random.choice(priorities)

        # Estimate hours based on difficulty and type
        base_hours = {
            TaskType.ASSIGNMENT: random.uniform(2, 6),
            TaskType.PROJECT: random.uniform(8, 20),
            TaskType.EXAM: random.uniform(10, 25)
        }[task_type]

        estimated_hours = base_hours * {
            DifficultyLevel.EASY: random.uniform(0.7, 0.9),
            DifficultyLevel.MEDIUM: random.uniform(0.9, 1.1),
            DifficultyLevel.HARD: random.uniform(1.2, 1.5)
        }[difficulty]

        assignment = Assignment(
            course_id=course.id,
            title=f"{task_type.value.title()} {i+1}",
            description=f"Mock {task_type.value} for {course.code}",
            due_date=datetime.now() + timedelta(days=random.randint(-30, -1)),  # Past assignments
            estimated_hours=round(estimated_hours, 1),
            difficulty=difficulty,
            task_type=task_type,
            priority=priority,
            is_completed=True  # Mark as completed
        )
        db.add(assignment)
        db.flush()

        # Create study session
        session_date = assignment.due_date - timedelta(days=random.randint(1, 5))
        session_duration_hours = random.uniform(1, 4)

        study_session = StudySession(
            user_id=user.id,
            assignment_id=assignment.id,
            start_time=session_date,
            end_time=session_date + timedelta(hours=session_duration_hours),
            is_completed=True,
            notes=f"Study session for {assignment.title}"
        )
        db.add(study_session)
        db.flush()

        # Generate realistic actual hours
        # People generally underestimate for hard tasks, overestimate for easy tasks
        actual_multiplier = {
            DifficultyLevel.EASY: random.uniform(0.7, 1.0),  # Often takes less than estimated
            DifficultyLevel.MEDIUM: random.uniform(0.9, 1.2),  # Pretty accurate
            DifficultyLevel.HARD: random.uniform(1.1, 1.6)  # Often takes more
        }[difficulty]

        # Additional variation based on task type
        task_multiplier = {
            TaskType.ASSIGNMENT: random.uniform(0.9, 1.1),
            TaskType.PROJECT: random.uniform(1.0, 1.3),  # Projects often take longer
            TaskType.EXAM: random.uniform(1.1, 1.4)  # Exam prep often takes longer
        }[task_type]

        actual_hours = estimated_hours * actual_multiplier * task_multiplier
        actual_hours = max(0.5, min(100, actual_hours))  # Clamp to reasonable range

        # Generate feedback ratings
        # Productivity correlates with whether it took more or less time than expected
        time_ratio = actual_hours / estimated_hours
        productivity = 5.0 if time_ratio < 0.9 else (
            4.0 if time_ratio < 1.1 else (
                3.0 if time_ratio < 1.3 else 2.0
            )
        )
        productivity += random.uniform(-0.5, 0.5)  # Add some noise
        productivity = max(1.0, min(5.0, productivity))

        # Difficulty rating correlates with assignment difficulty
        difficulty_rating = {
            DifficultyLevel.EASY: random.uniform(1.5, 2.5),
            DifficultyLevel.MEDIUM: random.uniform(2.5, 3.5),
            DifficultyLevel.HARD: random.uniform(3.5, 5.0)
        }[difficulty]

        # Was the time sufficient?
        was_sufficient = time_ratio < 1.2  # True if didn't take much more than expected

        # Create feedback
        feedback = StudySessionFeedback(
            study_session_id=study_session.id,
            actual_duration_hours=round(actual_hours, 2),
            productivity_rating=round(productivity, 1),
            difficulty_rating=round(difficulty_rating, 1),
            was_sufficient=was_sufficient,
            student_comments=f"Mock feedback for {assignment.title}"
        )
        db.add(feedback)

        created_count += 1

        if (i + 1) % 10 == 0:
            print(f"  Created {i + 1}/{num_samples} samples...")

    db.commit()
    print(f"\n✓ Successfully created {created_count} feedback samples!")
    return created_count


def main():
    print("\n" + "="*80)
    print("Mock Feedback Data Generator")
    print("="*80)

    db = SessionLocal()

    try:
        # Check existing data
        existing_feedback = db.query(StudySessionFeedback).count()
        print(f"\nExisting feedback entries: {existing_feedback}")

        # Generate mock data
        num_samples = 50
        created = generate_mock_feedback(db, num_samples)

        if created > 0:
            total_feedback = db.query(StudySessionFeedback).count()
            print(f"\nTotal feedback entries now: {total_feedback}")
            print("\nYou can now train the ML model using:")
            print("  python train_model.py")
            print("\nOr via API:")
            print("  POST /schedules/ml/train")

        return 0

    except Exception as e:
        logger.error(f"Failed to generate mock data: {e}", exc_info=True)
        print(f"\n❌ Error: {str(e)}")
        return 1

    finally:
        db.close()


if __name__ == "__main__":
    sys.exit(main())
