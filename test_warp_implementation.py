#!/usr/bin/env python3
"""
Test suite for Warp session scraping implementation in SpiralBridge.

This module contains comprehensive tests for the Warp session functionality,
including platform detection, content cleaning, and error handling.
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import sys
import os

# Add the parent directory to the path so we can import spiralbridge
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from spiralbridge import (
    detect_platform,
    clean_warp_conversation_content,
    get_platform_error_message,
    scrape_warp_conversation
)

class TestWarpImplementation(unittest.TestCase):
    """Test cases for Warp session scraping functionality."""
    
    def test_warp_platform_detection(self):
        """Test that Warp URLs are correctly detected."""
        warp_urls = [
            "https://app.warp.dev/session/12345",
            "https://app.warp.dev/session/abc-def-ghi?pwd=xyz",
            "http://app.warp.dev/session/test",
            "HTTPS://APP.WARP.DEV/SESSION/UPPERCASE"
        ]
        
        for url in warp_urls:
            with self.subTest(url=url):
                platform = detect_platform(url)
                self.assertEqual(platform, 'warp', f"Failed to detect Warp platform for URL: {url}")
    
    def test_non_warp_urls_not_detected_as_warp(self):
        """Test that non-Warp URLs are not detected as Warp."""
        non_warp_urls = [
            "https://claude.ai/chat/12345",
            "https://gemini.google.com/share/abc",
            "https://chat.openai.com/share/xyz",
            "https://example.com/warp",
            "https://warp.example.com",
            "https://app.notthewarp.dev/session/123"
        ]
        
        for url in non_warp_urls:
            with self.subTest(url=url):
                platform = detect_platform(url)
                self.assertNotEqual(platform, 'warp', f"Incorrectly detected Warp platform for URL: {url}")
    
    def test_warp_content_cleaning_basic(self):
        """Test basic Warp content cleaning functionality."""
        raw_content = """
        You need to enable JavaScript
        Warp Terminal
        
        $ ls -la
        total 24
        drwxr-xr-x  3 user user 4096 Jan 15 10:30 .
        drwxr-xr-x 10 user user 4096 Jan 15 10:29 ..
        -rw-r--r--  1 user user  220 Jan 15 10:29 .bash_logout
        
        $ pwd
        /home/user
        
        Sign in to Warp
        """
        
        cleaned = clean_warp_conversation_content(raw_content)
        
        # Should remove Warp UI elements
        self.assertNotIn("You need to enable JavaScript", cleaned)
        self.assertNotIn("Warp Terminal", cleaned)
        self.assertNotIn("Sign in to Warp", cleaned)
        
        # Should preserve terminal commands and output
        self.assertIn("$ ls -la", cleaned)
        self.assertIn("$ pwd", cleaned)
        self.assertIn("/home/user", cleaned)
    
    def test_warp_content_cleaning_javascript_warning(self):
        """Test handling of JavaScript-only content."""
        js_only_content = "You need to enable JavaScript to run this app."
        
        cleaned = clean_warp_conversation_content(js_only_content)
        
        # Should detect JavaScript warning and provide helpful message
        self.assertIn("Warp Session Access Limited", cleaned)
        self.assertIn("requires JavaScript", cleaned)
        self.assertIn("authentication", cleaned)
    
    def test_warp_content_cleaning_empty_content(self):
        """Test cleaning of empty or whitespace-only content."""
        test_cases = ["", "   ", "\n\n\n", None]
        
        for content in test_cases:
            with self.subTest(content=repr(content)):
                cleaned = clean_warp_conversation_content(content)
                if content is None:
                    self.assertIsNone(cleaned)
                else:
                    self.assertEqual(cleaned.strip(), "")
    
    def test_warp_content_preservation(self):
        """Test that important terminal content is preserved."""
        terminal_content = """
        $ git status
        On branch main
        Your branch is up to date with 'origin/main'.
        
        Changes not staged for commit:
          (use "git add <file>..." to update what will be committed)
          (use "git restore <file>..." to discard changes in working directory)
                modified:   test.py
        
        $ python test.py
        Running tests...
        All tests passed!
        """
        
        cleaned = clean_warp_conversation_content(terminal_content)
        
        # Should preserve all the terminal commands and output
        self.assertIn("$ git status", cleaned)
        self.assertIn("On branch main", cleaned)
        self.assertIn("$ python test.py", cleaned)
        self.assertIn("All tests passed!", cleaned)
        self.assertIn("modified:   test.py", cleaned)
    
    def test_warp_error_messages(self):
        """Test platform-specific error message generation for Warp."""
        error_scenarios = [
            ("timeout", "Session load timeout"),
            ("element not found", "Could not find session content"),
            ("connection", "Network connectivity issue"),
            ("access denied", "Access denied"),
            ("javascript", "JavaScript execution required"),
            ("unknown error", "Warp Error: unknown error")
        ]
        
        for error_text, expected_message in error_scenarios:
            with self.subTest(error=error_text):
                mock_error = Exception(error_text)
                error_msg = get_platform_error_message('warp', mock_error)
                self.assertIn(expected_message, error_msg)
                self.assertIn("Warp Error:", error_msg)
    
    @patch('spiralbridge.time.sleep')
    def test_warp_scraping_with_mock_browser(self, mock_sleep):
        """Test Warp scraping with a mocked browser."""
        # Create mock browser
        mock_browser = Mock()
        mock_element = Mock()
        mock_element.text = "$ echo 'Hello Warp'\nHello Warp\n$ date\nMon Jan 15 10:30:00 PST 2024"
        mock_browser.find_element.return_value = mock_element
        mock_browser.find_elements.return_value = []  # No specific selectors found
        
        # Test successful scraping
        result = scrape_warp_conversation(mock_browser, "https://app.warp.dev/session/test", timeout=5)
        
        # Verify browser interactions
        mock_browser.get.assert_called_once_with("https://app.warp.dev/session/test")
        mock_sleep.assert_called()
        
        # Verify content extraction
        self.assertIsNotNone(result)
        self.assertIn("echo 'Hello Warp'", result)
        self.assertIn("date", result)
    
    @patch('spiralbridge.time.sleep')
    def test_warp_scraping_no_content(self, mock_sleep):
        """Test Warp scraping when no content is found."""
        # Create mock browser with empty content
        mock_browser = Mock()
        mock_element = Mock()
        mock_element.text = ""
        mock_browser.find_element.return_value = mock_element
        mock_browser.find_elements.return_value = []
        
        # Test scraping with no content
        result = scrape_warp_conversation(mock_browser, "https://app.warp.dev/session/empty", timeout=5)
        
        # Should return None for empty content
        self.assertIsNone(result)
    
    @patch('spiralbridge.time.sleep')
    def test_warp_scraping_with_terminal_elements(self, mock_sleep):
        """Test Warp scraping when terminal-specific elements are found."""
        # Create mock browser with terminal elements
        mock_browser = Mock()
        
        # Mock terminal elements
        mock_terminal_element = Mock()
        mock_terminal_element.text = "$ ls\nfile1.txt file2.txt"
        
        # Mock the find_elements to return terminal elements for first selector
        mock_browser.find_elements.side_effect = [
            [mock_terminal_element],  # First selector finds terminal content
            []  # Other selectors find nothing
        ]
        
        # Test scraping with terminal elements
        result = scrape_warp_conversation(mock_browser, "https://app.warp.dev/session/terminal", timeout=5)
        
        # Should find and process terminal content
        self.assertIsNotNone(result)
        self.assertIn("ls", result)
        self.assertIn("file1.txt", result)
    
    def test_warp_ui_element_removal(self):
        """Test removal of various Warp UI elements."""
        content_with_ui = """
        Warp Terminal
        Settings
        New terminal
        Help
        
        $ cd /home
        $ whoami
        testuser
        
        Warp AI
        Command palette
        Theme
        Font size
        """
        
        cleaned = clean_warp_conversation_content(content_with_ui)
        
        # UI elements should be removed
        ui_elements = ["Warp Terminal", "Settings", "New terminal", "Help", 
                      "Warp AI", "Command palette", "Theme", "Font size"]
        
        for ui_element in ui_elements:
            self.assertNotIn(ui_element, cleaned)
        
        # Terminal content should be preserved
        self.assertIn("$ cd /home", cleaned)
        self.assertIn("$ whoami", cleaned)
        self.assertIn("testuser", cleaned)

class TestWarpIntegration(unittest.TestCase):
    """Integration tests for Warp functionality."""
    
    def test_warp_url_formats(self):
        """Test various Warp URL formats are supported."""
        url_formats = [
            "https://app.warp.dev/session/simple-id",
            "https://app.warp.dev/session/complex-id-with-dashes?pwd=password",
            "https://app.warp.dev/session/12345678-1234-1234-1234-123456789abc",
            "https://app.warp.dev/session/uuid?pwd=another-uuid&param=value"
        ]
        
        for url in url_formats:
            with self.subTest(url=url):
                platform = detect_platform(url)
                self.assertEqual(platform, 'warp')
    
    def test_warp_content_scenarios(self):
        """Test various Warp content scenarios."""
        scenarios = [
            # Command line session
            ("$ echo hello\nhello\n$ date\nMon Jan 15", "echo hello", "date"),
            
            # Programming session
            ("$ python\n>>> print('test')\ntest\n>>> exit()", "python", "print('test')"),
            
            # File operations
            ("$ cat file.txt\nfile contents here\n$ rm file.txt", "cat file.txt", "file contents"),
            
            # Mixed content with UI elements
            ("Warp Terminal\n$ ls\nfile1 file2\nSettings", "ls", "file1 file2")
        ]
        
        for content, expected1, expected2 in scenarios:
            with self.subTest(content=content[:20] + "..."):
                cleaned = clean_warp_conversation_content(content)
                self.assertIn(expected1, cleaned)
                self.assertIn(expected2, cleaned)

def run_tests():
    """Run all Warp implementation tests."""
    print("🧪 Running Warp Implementation Tests...")
    print("=" * 50)
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add test cases
    suite.addTests(loader.loadTestsFromTestCase(TestWarpImplementation))
    suite.addTests(loader.loadTestsFromTestCase(TestWarpIntegration))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "=" * 50)
    print(f"🎯 Tests run: {result.testsRun}")
    print(f"✅ Passed: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"❌ Failed: {len(result.failures)}")
    print(f"💥 Errors: {len(result.errors)}")
    
    if result.failures:
        print("\n❌ FAILURES:")
        for test, traceback in result.failures:
            print(f"- {test}: {traceback.splitlines()[-1]}")
    
    if result.errors:
        print("\n💥 ERRORS:")
        for test, traceback in result.errors:
            print(f"- {test}: {traceback.splitlines()[-1]}")
    
    success_rate = ((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun) * 100
    print(f"\n📊 Success Rate: {success_rate:.1f}%")
    
    return result.wasSuccessful()

if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
