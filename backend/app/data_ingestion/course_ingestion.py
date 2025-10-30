"""
Course Data Ingestion Module for Aptora

This module handles fetching course data from:
1. UIUC CIS API (current semester data)
2. Discovery CSV dataset (historical/descriptive data)

Combines both sources to create a comprehensive course catalog.
"""

import requests
import pandas as pd
from typing import List, Dict, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_
import logging
from datetime import datetime

from ..database import get_db
from ..models import CourseCatalog, CourseSection

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# UIUC CIS API Configuration
BASE_URL = "https://courses.illinois.edu/cisapi"
DISCOVERY_CSV_URL = "https://waf.cs.illinois.edu/discovery/course-catalog.csv"

# Current semester configuration (update as needed)
CURRENT_YEAR = 2025
CURRENT_SEMESTER = "spring"  # fall, spring, summer, winter


class CourseIngestionService:
    """Service class for ingesting course data from multiple sources."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_subjects(self, year: int, semester: str) -> List[str]:
        """
        Fetch all available subjects from UIUC CIS API.
        
        Args:
            year: Academic year
            semester: Semester (fall, spring, summer, winter)
            
        Returns:
            List of subject codes (e.g., ['CS', 'MATH', 'PHYS'])
        """
        try:
            url = f"{BASE_URL}/schedule/{year}/{semester}"
            headers = {"Accept": "application/json"}
            
            logger.info(f"Fetching subjects from {url}")
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            subjects = [subj['id'] for subj in data['subjects']['subject']]
            
            logger.info(f"Found {len(subjects)} subjects: {subjects[:10]}...")
            return subjects
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching subjects: {e}")
            return []
        except KeyError as e:
            logger.error(f"Unexpected API response format: {e}")
            return []
    
    def get_courses_for_subject(self, year: int, semester: str, subject: str) -> List[Dict]:
        """
        Fetch all courses for a specific subject from UIUC CIS API.
        
        Args:
            year: Academic year
            semester: Semester
            subject: Subject code (e.g., 'CS')
            
        Returns:
            List of course dictionaries
        """
        try:
            url = f"{BASE_URL}/schedule/{year}/{semester}/{subject}"
            headers = {"Accept": "application/json"}
            
            logger.info(f"Fetching courses for {subject} from {url}")
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            courses = []
            
            if 'courses' in data and 'course' in data['courses']:
                for course in data['courses']['course']:
                    courses.append({
                        "subject": subject,
                        "number": course["id"],
                        "title": course.get("label", ""),
                        "semester": semester,
                        "year": year
                    })
            
            logger.info(f"Found {len(courses)} courses for {subject}")
            return courses
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching courses for {subject}: {e}")
            return []
        except KeyError as e:
            logger.error(f"Unexpected API response format for {subject}: {e}")
            return []
    
    def get_course_details(self, year: int, semester: str, subject: str, number: str) -> Optional[Dict]:
        """
        Fetch detailed information for a specific course including sections.
        
        Args:
            year: Academic year
            semester: Semester
            subject: Subject code
            number: Course number
            
        Returns:
            Dictionary with course details and sections
        """
        try:
            url = f"{BASE_URL}/schedule/{year}/{semester}/{subject}/{number}"
            headers = {"Accept": "application/json"}
            
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            course_info = data.get('course', {})
            
            # Extract sections
            sections = []
            if 'sections' in course_info and 'section' in course_info['sections']:
                for section in course_info['sections']['section']:
                    sections.append({
                        "crn": section.get("id", ""),
                        "days": section.get("days", ""),
                        "times": section.get("times", ""),
                        "instructor": section.get("instructor", "")
                    })
            
            return {
                "subject": subject,
                "number": number,
                "title": course_info.get("label", ""),
                "semester": semester,
                "year": year,
                "sections": sections
            }
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching details for {subject} {number}: {e}")
            return None
        except KeyError as e:
            logger.error(f"Unexpected API response format for {subject} {number}: {e}")
            return None
    
    def load_discovery_dataset(self) -> pd.DataFrame:
        """
        Load the Discovery CSV dataset for historical course information.
        
        Returns:
            DataFrame with course information
        """
        try:
            logger.info(f"Loading Discovery dataset from {DISCOVERY_CSV_URL}")
            df = pd.read_csv(DISCOVERY_CSV_URL)
            
            # Clean column names
            df.columns = df.columns.str.lower().str.replace(' ', '_')
            
            # Select relevant columns
            relevant_columns = ["subject", "number", "title", "description", "credit_hours"]
            available_columns = [col for col in relevant_columns if col in df.columns]
            
            if not available_columns:
                logger.warning("No relevant columns found in Discovery dataset")
                return pd.DataFrame()
            
            df_clean = df[available_columns].copy()
            
            # Clean data
            df_clean = df_clean.dropna(subset=["subject", "number"])
            df_clean["number"] = df_clean["number"].astype(str)
            
            logger.info(f"Loaded {len(df_clean)} courses from Discovery dataset")
            return df_clean
            
        except Exception as e:
            logger.error(f"Error loading Discovery dataset: {e}")
            return pd.DataFrame()
    
    def combine_datasets(self, cis_data: List[Dict], discovery_df: pd.DataFrame) -> List[Dict]:
        """
        Combine CIS API data with Discovery dataset information.
        
        Args:
            cis_data: List of course dictionaries from CIS API
            discovery_df: DataFrame from Discovery dataset
            
        Returns:
            List of enriched course dictionaries
        """
        combined = []
        
        for course in cis_data:
            # Try to find matching record in discovery dataset
            if not discovery_df.empty:
                match = discovery_df[
                    (discovery_df["subject"] == course["subject"]) &
                    (discovery_df["number"].astype(str) == str(course["number"]))
                ]
                
                if not match.empty:
                    match_row = match.iloc[0]
                    course["description"] = match_row.get("description", "")
                    course["credit_hours"] = match_row.get("credit_hours", None)
                else:
                    course["description"] = ""
                    course["credit_hours"] = None
            else:
                course["description"] = ""
                course["credit_hours"] = None
            
            combined.append(course)
        
        logger.info(f"Combined {len(combined)} courses with Discovery data")
        return combined
    
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
    
    def fetch_and_update_courses(self, year: int = CURRENT_YEAR, semester: str = CURRENT_SEMESTER) -> Dict:
        """
        Main method to fetch and update all course data.
        
        Args:
            year: Academic year to fetch
            semester: Semester to fetch
            
        Returns:
            Dictionary with operation results
        """
        logger.info(f"Starting course ingestion for {semester} {year}")
        
        # Step 1: Load Discovery dataset
        discovery_df = self.load_discovery_dataset()
        
        # Step 2: Get all subjects
        subjects = self.get_subjects(year, semester)
        if not subjects:
            return {"error": "No subjects found", "courses_saved": 0}
        
        # Step 3: Fetch courses for each subject
        all_courses = []
        for subject in subjects:
            courses = self.get_courses_for_subject(year, semester, subject)
            all_courses.extend(courses)
        
        logger.info(f"Fetched {len(all_courses)} courses from CIS API")
        
        # Step 4: Get detailed information for each course (with sections)
        detailed_courses = []
        for course in all_courses:
            details = self.get_course_details(
                year, semester, course["subject"], course["number"]
            )
            if details:
                detailed_courses.append(details)
        
        logger.info(f"Fetched detailed information for {len(detailed_courses)} courses")
        
        # Step 5: Combine with Discovery data
        combined_courses = self.combine_datasets(detailed_courses, discovery_df)
        
        # Step 6: Save to database
        saved_count = self.save_courses_to_db(combined_courses)
        
        return {
            "success": True,
            "subjects_found": len(subjects),
            "courses_fetched": len(all_courses),
            "courses_with_details": len(detailed_courses),
            "courses_saved": saved_count,
            "semester": semester,
            "year": year
        }


def run_course_ingestion():
    """Standalone function to run course ingestion."""
    db = next(get_db())
    service = CourseIngestionService(db)
    result = service.fetch_and_update_courses()
    
    print("Course Ingestion Results:")
    print(f"Success: {result.get('success', False)}")
    print(f"Subjects Found: {result.get('subjects_found', 0)}")
    print(f"Courses Fetched: {result.get('courses_fetched', 0)}")
    print(f"Courses with Details: {result.get('courses_with_details', 0)}")
    print(f"Courses Saved: {result.get('courses_saved', 0)}")
    print(f"Semester: {result.get('semester', 'N/A')} {result.get('year', 'N/A')}")
    
    if "error" in result:
        print(f"Error: {result['error']}")
    
    return result


if __name__ == "__main__":
    run_course_ingestion()
