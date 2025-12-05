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
    generator = ScheduleGenerator(db)
    schedule = generator.generate_schedule(current_user.id, request)
    return schedule


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

    try:
        ml_service = MLScheduleService(db)
        result = ml_service.generate_ml_schedule(
            current_user.id,
            request.start_date,
            request.end_date
        )
        return result
    except Exception as e:
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
