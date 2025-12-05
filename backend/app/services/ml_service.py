"""
ML Service layer - orchestrates scrapers and ML models for intelligent scheduling
"""
import logging
from typing import Dict, List, Optional
from datetime import datetime
from sqlalchemy.orm import Session

from ..models import Assignment, StudySession, User, StudyTimePrediction, CourseInsight, ProfessorRating
from ..schedule_generator import ScheduleGenerator
from ..schemas import ScheduleRequest, ScheduleResponse
from .scrapers.scraper_manager import ScraperManager
from ..ml.models.time_estimator import StudyTimeEstimator

logger = logging.getLogger(__name__)


class MLScheduleService:
    """
    Orchestrates ML-powered schedule generation
    Combines web scraping, ML predictions, and enhanced scheduling
    """

    def __init__(self, db: Session):
        self.db = db
        self.scraper_manager = ScraperManager(db)
        self.time_estimator = StudyTimeEstimator(db)

    def generate_ml_schedule(
        self,
        user_id: int,
        start_date: datetime,
        end_date: datetime
    ) -> Dict:
        """
        Generate ML-enhanced study schedule

        Args:
            user_id: User ID
            start_date: Schedule start date
            end_date: Schedule end date

        Returns:
            Dictionary with schedule, predictions, and insights
        """
        try:
            # 1. Get user's assignments
            assignments = self._get_user_assignments(user_id, start_date, end_date)

            if not assignments:
                return {
                    'study_sessions': [],
                    'predictions': [],
                    'total_hours_scheduled': 0,
                    'ml_insights': {'message': 'No assignments to schedule'}
                }

            # 2. Enrich assignments with course insights
            enriched_assignments = []
            for assignment in assignments:
                course_code = assignment.course.code

                # Try to get/scrape course insights
                insights = self._get_or_scrape_course_insights(course_code)

                enriched_assignments.append({
                    'assignment': assignment,
                    'insights': insights
                })

            # 3. Generate ML predictions for each assignment
            predictions = []
            for item in enriched_assignments:
                assignment = item['assignment']

                # Get ML time prediction
                prediction = self.time_estimator.predict(assignment, user_id)

                # Store prediction in database
                self.db.add(StudyTimePrediction(
                    assignment_id=assignment.id,
                    predicted_hours=prediction['predicted_hours'],
                    confidence_score=prediction['confidence'],
                    model_version='rule-based-v1',
                    features_used=str(prediction.get('feature_importance', {}))
                ))

                # Update assignment with ML prediction
                assignment.estimated_hours = prediction['predicted_hours']

                predictions.append({
                    'assignment_id': assignment.id,
                    'assignment_title': assignment.title,
                    **prediction
                })

            self.db.commit()

            # 4. Generate schedule using enhanced greedy algorithm
            # (Using existing ScheduleGenerator with ML-adjusted times)
            generator = ScheduleGenerator(self.db)
            schedule_result = generator.generate_schedule(
                user_id,
                ScheduleRequest(start_date=start_date, end_date=end_date)
            )

            # 5. Compile response
            return {
                'study_sessions': [
                    {
                        'id': session.id,
                        'start_time': session.start_time,
                        'end_time': session.end_time,
                        'assignment_id': session.assignment_id,
                        'is_completed': session.is_completed,
                        'notes': session.notes
                    }
                    for session in schedule_result.study_sessions
                ],
                'predictions': predictions,
                'total_hours_scheduled': schedule_result.total_hours_scheduled,
                'ml_insights': {
                    'avg_confidence': sum(p['confidence'] for p in predictions) / len(predictions) if predictions else 0,
                    'assignments_analyzed': len(predictions),
                    'model_version': 'rule-based-v1'
                }
            }

        except Exception as e:
            logger.error(f"ML schedule generation failed: {e}", exc_info=True)
            # Fallback to basic scheduling
            generator = ScheduleGenerator(self.db)
            schedule_result = generator.generate_schedule(
                user_id,
                ScheduleRequest(start_date=start_date, end_date=end_date)
            )
            return {
                'study_sessions': schedule_result.study_sessions,
                'predictions': [],
                'total_hours_scheduled': schedule_result.total_hours_scheduled,
                'ml_insights': {'error': str(e), 'fallback': True}
            }

    def get_course_insights(self, course_code: str) -> Dict:
        """
        Get aggregated insights for a course

        Args:
            course_code: Course identifier (e.g., "CS 225")

        Returns:
            Dictionary with course insights and professor ratings
        """
        parts = course_code.split()
        subject = parts[0] if len(parts) > 0 else course_code
        number = parts[1] if len(parts) > 1 else ""

        # Get course insights
        insights = self.db.query(CourseInsight).filter(
            CourseInsight.course_subject == subject,
            CourseInsight.course_number == number
        ).all()

        # Get professor ratings
        prof_ratings = self.db.query(ProfessorRating).filter(
            ProfessorRating.course_subject == subject,
            ProfessorRating.course_number == number
        ).all()

        # Aggregate
        avg_difficulty = None
        avg_hours = None

        if insights:
            difficulty_scores = [i.difficulty_score for i in insights if i.difficulty_score]
            hours_scores = [i.avg_hours_per_week for i in insights if i.avg_hours_per_week]

            if difficulty_scores:
                avg_difficulty = sum(difficulty_scores) / len(difficulty_scores)
            if hours_scores:
                avg_hours = sum(hours_scores) / len(hours_scores)

        return {
            'course_code': course_code,
            'course_insights': [
                {
                    'source': i.source.value,
                    'difficulty_score': i.difficulty_score,
                    'avg_hours_per_week': i.avg_hours_per_week,
                    'last_updated': i.last_scraped_at.isoformat() if i.last_scraped_at else None
                }
                for i in insights
            ],
            'professor_ratings': [
                {
                    'professor_name': r.professor_name,
                    'overall_rating': r.overall_rating,
                    'difficulty_rating': r.difficulty_rating,
                    'would_take_again': r.would_take_again_percent,
                    'source': r.source.value
                }
                for r in prof_ratings
            ],
            'avg_difficulty': round(avg_difficulty, 2) if avg_difficulty else None,
            'avg_hours_per_week': round(avg_hours, 2) if avg_hours else None
        }

    def _get_user_assignments(self, user_id: int, start_date: datetime, end_date: datetime) -> List[Assignment]:
        """Get user's incomplete assignments within date range"""
        from ..models import Course

        return self.db.query(Assignment).join(Assignment.course).filter(
            Course.user_id == user_id,
            Assignment.due_date >= start_date,
            Assignment.due_date <= end_date,
            Assignment.is_completed == False
        ).all()

    def _get_or_scrape_course_insights(self, course_code: str) -> Optional[Dict]:
        """Get cached insights or scrape if needed"""
        # Try to get from cache
        insights = self.scraper_manager._get_cached_insights(course_code)

        if insights and not insights.get('cached'):
            return insights

        # If no recent data, trigger scraping (async in production)
        logger.info(f"Scraping course insights for {course_code}")
        scraped = self.scraper_manager.scrape_course_data(course_code)

        return scraped if scraped else insights
