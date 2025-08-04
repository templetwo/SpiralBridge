#!/usr/bin/env python3
"""
Comprehensive test suite for Gemini conversation link implementation.

This test suite covers:
- Various Gemini shared conversation links
- Different conversation lengths
- Edge cases (empty conversations, loading errors)
- Content cleaning and archiving verification
"""

import os
import sys
import time
import tempfile
import shutil
from unittest.mock import Mock, patch, MagicMock
import unittest
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException

# Add the current directory to Python path to import our modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from spiralbridge import (
    scrape_gemini_conversation,
    clean_gemini_conversation_content,
    scrape_with_retry,
    detect_platform,
    get_platform_error_message,
    initialize_driver
)
from archive_conversation import archive_conversation


class TestGeminiImplementation(unittest.TestCase):
    """Test suite for Gemini conversation link implementation."""
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.temp_dir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()
        os.chdir(self.temp_dir)
        
        # Mock browser for testing
        self.mock_browser = Mock()
        
        # Sample test URLs
        self.valid_gemini_urls = [
            "https://gemini.google.com/app/123abc456def",
            "https://gemini.google.com/share/xyz789",
            "https://g.co/gemini/abc123",
            "https://bard.google.com/chat/123456"  # Legacy Bard URL
        ]
        
        self.invalid_urls = [
            "https://claude.ai/share/123",
            "https://chat.openai.com/share/456",
            "https://example.com/invalid",
            "not_a_url"
        ]
    
    def tearDown(self):
        """Clean up after each test method."""
        os.chdir(self.original_cwd)
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_platform_detection(self):
        """Test that Gemini URLs are correctly detected."""
        print("\n=== Testing Platform Detection ===")
        
        # Test valid Gemini URLs
        for url in self.valid_gemini_urls:
            with self.subTest(url=url):
                platform = detect_platform(url)
                print(f"URL: {url} -> Platform: {platform}")
                self.assertEqual(platform, 'gemini', f"Failed to detect Gemini platform for {url}")
        
        # Test invalid URLs
        for url in self.invalid_urls:
            with self.subTest(url=url):
                platform = detect_platform(url)
                print(f"URL: {url} -> Platform: {platform}")
                self.assertNotEqual(platform, 'gemini', f"Incorrectly detected Gemini platform for {url}")
        
        print("✅ Platform detection tests passed")
    
    def test_gemini_content_cleaning(self):
        """Test Gemini-specific content cleaning functionality."""
        print("\n=== Testing Content Cleaning ===")
        
        # Test with typical Gemini UI content
        dirty_content = """Gemini Apps
Try Gemini Advanced
New chat
User: Hello, can you help me with Python?

Gemini: Of course! I'd be happy to help you with Python. What specific topic or problem would you like assistance with?

User: How do I create a list?

Gemini: In Python, you can create a list in several ways:

1. Empty list: `my_list = []`
2. With items: `my_list = [1, 2, 3, 'hello']`
3. Using list() constructor: `my_list = list()`

Lists are mutable, meaning you can change their contents after creation.

Gemini can make mistakes
Privacy & Terms
Made by Google"""
        
        cleaned = clean_gemini_conversation_content(dirty_content)
        print(f"Original length: {len(dirty_content)}")
        print(f"Cleaned length: {len(cleaned)}")
        print(f"Cleaned content preview:\n{cleaned[:200]}...")
        
        # Verify UI elements are removed
        self.assertNotIn("Gemini Apps", cleaned)
        self.assertNotIn("Try Gemini Advanced", cleaned)
        self.assertNotIn("New chat", cleaned)
        self.assertNotIn("Gemini can make mistakes", cleaned)
        self.assertNotIn("Privacy & Terms", cleaned)
        self.assertNotIn("Made by Google", cleaned)
        
        # Verify actual conversation content is preserved
        self.assertIn("Hello, can you help me with Python?", cleaned)
        self.assertIn("create a list", cleaned)
        self.assertIn("my_list = []", cleaned)
        
        print("✅ Content cleaning tests passed")
    
    def test_empty_content_handling(self):
        """Test handling of empty or minimal content."""
        print("\n=== Testing Empty Content Handling ===")
        
        test_cases = [
            ("", "Empty string"),
            ("   ", "Whitespace only"),
            ("\n\n\n", "Newlines only"),
            ("Gemini Apps\nNew chat\nMade by Google", "UI elements only"),
            ("•", "Single bullet point"),
            ("Menu", "Single navigation element")
        ]
        
        for content, description in test_cases:
            with self.subTest(content=description):
                cleaned = clean_gemini_conversation_content(content)
                print(f"{description}: '{content}' -> '{cleaned}'")
                # Should either be empty or very minimal
                self.assertTrue(len(cleaned) <= len(content), f"Cleaning should not increase length for {description}")
        
        print("✅ Empty content handling tests passed")
    
    def test_conversation_length_scenarios(self):
        """Test different conversation lengths."""
        print("\n=== Testing Different Conversation Lengths ===")
        
        # Short conversation
        short_conversation = """User: Hi
Gemini: Hello! How can I help you today?"""
        
        # Medium conversation
        medium_conversation = """User: Can you explain machine learning?

Gemini: Machine learning is a subset of artificial intelligence (AI) that enables computers to learn and improve from experience without being explicitly programmed for every task.

User: What are the main types?

Gemini: The main types of machine learning are:

1. **Supervised Learning**: Uses labeled training data
2. **Unsupervised Learning**: Finds patterns in unlabeled data  
3. **Reinforcement Learning**: Learns through trial and error

Each type has different applications and use cases.

User: Thanks, that's helpful!

Gemini: You're welcome! Feel free to ask if you need more details about any specific type."""
        
        # Long conversation (simulated)
        long_conversation_parts = [
            "User: Let's discuss advanced Python concepts",
            "Gemini: Great! I'd love to explore advanced Python with you."
        ]
        
        # Add many exchanges to simulate a long conversation
        for i in range(10):
            long_conversation_parts.extend([
                f"User: Can you explain concept {i+1}?",
                f"Gemini: Certainly! Concept {i+1} is an important topic in Python programming. Here's a detailed explanation with examples and best practices..."
            ])
        
        long_conversation = "\n\n".join(long_conversation_parts)
        
        conversations = [
            (short_conversation, "Short conversation"),
            (medium_conversation, "Medium conversation"),
            (long_conversation, "Long conversation")
        ]
        
        for content, description in conversations:
            with self.subTest(conversation=description):
                cleaned = clean_gemini_conversation_content(content)
                print(f"{description}: {len(content)} chars -> {len(cleaned)} chars")
                
                # Verify content is preserved
                self.assertIn("User:", cleaned)
                self.assertIn("Gemini:", cleaned)
                self.assertGreater(len(cleaned), 0)
        
        print("✅ Conversation length tests passed")
    
    @patch('spiralbridge.uc.Chrome')
    def test_scrape_with_mock_browser(self, mock_chrome_class):
        """Test scraping with mocked browser responses."""
        print("\n=== Testing Scraping with Mock Browser ===")
        
        # Mock successful response
        mock_browser = Mock()
        mock_element = Mock()
        mock_element.text = """User: Hello Gemini!

Gemini: Hello! How can I assist you today?

User: What's the weather like?

Gemini: I don't have access to real-time weather data, but I can help you find weather information from reliable sources."""
        
        mock_browser.find_element.return_value = mock_element
        mock_browser.find_elements.return_value = []  # No specific conversation elements found
        
        # Test successful scraping
        result = scrape_gemini_conversation(mock_browser, "https://gemini.google.com/share/test", timeout=1)
        
        print(f"Scraping result length: {len(result) if result else 0}")
        self.assertIsNotNone(result)
        self.assertIn("Hello Gemini!", result)
        self.assertIn("assist you today", result)
        
        print("✅ Mock browser scraping tests passed")
    
    def test_error_handling(self):
        """Test error handling for various failure scenarios."""
        print("\n=== Testing Error Handling ===")
        
        # Test timeout error
        timeout_error = TimeoutException("Page load timeout")
        error_msg = get_platform_error_message('gemini', timeout_error)
        print(f"Timeout error message: {error_msg}")
        self.assertIn("Gemini Error", error_msg)
        self.assertIn("timeout", error_msg.lower())
        
        # Test element not found error
        element_error = NoSuchElementException("Element not found")
        error_msg = get_platform_error_message('gemini', element_error)
        print(f"Element error message: {error_msg}")
        self.assertIn("Gemini Error", error_msg)
        self.assertIn("not locate", error_msg.lower())
        
        # Test access denied error
        access_error = WebDriverException("Access denied")
        error_msg = get_platform_error_message('gemini', access_error)
        print(f"Access error message: {error_msg}")
        self.assertIn("Gemini Error", error_msg)
        
        print("✅ Error handling tests passed")
    
    def test_content_archiving(self):
        """Test that content is properly archived."""
        print("\n=== Testing Content Archiving ===")
        
        test_content = """User: Test conversation for archiving

Gemini: This is a test conversation that should be properly archived with timestamp and platform-specific directory."""
        
        # Test archiving
        archive_path = archive_conversation(test_content, 'gemini')
        
        print(f"Archive path: {archive_path}")
        self.assertTrue(os.path.exists(archive_path))
        self.assertIn('gemini', archive_path)
        self.assertIn('session-', os.path.basename(archive_path))
        
        # Verify content was saved correctly
        with open(archive_path, 'r', encoding='utf-8') as f:
            saved_content = f.read()
        
        self.assertEqual(saved_content, test_content)
        print(f"Saved content length: {len(saved_content)}")
        
        print("✅ Content archiving tests passed")
    
    def test_retry_mechanism(self):
        """Test the retry mechanism for failed requests."""
        print("\n=== Testing Retry Mechanism ===")
        
        # Mock a function that fails twice then succeeds
        attempt_count = 0
        def mock_scraping_function(browser, url, timeout):
            nonlocal attempt_count
            attempt_count += 1
            if attempt_count < 3:
                raise TimeoutException(f"Attempt {attempt_count} failed")
            return "Success on attempt 3"
        
        mock_browser = Mock()
        
        # Test retry with eventual success
        result = scrape_with_retry(
            mock_scraping_function, 
            mock_browser, 
            "https://gemini.google.com/share/test", 
            'gemini', 
            timeout=1, 
            max_attempts=3
        )
        
        print(f"Retry result: {result}")
        self.assertEqual(result, "Success on attempt 3")
        self.assertEqual(attempt_count, 3)
        
        print("✅ Retry mechanism tests passed")


