"""
Reddit scraper for course reviews and insights using PRAW
"""
import praw
import re
import logging
from typing import Dict, List, Optional
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from .base_scraper import BaseScraper

logger = logging.getLogger(__name__)


class RedditScraper(BaseScraper):
    """
    Scrapes Reddit for course reviews, difficulty insights, and workload estimates
    """

    def __init__(self, client_id: str = None, client_secret: str = None, user_agent: str = None):
        super().__init__(rate_limit_requests=60, rate_limit_seconds=60)  # Reddit allows 60/min

        # Initialize PRAW (Python Reddit API Wrapper)
        # For now, use read-only mode if credentials not provided
        try:
            if client_id and client_secret:
                self.reddit = praw.Reddit(
                    client_id=client_id,
                    client_secret=client_secret,
                    user_agent=user_agent or 'Aptora Study Scheduler (Educational)'
                )
            else:
                # Read-only mode (no authentication)
                self.reddit = praw.Reddit(
                    client_id='dummy',
                    client_secret='dummy',
                    user_agent='Aptora Study Scheduler (Educational)',
                    check_for_async=False
                )
                logger.warning("Reddit scraper running in read-only mode without auth")
        except Exception as e:
            logger.error(f"Failed to initialize Reddit scraper: {e}")
            self.reddit = None

        # Initialize sentiment analyzer
        self.sentiment_analyzer = SentimentIntensityAnalyzer()

    def scrape(self, target: str, **kwargs) -> Dict:
        """
        Scrape Reddit for course insights

        Args:
            target: Course code (e.g., "CS 225")
            **kwargs: Additional parameters
                - subreddits: List of subreddits to search (default: ['UIUC'])
                - limit: Max posts to analyze (default: 50)

        Returns:
            Dictionary containing course insights from Reddit
        """
        if not self.reddit:
            return {}

        subreddits = kwargs.get('subreddits', ['UIUC', 'UIUCadmissions'])
        limit = kwargs.get('limit', 50)

        all_posts = []
        all_comments = []

        # Search each subreddit
        for subreddit_name in subreddits:
            try:
                subreddit = self.reddit.subreddit(subreddit_name)

                # Search for posts about this course
                search_queries = [
                    f"{target} difficulty",
                    f"{target} workload",
                    f"{target} hours",
                    f"{target} review"
                ]

                for query in search_queries:
                    for post in subreddit.search(query, limit=limit // len(search_queries)):
                        all_posts.append({
                            'title': post.title,
                            'text': post.selftext,
                            'score': post.score,
                            'created': post.created_utc
                        })

                        # Get top comments
                        post.comments.replace_more(limit=0)  # Remove "load more" placeholders
                        for comment in post.comments.list()[:10]:  # Top 10 comments
                            all_comments.append({
                                'text': comment.body,
                                'score': comment.score
                            })

            except Exception as e:
                logger.warning(f"Failed to scrape r/{subreddit_name}: {e}")
                continue

        # Analyze collected data
        insights = self._analyze_posts_and_comments(target, all_posts, all_comments)

        return insights

    def _analyze_posts_and_comments(self, course_code: str, posts: List[Dict], comments: List[Dict]) -> Dict:
        """
        Analyze Reddit posts and comments to extract course insights

        Args:
            course_code: Course identifier
            posts: List of post dictionaries
            comments: List of comment dictionaries

        Returns:
            Dictionary with analyzed insights
        """
        if not posts and not comments:
            return {}

        # Combine all text
        all_text = []
        all_text.extend([p['title'] + ' ' + p['text'] for p in posts])
        all_text.extend([c['text'] for c in comments])

        # Extract hours per week
        hours_per_week = self._extract_hours_per_week(all_text)

        # Analyze sentiment (proxy for difficulty)
        avg_sentiment = self._analyze_sentiment(all_text)

        # Convert sentiment to difficulty score (0-10 scale)
        # Negative sentiment = harder course
        difficulty_score = self._sentiment_to_difficulty(avg_sentiment)

        # Extract workload mentions
        workload_keywords = ['easy', 'hard', 'difficult', 'challenging', 'manageable', 'intense']
        workload_mentions = sum(1 for text in all_text
                               for keyword in workload_keywords
                               if keyword.lower() in text.lower())

        return {
            'course_code': course_code,
            'avg_hours_per_week': hours_per_week,
            'difficulty_score': difficulty_score,
            'sentiment_score': avg_sentiment,
            'posts_analyzed': len(posts),
            'comments_analyzed': len(comments),
            'workload_mentions': workload_mentions,
            'source': 'reddit'
        }

    def _extract_hours_per_week(self, texts: List[str]) -> Optional[float]:
        """
        Extract average hours per week from text mentions

        Args:
            texts: List of text strings to analyze

        Returns:
            Estimated hours per week or None
        """
        hours_pattern = re.compile(r'(\d+)[\s-]*(hours?|hrs?)[\s/]*(per\s)?week', re.IGNORECASE)
        hours_found = []

        for text in texts:
            matches = hours_pattern.findall(text)
            for match in matches:
                try:
                    hours = float(match[0])
                    if 1 <= hours <= 40:  # Sanity check
                        hours_found.append(hours)
                except ValueError:
                    continue

        if hours_found:
            return sum(hours_found) / len(hours_found)
        return None

    def _analyze_sentiment(self, texts: List[str]) -> float:
        """
        Analyze sentiment of texts using VADER

        Args:
            texts: List of text strings

        Returns:
            Average compound sentiment score (-1 to 1)
        """
        if not texts:
            return 0.0

        sentiments = []
        for text in texts:
            if text.strip():
                score = self.sentiment_analyzer.polarity_scores(text)
                sentiments.append(score['compound'])

        return sum(sentiments) / len(sentiments) if sentiments else 0.0

    def _sentiment_to_difficulty(self, sentiment: float) -> float:
        """
        Convert sentiment score to difficulty rating

        Args:
            sentiment: Sentiment score (-1 to 1, where -1 is very negative)

        Returns:
            Difficulty score (0-10, where 10 is most difficult)
        """
        # Negative sentiment (complaints) -> higher difficulty
        # Positive sentiment (praise) -> lower difficulty
        # Map [-1, 1] to [10, 2] (leaving some room, assuming no course is truly 0 or 1 difficulty)
        difficulty = 6 - (sentiment * 4)  # Centered at 6, ±4 based on sentiment
        return max(2.0, min(10.0, difficulty))  # Clamp to [2, 10]
