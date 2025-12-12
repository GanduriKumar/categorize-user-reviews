# Backend - Reddit Review Extractor & Processor

This module provides functionality to extract reviews and posts from Reddit subreddits using PRAW (Python Reddit API Wrapper), and to process and summarize them using Ollama LLM.

## Features

### Review Extraction
- Search for posts across all subreddits based on a search query
- Search for posts in specific subreddit(s)
- Extract post metadata (title, author, score, comments count, etc.)
- Retrieve comments from specific posts
- Filter results by time period

### Review Processing & Summarization
- Concatenate review title and body
- Clean text from excessive whitespaces, emojis, and special characters
- Summarize reviews into concise 2-line summaries using Ollama LLM
- Batch process multiple reviews efficiently

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Install Ollama (for Review Summarization)

To use the review summarization feature, you need to install and run Ollama:

1. **Install Ollama**: Visit https://ollama.ai and follow installation instructions for your OS
2. **Pull a model**: Run `ollama pull llama2` (or another model of your choice)
3. **Verify it's running**: The Ollama API should be available at `http://localhost:11434`

Note: The review extraction works independently of Ollama. Summarization is optional.

### 3. Configure Reddit API Credentials

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

### 4. Create Configuration File

Copy the example configuration file and add your credentials:

```bash
cp config.example.py config.py
```

Edit `config.py` and replace the placeholder values with your actual Reddit API credentials.

⚠️ **Important**: Never commit `config.py` to version control. It contains sensitive credentials.

## Usage

### Review Extraction - Basic Usage

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

## Review Processing & Summarization

### Basic Usage

```python
from review_processor import ReviewProcessor

# Initialize the processor
processor = ReviewProcessor(
    ollama_base_url="http://localhost:11434",  # Default Ollama URL
    model="llama2"  # Or any other model you have installed
)

# Example review data (from Reddit extraction)
review_data = {
    'id': 'abc123',
    'title': 'Amazing Product! 😊',
    'selftext': 'I   loved this product!!!  \n\n  Works great... #awesome',
    'score': 150
}

# Process the review (concatenate, clean, and summarize)
processed = processor.process_review(review_data, summarize=True)

# Access the results
print(f"Original: {review_data['title']} {review_data['selftext']}")
print(f"Cleaned: {processed['cleaned_text']}")
print(f"Summary: {processed['summary']}")
```

### Text Concatenation

Combine title and body:

```python
concatenated = processor.concatenate_review_text(
    title="Great Product",
    body="Works perfectly and exceeded expectations"
)
# Result: "Great Product Works perfectly and exceeded expectations"
```

### Text Cleaning

Clean text from whitespaces, emojis, and special characters:

```python
cleaned = processor.clean_text("I   loved this!!! 😊 #awesome @company")
# Result: "I loved this! awesome company"
```

### Summarization

Summarize cleaned text into 2 lines:

```python
summary = processor.summarize_with_ollama(
    text="Long review text here...",
    max_lines=2
)
```

### Batch Processing

Process multiple reviews at once:

```python
from reddit_review_extractor import RedditReviewExtractor
from review_processor import ReviewProcessor

# Extract reviews
extractor = RedditReviewExtractor(client_id, client_secret, user_agent)
reviews = extractor.search_all_subreddits("product review", limit=10)

# Process all reviews
processor = ReviewProcessor()
processed_reviews = processor.process_multiple_reviews(reviews, summarize=True)

# Each processed review now includes:
# - concatenated_text: Title + body combined
# - cleaned_text: Cleaned version without emojis/special chars
# - summary: 2-line summary (if Ollama is available)
```

### Complete Example

Run the complete example script:

```bash
python example_usage.py
```

This demonstrates the full workflow:
1. Extract reviews from Reddit
2. Concatenate title and body
3. Clean the text
4. Generate 2-line summaries using Ollama

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

### Processed Review Data

After processing with `ReviewProcessor`, each review additionally contains:

- `concatenated_text`: Combined title and body text
- `cleaned_text`: Text cleaned of emojis, special characters, and excessive whitespace
- `summary`: 2-line summary generated by Ollama (if summarization is enabled)
- `summary_error`: Error message if summarization failed
- `processing_error`: Error message if processing failed

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