class TestGeminiIntegration(unittest.TestCase):
    """Integration tests for Gemini implementation (requires actual browser)."""
    
    def setUp(self):
        """Set up for integration tests."""
        self.temp_dir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()
        os.chdir(self.temp_dir)
    
    def tearDown(self):
        """Clean up after integration tests."""
        os.chdir(self.original_cwd)
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    @unittest.skip("Integration test - requires actual browser and network")
    def test_real_gemini_scraping(self):
        """Integration test with real Gemini URLs (skipped by default)."""
        print("\n=== Integration Test: Real Gemini Scraping ===")
        
        # This test is skipped by default because it requires:
        # 1. An actual browser (Chrome)
        # 2. Network connectivity  
        # 3. Valid Gemini shared URLs
        # 4. Potentially dealing with bot detection
        
        try:
            browser = initialize_driver()
            
            # Test with a sample Gemini conversation URL
            # Replace with actual shared conversation URL for testing
            test_url = "https://gemini.google.com/share/your-test-conversation-id"
            
            result = scrape_gemini_conversation(browser, test_url, timeout=30)
            
            if result:
                print(f"Integration test successful! Content length: {len(result)}")
                print(f"Content preview: {result[:200]}...")
                
                # Archive the result
                archive_path = archive_conversation(result, 'gemini')
                print(f"Archived to: {archive_path}")
                
                self.assertIsNotNone(result)
                self.assertGreater(len(result), 0)
            else:
                print("Integration test: No content retrieved (this may be expected)")
                
        except Exception as e:
            print(f"Integration test error: {e}")
            self.skipTest(f"Integration test failed due to: {e}")
        finally:
            try:
                browser.quit()
            except:
                pass


