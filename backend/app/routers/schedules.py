from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from ..models import User, StudySession
from ..schemas import ScheduleRequest, ScheduleResponse, StudySession as StudySessionSchema, StudySessionUpdate
from ..auth import current_active_user
from ..schedule_generator import ScheduleGenerator
import logging

logger = logging.getLogger(__name__)
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


# ML Model Training Endpoints

@router.post("/ml/train")
async def train_ml_model(
    current_user: User = Depends(current_active_user),
    db: Session = Depends(get_db)
):
    """
    Train XGBoost model on historical feedback data.
    Requires admin privileges in production.
    """
    from ..ml.training.model_trainer import ModelTrainer

    try:
        trainer = ModelTrainer(db)
        results = trainer.train_model()

        if not results['success']:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=results.get('error', 'Training failed')
            )

        return {
            "message": "Model trained successfully",
            "results": results
        }

    except Exception as e:
        logger.error(f"Model training failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Model training failed: {str(e)}"
        )


@router.get("/ml/model-info")
async def get_model_info(
    db: Session = Depends(get_db)
):
    """Get information about the currently loaded ML model."""
    from ..ml.models.xgboost_estimator import XGBoostTimeEstimator

    try:
        estimator = XGBoostTimeEstimator(db)

        return {
            "model_type": "xgboost" if estimator.is_trained else "rule-based",
            "model_version": estimator.model_version,
            "is_trained": estimator.is_trained,
            "model_path": str(estimator.model_path)
        }
    except Exception as e:
        return {
            "error": str(e),
            "model_type": "unknown"
        }


@router.get("/ml/evaluate")
async def evaluate_model(
    current_user: User = Depends(current_active_user),
    db: Session = Depends(get_db)
):
    """Evaluate XGBoost model performance against baseline."""
    from ..ml.training.model_trainer import ModelTrainer

    try:
        trainer = ModelTrainer(db)
        results = trainer.evaluate_against_baseline()

        if 'error' in results:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=results['error']
            )

        return results

    except Exception as e:
        logger.error(f"Model evaluation failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Evaluation failed: {str(e)}"
        )


@router.get("/ml/training-data-stats")
async def get_training_data_stats(
    current_user: User = Depends(current_active_user),
    db: Session = Depends(get_db)
):
    """Get statistics about available training data."""
    from ..models import StudySessionFeedback, StudySession

    total_feedback = db.query(StudySessionFeedback).count()

    valid_feedback = db.query(StudySessionFeedback).join(
        StudySession
    ).filter(
        StudySession.is_completed == True,
        StudySessionFeedback.actual_duration_hours.isnot(None)
    ).count()

    return {
        "total_feedback_entries": total_feedback,
        "valid_training_samples": valid_feedback,
        "ready_for_training": valid_feedback >= 20,
        "min_samples_required": 20
    }


@router.post("/ml/retrain")
async def retrain_model(
    force: bool = False,
    current_user: User = Depends(current_active_user),
    db: Session = Depends(get_db)
):
    """
    Automatically retrain model if conditions are met.
    Checks if enough new feedback data is available and retrains accordingly.
    """
    from ..ml.training.retraining_service import RetrainingService

    try:
        retraining_service = RetrainingService(
            db,
            min_new_samples=50,  # Retrain after 50 new samples
            min_improvement_pct=5.0  # Accept model if not worse than 5%
        )

        results = retraining_service.retrain_model(force=force)

        if not results['success']:
            if results.get('retraining_needed') is False:
                # Not an error, just not needed yet
                return {
                    "message": "Retraining not needed",
                    "details": results
                }
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=results.get('error', 'Retraining failed')
                )

        return {
            "message": f"Model {results['action']}",
            "results": results
        }

    except Exception as e:
        logger.error(f"Retraining failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Retraining failed: {str(e)}"
        )


@router.get("/ml/retraining-status")
async def get_retraining_status(
    current_user: User = Depends(current_active_user),
    db: Session = Depends(get_db)
):
    """Check if model retraining is needed based on new feedback data."""
    from ..ml.training.retraining_service import RetrainingService

    retraining_service = RetrainingService(db)
    status_info = retraining_service.check_retraining_needed()

    return status_info
