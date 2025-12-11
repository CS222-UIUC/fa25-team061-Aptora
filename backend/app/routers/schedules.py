from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from ..models import User, StudySession
from ..schemas import ScheduleRequest, ScheduleResponse, StudySession as StudySessionSchema, StudySessionUpdate
from ..auth import current_active_user
from ..schedule_generator import ScheduleGenerator

router = APIRouter(prefix="/schedules", tags=["schedules"])


@router.post("/generate", response_model=ScheduleResponse)
async def generate_schedule(
    request: ScheduleRequest,
    current_user: User = Depends(current_active_user),
    db: Session = Depends(get_db)
):
    """Generate a personalized study schedule."""
    import logging
    from ..models import Assignment, AvailabilitySlot, Course
    logger = logging.getLogger(__name__)
    
    try:
        # Normalize datetimes (remove timezone if present for comparison)
        start_date = request.start_date
        end_date = request.end_date
        if start_date.tzinfo is not None:
            start_date = start_date.replace(tzinfo=None)
        if end_date.tzinfo is not None:
            end_date = end_date.replace(tzinfo=None)
        
        logger.info(f"Generating schedule for user {current_user.id} from {start_date} to {end_date}")
        
        # Check if user has assignments
        assignments_count = db.query(Assignment).join(Course).filter(
            Course.user_id == current_user.id,
            Assignment.due_date >= start_date,
            Assignment.due_date <= end_date,
            Assignment.is_completed == False
        ).count()
        
        # Check if user has availability slots
        availability_count = db.query(AvailabilitySlot).filter(
            AvailabilitySlot.user_id == current_user.id
        ).count()
        
        if assignments_count == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No assignments found in the selected date range. Please create assignments first."
            )
        
        if availability_count == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No availability slots found. Please set your availability in the Availability page first."
            )
        
        # Create a new request with normalized dates
        from ..schemas import ScheduleRequest
        normalized_request = ScheduleRequest(start_date=start_date, end_date=end_date)
        
        generator = ScheduleGenerator(db)
        schedule = generator.generate_schedule(current_user.id, normalized_request)
        logger.info(f"Successfully generated schedule with {len(schedule.study_sessions)} sessions")
        return schedule
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating schedule: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate schedule: {str(e)}"
        )


@router.get("/sessions", response_model=List[StudySessionSchema])
async def get_study_sessions(
    current_user: User = Depends(current_active_user),
    db: Session = Depends(get_db)
):
    """Get all study sessions for the current user."""
    sessions = db.query(StudySession).filter(
        StudySession.user_id == current_user.id
    ).all()
    return sessions


@router.get("/sessions/{session_id}", response_model=StudySessionSchema)
async def get_study_session(
    session_id: int,
    current_user: User = Depends(current_active_user),
    db: Session = Depends(get_db)
):
    """Get a specific study session by ID."""
    session = db.query(StudySession).filter(
        StudySession.id == session_id,
        StudySession.user_id == current_user.id
    ).first()
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Study session not found"
        )
    
    return session


@router.put("/sessions/{session_id}", response_model=StudySessionSchema)
async def update_study_session(
    session_id: int,
    session_update: StudySessionUpdate,
    current_user: User = Depends(current_active_user),
    db: Session = Depends(get_db)
):
    """Update a study session."""
    session = db.query(StudySession).filter(
        StudySession.id == session_id,
        StudySession.user_id == current_user.id
    ).first()
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Study session not found"
        )
    
    for field, value in session_update.dict(exclude_unset=True).items():
        setattr(session, field, value)
    
    db.commit()
    db.refresh(session)
    return session


@router.delete("/sessions/{session_id}")
async def delete_study_session(
    session_id: int,
    current_user: User = Depends(current_active_user),
    db: Session = Depends(get_db)
):
    """Delete a study session."""
    session = db.query(StudySession).filter(
        StudySession.id == session_id,
        StudySession.user_id == current_user.id
    ).first()
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Study session not found"
        )
    
    db.delete(session)
    db.commit()
    return {"message": "Study session deleted successfully"}


@router.patch("/sessions/{session_id}/complete")
async def mark_session_complete(
    session_id: int,
    current_user: User = Depends(current_active_user),
    db: Session = Depends(get_db)
):
    """Mark a study session as completed."""
    session = db.query(StudySession).filter(
        StudySession.id == session_id,
        StudySession.user_id == current_user.id
    ).first()
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Study session not found"
        )
    
    session.is_completed = True
    db.commit()
    return {"message": "Study session marked as completed"}


# ML-Powered Endpoints

@router.post("/generate-ml")
async def generate_ml_schedule(
    request: ScheduleRequest,
    current_user: User = Depends(current_active_user),
    db: Session = Depends(get_db)
):
    """Generate ML-powered intelligent study schedule with predictions."""
    from ..services.ml_service import MLScheduleService
    from ..models import Assignment, AvailabilitySlot, Course
    import logging
    logger = logging.getLogger(__name__)

    try:
        # Normalize datetimes (remove timezone if present for comparison)
        start_date = request.start_date
        end_date = request.end_date
        if start_date.tzinfo is not None:
            start_date = start_date.replace(tzinfo=None)
        if end_date.tzinfo is not None:
            end_date = end_date.replace(tzinfo=None)
        
        # Check prerequisites
        assignments_count = db.query(Assignment).join(Course).filter(
            Course.user_id == current_user.id,
            Assignment.due_date >= start_date,
            Assignment.due_date <= end_date,
            Assignment.is_completed == False
        ).count()
        
        availability_count = db.query(AvailabilitySlot).filter(
            AvailabilitySlot.user_id == current_user.id
        ).count()
        
        if assignments_count == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No assignments found in the selected date range. Please create assignments first."
            )
        
        if availability_count == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No availability slots found. Please set your availability in the Availability page first."
            )
        
        ml_service = MLScheduleService(db)
        result = ml_service.generate_ml_schedule(
            current_user.id,
            start_date,
            end_date
        )
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"ML schedule generation failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"ML schedule generation failed: {str(e)}"
        )


@router.get("/insights/{course_code}")
async def get_course_insights(
    course_code: str,
    db: Session = Depends(get_db)
):
    """Get aggregated insights for a course from web scraping."""
    from ..services.ml_service import MLScheduleService

    ml_service = MLScheduleService(db)
    insights = ml_service.get_course_insights(course_code)
    return insights


@router.post("/feedback")
async def submit_schedule_feedback(
    session_id: int,
    actual_hours: float,
    productivity: float,
    difficulty: float,
    was_sufficient: bool,
    comments: str = "",
    current_user: User = Depends(current_active_user),
    db: Session = Depends(get_db)
):
    """Submit feedback on a study session for ML improvement."""
    from ..models import StudySessionFeedback

    feedback = StudySessionFeedback(
        study_session_id=session_id,
        actual_duration_hours=actual_hours,
        productivity_rating=productivity,
        difficulty_rating=difficulty,
        was_sufficient=was_sufficient,
        student_comments=comments
    )

    db.add(feedback)
    db.commit()

    return {"message": "Feedback submitted successfully", "id": feedback.id}
