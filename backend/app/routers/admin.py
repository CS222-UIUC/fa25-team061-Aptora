"""
Admin Router for Aptora
Handles administrative tasks like data updates and system management
"""

import logging
from datetime import datetime
from typing import Dict, Any
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from sqlalchemy import func

from ..database import get_db
from ..data_ingestion.discovery_ingestion import load_discovery_dataset, save_courses_to_db
from ..models import CourseCatalog, CourseSection, User
from ..scheduler import scheduler
from ..config import settings

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/admin", tags=["admin"])

@router.get("/status")
async def get_system_status(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """Get system status and statistics"""
    try:
        # Get course statistics
        total_courses = db.query(CourseCatalog).count()
        total_sections = db.query(CourseSection).count()
        
        # Get unique subjects count
        unique_subjects = db.query(func.count(func.distinct(CourseCatalog.subject))).scalar()
        
        # Get latest course update
        latest_course = db.query(CourseCatalog).order_by(CourseCatalog.updated_at.desc()).first()
        last_updated = latest_course.updated_at if latest_course else None
        
        # Get scheduler status
        scheduler_status = scheduler.get_scheduler_status()
        
        return {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "database": {
                "total_courses": total_courses,
                "total_sections": total_sections,
                "unique_subjects": unique_subjects,
                "last_updated": last_updated.isoformat() if last_updated else None
            },
            "scheduler": scheduler_status
        }
        
    except Exception as e:
        logger.error(f"Error getting system status: {e}")
        raise HTTPException(status_code=500, detail="Failed to get system status")

@router.post("/refresh-courses")
async def refresh_course_data(
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Manually trigger course data refresh"""
    try:
        logger.info("Manual course data refresh triggered")
        
        # Add the refresh task to background tasks
        background_tasks.add_task(update_course_data_task, db)
        
        return {
            "message": "Course data refresh started",
            "timestamp": datetime.utcnow().isoformat(),
            "status": "processing"
        }
        
    except Exception as e:
        logger.error(f"Error starting course data refresh: {e}")
        raise HTTPException(status_code=500, detail="Failed to start course data refresh")

async def update_course_data_task(db: Session):
    """Background task to update course data"""
    try:
        logger.info("Starting background course data update...")
        
        # Load fresh data from Discovery dataset
        df = load_discovery_dataset()
        
        # Save to database
        courses_added, courses_updated = save_courses_to_db(df, db)
        
        logger.info(f"Background course data update completed: {courses_added} added, {courses_updated} updated")
        
    except Exception as e:
        logger.error(f"Error during background course data update: {e}")
    finally:
        db.close()

@router.get("/courses/stats")
async def get_course_statistics(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """Get detailed course statistics"""
    try:
        # Get courses by subject
        subject_stats = db.query(
            CourseCatalog.subject,
            func.count(CourseCatalog.id).label('count')
        ).group_by(CourseCatalog.subject).order_by(func.count(CourseCatalog.id).desc()).limit(20).all()
        
        # Get courses by semester
        semester_stats = db.query(
            CourseCatalog.semester,
            CourseCatalog.year,
            func.count(CourseCatalog.id).label('count')
        ).group_by(CourseCatalog.semester, CourseCatalog.year).order_by(
            CourseCatalog.year.desc(), CourseCatalog.semester
        ).all()
        
        # Get courses with sections
        courses_with_sections = db.query(CourseCatalog).join(CourseSection).distinct().count()
        
        return {
            "top_subjects": [{"subject": s.subject, "count": s.count} for s in subject_stats],
            "by_semester": [{"semester": s.semester, "year": s.year, "count": s.count} for s in semester_stats],
            "courses_with_sections": courses_with_sections,
            "total_courses": db.query(CourseCatalog).count(),
            "total_sections": db.query(CourseSection).count()
        }
        
    except Exception as e:
        logger.error(f"Error getting course statistics: {e}")
        raise HTTPException(status_code=500, detail="Failed to get course statistics")

@router.post("/scheduler/start")
async def start_scheduler() -> Dict[str, str]:
    """Start the background scheduler"""
    try:
        scheduler.start()
        return {"message": "Scheduler started successfully"}
    except Exception as e:
        logger.error(f"Error starting scheduler: {e}")
        raise HTTPException(status_code=500, detail="Failed to start scheduler")

@router.post("/scheduler/stop")
async def stop_scheduler() -> Dict[str, str]:
    """Stop the background scheduler"""
    try:
        scheduler.stop()
        return {"message": "Scheduler stopped successfully"}
    except Exception as e:
        logger.error(f"Error stopping scheduler: {e}")
        raise HTTPException(status_code=500, detail="Failed to stop scheduler")

@router.get("/scheduler/status")
async def get_scheduler_status() -> Dict[str, Any]:
    """Get scheduler status and job information"""
    return scheduler.get_scheduler_status()

@router.get("/pending-verifications")
async def get_pending_verifications(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """
    Get list of users with pending email verifications (development only).
    This endpoint is useful when SMTP is not configured.
    """
    try:
        unverified_users = db.query(User).filter(
            User.is_verified == False,
            User.is_active == True
        ).all()
        
        verification_links = []
        for user in unverified_users:
            if user.verification_token:
                verification_link = f"{settings.frontend_url}/verify-email?token={user.verification_token}"
                verification_links.append({
                    "email": user.email,
                    "name": f"{user.first_name} {user.last_name}",
                    "user_id": user.id,
                    "verification_link": verification_link,
                    "token_expires": user.verification_token_expires.isoformat() if user.verification_token_expires else None,
                    "created_at": user.created_at.isoformat() if user.created_at else None
                })
        
        return {
            "smtp_configured": settings.smtp_server is not None,
            "total_unverified": len(unverified_users),
            "pending_verifications": verification_links,
            "note": "If SMTP is not configured, verification links are logged to console when users register."
        }
        
    except Exception as e:
        logger.error(f"Error getting pending verifications: {e}")
        raise HTTPException(status_code=500, detail="Failed to get pending verifications")
