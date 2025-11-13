"""
Background Scheduler for Aptora
Handles automatic data updates and maintenance tasks
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Optional
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
from sqlalchemy.orm import Session

from .database import get_db
from .data_ingestion.discovery_ingestion import load_discovery_dataset, save_courses_to_db
from .models import CourseCatalog
from .services.reminder_service import ReminderService

logger = logging.getLogger(__name__)

class AptoraScheduler:
    def __init__(self):
        self.scheduler = AsyncIOScheduler()
        self.is_running = False
        
    def start(self):
        """Start the background scheduler"""
        if not self.is_running:
            # Schedule course data updates
            self.scheduler.add_job(
                self.update_course_data,
                CronTrigger(day_of_week=0, hour=2, minute=0),  # Every Sunday at 2 AM
                id='weekly_course_update',
                name='Weekly Course Data Update',
                replace_existing=True
            )
            
            # Schedule daily health check
            self.scheduler.add_job(
                self.health_check,
                CronTrigger(hour=6, minute=0),  # Every day at 6 AM
                id='daily_health_check',
                name='Daily Health Check',
                replace_existing=True
            )
            
            # Schedule data cleanup (remove old courses)
            self.scheduler.add_job(
                self.cleanup_old_data,
                CronTrigger(day=1, hour=3, minute=0),  # First day of month at 3 AM
                id='monthly_cleanup',
                name='Monthly Data Cleanup',
                replace_existing=True
            )

            # Schedule study session reminders
            self.scheduler.add_job(
                self.dispatch_study_session_reminders,
                IntervalTrigger(minutes=1),  # Run every minute to catch upcoming sessions
                id='study_session_reminders',
                name='Study Session Reminder Dispatcher',
                replace_existing=True
            )
            
            self.scheduler.start()
            self.is_running = True
            logger.info("Aptora scheduler started successfully")
            
    def stop(self):
        """Stop the background scheduler"""
        if self.is_running:
            self.scheduler.shutdown()
            self.is_running = False
            logger.info("Aptora scheduler stopped")
            
    async def update_course_data(self):
        """Update course data from external sources"""
        try:
            logger.info("Starting scheduled course data update...")
            
            # Get database session
            db = next(get_db())
            
            # Load fresh data from Discovery dataset
            df = load_discovery_dataset()
            
            # Save to database
            courses_added, courses_updated = save_courses_to_db(df, db)
            
            logger.info(f"Course data update completed: {courses_added} added, {courses_updated} updated")
            
            # Update last_updated timestamp
            self._update_last_sync_timestamp(db)
            
        except Exception as e:
            logger.error(f"Error during scheduled course data update: {e}")
        finally:
            db.close()
            
    async def health_check(self):
        """Daily health check of the system"""
        try:
            logger.info("Running daily health check...")
            
            db = next(get_db())
            
            # Check database connectivity
            course_count = db.query(CourseCatalog).count()
            logger.info(f"Health check: {course_count} courses in database")
            
            # Check for stale data
            stale_courses = db.query(CourseCatalog).filter(
                CourseCatalog.updated_at < datetime.utcnow() - timedelta(days=30)
            ).count()
            
            if stale_courses > 0:
                logger.warning(f"Found {stale_courses} courses with stale data (older than 30 days)")
                
        except Exception as e:
            logger.error(f"Error during health check: {e}")
        finally:
            db.close()
            
    async def cleanup_old_data(self):
        """Clean up old or invalid course data"""
        try:
            logger.info("Starting monthly data cleanup...")
            
            db = next(get_db())
            
            # Remove courses older than 2 years
            cutoff_date = datetime.utcnow() - timedelta(days=730)
            old_courses = db.query(CourseCatalog).filter(
                CourseCatalog.created_at < cutoff_date
            ).delete()
            
            logger.info(f"Cleaned up {old_courses} old courses")
            
            db.commit()
            
        except Exception as e:
            logger.error(f"Error during data cleanup: {e}")
            db.rollback()
        finally:
            db.close()

    async def dispatch_study_session_reminders(self):
        """Send reminders for upcoming study sessions."""
        db = next(get_db())
        try:
            service = ReminderService(db)
            results = service.send_upcoming_session_reminders()
            if results:
                logger.info(
                    "Sent %d study session reminder(s): %s",
                    len(results),
                    [item["study_session_id"] for item in results],
                )
        except Exception as e:  # pylint: disable=broad-except
            logger.error(f"Error dispatching study session reminders: {e}")
            db.rollback()
        finally:
            db.close()
            
    def _update_last_sync_timestamp(self, db: Session):
        """Update the last sync timestamp"""
        # This could be stored in a settings table or environment variable
        # For now, we'll just log it
        logger.info(f"Last sync completed at: {datetime.utcnow()}")
        
    def get_scheduler_status(self) -> dict:
        """Get current scheduler status"""
        if not self.is_running:
            return {"status": "stopped", "jobs": []}
            
        jobs = []
        for job in self.scheduler.get_jobs():
            jobs.append({
                "id": job.id,
                "name": job.name,
                "next_run": job.next_run_time.isoformat() if job.next_run_time else None,
                "trigger": str(job.trigger)
            })
            
        return {
            "status": "running",
            "jobs": jobs
        }

# Global scheduler instance
scheduler = AptoraScheduler()
