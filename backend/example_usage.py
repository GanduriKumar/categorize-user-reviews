"""
Example script demonstrating the complete workflow:
1. Extract reviews from Reddit using RedditReviewExtractor
2. Process and summarize reviews using ReviewProcessor
"""

import logging
from reddit_review_extractor import RedditReviewExtractor
from review_processor import ReviewProcessor

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def main():
    """
    Complete workflow example for extracting and processing Reddit reviews.
    """
    print("=" * 80)
    print("Reddit Review Extraction and Summarization Example")
    print("=" * 80)
    print()
    
    # Step 1: Initialize Reddit Extractor
    print("Step 1: Initializing Reddit Review Extractor...")
    try:
        from config import REDDIT_CLIENT_ID, REDDIT_CLIENT_SECRET, REDDIT_USER_AGENT
    except ImportError:
        logger.error("Error: config.py not found. Please create one from config.example.py")
        print("\nNote: For testing without Reddit API, use the demo mode below.")
        demo_mode()
        return
    
    extractor = RedditReviewExtractor(
        client_id=REDDIT_CLIENT_ID,
        client_secret=REDDIT_CLIENT_SECRET,
        user_agent=REDDIT_USER_AGENT
    )
    print("✓ Reddit extractor initialized")
    print()
    
    # Step 2: Initialize Review Processor
    print("Step 2: Initializing Review Processor...")
    # You can customize these parameters based on your Ollama setup
    processor = ReviewProcessor(
        ollama_base_url="http://localhost:11434",
        model="llama2"  # or another model you have installed
    )
    print("✓ Review processor initialized")
    print()
    
    # Step 3: Extract reviews from Reddit
    print("Step 3: Extracting reviews from Reddit...")
    search_query = "product review"
    print(f"Search query: '{search_query}'")
    print(f"Limit: 5 posts")
    
    reviews = extractor.search_all_subreddits(search_query, limit=5)
    print(f"✓ Extracted {len(reviews)} reviews")
    print()
    
    # Step 4: Process and summarize reviews
    print("Step 4: Processing and summarizing reviews...")
    print("Note: This step requires Ollama to be running locally.")
    print("If Ollama is not available, processing will skip summarization.")
    print()
    
    processed_reviews = processor.process_multiple_reviews(reviews, summarize=True)
    
    # Step 5: Display results
    print("=" * 80)
    print("RESULTS")
    print("=" * 80)
    print()
    
    for idx, review in enumerate(processed_reviews, 1):
        print(f"Review #{idx}")
        print("-" * 80)
        print(f"ID: {review.get('id', 'N/A')}")
        print(f"Subreddit: r/{review.get('subreddit', 'N/A')}")
        print(f"Score: {review.get('score', 'N/A')}")
        print()
        
        print("Original:")
        print(f"  Title: {review.get('title', 'N/A')[:100]}...")
        body = review.get('selftext', 'N/A')
        print(f"  Body: {body[:100] if body else 'N/A'}...")
        print()
        
        print("Processed:")
        print(f"  Cleaned Text: {review.get('cleaned_text', 'N/A')[:150]}...")
        print()
        
        if 'summary' in review and review['summary']:
            print("Summary:")
            print(f"  {review['summary']}")
        elif 'summary_error' in review:
            print(f"Summary: [Error - {review['summary_error']}]")
        else:
            print("Summary: [Not generated]")
        
        print()
        print()


def demo_mode():
    """
    Demonstration mode with sample data (no Reddit API required).
    """
    print("\n" + "=" * 80)
    print("DEMO MODE - Using Sample Data")
    print("=" * 80)
    print()
    
    # Sample reviews for demonstration
    sample_reviews = [
        {
            'id': 'demo1',
            'title': 'Amazing Smartphone! 📱',
            'selftext': 'I recently bought this phone and I am   extremely satisfied!!!  The camera quality is outstanding... Battery life is incredible. Highly recommend! 😊 #tech @smartphone',
            'subreddit': 'gadgets',
            'score': 250,
            'num_comments': 45
        },
        {
            'id': 'demo2',
            'title': 'Disappointed with Laptop Purchase 😞',
            'selftext': 'Expected much better performance for the price.   \n\n  The build quality feels cheap and it overheats constantly!!! Not worth the money. @laptop #review',
            'subreddit': 'technology',
            'score': 120,
            'num_comments': 78
        },
        {
            'id': 'demo3',
            'title': 'Coffee Maker Review ☕',
            'selftext': 'This coffee maker is decent for the price. Makes good coffee, easy to clean. Minor issue with the timer but overall satisfied. Would buy again.',
            'subreddit': 'BuyItForLife',
            'score': 89,
            'num_comments': 23
        }
    ]
    
    # Initialize processor
    processor = ReviewProcessor()
    
    print("Processing sample reviews...")
    print("(Note: Summarization requires Ollama to be running)")
    print()
    
    # Process without summarization first to show text cleaning
    for idx, review in enumerate(sample_reviews, 1):
        print(f"Review #{idx}")
        print("-" * 80)
        print(f"Subreddit: r/{review['subreddit']}")
        print(f"Score: {review['score']}")
        print()
        
        print("Original:")
        print(f"  Title: {review['title']}")
        print(f"  Body: {review['selftext']}")
        print()
        
        # Process the review
        processed = processor.process_review(review, summarize=False)
        
        print("After Processing:")
        print(f"  Concatenated: {processed['concatenated_text']}")
        print()
        print(f"  Cleaned: {processed['cleaned_text']}")
        print()
        
        # Try to summarize if Ollama is available
        try:
            summary = processor.summarize_with_ollama(processed['cleaned_text'], max_lines=2)
            print("Summary (2 lines):")
            print(f"  {summary}")
        except Exception as e:
            print(f"Summary: [Ollama not available - {str(e)[:50]}]")
        
        print()
        print()


if __name__ == "__main__":
    # Uncomment one of these:
    main()        # Use this if you have Reddit API credentials
    # demo_mode() # Use this for testing without Reddit API
