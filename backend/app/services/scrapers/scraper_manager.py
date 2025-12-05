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

logger = logging.getLogger(__name__)


class ScraperManager:
    """
    Orchestrates all web scrapers and manages scraped data storage
    """

    def __init__(self, db: Session, reddit_config: Optional[Dict] = None):
        self.db = db

        # Initialize scrapers
        if reddit_config:
            self.reddit_scraper = RedditScraper(
                client_id=reddit_config.get('client_id'),
                client_secret=reddit_config.get('client_secret'),
                user_agent=reddit_config.get('user_agent')
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
        """Save course insight to database"""
        parts = course_code.split()
        subject = parts[0] if len(parts) > 0 else course_code
        number = parts[1] if len(parts) > 1 else ""

        insight = CourseInsight(
            course_subject=subject,
            course_number=number,
            avg_hours_per_week=data.get('avg_hours_per_week'),
            difficulty_score=data.get('difficulty_score'),
            workload_rating=data.get('workload_rating'),
            source=source,
            last_scraped_at=datetime.now()
        )

        self.db.add(insight)
        self.db.commit()

    def _save_professor_rating(self, data: Dict):
        """Save professor rating to database"""
        rating = ProfessorRating(
            professor_name=data.get('professor_name', ''),
            course_subject=data.get('course_code', '').split()[0] if data.get('course_code') else '',
            course_number=data.get('course_code', '').split()[1] if data.get('course_code') and len(data.get('course_code', '').split()) > 1 else '',
            overall_rating=data.get('overall_rating'),
            difficulty_rating=data.get('difficulty_rating'),
            would_take_again_percent=data.get('would_take_again_percent'),
            source=ScraperSource.RATEMYPROFESSOR,
            source_url=data.get('source_url'),
            rating_count=data.get('rating_count', 0),
            last_scraped_at=datetime.now()
        )

        self.db.add(rating)
        self.db.commit()

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
