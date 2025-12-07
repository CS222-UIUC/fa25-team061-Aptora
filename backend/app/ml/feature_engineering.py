"""
Feature engineering for ML time estimation model
"""
import numpy as np
from datetime import datetime
from typing import Dict, List, Optional
from sqlalchemy.orm import Session

from ..models import Assignment, StudySession, CourseInsight, ProfessorRating, DifficultyLevel, TaskType, PriorityLevel


class FeatureEngineer:
    """Extract features for study time prediction"""

    def __init__(self, db: Session):
        self.db = db

    def extract_features(self, assignment: Assignment, user_id: int) -> Dict[str, float]:
        """
        Extract all features for an assignment

        Args:
            assignment: Assignment object
            user_id: User ID for historical features

        Returns:
            Dictionary of feature names to values
        """
        features = {}

        # Assignment features
        features.update(self._extract_assignment_features(assignment))

        # Course features (from scraped data)
        features.update(self._extract_course_features(assignment))

        # Student historical features
        features.update(self._extract_student_features(user_id))

        # Temporal features
        features.update(self._extract_temporal_features(assignment, user_id))

        return features

    def _extract_assignment_features(self, assignment: Assignment) -> Dict[str, float]:
        """Extract features from the assignment itself"""
        return {
            'task_type_assignment': 1.0 if assignment.task_type == TaskType.ASSIGNMENT else 0.0,
            'task_type_exam': 1.0 if assignment.task_type == TaskType.EXAM else 0.0,
            'task_type_project': 1.0 if assignment.task_type == TaskType.PROJECT else 0.0,
            'difficulty_easy': 1.0 if assignment.difficulty == DifficultyLevel.EASY else 0.0,
            'difficulty_medium': 1.0 if assignment.difficulty == DifficultyLevel.MEDIUM else 0.0,
            'difficulty_hard': 1.0 if assignment.difficulty == DifficultyLevel.HARD else 0.0,
            'estimated_hours': float(assignment.estimated_hours),
            'priority_low': 1.0 if assignment.priority == PriorityLevel.LOW else 0.0,
            'priority_medium': 1.0 if assignment.priority == PriorityLevel.MEDIUM else 0.0,
            'priority_high': 1.0 if assignment.priority == PriorityLevel.HIGH else 0.0,
            'days_until_due': (assignment.due_date - datetime.now()).days,
        }

    def _extract_course_features(self, assignment: Assignment) -> Dict[str, float]:
        """Extract features from course data (scraped insights)"""
        course = assignment.course
        course_code = course.code

        # Parse course code to get subject and number
        parts = course_code.split()
        subject = parts[0] if len(parts) > 0 else ""
        number = parts[1] if len(parts) > 1 else ""

        # Get course insights from database
        insights = self.db.query(CourseInsight).filter(
            CourseInsight.course_subject == subject,
            CourseInsight.course_number == number
        ).all()

        # Aggregate insights
        if insights:
            difficulty_scores = [i.difficulty_score for i in insights if i.difficulty_score is not None]
            hours_scores = [i.avg_hours_per_week for i in insights if i.avg_hours_per_week is not None]
            
            if difficulty_scores:
                avg_difficulty = np.mean(difficulty_scores)
            else:
                avg_difficulty = 5.0  # Default middle value
            
            if hours_scores:
                avg_hours = np.mean(hours_scores)
            else:
                avg_hours = 10.0  # Default
        else:
            avg_difficulty = 5.0  # Default middle value
            avg_hours = 10.0  # Default

        # Extract course level from number (e.g., CS 225 -> 200 level)
        try:
            course_level = int(number[0]) * 100 if number and number[0].isdigit() else 200
        except:
            course_level = 200

        return {
            'course_difficulty_score': float(avg_difficulty) if not np.isnan(avg_difficulty) else 5.0,
            'avg_weekly_hours': float(avg_hours) if not np.isnan(avg_hours) else 10.0,
            'course_level': float(course_level),
        }

    def _extract_student_features(self, user_id: int) -> Dict[str, float]:
        """Extract features from student's historical performance"""
        # Get completed study sessions
        completed_sessions = self.db.query(StudySession).filter(
            StudySession.user_id == user_id,
            StudySession.is_completed == True
        ).all()

        if not completed_sessions:
            return {
                'avg_completion_ratio': 1.0,  # No history, assume they're on track
                'completion_rate': 1.0,
                'total_completed_sessions': 0.0,
            }

        # Calculate completion statistics
        total_sessions = len(completed_sessions)

        # Calculate average session duration
        avg_duration = np.mean([
            (session.end_time - session.start_time).total_seconds() / 3600.0
            for session in completed_sessions
        ])

        return {
            'avg_session_duration': float(avg_duration),
            'total_completed_sessions': float(total_sessions),
            'completion_rate': 1.0,  # Simplified - all queried sessions are completed
        }

    def _extract_temporal_features(self, assignment: Assignment, user_id: int) -> Dict[str, float]:
        """Extract time-based features"""
        now = datetime.now()

        # Count concurrent assignments (due within 7 days of this assignment)
        week_before = assignment.due_date - timedelta(days=7)
        week_after = assignment.due_date + timedelta(days=7)

        from ..models import Course
        concurrent = self.db.query(Assignment).join(Assignment.course).filter(
            Course.user_id == user_id,
            Assignment.due_date.between(week_before, week_after),
            Assignment.id != assignment.id,
            Assignment.is_completed == False
        ).count()

        return {
            'concurrent_assignments': float(concurrent),
            'week_of_semester': float((now - datetime(now.year, 8, 15)).days // 7),  # Rough estimate
        }


from datetime import timedelta

