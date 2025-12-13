"""
Review Processor Module

This module provides functionality to process and summarize Reddit reviews using:
- Text concatenation (title + body)
- Text cleaning (whitespaces, emojis, special characters)
- Ollama LLM-based summarization
"""

import re
import logging
from typing import Dict, Optional, List
import requests
import json
import os
from datetime import datetime, timezone

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
        
    def concatenate_review_text(self, title: Optional[str], body: Optional[str]) -> str:
        """
        Concatenate the title and body of a review.
        
        Args:
            title: Review title (can be None or empty)
            body: Review body/selftext (can be None or empty)
            
        Returns:
            Concatenated text
        """
        # Handle None values
        title = title or ""
        body = body or ""
        
        # Concatenate with a space separator
        return f"{title} {body}".strip()
    
    def clean_text(self, text: Optional[str]) -> str:
        """
        Clean text by removing excessive whitespaces, emojis, and special characters.
        
        Args:
            text: Input text to clean (can be None or empty)
            
        Returns:
            Cleaned text
        """
        if not text:
            return ""
        
        # Remove emojis (Unicode emoji ranges)
        # Using specific emoji ranges to avoid removing CJK characters
        emoji_pattern = re.compile(
            "["
            "\U0001F600-\U0001F64F"  # emoticons
            "\U0001F300-\U0001F5FF"  # symbols & pictographs
            "\U0001F680-\U0001F6FF"  # transport & map symbols
            "\U0001F1E0-\U0001F1FF"  # flags (iOS)
            "\U0001F900-\U0001F9FF"  # Supplemental Symbols and Pictographs
            "\U0001FA00-\U0001FA6F"  # Chess Symbols
            "\U0001FA70-\U0001FAFF"  # Symbols and Pictographs Extended-A
            "\U00002600-\U000026FF"  # Miscellaneous Symbols
            "\U00002700-\U000027BF"  # Dingbats (merged range)
            "]+", 
            flags=re.UNICODE
        )
        text = emoji_pattern.sub(r'', text)
        
        # Remove special characters but keep basic punctuation (.,!?;:'"-)
        # Using UNICODE flag to properly handle international characters
        text = re.sub(r'[^\w\s.,!?;:\'\"-]', '', text, flags=re.UNICODE)
        
        # Replace multiple whitespaces (including newlines, tabs) with single space
        text = re.sub(r'\s+', ' ', text, flags=re.UNICODE)
        
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
    
    def process_multiple_reviews(self, reviews: List[Dict], summarize: bool = True) -> List[Dict]:
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
    
    def extract_structured_info(self, summary: str) -> Dict:
        """
        Extract structured information from a summarized review using Ollama LLM.
        
        Args:
            summary: Summarized review text
            
        Returns:
            Dictionary containing structured information with the following keys:
            - product_or_service_name: str
            - key_point_description: str
            - key_pain_point: str
            - sentiment: str
            - test_steps: List[str]
            - test_environment: Dict[str, str]
        """
        if not summary or len(summary.strip()) == 0:
            return self._get_empty_structured_info()
        
        # Prepare the prompt for structured extraction
        prompt = f"""Analyze the following review summary and extract structured information in JSON format.

Review Summary:
{summary}

Extract the following information and respond ONLY with a valid JSON object (no additional text):
{{
  "product_or_service_name": "The name of the product or service mentioned (if not clearly stated, use 'Not specified')",
  "key_point_description": "A short description (1-2 sentences) of the key point in the review",
  "key_pain_point": "The key pain point or essence of the user feedback (if positive review, state the main benefit)",
  "sentiment": "The sentiment expressed (Positive, Negative, Neutral, or Mixed)",
  "test_steps": ["Step 1", "Step 2", "..."] (list of recommended test steps to reproduce the issue, or empty list if not applicable),
  "test_environment": {{
    "os": "Operating system (if mentioned)",
    "software_version": "Software/app version (if mentioned)",
    "product_model": "Product model name (if mentioned)",
    "other": "Any other relevant environment details (if mentioned)"
  }}
}}

Important: Return ONLY the JSON object, no additional text or explanation."""
        
        try:
            # Call Ollama API
            url = f"{self.ollama_base_url}/api/generate"
            payload = {
                "model": self.model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.2,  # Lower temperature for more consistent structured output
                    "top_p": 0.9
                }
            }
            
            logger.info(f"Calling Ollama API for structured extraction with model {self.model}")
            response = requests.post(url, json=payload, timeout=90)
            response.raise_for_status()
            
            result = response.json()
            llm_response = result.get('response', '').strip()
            
            # Try to parse the JSON response
            # Sometimes LLM might add extra text, so we need to extract the JSON part
            try:
                # Try to find JSON object in the response
                json_start = llm_response.find('{')
                json_end = llm_response.rfind('}') + 1
                
                if json_start >= 0 and json_end > json_start:
                    json_str = llm_response[json_start:json_end]
                    structured_info = json.loads(json_str)
                else:
                    # If no JSON found, try parsing the entire response
                    structured_info = json.loads(llm_response)
                
                # Validate and ensure all required fields are present
                return self._validate_structured_info(structured_info)
                
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse JSON from LLM response: {str(e)}")
                logger.error(f"LLM Response: {llm_response}")
                # Return empty structure with error
                result = self._get_empty_structured_info()
                result['extraction_error'] = f"JSON parsing error: {str(e)}"
                return result
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Error calling Ollama API: {str(e)}")
            result = self._get_empty_structured_info()
            result['extraction_error'] = f"API error: {str(e)}"
            return result
        except Exception as e:
            logger.error(f"Unexpected error during structured extraction: {str(e)}")
            result = self._get_empty_structured_info()
            result['extraction_error'] = f"Unexpected error: {str(e)}"
            return result
    
    def _get_empty_structured_info(self) -> Dict:
        """
        Get an empty structured information dictionary with default values.
        
        Returns:
            Dictionary with empty/default values for all structured fields
        """
        return {
            'product_or_service_name': 'Not specified',
            'key_point_description': '',
            'key_pain_point': '',
            'sentiment': 'Unknown',
            'test_steps': [],
            'test_environment': {
                'os': 'Not specified',
                'software_version': 'Not specified',
                'product_model': 'Not specified',
                'other': 'Not specified'
            }
        }
    
    def _validate_structured_info(self, info: Dict) -> Dict:
        """
        Validate and normalize structured information dictionary.
        
        Args:
            info: Dictionary with extracted structured information
            
        Returns:
            Validated and normalized dictionary
        """
        # Get default structure
        validated = self._get_empty_structured_info()
        
        # Update with extracted values
        if 'product_or_service_name' in info:
            validated['product_or_service_name'] = str(info['product_or_service_name'])
        
        if 'key_point_description' in info:
            validated['key_point_description'] = str(info['key_point_description'])
        
        if 'key_pain_point' in info:
            validated['key_pain_point'] = str(info['key_pain_point'])
        
        if 'sentiment' in info:
            validated['sentiment'] = str(info['sentiment'])
        
        if 'test_steps' in info:
            if isinstance(info['test_steps'], list):
                validated['test_steps'] = [str(step) for step in info['test_steps']]
            else:
                validated['test_steps'] = [str(info['test_steps'])]
        
        if 'test_environment' in info and isinstance(info['test_environment'], dict):
            # Update test_environment with extracted values
            for key in ['os', 'software_version', 'product_model', 'other']:
                if key in info['test_environment']:
                    validated['test_environment'][key] = str(info['test_environment'][key])
        
        return validated
    
    def save_structured_reviews_to_json(self, reviews: List[Dict], output_file: str) -> None:
        """
        Save structured review information to a JSON file.
        
        Args:
            reviews: List of review dictionaries with structured information
            output_file: Path to the output JSON file
        """
        try:
            # Create the directory if it doesn't exist
            output_dir = os.path.dirname(output_file)
            if output_dir and not os.path.exists(output_dir):
                os.makedirs(output_dir)
            
            # Prepare the output data
            output_data = {
                'metadata': {
                    'generated_at': datetime.now(timezone.utc).isoformat(),
                    'total_reviews': len(reviews),
                    'model_used': self.model
                },
                'reviews': reviews
            }
            
            # Write to JSON file
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(output_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Successfully saved {len(reviews)} structured reviews to {output_file}")
            
        except Exception as e:
            logger.error(f"Error saving structured reviews to JSON: {str(e)}")
            raise


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
