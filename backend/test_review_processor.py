"""
Unit tests for the ReviewProcessor module.

Run with: python -m pytest test_review_processor.py
Or simply: python test_review_processor.py
"""

import unittest
import json
import os
import tempfile
from review_processor import ReviewProcessor


class TestReviewProcessor(unittest.TestCase):
    """Test cases for ReviewProcessor class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.processor = ReviewProcessor()
    
    def test_concatenate_review_text_basic(self):
        """Test basic concatenation of title and body."""
        title = "Great Product"
        body = "Works perfectly"
        result = self.processor.concatenate_review_text(title, body)
        self.assertEqual(result, "Great Product Works perfectly")
    
    def test_concatenate_review_text_with_none(self):
        """Test concatenation with None values."""
        # Both None
        result = self.processor.concatenate_review_text(None, None)
        self.assertEqual(result, "")
        
        # Title None
        result = self.processor.concatenate_review_text(None, "Body text")
        self.assertEqual(result, "Body text")
        
        # Body None
        result = self.processor.concatenate_review_text("Title text", None)
        self.assertEqual(result, "Title text")
    
    def test_concatenate_review_text_with_empty(self):
        """Test concatenation with empty strings."""
        result = self.processor.concatenate_review_text("", "")
        self.assertEqual(result, "")
        
        result = self.processor.concatenate_review_text("Title", "")
        self.assertEqual(result, "Title")
    
    def test_clean_text_remove_emojis(self):
        """Test removal of emojis."""
        text = "Great product! 😊 Love it! ❤️"
        result = self.processor.clean_text(text)
        self.assertNotIn("😊", result)
        self.assertNotIn("❤️", result)
        self.assertIn("Great product!", result)
    
    def test_clean_text_remove_special_characters(self):
        """Test removal of special characters."""
        text = "Amazing product!!! #awesome @company"
        result = self.processor.clean_text(text)
        self.assertNotIn("#", result)
        self.assertNotIn("@", result)
        self.assertIn("Amazing product", result)
    
    def test_clean_text_normalize_whitespace(self):
        """Test normalization of whitespace."""
        text = "I   absolutely  loved   this\n\nproduct!!!"
        result = self.processor.clean_text(text)
        # Should have single spaces only
        self.assertNotIn("  ", result)
        self.assertNotIn("\n", result)
        self.assertEqual(result.count("  "), 0)
    
    def test_clean_text_keep_punctuation(self):
        """Test that basic punctuation is preserved."""
        text = "Great! Works perfectly. Really amazing, isn't it?"
        result = self.processor.clean_text(text)
        self.assertIn("!", result)
        self.assertIn(".", result)
        self.assertIn(",", result)
        self.assertIn("?", result)
    
    def test_clean_text_empty_input(self):
        """Test cleaning with empty or None input."""
        self.assertEqual(self.processor.clean_text(""), "")
        self.assertEqual(self.processor.clean_text(None), "")
    
    def test_clean_text_comprehensive(self):
        """Test comprehensive cleaning with multiple issues."""
        text = "I   loved 😊 this product!!!  \n\n  #amazing @company"
        result = self.processor.clean_text(text)
        expected = "I loved this product!!! amazing company"
        self.assertEqual(result, expected)
    
    def test_process_review_without_summarization(self):
        """Test processing review without summarization."""
        review_data = {
            'id': 'test123',
            'title': 'Great Product! 😊',
            'selftext': 'I   loved this!!!  #awesome',
            'score': 150
        }
        
        result = self.processor.process_review(review_data, summarize=False)
        
        # Check all fields are present
        self.assertIn('id', result)
        self.assertIn('title', result)
        self.assertIn('concatenated_text', result)
        self.assertIn('cleaned_text', result)
        
        # Check original data is preserved
        self.assertEqual(result['id'], 'test123')
        self.assertEqual(result['score'], 150)
        
        # Check cleaned text
        self.assertNotIn('😊', result['cleaned_text'])
        self.assertNotIn('#', result['cleaned_text'])
    
    def test_process_review_with_empty_body(self):
        """Test processing review with empty body."""
        review_data = {
            'id': 'test456',
            'title': 'Just a title',
            'selftext': '',
            'score': 50
        }
        
        result = self.processor.process_review(review_data, summarize=False)
        
        self.assertEqual(result['concatenated_text'], 'Just a title')
        self.assertEqual(result['cleaned_text'], 'Just a title')
    
    def test_process_multiple_reviews(self):
        """Test batch processing of multiple reviews."""
        reviews = [
            {
                'id': 'review1',
                'title': 'Great! 😊',
                'selftext': 'Loved it',
                'score': 100
            },
            {
                'id': 'review2',
                'title': 'Not bad',
                'selftext': 'It works',
                'score': 50
            }
        ]
        
        results = self.processor.process_multiple_reviews(reviews, summarize=False)
        
        self.assertEqual(len(results), 2)
        self.assertEqual(results[0]['id'], 'review1')
        self.assertEqual(results[1]['id'], 'review2')
        self.assertIn('cleaned_text', results[0])
        self.assertIn('cleaned_text', results[1])
    
    def test_process_review_preserves_original_data(self):
        """Test that processing preserves all original review data."""
        review_data = {
            'id': 'test789',
            'title': 'Test',
            'selftext': 'Body',
            'score': 200,
            'author': 'testuser',
            'subreddit': 'test',
            'custom_field': 'custom_value'
        }
        
        result = self.processor.process_review(review_data, summarize=False)
        
        # All original fields should be present
        self.assertEqual(result['id'], 'test789')
        self.assertEqual(result['score'], 200)
        self.assertEqual(result['author'], 'testuser')
        self.assertEqual(result['subreddit'], 'test')
        self.assertEqual(result['custom_field'], 'custom_value')
    
    def test_clean_text_unicode_handling(self):
        """Test that unicode characters are handled properly."""
        text = "Café résumé naïve"
        result = self.processor.clean_text(text)
        # Should preserve unicode letters
        self.assertIn("Café", result)
        self.assertIn("résumé", result)
        self.assertIn("naïve", result)


class TestReviewProcessorEdgeCases(unittest.TestCase):
    """Test edge cases and error handling."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.processor = ReviewProcessor()
    
    def test_very_long_text(self):
        """Test handling of very long text."""
        long_text = "word " * 10000  # 10000 words
        result = self.processor.clean_text(long_text)
        # Should complete without error
        self.assertIsInstance(result, str)
        self.assertGreater(len(result), 0)
    
    def test_text_with_only_emojis(self):
        """Test text containing only emojis."""
        text = "😊😂❤️🎉"
        result = self.processor.clean_text(text)
        self.assertEqual(result, "")
    
    def test_text_with_only_special_chars(self):
        """Test text containing only special characters."""
        text = "###@@@$$$%%%"
        result = self.processor.clean_text(text)
        self.assertEqual(result, "")
    
    def test_text_with_only_whitespace(self):
        """Test text containing only whitespace."""
        text = "   \n\n   \t\t   "
        result = self.processor.clean_text(text)
        self.assertEqual(result, "")
    
    def test_mixed_language_text(self):
        """Test text with mixed languages."""
        text = "Great product! Excellent качество! 很好!"
        result = self.processor.clean_text(text)
        # Should handle non-ASCII characters
        self.assertIn("Great", result)


