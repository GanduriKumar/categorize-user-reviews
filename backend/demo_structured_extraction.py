"""
Demonstration script for structured information extraction from reviews.

This script shows how to:
1. Process reviews (concatenate, clean text)
2. Extract structured information (without needing Ollama for demo)
3. Save structured data to JSON file

Note: This demo works without Ollama. For actual LLM-based extraction,
ensure Ollama is running and use the extract_structured_info() method.
"""

import json
from review_processor import ReviewProcessor


def demo_without_ollama():
    """
    Demonstrate the structured information extraction workflow.
    Uses mock data instead of calling Ollama API.
    """
    print("=" * 80)
    print("Structured Information Extraction Demo")
    print("=" * 80)
    print()
    
    # Sample reviews
    sample_reviews = [
        {
            'id': 'review1',
            'title': 'Great Smartphone Camera! 📱',
            'selftext': 'I bought the Galaxy S23 last week. The camera is amazing, takes great photos in low light. Battery lasts all day. Running Android 13 on it. Highly recommend!',
            'subreddit': 'smartphones',
            'score': 250
        },
        {
            'id': 'review2',
            'title': 'Laptop Overheating Issue 💻',
            'selftext': 'My Dell XPS 15 keeps overheating when running Photoshop. Fans are loud. Using Windows 11 Pro. Steps to reproduce: 1. Open Photoshop 2. Load large image file 3. Apply multiple filters 4. Watch temperature rise to 95C',
            'subreddit': 'laptops',
            'score': 89
        },
        {
            'id': 'review3',
            'title': 'Coffee Maker Review',
            'selftext': 'Bought the Keurig K-Elite. Makes decent coffee, easy to use. Timer sometimes doesn\'t work properly but overall satisfied.',
            'subreddit': 'coffee',
            'score': 42
        }
    ]
    
    # Initialize processor
    processor = ReviewProcessor()
    
    print("Step 1: Processing reviews (concatenate and clean text)")
    print("-" * 80)
    
    processed_reviews = []
    for idx, review in enumerate(sample_reviews, 1):
        processed = processor.process_review(review, summarize=False)
        processed_reviews.append(processed)
        
        print(f"\nReview #{idx} (ID: {review['id']})")
        print(f"Original Title: {review['title']}")
        print(f"Cleaned Text: {processed['cleaned_text'][:100]}...")
    
    print()
    print("=" * 80)
    print("Step 2: Mock Structured Information Extraction")
    print("=" * 80)
    print()
    print("Note: In real usage, call processor.extract_structured_info(summary)")
    print("      which uses Ollama LLM to extract structured data.")
    print()
    
    # For demo, create mock structured information
    # In real usage, this would come from extract_structured_info()
    structured_reviews = [
        {
            **processed_reviews[0],
            'summary': 'User highly recommends the Galaxy S23 for its excellent camera and battery life.',
            'product_or_service_name': 'Samsung Galaxy S23',
            'key_point_description': 'Excellent camera quality especially in low light, and all-day battery life.',
            'key_pain_point': 'None mentioned - positive review highlighting main benefits.',
            'sentiment': 'Positive',
            'test_steps': [],
            'test_environment': {
                'os': 'Android 13',
                'software_version': 'Not specified',
                'product_model': 'Samsung Galaxy S23',
                'other': 'Not specified'
            }
        },
        {
            **processed_reviews[1],
            'summary': 'Dell XPS 15 experiences severe overheating issues when running Photoshop on Windows 11 Pro.',
            'product_or_service_name': 'Dell XPS 15',
            'key_point_description': 'Laptop overheats to 95C when running demanding applications like Photoshop.',
            'key_pain_point': 'Severe overheating issue with loud fan noise during graphics-intensive tasks.',
            'sentiment': 'Negative',
            'test_steps': [
                'Open Photoshop',
                'Load large image file',
                'Apply multiple filters',
                'Monitor temperature - rises to 95C'
            ],
            'test_environment': {
                'os': 'Windows 11 Pro',
                'software_version': 'Photoshop (version not specified)',
                'product_model': 'Dell XPS 15',
                'other': 'Graphics-intensive workload'
            }
        },
        {
            **processed_reviews[2],
            'summary': 'Keurig K-Elite makes decent coffee and is easy to use, with minor timer issues.',
            'product_or_service_name': 'Keurig K-Elite',
            'key_point_description': 'Easy to use coffee maker that produces decent coffee quality.',
            'key_pain_point': 'Timer function occasionally malfunctions.',
            'sentiment': 'Mixed',
            'test_steps': [
                'Set timer for morning coffee',
                'Observe if timer triggers at scheduled time',
                'Note: Timer sometimes fails to activate'
            ],
            'test_environment': {
                'os': 'Not applicable',
                'software_version': 'Not specified',
                'product_model': 'Keurig K-Elite',
                'other': 'Not specified'
            }
        }
    ]
    
    # Display structured information
    for idx, review in enumerate(structured_reviews, 1):
        print(f"Review #{idx}: {review['id']}")
        print("-" * 80)
        print(f"Product/Service: {review['product_or_service_name']}")
        print(f"Sentiment: {review['sentiment']}")
        print(f"Key Point: {review['key_point_description']}")
        print(f"Pain Point: {review['key_pain_point']}")
        
        if review['test_steps']:
            print(f"Test Steps ({len(review['test_steps'])} steps):")
            for i, step in enumerate(review['test_steps'], 1):
                print(f"  {i}. {step}")
        
        print("Test Environment:")
        for key, value in review['test_environment'].items():
            if value != 'Not specified':
                print(f"  - {key}: {value}")
        
        print()
    
    print("=" * 80)
    print("Step 3: Saving to JSON file")
    print("=" * 80)
    print()
    
    output_file = 'structured_reviews_demo.json'
    processor.save_structured_reviews_to_json(structured_reviews, output_file)
    
    print(f"✓ Saved {len(structured_reviews)} structured reviews to: {output_file}")
    print()
    
    # Show a sample of the JSON output
    with open(output_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print("Sample JSON output:")
    print("-" * 80)
    print(json.dumps(data['reviews'][0], indent=2))
    print()
    print("=" * 80)
    print("Demo Complete!")
    print("=" * 80)
    print()
    print("Next Steps:")
    print("1. Install and run Ollama: https://ollama.ai")
    print("2. Pull a model: ollama pull llama2")
    print("3. Use processor.extract_structured_info(summary) for real LLM extraction")
    print("4. Run example_usage.py for full workflow with Reddit + Ollama")
    print()


if __name__ == "__main__":
    demo_without_ollama()
