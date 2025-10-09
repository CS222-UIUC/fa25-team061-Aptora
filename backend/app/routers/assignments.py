from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from ..models import User, Assignment, Course
from ..schemas import AssignmentCreate, AssignmentUpdate, Assignment as AssignmentSchema
from ..auth import current_active_user

router = APIRouter(prefix="/assignments", tags=["assignments"])


@router.post("/", response_model=AssignmentSchema)
async def create_assignment(
    assignment: AssignmentCreate,
    current_user: User = Depends(current_active_user),
    db: Session = Depends(get_db)
):
    """Create a new assignment."""
    # Verify that the course belongs to the user
    course = db.query(Course).filter(
        Course.id == assignment.course_id,
        Course.user_id == current_user.id
    ).first()
    
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found"
        )
    
    db_assignment = Assignment(**assignment.dict())
    db.add(db_assignment)
    db.commit()
    db.refresh(db_assignment)
    return db_assignment


@router.get("/", response_model=List[AssignmentSchema])
async def get_assignments(
    current_user: User = Depends(current_active_user),
    db: Session = Depends(get_db)
):
    """Get all assignments for the current user."""
    assignments = db.query(Assignment).join(Course).filter(
        Course.user_id == current_user.id
    ).all()
    return assignments


@router.get("/{assignment_id}", response_model=AssignmentSchema)
async def get_assignment(
    assignment_id: int,
    current_user: User = Depends(current_active_user),
    db: Session = Depends(get_db)
):
    """Get a specific assignment by ID."""
    assignment = db.query(Assignment).join(Course).filter(
        Assignment.id == assignment_id,
        Course.user_id == current_user.id
    ).first()
    
    if not assignment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assignment not found"
        )
    
    return assignment


@router.put("/{assignment_id}", response_model=AssignmentSchema)
async def update_assignment(
    assignment_id: int,
    assignment_update: AssignmentUpdate,
    current_user: User = Depends(current_active_user),
    db: Session = Depends(get_db)
):
    """Update an assignment."""
    assignment = db.query(Assignment).join(Course).filter(
        Assignment.id == assignment_id,
        Course.user_id == current_user.id
    ).first()
    
    if not assignment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assignment not found"
        )
    
    for field, value in assignment_update.dict(exclude_unset=True).items():
        setattr(assignment, field, value)
    
    db.commit()
    db.refresh(assignment)
    return assignment


@router.delete("/{assignment_id}")
async def delete_assignment(
    assignment_id: int,
    current_user: User = Depends(current_active_user),
    db: Session = Depends(get_db)
):
    """Delete an assignment."""
    assignment = db.query(Assignment).join(Course).filter(
        Assignment.id == assignment_id,
        Course.user_id == current_user.id
    ).first()
    
    if not assignment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assignment not found"
        )
    
    db.delete(assignment)
    db.commit()
    return {"message": "Assignment deleted successfully"}


@router.patch("/{assignment_id}/complete")
async def mark_assignment_complete(
    assignment_id: int,
    current_user: User = Depends(current_active_user),
    db: Session = Depends(get_db)
):
    """Mark an assignment as completed."""
    assignment = db.query(Assignment).join(Course).filter(
        Assignment.id == assignment_id,
        Course.user_id == current_user.id
    ).first()
    
    if not assignment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assignment not found"
        )
    
    assignment.is_completed = True
    db.commit()
    return {"message": "Assignment marked as completed"}