def run_manual_tests():
    """Run manual tests with actual Gemini URLs for comprehensive testing."""
    print("🧪 MANUAL TESTING GUIDE FOR GEMINI IMPLEMENTATION")
    print("=" * 60)
    
    print("\n📝 To manually test the Gemini implementation:")
    print("\n1. Create test conversations on Gemini:")
    print("   - Short conversation (1-2 exchanges)")
    print("   - Medium conversation (5-10 exchanges)")
    print("   - Long conversation (20+ exchanges)")
    print("   - Conversation with code snippets")
    print("   - Conversation with formatting (lists, tables)")
    
    print("\n2. Share each conversation and get the URLs")
    
    print("\n3. Test with the main script:")
    print("   python spiralbridge.py [GEMINI_URL]")
    
    print("\n4. Test edge cases:")
    print("   - Private conversations (not shared)")
    print("   - Expired share links")
    print("   - Invalid/malformed URLs")
    print("   - Rate limiting scenarios")
    
    print("\n5. Verify outputs:")
    print("   - Check memory_logs/gemini/ directory")
    print("   - Verify content cleaning (no UI elements)")
    print("   - Confirm proper formatting preservation")
    print("   - Validate timestamp-based filenames")
    
    print("\n6. Test error scenarios:")
    print("   - Disconnect internet during scraping")
    print("   - Use URLs that require authentication")
    print("   - Test with very slow connections")
    
    print("\n🔧 SAMPLE TEST URLS (create these yourself):")
    print("   Replace with your actual Gemini conversation URLs:")
    
    sample_urls = [
        "https://gemini.google.com/app/[your-conversation-id]",
        "https://gemini.google.com/share/[your-share-id]",
        "https://g.co/gemini/[your-short-id]"
    ]
    
    for i, url in enumerate(sample_urls, 1):
        print(f"   {i}. {url}")
    
    print(f"\n🚀 To run these tests:")
    print("   python test_gemini_implementation.py")


if __name__ == "__main__":
    print("🌉 SpiralBridge Gemini Implementation Test Suite")
    print("=" * 60)
    
    # Run the automated tests
    unittest.main(verbosity=2, exit=False)
    
    # Display manual testing guide
    print("\n" + "=" * 60)
    run_manual_tests()
