"""
Scraper manager to orchestrate all scrapers and manage data collection
"""
import logging
from sqlalchemy.orm import Session
from typing import Dict, List, Optional
from datetime import datetime, timedelta

from .reddit_scraper import RedditScraper
from .ratemyprofessor_scraper import RateMyProfessorScraper
from ...models import CourseInsight, ProfessorRating, ScraperJob, JobStatus, ScraperSource
from ...config import settings

logger = logging.getLogger(__name__)


class ScraperManager:
    """
    Orchestrates all web scrapers and manages scraped data storage
    """

    def __init__(self, db: Session, reddit_config: Optional[Dict] = None):
        self.db = db

        # Initialize scrapers with config if available
        if reddit_config:
            reddit_client_id = reddit_config.get('client_id')
            reddit_client_secret = reddit_config.get('client_secret')
            reddit_user_agent = reddit_config.get('user_agent')
        else:
            # Try to get from settings
            reddit_client_id = settings.reddit_client_id
            reddit_client_secret = settings.reddit_client_secret
            reddit_user_agent = settings.reddit_user_agent

        if reddit_client_id and reddit_client_secret:
            self.reddit_scraper = RedditScraper(
                client_id=reddit_client_id,
                client_secret=reddit_client_secret,
                user_agent=reddit_user_agent
            )
        else:
            self.reddit_scraper = RedditScraper()

        self.rmp_scraper = RateMyProfessorScraper()

    def scrape_course_data(self, course_code: str, force_refresh: bool = False) -> Dict:
        """
        Scrape all available data for a course

        Args:
            course_code: Course identifier (e.g., "CS 225")
            force_refresh: Force re-scrape even if recent data exists

        Returns:
            Dictionary with aggregated insights
        """
        # Check if we have recent data (last 7 days)
        if not force_refresh and self._has_recent_data(course_code, days=7):
            logger.info(f"Using cached data for {course_code}")
            return self._get_cached_insights(course_code)

        # Create scraper job
        job = ScraperJob(
            job_type='course',
            target_identifier=course_code,
            status=JobStatus.RUNNING,
            started_at=datetime.now()
        )
        self.db.add(job)
        self.db.commit()

        insights = {}
        records_scraped = 0

        try:
            # Scrape Reddit
            logger.info(f"Scraping Reddit for {course_code}")
            reddit_data = self.reddit_scraper.scrape_with_error_handling(course_code)

            if reddit_data:
                self._save_course_insight(course_code, reddit_data, ScraperSource.REDDIT)
                insights['reddit'] = reddit_data
                records_scraped += 1

            # Update job status
            job.status = JobStatus.COMPLETED
            job.completed_at = datetime.now()
            job.records_scraped = records_scraped

        except Exception as e:
            logger.error(f"Scraping failed for {course_code}: {e}")
            job.status = JobStatus.FAILED
            job.error_message = str(e)
            job.completed_at = datetime.now()

        self.db.commit()

        return insights

    def scrape_professor_rating(self, professor_name: str, course_code: Optional[str] = None) -> Optional[Dict]:
        """
        Scrape professor ratings

        Args:
            professor_name: Name of professor
            course_code: Optional course code to associate

        Returns:
            Professor rating data or None
        """
        logger.info(f"Scraping professor rating for {professor_name}")

        try:
            data = self.rmp_scraper.scrape_with_error_handling(
                professor_name,
                course_code=course_code
            )

            if data:
                self._save_professor_rating(data)
                return data

        except Exception as e:
            logger.error(f"Failed to scrape professor {professor_name}: {e}")

        return None

    def _save_course_insight(self, course_code: str, data: Dict, source: ScraperSource):
        """Save course insight to database with validation"""
        if not data:
            logger.warning(f"No data to save for course {course_code}")
            return
        
        # Validate course code format
        parts = course_code.split()
        if len(parts) < 2:
            logger.warning(f"Invalid course code format: {course_code}")
            return
        
        subject = parts[0] if len(parts) > 0 else course_code
        number = parts[1] if len(parts) > 1 else ""

        # Validate and sanitize data
        avg_hours = data.get('avg_hours_per_week')
        if avg_hours is not None:
            try:
                avg_hours = float(avg_hours)
                if avg_hours < 0 or avg_hours > 100:  # Sanity check
                    logger.warning(f"Invalid hours per week: {avg_hours} for {course_code}")
                    avg_hours = None
            except (ValueError, TypeError):
                logger.warning(f"Invalid hours per week format: {data.get('avg_hours_per_week')}")
                avg_hours = None

        difficulty_score = data.get('difficulty_score')
        if difficulty_score is not None:
            try:
                difficulty_score = float(difficulty_score)
                if difficulty_score < 0 or difficulty_score > 10:  # Should be 0-10 scale
                    logger.warning(f"Invalid difficulty score: {difficulty_score} for {course_code}")
                    difficulty_score = None
            except (ValueError, TypeError):
                logger.warning(f"Invalid difficulty score format: {data.get('difficulty_score')}")
                difficulty_score = None

        workload_rating = data.get('workload_rating')
        if workload_rating is not None:
            try:
                workload_rating = float(workload_rating)
                if workload_rating < 1 or workload_rating > 5:  # Should be 1-5 scale
                    logger.warning(f"Invalid workload rating: {workload_rating} for {course_code}")
                    workload_rating = None
            except (ValueError, TypeError):
                logger.warning(f"Invalid workload rating format: {data.get('workload_rating')}")
                workload_rating = None

        # Only save if we have at least one valid metric
        if avg_hours is None and difficulty_score is None and workload_rating is None:
            logger.warning(f"No valid data to save for course {course_code}")
            return

        try:
            insight = CourseInsight(
                course_subject=subject,
                course_number=number,
                avg_hours_per_week=avg_hours,
                difficulty_score=difficulty_score,
                workload_rating=workload_rating,
                source=source,
                last_scraped_at=datetime.now()
            )

            self.db.add(insight)
            self.db.commit()
            logger.info(f"Saved course insight for {course_code} from {source.value}")
        except Exception as e:
            logger.error(f"Failed to save course insight for {course_code}: {e}")
            self.db.rollback()

    def _save_professor_rating(self, data: Dict):
        """Save professor rating to database with validation"""
        if not data:
            logger.warning("No data to save for professor rating")
            return
        
        # Validate professor name
        professor_name = data.get('professor_name', '').strip()
        if not professor_name:
            logger.warning("Missing professor name in rating data")
            return

        # Validate and sanitize ratings
        overall_rating = data.get('overall_rating')
        if overall_rating is not None:
            try:
                overall_rating = float(overall_rating)
                if overall_rating < 1 or overall_rating > 5:  # Should be 1-5 scale
                    logger.warning(f"Invalid overall rating: {overall_rating} for {professor_name}")
                    overall_rating = None
            except (ValueError, TypeError):
                logger.warning(f"Invalid overall rating format: {data.get('overall_rating')}")
                overall_rating = None

        difficulty_rating = data.get('difficulty_rating')
        if difficulty_rating is not None:
            try:
                difficulty_rating = float(difficulty_rating)
                if difficulty_rating < 1 or difficulty_rating > 5:  # Should be 1-5 scale
                    logger.warning(f"Invalid difficulty rating: {difficulty_rating} for {professor_name}")
                    difficulty_rating = None
            except (ValueError, TypeError):
                logger.warning(f"Invalid difficulty rating format: {data.get('difficulty_rating')}")
                difficulty_rating = None

        would_take_again = data.get('would_take_again_percent')
        if would_take_again is not None:
            try:
                would_take_again = float(would_take_again)
                if would_take_again < 0 or would_take_again > 100:  # Should be 0-100%
                    logger.warning(f"Invalid would take again percent: {would_take_again} for {professor_name}")
                    would_take_again = None
            except (ValueError, TypeError):
                logger.warning(f"Invalid would take again format: {data.get('would_take_again_percent')}")
                would_take_again = None

        rating_count = data.get('rating_count', 0)
        try:
            rating_count = int(rating_count)
            if rating_count < 0:
                rating_count = 0
        except (ValueError, TypeError):
            rating_count = 0

        # Parse course code if provided
        course_code = data.get('course_code', '')
        course_subject = ''
        course_number = ''
        if course_code:
            parts = course_code.split()
            course_subject = parts[0] if len(parts) > 0 else ''
            course_number = parts[1] if len(parts) > 1 else ''

        # Only save if we have at least one valid rating
        if overall_rating is None and difficulty_rating is None and would_take_again is None:
            logger.warning(f"No valid rating data to save for professor {professor_name}")
            return

        try:
            rating = ProfessorRating(
                professor_name=professor_name,
                course_subject=course_subject,
                course_number=course_number,
                overall_rating=overall_rating,
                difficulty_rating=difficulty_rating,
                would_take_again_percent=would_take_again,
                source=ScraperSource.RATEMYPROFESSOR,
                source_url=data.get('source_url'),
                rating_count=rating_count,
                last_scraped_at=datetime.now()
            )

            self.db.add(rating)
            self.db.commit()
            logger.info(f"Saved professor rating for {professor_name}")
        except Exception as e:
            logger.error(f"Failed to save professor rating for {professor_name}: {e}")
            self.db.rollback()

    def _has_recent_data(self, course_code: str, days: int = 7) -> bool:
        """Check if we have recent data for this course"""
        parts = course_code.split()
        subject = parts[0] if len(parts) > 0 else course_code
        number = parts[1] if len(parts) > 1 else ""

        cutoff = datetime.now() - timedelta(days=days)

        recent_insight = self.db.query(CourseInsight).filter(
            CourseInsight.course_subject == subject,
            CourseInsight.course_number == number,
            CourseInsight.last_scraped_at >= cutoff
        ).first()

        return recent_insight is not None

    def _get_cached_insights(self, course_code: str) -> Dict:
        """Get cached insights from database"""
        parts = course_code.split()
        subject = parts[0] if len(parts) > 0 else course_code
        number = parts[1] if len(parts) > 1 else ""

        insights = self.db.query(CourseInsight).filter(
            CourseInsight.course_subject == subject,
            CourseInsight.course_number == number
        ).all()

        if not insights:
            return {}

        # Aggregate insights
        return {
            'avg_hours_per_week': sum(i.avg_hours_per_week for i in insights if i.avg_hours_per_week) / len([i for i in insights if i.avg_hours_per_week]) if any(i.avg_hours_per_week for i in insights) else None,
            'difficulty_score': sum(i.difficulty_score for i in insights if i.difficulty_score) / len([i for i in insights if i.difficulty_score]) if any(i.difficulty_score for i in insights) else None,
            'cached': True
        }
