"""
Backend module for extracting user reviews from Reddit.

This module provides tools to search and extract reviews/posts from Reddit
subreddits using the PRAW (Python Reddit API Wrapper) library.
"""

from .reddit_review_extractor import RedditReviewExtractor

__all__ = ['RedditReviewExtractor']
__version__ = '1.0.0'
