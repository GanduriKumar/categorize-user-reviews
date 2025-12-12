"""
Reddit Review Extractor using PRAW (Python Reddit API Wrapper)

This module provides functionality to extract reviews/posts from Reddit subreddits
based on a given search string.
"""

import praw
from typing import List, Dict, Optional
from datetime import datetime


class RedditReviewExtractor:
    """
    A class to extract reviews/posts from Reddit subreddits using PRAW.
    """
    
    def __init__(self, client_id: str, client_secret: str, user_agent: str):
        """
        Initialize the Reddit API client.
        
        Args:
            client_id: Reddit API client ID
            client_secret: Reddit API client secret
            user_agent: User agent string for Reddit API
        """
        self.reddit = praw.Reddit(
            client_id=client_id,
            client_secret=client_secret,
            user_agent=user_agent
        )
    
    def search_all_subreddits(
        self, 
        search_query: str, 
        limit: int = 100,
        time_filter: str = "all"
    ) -> List[Dict]:
        """
        Search for posts across all subreddits based on a search query.
        
        Args:
            search_query: The search string to look for
            limit: Maximum number of results to return (default: 100)
            time_filter: Time filter for search - 'all', 'day', 'hour', 'month', 'week', 'year'
        
        Returns:
            List of dictionaries containing post information
        """
        results = []
        
        try:
            # Search across all subreddits
            for submission in self.reddit.subreddit('all').search(
                search_query, 
                limit=limit,
                time_filter=time_filter
            ):
                post_data = self._extract_post_data(submission)
                results.append(post_data)
        except Exception as e:
            print(f"Error searching subreddits: {str(e)}")
        
        return results
    
    def search_specific_subreddit(
        self,
        subreddit_name: str,
        search_query: str,
        limit: int = 100,
        time_filter: str = "all"
    ) -> List[Dict]:
        """
        Search for posts in a specific subreddit based on a search query.
        
        Args:
            subreddit_name: Name of the subreddit to search
            search_query: The search string to look for
            limit: Maximum number of results to return (default: 100)
            time_filter: Time filter for search - 'all', 'day', 'hour', 'month', 'week', 'year'
        
        Returns:
            List of dictionaries containing post information
        """
        results = []
        
        try:
            subreddit = self.reddit.subreddit(subreddit_name)
            for submission in subreddit.search(
                search_query,
                limit=limit,
                time_filter=time_filter
            ):
                post_data = self._extract_post_data(submission)
                results.append(post_data)
        except Exception as e:
            print(f"Error searching subreddit {subreddit_name}: {str(e)}")
        
        return results
    
    def search_multiple_subreddits(
        self,
        subreddit_names: List[str],
        search_query: str,
        limit: int = 100,
        time_filter: str = "all"
    ) -> Dict[str, List[Dict]]:
        """
        Search for posts across multiple specific subreddits.
        
        Args:
            subreddit_names: List of subreddit names to search
            search_query: The search string to look for
            limit: Maximum number of results per subreddit (default: 100)
            time_filter: Time filter for search - 'all', 'day', 'hour', 'month', 'week', 'year'
        
        Returns:
            Dictionary with subreddit names as keys and lists of post data as values
        """
        all_results = {}
        
        for subreddit_name in subreddit_names:
            results = self.search_specific_subreddit(
                subreddit_name,
                search_query,
                limit,
                time_filter
            )
            all_results[subreddit_name] = results
        
        return all_results
    
    def get_post_comments(self, submission_id: str, limit: Optional[int] = None) -> List[Dict]:
        """
        Get comments from a specific post.
        
        Args:
            submission_id: Reddit submission ID
            limit: Maximum number of comments to retrieve (None for all)
        
        Returns:
            List of dictionaries containing comment information
        """
        comments = []
        
        try:
            submission = self.reddit.submission(id=submission_id)
            submission.comments.replace_more(limit=limit)
            
            for comment in submission.comments.list():
                comment_data = {
                    'id': comment.id,
                    'author': str(comment.author) if comment.author else '[deleted]',
                    'body': comment.body,
                    'score': comment.score,
                    'created_utc': datetime.fromtimestamp(comment.created_utc).isoformat(),
                    'parent_id': comment.parent_id,
                    'is_submitter': comment.is_submitter
                }
                comments.append(comment_data)
        except Exception as e:
            print(f"Error fetching comments for submission {submission_id}: {str(e)}")
        
        return comments
    
    def _extract_post_data(self, submission) -> Dict:
        """
        Extract relevant data from a Reddit submission.
        
        Args:
            submission: PRAW submission object
        
        Returns:
            Dictionary containing post information
        """
        return {
            'id': submission.id,
            'title': submission.title,
            'author': str(submission.author) if submission.author else '[deleted]',
            'subreddit': str(submission.subreddit),
            'score': submission.score,
            'upvote_ratio': submission.upvote_ratio,
            'num_comments': submission.num_comments,
            'created_utc': datetime.fromtimestamp(submission.created_utc).isoformat(),
            'url': submission.url,
            'selftext': submission.selftext,
            'link_flair_text': submission.link_flair_text,
            'permalink': f"https://reddit.com{submission.permalink}"
        }


def main():
    """
    Example usage of the RedditReviewExtractor class.
    """
    # Load credentials from config
    try:
        from config import REDDIT_CLIENT_ID, REDDIT_CLIENT_SECRET, REDDIT_USER_AGENT
    except ImportError:
        print("Error: config.py not found. Please create one from config.example.py")
        return
    
    # Initialize extractor
    extractor = RedditReviewExtractor(
        client_id=REDDIT_CLIENT_ID,
        client_secret=REDDIT_CLIENT_SECRET,
        user_agent=REDDIT_USER_AGENT
    )
    
    # Example: Search for reviews across all subreddits
    search_query = "product review"
    print(f"Searching for: {search_query}")
    
    results = extractor.search_all_subreddits(search_query, limit=10)
    
    print(f"\nFound {len(results)} posts:")
    for idx, post in enumerate(results, 1):
        print(f"\n{idx}. {post['title']}")
        print(f"   Subreddit: r/{post['subreddit']}")
        print(f"   Score: {post['score']}")
        print(f"   Comments: {post['num_comments']}")
        print(f"   URL: {post['permalink']}")


if __name__ == "__main__":
    main()
