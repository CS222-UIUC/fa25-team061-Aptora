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
