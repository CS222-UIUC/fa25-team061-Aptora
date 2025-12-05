"""
Base scraper framework with rate limiting, caching, and error handling
"""
from abc import ABC, abstractmethod
from typing import Optional, Dict, List
import time
import requests
from datetime import datetime, timedelta
import logging
from functools import wraps

logger = logging.getLogger(__name__)


class RateLimiter:
    """Simple rate limiter to prevent overwhelming source servers"""

    def __init__(self, max_requests: int = 30, per_seconds: int = 60):
        self.max_requests = max_requests
        self.per_seconds = per_seconds
        self.requests = []

    def wait_if_needed(self):
        """Wait if we've hit the rate limit"""
        now = time.time()
        # Remove requests older than the time window
        self.requests = [req_time for req_time in self.requests
                        if now - req_time < self.per_seconds]

        if len(self.requests) >= self.max_requests:
            # Calculate how long to wait
            oldest_request = min(self.requests)
            wait_time = self.per_seconds - (now - oldest_request)
            if wait_time > 0:
                logger.info(f"Rate limit reached. Waiting {wait_time:.2f} seconds...")
                time.sleep(wait_time)

        self.requests.append(time.time())


class BaseScraper(ABC):
    """
    Abstract base class for all scrapers
    Provides rate limiting, user-agent rotation, retry logic, and error handling
    """

    def __init__(self, rate_limit_requests: int = 30, rate_limit_seconds: int = 60):
        self.rate_limiter = RateLimiter(rate_limit_requests, rate_limit_seconds)
        self.user_agents = [
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36',
        ]
        self.current_agent_idx = 0
        self.session = requests.Session()

    def _get_user_agent(self) -> str:
        """Rotate through user agents"""
        agent = self.user_agents[self.current_agent_idx]
        self.current_agent_idx = (self.current_agent_idx + 1) % len(self.user_agents)
        return agent

    def _make_request(self, url: str, method: str = 'GET', **kwargs) -> Optional[requests.Response]:
        """
        Make HTTP request with rate limiting, retry logic, and error handling

        Args:
            url: URL to request
            method: HTTP method (GET, POST, etc.)
            **kwargs: Additional arguments to pass to requests

        Returns:
            Response object or None if all retries failed
        """
        max_retries = 3
        retry_delay = 2  # seconds

        for attempt in range(max_retries):
            try:
                # Wait if rate limited
                self.rate_limiter.wait_if_needed()

                # Set headers
                headers = kwargs.get('headers', {})
                headers['User-Agent'] = self._get_user_agent()
                kwargs['headers'] = headers

                # Make request
                if method.upper() == 'GET':
                    response = self.session.get(url, timeout=10, **kwargs)
                elif method.upper() == 'POST':
                    response = self.session.post(url, timeout=10, **kwargs)
                else:
                    raise ValueError(f"Unsupported HTTP method: {method}")

                # Check response status
                response.raise_for_status()
                return response

            except requests.exceptions.RequestException as e:
                logger.warning(f"Request failed (attempt {attempt + 1}/{max_retries}): {e}")

                if attempt < max_retries - 1:
                    # Exponential backoff
                    wait_time = retry_delay * (2 ** attempt)
                    logger.info(f"Retrying in {wait_time} seconds...")
                    time.sleep(wait_time)
                else:
                    logger.error(f"All {max_retries} attempts failed for URL: {url}")
                    return None

        return None

    @abstractmethod
    def scrape(self, target: str, **kwargs) -> Dict:
        """
        Scrape data from the target source

        Args:
            target: Target identifier (course code, professor name, etc.)
            **kwargs: Additional scraper-specific parameters

        Returns:
            Dictionary containing scraped data
        """
        pass

    def scrape_with_error_handling(self, target: str, **kwargs) -> Optional[Dict]:
        """
        Wrapper around scrape() with comprehensive error handling

        Args:
            target: Target identifier
            **kwargs: Additional parameters

        Returns:
            Scraped data dictionary or None if scraping failed
        """
        try:
            logger.info(f"Starting scrape for: {target}")
            data = self.scrape(target, **kwargs)
            logger.info(f"Successfully scraped data for: {target}")
            return data
        except Exception as e:
            logger.error(f"Scraping failed for {target}: {e}", exc_info=True)
            return None

    def validate_data(self, data: Dict, required_fields: List[str]) -> bool:
        """
        Validate that scraped data contains required fields

        Args:
            data: Scraped data dictionary
            required_fields: List of required field names

        Returns:
            True if valid, False otherwise
        """
        for field in required_fields:
            if field not in data or data[field] is None:
                logger.warning(f"Missing required field: {field}")
                return False
        return True