class TestStructuredInfoExtraction(unittest.TestCase):
    """Test structured information extraction."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.processor = ReviewProcessor()
    
    def test_get_empty_structured_info(self):
        """Test getting empty structured info."""
        result = self.processor._get_empty_structured_info()
        
        # Check all required fields are present
        self.assertIn('product_or_service_name', result)
        self.assertIn('key_point_description', result)
        self.assertIn('key_pain_point', result)
        self.assertIn('sentiment', result)
        self.assertIn('test_steps', result)
        self.assertIn('test_environment', result)
        
        # Check test_environment has all required fields
        self.assertIn('os', result['test_environment'])
        self.assertIn('software_version', result['test_environment'])
        self.assertIn('product_model', result['test_environment'])
        self.assertIn('other', result['test_environment'])
    
    def test_validate_structured_info_with_valid_data(self):
        """Test validation with valid structured data."""
        input_data = {
            'product_or_service_name': 'Test Product',
            'key_point_description': 'Great product',
            'key_pain_point': 'None',
            'sentiment': 'Positive',
            'test_steps': ['Step 1', 'Step 2'],
            'test_environment': {
                'os': 'Windows 10',
                'software_version': '1.0.0',
                'product_model': 'Model X',
                'other': 'None'
            }
        }
        
        result = self.processor._validate_structured_info(input_data)
        
        self.assertEqual(result['product_or_service_name'], 'Test Product')
        self.assertEqual(result['key_point_description'], 'Great product')
        self.assertEqual(result['sentiment'], 'Positive')
        self.assertEqual(len(result['test_steps']), 2)
        self.assertEqual(result['test_environment']['os'], 'Windows 10')
    
    def test_validate_structured_info_with_partial_data(self):
        """Test validation with partial structured data."""
        input_data = {
            'product_or_service_name': 'Test Product',
            'sentiment': 'Neutral'
        }
        
        result = self.processor._validate_structured_info(input_data)
        
        # Should have the provided fields
        self.assertEqual(result['product_or_service_name'], 'Test Product')
        self.assertEqual(result['sentiment'], 'Neutral')
        
        # Should have default values for missing fields
        self.assertEqual(result['key_point_description'], '')
        self.assertEqual(result['test_steps'], [])
    
    def test_validate_structured_info_converts_types(self):
        """Test that validation converts values to strings."""
        input_data = {
            'product_or_service_name': 123,
            'sentiment': True,
            'test_steps': [1, 2, 3]
        }
        
        result = self.processor._validate_structured_info(input_data)
        
        # Should convert to strings
        self.assertEqual(result['product_or_service_name'], '123')
        self.assertEqual(result['sentiment'], 'True')
        self.assertEqual(result['test_steps'], ['1', '2', '3'])
    
    def test_extract_structured_info_with_empty_summary(self):
        """Test structured extraction with empty summary."""
        result = self.processor.extract_structured_info("")
        
        # Should return default values
        self.assertEqual(result['product_or_service_name'], 'Not specified')
        self.assertEqual(result['sentiment'], 'Unknown')
        self.assertIsInstance(result['test_steps'], list)
    
    def test_save_structured_reviews_to_json(self):
        """Test saving structured reviews to JSON file."""
        # Create a temporary file
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as temp_file:
            temp_path = temp_file.name
        
        try:
            # Sample structured reviews
            reviews = [
                {
                    'id': 'review1',
                    'product_or_service_name': 'Test Product',
                    'key_point_description': 'Great features',
                    'key_pain_point': 'None',
                    'sentiment': 'Positive',
                    'test_steps': [],
                    'test_environment': {
                        'os': 'Windows 10',
                        'software_version': '1.0',
                        'product_model': 'Model X',
                        'other': 'None'
                    }
                },
                {
                    'id': 'review2',
                    'product_or_service_name': 'Another Product',
                    'key_point_description': 'Has issues',
                    'key_pain_point': 'Crashes often',
                    'sentiment': 'Negative',
                    'test_steps': ['Open app', 'Click button', 'Observe crash'],
                    'test_environment': {
                        'os': 'macOS',
                        'software_version': '2.0',
                        'product_model': 'Model Y',
                        'other': 'None'
                    }
                }
            ]
            
            # Save to JSON
            self.processor.save_structured_reviews_to_json(reviews, temp_path)
            
            # Verify file exists
            self.assertTrue(os.path.exists(temp_path))
            
            # Read and verify content
            with open(temp_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Check structure
            self.assertIn('metadata', data)
            self.assertIn('reviews', data)
            self.assertIn('generated_at', data['metadata'])
            self.assertIn('total_reviews', data['metadata'])
            self.assertEqual(data['metadata']['total_reviews'], 2)
            
            # Check reviews
            self.assertEqual(len(data['reviews']), 2)
            self.assertEqual(data['reviews'][0]['id'], 'review1')
            self.assertEqual(data['reviews'][1]['id'], 'review2')
            
        finally:
            # Clean up
            if os.path.exists(temp_path):
                os.remove(temp_path)
    
    def test_save_structured_reviews_creates_directory(self):
        """Test that saving creates output directory if it doesn't exist."""
        # Create a temporary directory
        with tempfile.TemporaryDirectory() as temp_dir:
            # Path with non-existent subdirectory
            output_path = os.path.join(temp_dir, 'subdir', 'output.json')
            
            reviews = [{'id': 'test1', 'sentiment': 'Positive'}]
            
            # Should create directory and file
            self.processor.save_structured_reviews_to_json(reviews, output_path)
            
            # Verify file was created
            self.assertTrue(os.path.exists(output_path))
            
            # Verify content
            with open(output_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            self.assertEqual(len(data['reviews']), 1)


def run_tests():
    """Run all tests."""
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test cases
    suite.addTests(loader.loadTestsFromTestCase(TestReviewProcessor))
    suite.addTests(loader.loadTestsFromTestCase(TestReviewProcessorEdgeCases))
    suite.addTests(loader.loadTestsFromTestCase(TestStructuredInfoExtraction))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Return exit code
    return 0 if result.wasSuccessful() else 1


if __name__ == '__main__':
    exit(run_tests())
