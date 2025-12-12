"""
Backend module for extracting user reviews from Reddit.

This module provides tools to search and extract reviews/posts from Reddit
subreddits using the PRAW (Python Reddit API Wrapper) library, and to
process and summarize those reviews.
"""

from .reddit_review_extractor import RedditReviewExtractor
from .review_processor import ReviewProcessor

__all__ = ['RedditReviewExtractor', 'ReviewProcessor']
__version__ = '1.0.0'
