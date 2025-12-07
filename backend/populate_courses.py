#!/usr/bin/env python3
"""
Script to populate the course catalog database from UIUC sources
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from app.database import SessionLocal
from app.data_ingestion.course_ingestion import CourseIngestionService
from app.data_ingestion.discovery_ingestion import DiscoveryIngestionService
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    """Populate course catalog database"""
    print("="*80)
    print("POPULATING COURSE CATALOG FROM UIUC")
    print("="*80)
    print()
    
    db = SessionLocal()
    try:
        # Try CIS API first
        print("Attempting to fetch from UIUC CIS API...")
        service = CourseIngestionService(db)
        result = service.fetch_and_update_courses(
            year=2025,
            semester="spring"
        )
        
        # If CIS API fails, fall back to Discovery dataset
        if "error" in result:
            print()
            print("⚠ CIS API unavailable. Falling back to Discovery dataset...")
            print("This may take a few minutes...")
            print()
            
            discovery_service = DiscoveryIngestionService(db)
            result = discovery_service.ingest_discovery_data()
            
            if "error" in result:
                print(f"❌ Error: {result['error']}")
                return 1
        
        print()
        print("="*80)
        print("COURSE CATALOG POPULATION COMPLETE")
        print("="*80)
        if "subjects_found" in result:
            print(f"✓ Subjects found: {result.get('subjects_found', 0)}")
            print(f"✓ Courses fetched: {result.get('courses_fetched', 0)}")
            print(f"✓ Courses with details: {result.get('courses_with_details', 0)}")
        else:
            print(f"✓ Total rows processed: {result.get('total_rows', 0)}")
            print(f"✓ Unique courses: {result.get('unique_courses', 0)}")
        print(f"✓ Courses saved: {result.get('courses_saved', 0)}")
        if "semester" in result:
            print(f"✓ Semester: {result.get('semester', 'N/A')} {result.get('year', 'N/A')}")
        if "data_source" in result:
            print(f"✓ Data source: {result.get('data_source', 'N/A')}")
        print("="*80)
        print()
        print("✅ Course catalog is now ready to use!")
        
        return 0
        
    except Exception as e:
        logger.error(f"Failed to populate course catalog: {e}", exc_info=True)
        print(f"❌ Error: {e}")
        return 1
    finally:
        db.close()

if __name__ == "__main__":
    sys.exit(main())

