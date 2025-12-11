"""
RateMyProfessor scraper for professor ratings
"""
from bs4 import BeautifulSoup
import json
import logging
import re
from typing import Dict, List, Optional
from .base_scraper import BaseScraper

logger = logging.getLogger(__name__)


class RateMyProfessorScraper(BaseScraper):
    """
    Scrapes RateMyProfessors.com for professor ratings
    """

    def __init__(self):
        super().__init__(rate_limit_requests=20, rate_limit_seconds=60)  # Be respectful
        self.base_url = "https://www.ratemyprofessors.com"
        self.search_url = f"{self.base_url}/search/professors"
        self.school_id = "1137"  # University of Illinois at Urbana-Champaign

    def scrape(self, target: str, **kwargs) -> Dict:
        """
        Scrape RateMyProfessor for a professor

        Args:
            target: Professor name (e.g., "Geoffrey Challen")
            **kwargs: Additional parameters
                - course_code: Course code to filter by (optional)

        Returns:
            Dictionary containing professor rating data
        """
        professor_name = target
        course_code = kwargs.get('course_code', None)

        # Search for professor
        search_results = self._search_professor(professor_name)

        if not search_results:
            logger.warning(f"No results found for professor: {professor_name}")
            return {}

        # Get the first matching result
        professor_data = search_results[0] if search_results else None

        if not professor_data:
            return {}

        # Enrich with course code if provided
        if course_code:
            professor_data['course_code'] = course_code

        return professor_data

    def _search_professor(self, name: str) -> List[Dict]:
        """
        Search for a professor by name using RateMyProfessors API

        Args:
            name: Professor name to search

        Returns:
            List of professor data dictionaries
        """
        # RateMyProfessors uses a GraphQL-like API
        # Try the search endpoint first
        search_url = f"{self.base_url}/search.jsp?queryoption=HEADER&queryBy=teacherName&schoolName=University+of+Illinois+at+Urbana-Champaign&query={name.replace(' ', '+')}"
        
        response = self._make_request(search_url)
        if not response:
            return []

        try:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Try to find professor links in the search results
            results = self._parse_search_results(soup, name)
            
            # If no results from HTML parsing, try to extract from embedded data
            if not results:
                results = self._extract_from_embedded_data(soup, name)
            
            return results

        except Exception as e:
            logger.error(f"Failed to parse search results: {e}")
            return []

    def _parse_search_results(self, soup: BeautifulSoup, search_name: str) -> List[Dict]:
        """
        Parse search results from HTML

        Args:
            soup: BeautifulSoup parsed HTML
            search_name: Original search name for matching

        Returns:
            List of professor dictionaries
        """
        results = []
        
        try:
            # Look for professor result cards/links
            # RateMyProfessors typically has links like /ShowRatings.jsp?tid=...
            professor_links = soup.find_all('a', href=lambda x: x and '/ShowRatings.jsp' in x)
            
            for link in professor_links[:5]:  # Limit to top 5 results
                try:
                    # Extract professor ID from URL
                    href = link.get('href', '')
                    if 'tid=' in href:
                        # Get professor name from link text or nearby elements
                        professor_name_elem = link.find(text=True, recursive=True)
                        if not professor_name_elem:
                            # Try finding name in parent elements
                            parent = link.find_parent(['div', 'li', 'span'])
                            if parent:
                                professor_name_elem = parent.get_text(strip=True)
                        
                        professor_name = professor_name_elem.strip() if professor_name_elem else search_name
                        
                        # Extract tid (teacher ID)
                        tid_match = re.search(r'tid=(\d+)', href)
                        if tid_match:
                            professor_id = tid_match.group(1)
                            
                            # Scrape the professor's page
                            professor_data = self.scrape_by_id(professor_id)
                            if professor_data:
                                professor_data['professor_name'] = professor_name
                                results.append(professor_data)
                
                except Exception as e:
                    logger.warning(f"Failed to parse professor link: {e}")
                    continue
        
        except Exception as e:
            logger.error(f"Error parsing search results: {e}")
        
        return results
    
    def _extract_from_embedded_data(self, soup: BeautifulSoup, search_name: str) -> List[Dict]:
        """
        Try to extract professor data from embedded JSON/script tags
        
        Args:
            soup: BeautifulSoup parsed HTML
            search_name: Original search name
            
        Returns:
            List of professor dictionaries
        """
        results = []
        
        try:
            # Look for embedded JSON data in script tags
            script_tags = soup.find_all('script', type='application/json')
            
            for script in script_tags:
                try:
                    data = json.loads(script.string)
                    # Navigate through the JSON structure to find professor data
                    # This is a generic approach - structure may vary
                    if isinstance(data, dict):
                        professors = self._extract_professors_from_json(data, search_name)
                        results.extend(professors)
                except (json.JSONDecodeError, AttributeError):
                    continue
            
            # Also check for window.__RELAY_STORE__ or similar
            all_scripts = soup.find_all('script')
            for script in all_scripts:
                if script.string and ('__RELAY_STORE__' in script.string or 'legacyId' in script.string):
                    try:
                        # Try to extract JSON from the script
                        json_match = re.search(r'\{.*"legacyId".*\}', script.string, re.DOTALL)
                        if json_match:
                            data = json.loads(json_match.group(0))
                            professors = self._extract_professors_from_json(data, search_name)
                            results.extend(professors)
                    except:
                        pass
        
        except Exception as e:
            logger.warning(f"Failed to extract from embedded data: {e}")
        
        return results
    
    def _extract_professors_from_json(self, data: dict, search_name: str) -> List[Dict]:
        """Recursively extract professor data from JSON structure"""
        results = []
        
        def search_dict(obj, path=""):
            if isinstance(obj, dict):
                # Check if this looks like professor data
                if 'legacyId' in obj or 'overallRating' in obj or 'avgRating' in obj:
                    try:
                        professor_data = {
                            'professor_name': obj.get('firstName', '') + ' ' + obj.get('lastName', ''),
                            'overall_rating': float(obj.get('overallRating', obj.get('avgRating', 0))),
                            'difficulty_rating': float(obj.get('avgDifficulty', 0)),
                            'would_take_again_percent': float(obj.get('wouldTakeAgainPercent', 0)),
                            'rating_count': int(obj.get('numRatings', 0)),
                            'source': 'ratemyprofessor',
                            'source_url': f"{self.base_url}/ShowRatings.jsp?tid={obj.get('legacyId', '')}"
                        }
                        if professor_data['professor_name'].strip():
                            results.append(professor_data)
                    except (ValueError, TypeError) as e:
                        logger.warning(f"Failed to parse professor JSON: {e}")
                
                # Recursively search nested dicts
                for key, value in obj.items():
                    search_dict(value, f"{path}.{key}")
            
            elif isinstance(obj, list):
                for item in obj:
                    search_dict(item, path)
        
        search_dict(data)
        return results

    def scrape_by_id(self, professor_id: str) -> Optional[Dict]:
        """
        Scrape professor data by their RateMyProfessors ID

        Args:
            professor_id: RMP professor ID

        Returns:
            Professor data dictionary
        """
        url = f"{self.base_url}/professor/{professor_id}"

        response = self._make_request(url)
        if not response:
            return None

        try:
            soup = BeautifulSoup(response.text, 'html.parser')
            return self._parse_professor_page(soup)
        except Exception as e:
            logger.error(f"Failed to parse professor page: {e}")
            return None

    def _parse_professor_page(self, soup: BeautifulSoup) -> Dict:
        """
        Parse professor profile page

        Args:
            soup: BeautifulSoup parsed HTML

        Returns:
            Professor data dictionary
        """
        data = {
            'professor_name': '',
            'overall_rating': None,
            'difficulty_rating': None,
            'would_take_again_percent': None,
            'rating_count': 0,
            'source': 'ratemyprofessor',
            'source_url': ''
        }
        
        try:
            # Try to extract from embedded JSON first (most reliable)
            script_tags = soup.find_all('script', type='application/json')
            for script in script_tags:
                try:
                    json_data = json.loads(script.string)
                    if isinstance(json_data, dict):
                        # Look for professor data in the JSON
                        prof_data = self._extract_professor_from_json(json_data)
                        if prof_data:
                            data.update(prof_data)
                            break
                except (json.JSONDecodeError, AttributeError):
                    continue
            
            # Fallback to HTML parsing if JSON extraction failed
            if not data.get('overall_rating'):
                # Look for rating elements in HTML
                # RateMyProfessors uses various class names
                rating_selectors = [
                    '.RatingValue__Numerator-tv1',
                    '.RatingValue',
                    '[data-testid="rating"]',
                    '.rating'
                ]
                
                for selector in rating_selectors:
                    rating_elem = soup.select_one(selector)
                    if rating_elem:
                        try:
                            rating_text = rating_elem.get_text(strip=True)
                            # Extract number from text like "4.2" or "4.2/5"
                            import re
                            rating_match = re.search(r'(\d+\.?\d*)', rating_text)
                            if rating_match:
                                data['overall_rating'] = float(rating_match.group(1))
                                break
                        except (ValueError, AttributeError):
                            continue
                
                # Look for difficulty rating
                difficulty_selectors = [
                    '.FeedbackItem__FeedbackNumber',
                    '[data-testid="difficulty"]',
                    '.difficulty'
                ]
                
                for selector in difficulty_selectors:
                    diff_elem = soup.select_one(selector)
                    if diff_elem:
                        try:
                            diff_text = diff_elem.get_text(strip=True)
                            diff_match = re.search(r'(\d+\.?\d*)', diff_text)
                            if diff_match:
                                data['difficulty_rating'] = float(diff_match.group(1))
                                break
                        except (ValueError, AttributeError):
                            continue
                
                # Look for "Would Take Again" percentage
                take_again_elem = soup.find(string=re.compile(r'would.*take.*again', re.I))
                if take_again_elem:
                    parent = take_again_elem.find_parent()
                    if parent:
                        percent_text = parent.get_text()
                        percent_match = re.search(r'(\d+)%', percent_text)
                        if percent_match:
                            data['would_take_again_percent'] = float(percent_match.group(1))
                
                # Look for rating count
                count_elem = soup.find(string=re.compile(r'\d+.*rating', re.I))
                if count_elem:
                    count_match = re.search(r'(\d+)', count_elem)
                    if count_match:
                        data['rating_count'] = int(count_match.group(1))
            
            # Extract professor name
            name_elem = soup.find('h1') or soup.find('h2') or soup.select_one('.NameTitle__Name')
            if name_elem:
                data['professor_name'] = name_elem.get_text(strip=True)
        
        except Exception as e:
            logger.error(f"Error parsing professor page: {e}")
        
        return data
    
    def _extract_professor_from_json(self, data: dict) -> Optional[Dict]:
        """Extract professor data from JSON structure"""
        result = {}
        
        def search_dict(obj):
            if isinstance(obj, dict):
                # Check for professor data fields
                if 'overallRating' in obj or 'avgRating' in obj:
                    try:
                        result['overall_rating'] = float(obj.get('overallRating', obj.get('avgRating', 0)))
                        result['difficulty_rating'] = float(obj.get('avgDifficulty', 0))
                        result['would_take_again_percent'] = float(obj.get('wouldTakeAgainPercent', 0))
                        result['rating_count'] = int(obj.get('numRatings', 0))
                        if 'firstName' in obj and 'lastName' in obj:
                            result['professor_name'] = f"{obj['firstName']} {obj['lastName']}"
                        return result
                    except (ValueError, TypeError):
                        pass
                
                # Recursively search
                for value in obj.values():
                    if search_dict(value):
                        return result
            
            elif isinstance(obj, list):
                for item in obj:
                    if search_dict(item):
                        return result
        
        search_dict(data)
        return result if result else None
