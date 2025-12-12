# Backend - Reddit Review Extractor

This module provides functionality to extract reviews and posts from Reddit subreddits using PRAW (Python Reddit API Wrapper).

## Features

- Search for posts across all subreddits based on a search query
- Search for posts in specific subreddit(s)
- Extract post metadata (title, author, score, comments count, etc.)
- Retrieve comments from specific posts
- Filter results by time period

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Reddit API Credentials

1. Go to https://www.reddit.com/prefs/apps
2. Click "Create App" or "Create Another App"
3. Fill in the details:
   - **name**: Your app name (e.g., "Categorize User Reviews")
   - **App type**: Select "script"
   - **description**: Optional description
   - **about url**: Leave blank
   - **redirect uri**: http://localhost:8080 (required but not used)
4. Click "Create app"
5. Note down your:
   - **client_id**: The string under your app name (e.g., "abc123def456")
   - **client_secret**: The "secret" value shown

### 3. Create Configuration File

Copy the example configuration file and add your credentials:

```bash
cp config.example.py config.py
```

Edit `config.py` and replace the placeholder values with your actual Reddit API credentials.

⚠️ **Important**: Never commit `config.py` to version control. It contains sensitive credentials.

## Usage

### Basic Usage

```python
from reddit_review_extractor import RedditReviewExtractor

# Initialize the extractor
extractor = RedditReviewExtractor(
    client_id="your_client_id",
    client_secret="your_client_secret",
    user_agent="python:categorize-user-reviews:v1.0.0 (by /u/your_username)"
)

# Search across all subreddits
results = extractor.search_all_subreddits("product review", limit=50)

# Print results
for post in results:
    print(f"{post['title']} - r/{post['subreddit']}")
```

### Search Specific Subreddit

```python
# Search in a specific subreddit
results = extractor.search_specific_subreddit(
    subreddit_name="technology",
    search_query="smartphone review",
    limit=100
)
```

### Search Multiple Subreddits

```python
# Search across multiple subreddits
subreddits = ["technology", "gadgets", "reviews"]
results = extractor.search_multiple_subreddits(
    subreddit_names=subreddits,
    search_query="laptop review",
    limit=50
)

# Results are organized by subreddit
for subreddit, posts in results.items():
    print(f"\nSubreddit: r/{subreddit} - {len(posts)} posts found")
```

### Get Post Comments

```python
# Get comments from a specific post
comments = extractor.get_post_comments(submission_id="abc123")

for comment in comments:
    print(f"{comment['author']}: {comment['body'][:100]}...")
```

### Time Filters

You can filter results by time period:

```python
results = extractor.search_all_subreddits(
    search_query="review",
    limit=100,
    time_filter="week"  # Options: 'all', 'day', 'hour', 'month', 'week', 'year'
)
```

### Running the Example

You can run the example script directly:

```bash
python reddit_review_extractor.py
```

This will search for "product review" across all subreddits and display the first 10 results.

## Data Structure

### Post Data

Each post returned contains the following fields:

- `id`: Reddit submission ID
- `title`: Post title
- `author`: Username of the post author
- `subreddit`: Name of the subreddit
- `score`: Post score (upvotes - downvotes)
- `upvote_ratio`: Ratio of upvotes
- `num_comments`: Number of comments
- `created_utc`: Post creation timestamp (ISO format)
- `url`: URL linked in the post
- `selftext`: Text content of the post
- `link_flair_text`: Post flair (if any)
- `permalink`: Direct link to the Reddit post

### Comment Data

Each comment contains:

- `id`: Comment ID
- `author`: Username of the comment author
- `body`: Comment text
- `score`: Comment score
- `created_utc`: Comment creation timestamp (ISO format)
- `parent_id`: ID of parent comment/post
- `is_submitter`: Whether the commenter is the post author

## Rate Limits

PRAW respects Reddit's API rate limits automatically. If you make too many requests, PRAW will automatically sleep and retry. Be mindful of:

- Maximum of 60 requests per minute
- Avoid running large batch operations in tight loops
- Use appropriate `limit` parameters to avoid unnecessary API calls

## Troubleshooting

### Authentication Errors

If you get authentication errors:
1. Verify your credentials in `config.py`
2. Ensure your Reddit app is of type "script"
3. Check that you're using the correct client_id (not the app name)

### 403 Forbidden Errors

- Your user agent string must be unique and descriptive
- Format: `platform:app_name:version (by /u/your_username)`

### No Results Found

- Try different search queries
- Adjust the `time_filter` parameter
- Some subreddits may have limited or no matching content

## License

This project is licensed under the same license as the parent repository.
