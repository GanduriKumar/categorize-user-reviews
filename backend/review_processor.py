"""
Review Processor Module

This module provides functionality to process and summarize Reddit reviews using:
- Text concatenation (title + body)
- Text cleaning (whitespaces, emojis, special characters)
- Ollama LLM-based summarization
"""

import re
import logging
from typing import Dict, Optional
import requests
import json

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ReviewProcessor:
    """
    A class to process and summarize Reddit reviews using text cleaning
    and Ollama LLM-based summarization.
    """
    
    def __init__(self, ollama_base_url: str = "http://localhost:11434", model: str = "llama2"):
        """
        Initialize the ReviewProcessor.
        
        Args:
            ollama_base_url: Base URL for Ollama API (default: http://localhost:11434)
            model: Ollama model to use for summarization (default: llama2)
        """
        self.ollama_base_url = ollama_base_url.rstrip('/')
        self.model = model
        
    def concatenate_review_text(self, title: str, body: str) -> str:
        """
        Concatenate the title and body of a review.
        
        Args:
            title: Review title
            body: Review body/selftext
            
        Returns:
            Concatenated text
        """
        # Handle None values
        title = title or ""
        body = body or ""
        
        # Concatenate with a space separator
        return f"{title} {body}".strip()
    
    def clean_text(self, text: str) -> str:
        """
        Clean text by removing excessive whitespaces, emojis, and special characters.
        
        Args:
            text: Input text to clean
            
        Returns:
            Cleaned text
        """
        if not text:
            return ""
        
        # Remove emojis (Unicode emoji ranges)
        emoji_pattern = re.compile(
            "["
            "\U0001F600-\U0001F64F"  # emoticons
            "\U0001F300-\U0001F5FF"  # symbols & pictographs
            "\U0001F680-\U0001F6FF"  # transport & map symbols
            "\U0001F1E0-\U0001F1FF"  # flags (iOS)
            "\U00002702-\U000027B0"
            "\U000024C2-\U0001F251"
            "\U0001F900-\U0001F9FF"  # Supplemental Symbols and Pictographs
            "\U0001FA00-\U0001FA6F"  # Chess Symbols
            "\U0001FA70-\U0001FAFF"  # Symbols and Pictographs Extended-A
            "\U00002600-\U000026FF"  # Miscellaneous Symbols
            "\U00002700-\U000027BF"  # Dingbats
            "]+", 
            flags=re.UNICODE
        )
        text = emoji_pattern.sub(r'', text)
        
        # Remove special characters but keep basic punctuation (.,!?;:'"-)
        text = re.sub(r'[^\w\s.,!?;:\'\"-]', '', text)
        
        # Replace multiple whitespaces (including newlines, tabs) with single space
        text = re.sub(r'\s+', ' ', text)
        
        # Remove leading/trailing whitespace
        text = text.strip()
        
        return text
    
    def summarize_with_ollama(self, text: str, max_lines: int = 2) -> str:
        """
        Summarize text using Ollama LLM into specified number of lines.
        
        Args:
            text: Text to summarize
            max_lines: Maximum number of lines for summary (default: 2)
            
        Returns:
            Summarized text
        """
        if not text or len(text.strip()) == 0:
            return ""
        
        # Prepare the prompt
        prompt = (
            f"Summarize the following review into exactly {max_lines} lines, "
            f"retaining all key and important information. Be concise and clear:\n\n"
            f"{text}\n\n"
            f"Summary ({max_lines} lines):"
        )
        
        try:
            # Call Ollama API
            url = f"{self.ollama_base_url}/api/generate"
            payload = {
                "model": self.model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.3,  # Lower temperature for more focused summaries
                    "top_p": 0.9
                }
            }
            
            logger.info(f"Calling Ollama API at {url} with model {self.model}")
            response = requests.post(url, json=payload, timeout=60)
            response.raise_for_status()
            
            result = response.json()
            summary = result.get('response', '').strip()
            
            # Ensure the summary doesn't exceed max_lines
            lines = summary.split('\n')
            summary = '\n'.join(line.strip() for line in lines[:max_lines] if line.strip())
            
            return summary
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error calling Ollama API: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error during summarization: {str(e)}")
            raise
    
    def process_review(self, review_data: Dict, summarize: bool = True) -> Dict:
        """
        Process a review: concatenate, clean, and optionally summarize.
        
        Args:
            review_data: Dictionary containing review data with 'title' and 'selftext' keys
            summarize: Whether to generate summary (default: True)
            
        Returns:
            Dictionary with processed review data including cleaned_text and summary
        """
        # Extract title and body
        title = review_data.get('title', '')
        body = review_data.get('selftext', '')
        
        # Concatenate
        concatenated = self.concatenate_review_text(title, body)
        
        # Clean
        cleaned = self.clean_text(concatenated)
        
        # Create result dictionary
        result = {
            **review_data,  # Include all original data
            'concatenated_text': concatenated,
            'cleaned_text': cleaned
        }
        
        # Summarize if requested
        if summarize and cleaned:
            try:
                summary = self.summarize_with_ollama(cleaned, max_lines=2)
                result['summary'] = summary
            except Exception as e:
                logger.warning(f"Failed to summarize review {review_data.get('id', 'unknown')}: {str(e)}")
                result['summary'] = None
                result['summary_error'] = str(e)
        
        return result
    
    def process_multiple_reviews(self, reviews: list, summarize: bool = True) -> list:
        """
        Process multiple reviews.
        
        Args:
            reviews: List of review dictionaries
            summarize: Whether to generate summaries (default: True)
            
        Returns:
            List of processed review dictionaries
        """
        processed_reviews = []
        
        for idx, review in enumerate(reviews, 1):
            logger.info(f"Processing review {idx}/{len(reviews)}: {review.get('id', 'unknown')}")
            try:
                processed = self.process_review(review, summarize=summarize)
                processed_reviews.append(processed)
            except Exception as e:
                logger.error(f"Error processing review {review.get('id', 'unknown')}: {str(e)}")
                # Still add the review with error information
                processed_reviews.append({
                    **review,
                    'processing_error': str(e)
                })
        
        return processed_reviews


def main():
    """
    Example usage of the ReviewProcessor class.
    """
    # Example review data
    sample_review = {
        'id': 'test123',
        'title': 'Great Product! 😊',
        'selftext': 'I   absolutely loved this product!!!  \n\n  It works perfectly... #amazing @company',
        'score': 150
    }
    
    # Initialize processor
    processor = ReviewProcessor()
    
    print("Original Review:")
    print(f"Title: {sample_review['title']}")
    print(f"Body: {sample_review['selftext']}")
    print()
    
    # Process review (without summarization for demo purposes)
    processed = processor.process_review(sample_review, summarize=False)
    
    print("Processed Review:")
    print(f"Concatenated: {processed['concatenated_text']}")
    print(f"Cleaned: {processed['cleaned_text']}")
    
    # To enable summarization, ensure Ollama is running and uncomment:
    # processed_with_summary = processor.process_review(sample_review, summarize=True)
    # print(f"Summary: {processed_with_summary.get('summary', 'N/A')}")


if __name__ == "__main__":
    main()
