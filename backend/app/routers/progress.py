from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..database import get_db
from ..auth import current_active_user
from ..models import User, Assignment, StudySession, Course


router = APIRouter(prefix="/progress", tags=["progress"])


@router.get("/")
async def get_progress(
    current_user: User = Depends(current_active_user),
    db: Session = Depends(get_db)
):
    assignments_total = db.query(Assignment).join(Course).filter(Course.user_id == current_user.id).count()
    assignments_completed = (
        db.query(Assignment)
        .join(Course)
        .filter(Course.user_id == current_user.id, Assignment.is_completed == True)
        .count()
    )

    sessions_total = db.query(StudySession).filter(StudySession.user_id == current_user.id).count()
    sessions_completed = (
        db.query(StudySession)
        .filter(StudySession.user_id == current_user.id, StudySession.is_completed == True)
        .count()
    )

    def pct(done: int, total: int) -> float:
        return round((done / total) * 100.0, 2) if total > 0 else 0.0

    return {
        "assignments": {
            "total": assignments_total,
            "completed": assignments_completed,
            "percent": pct(assignments_completed, assignments_total),
        },
        "study_sessions": {
            "total": sessions_total,
            "completed": sessions_completed,
            "percent": pct(sessions_completed, sessions_total),
        },
    }


