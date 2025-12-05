from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from ..models import User, Course
from ..schemas import CourseCreate, CourseUpdate, Course as CourseSchema
from ..auth import current_active_user

router = APIRouter(prefix="/courses", tags=["courses"])


@router.post("/", response_model=CourseSchema)
async def create_course(
    course: CourseCreate,
    current_user: User = Depends(current_active_user),
    db: Session = Depends(get_db)
):
    """Create a new course."""
    try:
        course_dict = course.dict(exclude_unset=True)
        db_course = Course(**course_dict, user_id=current_user.id)
        db.add(db_course)
        db.commit()
        db.refresh(db_course)
        return db_course
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create course: {str(e)}"
        )


@router.get("/", response_model=List[CourseSchema])
async def get_courses(
    current_user: User = Depends(current_active_user),
    db: Session = Depends(get_db)
):
    """Get all courses for the current user."""
    courses = db.query(Course).filter(Course.user_id == current_user.id).all()
    return courses


@router.get("/{course_id}", response_model=CourseSchema)
async def get_course(
    course_id: int,
    current_user: User = Depends(current_active_user),
    db: Session = Depends(get_db)
):
    """Get a specific course by ID."""
    course = db.query(Course).filter(
        Course.id == course_id,
        Course.user_id == current_user.id
    ).first()
    
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found"
        )
    
    return course


@router.put("/{course_id}", response_model=CourseSchema)
async def update_course(
    course_id: int,
    course_update: CourseUpdate,
    current_user: User = Depends(current_active_user),
    db: Session = Depends(get_db)
):
    """Update a course."""
    course = db.query(Course).filter(
        Course.id == course_id,
        Course.user_id == current_user.id
    ).first()
    
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found"
        )
    
    for field, value in course_update.dict(exclude_unset=True).items():
        setattr(course, field, value)
    
    db.commit()
    db.refresh(course)
    return course


@router.delete("/{course_id}")
async def delete_course(
    course_id: int,
    current_user: User = Depends(current_active_user),
    db: Session = Depends(get_db)
):
    """Delete a course."""
    course = db.query(Course).filter(
        Course.id == course_id,
        Course.user_id == current_user.id
    ).first()
    
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found"
        )
    
    db.delete(course)
    db.commit()
    return {"message": "Course deleted successfully"}
