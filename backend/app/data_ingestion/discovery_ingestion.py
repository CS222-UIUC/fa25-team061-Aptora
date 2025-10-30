"""
Discovery Dataset Ingestion Module

This module handles loading and processing the UIUC Discovery course catalog CSV.
Since the CIS API is currently unavailable, this provides a working alternative.
"""

import pandas as pd
from typing import List, Dict
from sqlalchemy.orm import Session
from sqlalchemy import and_
import logging
from datetime import datetime

from ..database import get_db
from ..models import CourseCatalog, CourseSection

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Discovery CSV URL
DISCOVERY_CSV_URL = "https://waf.cs.illinois.edu/discovery/course-catalog.csv"


class DiscoveryIngestionService:
    """Service class for ingesting course data from the Discovery dataset."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def load_discovery_dataset(self) -> pd.DataFrame:
        """
        Load the Discovery CSV dataset.
        
        Returns:
            DataFrame with course information
        """
        try:
            logger.info(f"Loading Discovery dataset from {DISCOVERY_CSV_URL}")
            df = pd.read_csv(DISCOVERY_CSV_URL)
            
            logger.info(f"Loaded {len(df)} rows from Discovery dataset")
            logger.info(f"Columns: {list(df.columns)}")
            
            return df
            
        except Exception as e:
            logger.error(f"Error loading Discovery dataset: {e}")
            return pd.DataFrame()
    
    def process_discovery_data(self, df: pd.DataFrame) -> List[Dict]:
        """
        Process the Discovery dataset into our course format.
        
        Args:
            df: Raw DataFrame from Discovery dataset
            
        Returns:
            List of processed course dictionaries
        """
        try:
            # Clean and filter the data
            df_clean = df.copy()
            
            # Remove rows with missing essential data
            df_clean = df_clean.dropna(subset=['Subject', 'Number', 'Name'])
            
            # Convert number to string for consistency
            df_clean['Number'] = df_clean['Number'].astype(str)
            
            # Group by course (Subject + Number + Name) to aggregate sections
            courses = []
            
            for (subject, number, name), group in df_clean.groupby(['Subject', 'Number', 'Name']):
                # Get course-level information from first row
                first_row = group.iloc[0]
                
                # Extract sections
                sections = []
                for _, section_row in group.iterrows():
                    if pd.notna(section_row.get('CRN')):
                        sections.append({
                            "crn": str(int(section_row['CRN'])),
                            "days": str(section_row.get('Days of Week', '')),
                            "times": f"{section_row.get('Start Time', '')} - {section_row.get('End Time', '')}".strip(' -'),
                            "instructor": str(section_row.get('Instructors', '')),
                            "room": str(section_row.get('Room', '')),
                            "building": str(section_row.get('Building', '')),
                            "type": str(section_row.get('Type', '')),
                            "enrollment_status": str(section_row.get('Enrollment Status', ''))
                        })
                
                # Extract credit hours
                credit_hours = None
                if pd.notna(first_row.get('Credit Hours')):
                    credit_str = str(first_row['Credit Hours'])
                    # Extract number from strings like "3 hours." or "3"
                    import re
                    match = re.search(r'(\d+(?:\.\d+)?)', credit_str)
                    if match:
                        credit_hours = float(match.group(1))
                
                # Create course dictionary
                course = {
                    "subject": str(subject),
                    "number": str(number),
                    "title": str(name),
                    "description": str(first_row.get('Description', '')),
                    "credit_hours": credit_hours,
                    "semester": str(first_row.get('Term', 'Unknown')),
                    "year": int(first_row.get('Year', 2024)),
                    "sections": sections,
                    "degree_attributes": str(first_row.get('Degree Attributes', '')),
                    "section_info": str(first_row.get('Section Info', ''))
                }
                
                courses.append(course)
            
            logger.info(f"Processed {len(courses)} unique courses from Discovery dataset")
            return courses
            
        except Exception as e:
            logger.error(f"Error processing Discovery data: {e}")
            return []
    
    def save_courses_to_db(self, courses: List[Dict]) -> int:
        """
        Save courses to the database.
        
        Args:
            courses: List of course dictionaries
            
        Returns:
            Number of courses saved
        """
        saved_count = 0
        
        for course_data in courses:
            try:
                # Check if course already exists
                existing_course = self.db.query(CourseCatalog).filter(
                    and_(
                        CourseCatalog.subject == course_data["subject"],
                        CourseCatalog.number == course_data["number"],
                        CourseCatalog.semester == course_data["semester"],
                        CourseCatalog.year == course_data["year"]
                    )
                ).first()
                
                if existing_course:
                    # Update existing course
                    existing_course.title = course_data["title"]
                    existing_course.description = course_data.get("description", "")
                    existing_course.credit_hours = course_data.get("credit_hours")
                    existing_course.updated_at = datetime.utcnow()
                    
                    # Update sections
                    if "sections" in course_data:
                        # Clear existing sections
                        self.db.query(CourseSection).filter(
                            CourseSection.course_catalog_id == existing_course.id
                        ).delete()
                        
                        # Add new sections
                        for section_data in course_data["sections"]:
                            section = CourseSection(
                                crn=section_data["crn"],
                                days=section_data.get("days"),
                                times=section_data.get("times"),
                                instructor=section_data.get("instructor"),
                                course_catalog_id=existing_course.id
                            )
                            self.db.add(section)
                else:
                    # Create new course
                    new_course = CourseCatalog(
                        subject=course_data["subject"],
                        number=course_data["number"],
                        title=course_data["title"],
                        description=course_data.get("description", ""),
                        credit_hours=course_data.get("credit_hours"),
                        semester=course_data["semester"],
                        year=course_data["year"]
                    )
                    self.db.add(new_course)
                    self.db.flush()  # Get the ID
                    
                    # Add sections
                    if "sections" in course_data:
                        for section_data in course_data["sections"]:
                            section = CourseSection(
                                crn=section_data["crn"],
                                days=section_data.get("days"),
                                times=section_data.get("times"),
                                instructor=section_data.get("instructor"),
                                course_catalog_id=new_course.id
                            )
                            self.db.add(section)
                
                saved_count += 1
                
            except Exception as e:
                logger.error(f"Error saving course {course_data.get('subject', '')} {course_data.get('number', '')}: {e}")
                continue
        
        try:
            self.db.commit()
            logger.info(f"Successfully saved {saved_count} courses to database")
        except Exception as e:
            logger.error(f"Error committing to database: {e}")
            self.db.rollback()
            return 0
        
        return saved_count
    
    def save_courses_to_db_with_stats(self, courses: List[Dict]) -> tuple[int, int]:
        """
        Save courses to the database with detailed statistics.
        
        Args:
            courses: List of course dictionaries
            
        Returns:
            Tuple of (courses_added, courses_updated)
        """
        added_count = 0
        updated_count = 0
        
        for course_data in courses:
            try:
                # Check if course already exists
                existing_course = self.db.query(CourseCatalog).filter(
                    and_(
                        CourseCatalog.subject == course_data["subject"],
                        CourseCatalog.number == course_data["number"],
                        CourseCatalog.semester == course_data["semester"],
                        CourseCatalog.year == course_data["year"]
                    )
                ).first()
                
                if existing_course:
                    # Update existing course
                    existing_course.title = course_data["title"]
                    existing_course.description = course_data.get("description", "")
                    existing_course.credit_hours = course_data.get("credit_hours")
                    existing_course.updated_at = datetime.utcnow()
                    
                    # Update sections
                    if "sections" in course_data:
                        # Clear existing sections
                        self.db.query(CourseSection).filter(
                            CourseSection.course_catalog_id == existing_course.id
                        ).delete()
                        
                        # Add new sections
                        for section_data in course_data["sections"]:
                            section = CourseSection(
                                crn=section_data["crn"],
                                days=section_data.get("days"),
                                times=section_data.get("times"),
                                instructor=section_data.get("instructor"),
                                course_catalog_id=existing_course.id
                            )
                            self.db.add(section)
                    updated_count += 1
                else:
                    # Create new course
                    new_course = CourseCatalog(
                        subject=course_data["subject"],
                        number=course_data["number"],
                        title=course_data["title"],
                        description=course_data.get("description", ""),
                        credit_hours=course_data.get("credit_hours"),
                        semester=course_data["semester"],
                        year=course_data["year"]
                    )
                    self.db.add(new_course)
                    self.db.flush()  # Get the ID
                    
                    # Add sections
                    if "sections" in course_data:
                        for section_data in course_data["sections"]:
                            section = CourseSection(
                                crn=section_data["crn"],
                                days=section_data.get("days"),
                                times=section_data.get("times"),
                                instructor=section_data.get("instructor"),
                                course_catalog_id=new_course.id
                            )
                            self.db.add(section)
                    added_count += 1
                
            except Exception as e:
                logger.error(f"Error saving course {course_data.get('subject', '')} {course_data.get('number', '')}: {e}")
                continue
        
        try:
            self.db.commit()
            logger.info(f"Successfully processed {added_count} new courses and {updated_count} updated courses")
        except Exception as e:
            logger.error(f"Error committing to database: {e}")
            self.db.rollback()
            return 0, 0
        
        return added_count, updated_count
    
    def ingest_discovery_data(self) -> Dict:
        """
        Main method to ingest Discovery dataset.
        
        Returns:
            Dictionary with operation results
        """
        logger.info("Starting Discovery dataset ingestion")
        
        # Step 1: Load Discovery dataset
        df = self.load_discovery_dataset()
        if df.empty:
            return {"error": "Failed to load Discovery dataset", "courses_saved": 0}
        
        # Step 2: Process the data
        courses = self.process_discovery_data(df)
        if not courses:
            return {"error": "Failed to process Discovery data", "courses_saved": 0}
        
        # Step 3: Save to database
        saved_count = self.save_courses_to_db(courses)
        
        return {
            "success": True,
            "total_rows": len(df),
            "unique_courses": len(courses),
            "courses_saved": saved_count,
            "data_source": "Discovery CSV"
        }


def run_discovery_ingestion():
    """Standalone function to run Discovery dataset ingestion."""
    db = next(get_db())
    service = DiscoveryIngestionService(db)
    result = service.ingest_discovery_data()
    
    print("Discovery Dataset Ingestion Results:")
    print(f"Success: {result.get('success', False)}")
    print(f"Total Rows: {result.get('total_rows', 0)}")
    print(f"Unique Courses: {result.get('unique_courses', 0)}")
    print(f"Courses Saved: {result.get('courses_saved', 0)}")
    print(f"Data Source: {result.get('data_source', 'N/A')}")
    
    if "error" in result:
        print(f"Error: {result['error']}")
    
    return result


def load_discovery_dataset() -> pd.DataFrame:
    """Standalone function to load Discovery dataset."""
    service = DiscoveryIngestionService(None)
    return service.load_discovery_dataset()


def save_courses_to_db(df: pd.DataFrame, db: Session) -> tuple[int, int]:
    """Standalone function to save courses to database with statistics."""
    service = DiscoveryIngestionService(db)
    courses = service.process_discovery_data(df)
    return service.save_courses_to_db_with_stats(courses)


if __name__ == "__main__":
    run_discovery_ingestion()
