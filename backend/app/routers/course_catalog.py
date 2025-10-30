"""
Course Catalog API Router

Provides endpoints for accessing UIUC course catalog data.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from typing import List, Optional
import logging

from ..database import get_db
from ..models import CourseCatalog, CourseSection
from ..schemas import CourseCatalog as CourseCatalogSchema, CourseCatalogSearch
from ..data_ingestion.course_ingestion import CourseIngestionService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/course-catalog", tags=["course-catalog"])


@router.get("/", response_model=List[CourseCatalogSchema])
async def get_courses(
    skip: int = Query(0, ge=0, description="Number of courses to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of courses to return"),
    subject: Optional[str] = Query(None, description="Filter by subject code (e.g., 'CS')"),
    number: Optional[str] = Query(None, description="Filter by course number (e.g., '225')"),
    title: Optional[str] = Query(None, description="Filter by course title (partial match)"),
    semester: Optional[str] = Query(None, description="Filter by semester (fall, spring, summer, winter)"),
    year: Optional[int] = Query(None, description="Filter by academic year"),
    db: Session = Depends(get_db)
):
    """
    Get courses from the catalog with optional filtering.
    
    Returns a paginated list of courses matching the specified criteria.
    """
    try:
        query = db.query(CourseCatalog)
        
        # Apply filters
        if subject:
            query = query.filter(CourseCatalog.subject.ilike(f"%{subject}%"))
        
        if number:
            query = query.filter(CourseCatalog.number.ilike(f"%{number}%"))
        
        if title:
            query = query.filter(CourseCatalog.title.ilike(f"%{title}%"))
        
        if semester:
            query = query.filter(CourseCatalog.semester == semester)
        
        if year:
            query = query.filter(CourseCatalog.year == year)
        
        # Apply pagination
        courses = query.offset(skip).limit(limit).all()
        
        logger.info(f"Retrieved {len(courses)} courses with filters: subject={subject}, number={number}, title={title}, semester={semester}, year={year}")
        
        return courses
        
    except Exception as e:
        logger.error(f"Error retrieving courses: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/subjects", response_model=List[str])
async def get_subjects(db: Session = Depends(get_db)):
    """
    Get all unique subject codes from the catalog.
    
    Returns a list of subject codes (e.g., ['CS', 'MATH', 'PHYS']).
    """
    try:
        subjects = db.query(CourseCatalog.subject).distinct().all()
        subject_list = [subject[0] for subject in subjects]
        subject_list.sort()
        
        logger.info(f"Retrieved {len(subject_list)} unique subjects")
        return subject_list
        
    except Exception as e:
        logger.error(f"Error retrieving subjects: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/search", response_model=List[CourseCatalogSchema])
async def search_courses(
    q: str = Query(..., description="Search query (searches subject, number, and title)"),
    limit: int = Query(50, ge=1, le=200, description="Maximum number of results"),
    db: Session = Depends(get_db)
):
    """
    Search courses by subject, number, or title.
    
    Performs a case-insensitive search across subject, number, and title fields.
    Also handles combined searches like "CS 101" by splitting the query.
    """
    try:
        search_term = f"%{q}%"
        
        # Check if the query contains a space (e.g., "CS 101")
        if ' ' in q.strip():
            parts = q.strip().split()
            if len(parts) == 2:
                # Try to match subject and number separately
                subject_part = parts[0].upper()
                number_part = parts[1]
                
                courses = db.query(CourseCatalog).filter(
                    and_(
                        CourseCatalog.subject.ilike(f"%{subject_part}%"),
                        CourseCatalog.number.ilike(f"%{number_part}%")
                    )
                ).limit(limit).all()
                
                # If no results, fall back to general search
                if not courses:
                    courses = db.query(CourseCatalog).filter(
                        or_(
                            CourseCatalog.subject.ilike(search_term),
                            CourseCatalog.number.ilike(search_term),
                            CourseCatalog.title.ilike(search_term)
                        )
                    ).limit(limit).all()
            else:
                # Multiple words, search in title
                courses = db.query(CourseCatalog).filter(
                    CourseCatalog.title.ilike(search_term)
                ).limit(limit).all()
        else:
            # Single word search
            courses = db.query(CourseCatalog).filter(
                or_(
                    CourseCatalog.subject.ilike(search_term),
                    CourseCatalog.number.ilike(search_term),
                    CourseCatalog.title.ilike(search_term)
                )
            ).limit(limit).all()
        
        logger.info(f"Search for '{q}' returned {len(courses)} results")
        return courses
        
    except Exception as e:
        logger.error(f"Error searching courses: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/{subject}/{number}", response_model=CourseCatalogSchema)
async def get_course_by_subject_number(
    subject: str,
    number: str,
    semester: Optional[str] = Query(None, description="Semester (fall, spring, summer, winter)"),
    year: Optional[int] = Query(None, description="Academic year"),
    db: Session = Depends(get_db)
):
    """
    Get a specific course by subject and number.
    
    Returns the course details including sections.
    """
    try:
        query = db.query(CourseCatalog).filter(
            and_(
                CourseCatalog.subject == subject.upper(),
                CourseCatalog.number == number
            )
        )
        
        if semester:
            query = query.filter(CourseCatalog.semester == semester)
        
        if year:
            query = query.filter(CourseCatalog.year == year)
        
        course = query.first()
        
        if not course:
            raise HTTPException(
                status_code=404, 
                detail=f"Course {subject} {number} not found"
            )
        
        logger.info(f"Retrieved course {subject} {number}")
        return course
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving course {subject} {number}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/{subject}/{number}/sections", response_model=List[dict])
async def get_course_sections(
    subject: str,
    number: str,
    semester: Optional[str] = Query(None, description="Semester"),
    year: Optional[int] = Query(None, description="Academic year"),
    db: Session = Depends(get_db)
):
    """
    Get all sections for a specific course.
    
    Returns a list of sections with CRN, days, times, and instructor information.
    """
    try:
        # First find the course
        course_query = db.query(CourseCatalog).filter(
            and_(
                CourseCatalog.subject == subject.upper(),
                CourseCatalog.number == number
            )
        )
        
        if semester:
            course_query = course_query.filter(CourseCatalog.semester == semester)
        
        if year:
            course_query = course_query.filter(CourseCatalog.year == year)
        
        course = course_query.first()
        
        if not course:
            raise HTTPException(
                status_code=404, 
                detail=f"Course {subject} {number} not found"
            )
        
        # Get sections
        sections = db.query(CourseSection).filter(
            CourseSection.course_catalog_id == course.id
        ).all()
        
        # Convert to dict format
        sections_data = [
            {
                "crn": section.crn,
                "days": section.days,
                "times": section.times,
                "instructor": section.instructor
            }
            for section in sections
        ]
        
        logger.info(f"Retrieved {len(sections_data)} sections for {subject} {number}")
        return sections_data
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving sections for {subject} {number}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/admin/refresh")
async def refresh_course_catalog(
    year: Optional[int] = Query(None, description="Academic year to fetch"),
    semester: Optional[str] = Query(None, description="Semester to fetch"),
    db: Session = Depends(get_db)
):
    """
    Admin endpoint to refresh the course catalog data.
    
    Fetches fresh data from UIUC CIS API and Discovery dataset.
    This operation may take several minutes to complete.
    """
    try:
        logger.info("Starting course catalog refresh")
        
        service = CourseIngestionService(db)
        result = service.fetch_and_update_courses(
            year=year or 2025,
            semester=semester or "spring"
        )
        
        if "error" in result:
            raise HTTPException(status_code=500, detail=result["error"])
        
        logger.info("Course catalog refresh completed successfully")
        return {
            "message": "Course catalog refreshed successfully",
            "results": result
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error refreshing course catalog: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/admin/stats")
async def get_catalog_stats(db: Session = Depends(get_db)):
    """
    Get statistics about the course catalog.
    
    Returns counts of courses, subjects, and other useful metrics.
    """
    try:
        total_courses = db.query(CourseCatalog).count()
        total_subjects = db.query(CourseCatalog.subject).distinct().count()
        total_sections = db.query(CourseSection).count()
        
        # Get semester/year breakdown
        semester_stats = db.query(
            CourseCatalog.semester,
            CourseCatalog.year,
            db.func.count(CourseCatalog.id).label('count')
        ).group_by(CourseCatalog.semester, CourseCatalog.year).all()
        
        stats = {
            "total_courses": total_courses,
            "total_subjects": total_subjects,
            "total_sections": total_sections,
            "by_semester": [
                {
                    "semester": stat.semester,
                    "year": stat.year,
                    "count": stat.count
                }
                for stat in semester_stats
            ]
        }
        
        logger.info(f"Retrieved catalog stats: {total_courses} courses, {total_subjects} subjects, {total_sections} sections")
        return stats
        
    except Exception as e:
        logger.error(f"Error retrieving catalog stats: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
