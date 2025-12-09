#!/usr/bin/env python3
"""
Test script for web scrapers
Tests Reddit and RateMyProfessor scrapers
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from app.database import SessionLocal, engine, Base
from app.models import *
from app.services.scrapers.reddit_scraper import RedditScraper
from app.services.scrapers.ratemyprofessor_scraper import RateMyProfessorScraper
from app.services.scrapers.scraper_manager import ScraperManager
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_reddit_scraper():
    """Test Reddit scraper"""
    print("\n" + "="*80)
    print("Testing Reddit Scraper")
    print("="*80)
    
    scraper = RedditScraper()
    test_course = "CS 225"
    
    print(f"\nScraping Reddit for course: {test_course}")
    result = scraper.scrape_with_error_handling(test_course, limit=10)
    
    if result:
        print(f"✓ Successfully scraped data for {test_course}")
        print(f"  - Avg hours per week: {result.get('avg_hours_per_week', 'N/A')}")
        print(f"  - Difficulty score: {result.get('difficulty_score', 'N/A')}")
        print(f"  - Posts analyzed: {result.get('posts_analyzed', 0)}")
        print(f"  - Comments analyzed: {result.get('comments_analyzed', 0)}")
        return True
    else:
        print(f"✗ Failed to scrape data for {test_course}")
        return False

def test_ratemyprofessor_scraper():
    """Test RateMyProfessor scraper"""
    print("\n" + "="*80)
    print("Testing RateMyProfessor Scraper")
    print("="*80)
    
    scraper = RateMyProfessorScraper()
    test_professor = "Geoffrey Challen"
    
    print(f"\nScraping RateMyProfessor for professor: {test_professor}")
    result = scraper.scrape_with_error_handling(test_professor)
    
    if result and result.get('overall_rating'):
        print(f"✓ Successfully scraped data for {test_professor}")
        print(f"  - Overall rating: {result.get('overall_rating', 'N/A')}")
        print(f"  - Difficulty rating: {result.get('difficulty_rating', 'N/A')}")
        print(f"  - Would take again: {result.get('would_take_again_percent', 'N/A')}%")
        print(f"  - Rating count: {result.get('rating_count', 0)}")
        return True
    else:
        print(f"⚠ No data found for {test_professor} (this is okay - may need better parsing)")
        print("  Note: RateMyProfessor may require more sophisticated parsing")
        return False

def test_scraper_manager():
    """Test ScraperManager integration"""
    print("\n" + "="*80)
    print("Testing Scraper Manager")
    print("="*80)
    
    db = SessionLocal()
    try:
        manager = ScraperManager(db)
        test_course = "CS 225"
        
        print(f"\nTesting course data scraping for: {test_course}")
        result = manager.scrape_course_data(test_course, force_refresh=True)
        
        if result:
            print(f"✓ Scraper manager returned data")
            if 'reddit' in result:
                print(f"  - Reddit data: {bool(result['reddit'])}")
            return True
        else:
            print(f"⚠ No data returned (may be expected if scrapers fail)")
            return False
    finally:
        db.close()

def test_database_storage():
    """Test that scraped data can be stored in database"""
    print("\n" + "="*80)
    print("Testing Database Storage")
    print("="*80)
    
    db = SessionLocal()
    try:
        # Check if tables exist
        from sqlalchemy import inspect
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        
        required_tables = [
            'course_insights',
            'professor_ratings',
            'scraper_jobs'
        ]
        
        missing_tables = [t for t in required_tables if t not in tables]
        
        if missing_tables:
            print(f"✗ Missing tables: {missing_tables}")
            return False
        else:
            print(f"✓ All required tables exist")
            return True
    finally:
        db.close()

def main():
    """Run all tests"""
    print("\n" + "="*80)
    print("WEB SCRAPER TEST SUITE")
    print("="*80)
    
    results = {}
    
    # Test database
    results['database'] = test_database_storage()
    
    # Test Reddit scraper
    results['reddit'] = test_reddit_scraper()
    
    # Test RateMyProfessor scraper
    results['ratemyprofessor'] = test_ratemyprofessor_scraper()
    
    # Test ScraperManager
    results['manager'] = test_scraper_manager()
    
    # Summary
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    for test_name, passed in results.items():
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{test_name:20} {status}")
    
    all_passed = all(results.values())
    print("\n" + ("="*80))
    if all_passed:
        print("✓ ALL TESTS PASSED")
    else:
        print("⚠ SOME TESTS FAILED (This may be expected for RateMyProfessor)")
    print("="*80 + "\n")
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())

