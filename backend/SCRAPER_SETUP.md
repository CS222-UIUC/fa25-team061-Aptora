# Web Scraper Setup and Configuration

## ✅ Completed Tasks

### 1. RateMyProfessor Scraper Implementation
- ✅ Implemented actual HTML parsing logic
- ✅ Added JSON extraction from embedded data
- ✅ Added fallback HTML parsing for ratings
- ✅ Handles professor search and profile page scraping

### 2. Database Migrations
- ✅ All tables created successfully
- ✅ Database schema is up to date

### 3. Test Script
- ✅ Created `test_scrapers.py` for testing scrapers
- ✅ Tests database storage, Reddit scraper, RateMyProfessor scraper, and ScraperManager

### 4. Reddit API Configuration
- ✅ Added Reddit credentials to `config.py`:
  - `reddit_client_id`
  - `reddit_client_secret`
  - `reddit_user_agent`
- ✅ ScraperManager now uses config settings automatically

### 5. Error Handling Improvements
- ✅ Enhanced error handling in `BaseScraper`:
  - HTTP error codes (401, 403, 404, 429)
  - Timeout handling
  - Connection error handling
  - Better logging
- ✅ Added PRAW-specific error handling in Reddit scraper

### 6. Data Validation
- ✅ Added validation before saving course insights:
  - Validates hours per week (0-100)
  - Validates difficulty score (0-10)
  - Validates workload rating (1-5)
- ✅ Added validation before saving professor ratings:
  - Validates overall rating (1-5)
  - Validates difficulty rating (1-5)
  - Validates would take again percent (0-100)
  - Validates rating count

## 🔧 Configuration

### Reddit API Setup (Optional but Recommended)

To use Reddit scraping with authentication, add to `.env`:

```env
REDDIT_CLIENT_ID=your_client_id_here
REDDIT_CLIENT_SECRET=your_client_secret_here
REDDIT_USER_AGENT=Aptora Study Scheduler v1.0
```

To get Reddit API credentials:
1. Go to https://www.reddit.com/prefs/apps
2. Click "create another app..." or "create app"
3. Choose "script" as the app type
4. Copy the client ID (under the app name) and secret

### RateMyProfessor

RateMyProfessor scraper works without authentication but may have rate limits.
The scraper includes multiple parsing strategies to extract data.

## 📊 Usage

### Testing Scrapers

```bash
cd backend
python test_scrapers.py
```

### Using in Code

```python
from app.services.scrapers.scraper_manager import ScraperManager
from app.database import SessionLocal

db = SessionLocal()
manager = ScraperManager(db)

# Scrape course data
insights = manager.scrape_course_data("CS 225")

# Scrape professor rating
rating = manager.scrape_professor_rating("Geoffrey Challen", course_code="CS 225")
```

### Using ML Service

```python
from app.services.ml_service import MLScheduleService
from app.database import SessionLocal
from datetime import datetime

db = SessionLocal()
ml_service = MLScheduleService(db)

# Generate ML-powered schedule
result = ml_service.generate_ml_schedule(
    user_id=1,
    start_date=datetime.now(),
    end_date=datetime.now() + timedelta(days=30)
)
```

## 🚀 API Endpoints

- `POST /schedules/generate-ml` - Generate ML-powered schedule
- `GET /schedules/insights/{course_code}` - Get course insights from scraping

## 📝 Notes

- Reddit scraper works in read-only mode without credentials but may have limited access
- RateMyProfessor parsing may need updates if their site structure changes
- All scraped data is validated before saving to database
- Scrapers include rate limiting to be respectful to source sites

