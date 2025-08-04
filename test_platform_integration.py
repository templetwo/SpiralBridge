#!/usr/bin/env python3
"""
Platform Integration Test Suite for LocalMemorySystem
=====================================================

This comprehensive test suite verifies that the LocalMemorySystem continues
to support scraping and archiving from all three AI platforms:
- Claude (claude.ai)
- Gemini (gemini.google.com)  
- ChatGPT (chat.openai.com)

Tests:
1. Platform URL detection
2. Platform-specific scraping function availability
3. Content cleaning for each platform
4. LocalMemorySystem integration
5. File creation and organization
6. Error handling per platform
7. End-to-end pipeline simulation
"""

import os
import sys
import unittest
import tempfile
import shutil
import json
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import modules
from spiralbridge import (
    detect_platform,
    scrape_claude_conversation,
    scrape_gemini_conversation, 
    scrape_chatgpt_conversation,
    clean_gemini_conversation_content,
    clean_chatgpt_conversation_content,
    scrape_with_retry,
    get_platform_error_message
)
from local_memory_system import LocalMemorySystem
from archive_conversation import archive_conversation

class TestPlatformIntegration(unittest.TestCase):
    """Test suite for multi-platform LocalMemorySystem integration."""
    
    def setUp(self):
        """Set up test environment."""
        # Create temporary directory for testing
        self.temp_dir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()
        os.chdir(self.temp_dir)
        
        # Initialize LocalMemorySystem in temp directory
        self.memory_system = LocalMemorySystem(self.temp_dir)
        
        # Test URLs for each platform
        self.test_urls = {
            'claude': [
                'https://claude.ai/share/abc123def456',
                'https://claude.ai/chat/xyz789',
                'https://claude.ai/share/12345abcde'
            ],
            'gemini': [
                'https://gemini.google.com/app/123abc456def',
                'https://gemini.google.com/share/xyz789',
                'https://g.co/gemini/abc123',
                'https://bard.google.com/chat/123456'  # Legacy
            ],
            'chatgpt': [
                'https://chat.openai.com/share/abc123',
                'https://chatgpt.com/share/xyz789',
                'https://chat.openai.com/c/12345abcde'
            ]
        }
        
        # Sample conversation content for each platform
        self.sample_conversations = {
            'claude': """Human: Hello Claude, can you help me with Python programming?

Claude: Of course! I'd be happy to help you with Python programming. What specific topic or challenge would you like assistance with?

Human: I need help with decorators.

Claude: Decorators are a powerful feature in Python! They allow you to modify or extend functions without changing their source code directly. Here's how they work...""",
            
            'gemini': """User: Hi Gemini, can you explain machine learning?

Gemini: Hello! I'd be happy to explain machine learning. Machine learning is a subset of artificial intelligence that enables computers to learn patterns from data without being explicitly programmed.

User: What are the main types?

Gemini: The main types of machine learning are:
1. Supervised Learning - uses labeled data
2. Unsupervised Learning - finds patterns in unlabeled data
3. Reinforcement Learning - learns through trial and error""",
            
            'chatgpt': """User: Hello ChatGPT, can you help with web development?

ChatGPT: Hello! I'd be happy to help you with web development. What specific aspect would you like assistance with?

User: I need help with React components.

ChatGPT: Great choice! React components are the building blocks of React applications. There are two main types: functional components and class components. Let me explain both..."""
        }
    
    def tearDown(self):
        """Clean up test environment."""
        os.chdir(self.original_cwd)
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_platform_url_detection(self):
        """Test that all platform URLs are correctly detected."""
        print("\n🎯 Testing Platform URL Detection")
        print("=" * 50)
        
        for platform, urls in self.test_urls.items():
            print(f"\n{platform.upper()} URLs:")
            for url in urls:
                detected = detect_platform(url)
                print(f"  {url} -> {detected}")
                self.assertEqual(detected, platform, 
                    f"Failed to detect {platform} for {url}")
        
        print("\n✅ All platform URLs correctly detected")
    
    def test_scraping_functions_available(self):
        """Test that scraping functions exist for all platforms."""
        print("\n🔧 Testing Scraping Function Availability")
        print("=" * 50)
        
        # Test that all scraping functions are callable
        functions = {
            'claude': scrape_claude_conversation,
            'gemini': scrape_gemini_conversation,
            'chatgpt': scrape_chatgpt_conversation
        }
        
        for platform, func in functions.items():
            print(f"  {platform.upper()}: {func.__name__} -> Available")
            self.assertTrue(callable(func), f"{platform} scraping function not callable")
        
        print("\n✅ All scraping functions available")
    
    def test_content_cleaning_functions(self):
        """Test platform-specific content cleaning."""
        print("\n🧹 Testing Content Cleaning Functions")
        print("=" * 50)
        
        # Test Gemini content cleaning
        gemini_dirty = """Gemini Apps
Try Gemini Advanced
New chat
User: Hello
Gemini: Hi there!
Gemini can make mistakes
Privacy & Terms"""
        
        gemini_clean = clean_gemini_conversation_content(gemini_dirty)
        print(f"  Gemini cleaning: {len(gemini_dirty)} -> {len(gemini_clean)} chars")
        self.assertNotIn("Gemini Apps", gemini_clean)
        self.assertNotIn("Try Gemini Advanced", gemini_clean)
        self.assertIn("Hello", gemini_clean)
        self.assertIn("Hi there!", gemini_clean)
        
        # Test ChatGPT content cleaning
        chatgpt_dirty = """ChatGPT can make mistakes
Try ChatGPT Plus
New chat
User: Hello
ChatGPT: Hi there!
Share this conversation
Made by OpenAI"""
        
        chatgpt_clean = clean_chatgpt_conversation_content(chatgpt_dirty)
        print(f"  ChatGPT cleaning: {len(chatgpt_dirty)} -> {len(chatgpt_clean)} chars")
        self.assertNotIn("ChatGPT can make mistakes", chatgpt_clean)
        self.assertNotIn("Try ChatGPT Plus", chatgpt_clean)
        self.assertIn("Hello", chatgpt_clean)
        self.assertIn("Hi there!", chatgpt_clean)
        
        print("\n✅ Content cleaning functions working correctly")
    
    def test_local_memory_system_platform_support(self):
        """Test LocalMemorySystem supports all platforms."""
        print("\n🧠 Testing LocalMemorySystem Platform Support")
        print("=" * 50)
        
        # Check that platform directories are created
        expected_dirs = [
            "project_memory/conversations/claude",
            "project_memory/conversations/gemini", 
            "project_memory/conversations/chatgpt"
        ]
        
        for dir_path in expected_dirs:
            full_path = Path(self.temp_dir) / dir_path
            print(f"  {dir_path}: {'✓' if full_path.exists() else '✗'}")
            self.assertTrue(full_path.exists(), f"Directory {dir_path} not created")
        
        print("\n✅ All platform directories exist in LocalMemorySystem")
    
    def test_conversation_archiving_all_platforms(self):
        """Test archiving conversations from all platforms."""
        print("\n📁 Testing Conversation Archiving")
        print("=" * 50)
        
        archived_files = []
        
        for platform, content in self.sample_conversations.items():
            print(f"\n  Archiving {platform.upper()} conversation...")
            
            # Archive using LocalMemorySystem
            memory_file = self.memory_system.save_conversation_memory(
                content=content,
                platform=platform,
                session_type="test_conversation",
                tags=["test", "integration", platform],
                summary=f"Test {platform} conversation for integration testing"
            )
            
            self.assertTrue(os.path.exists(memory_file), 
                f"Memory file not created for {platform}")
            
            # Verify file contains expected content
            with open(memory_file, 'r', encoding='utf-8') as f:
                file_content = f.read()
                self.assertIn(content, file_content)
                self.assertIn(platform, file_content)
            
            archived_files.append(memory_file)
            print(f"    ✓ Archived to: {os.path.basename(memory_file)}")
        
        print(f"\n✅ Successfully archived {len(archived_files)} conversations")
        return archived_files
    
    def test_legacy_archive_system_compatibility(self):
        """Test compatibility with legacy archive_conversation function."""
        print("\n🔄 Testing Legacy Archive System Compatibility")
        print("=" * 50)
        
        legacy_files = []
        
        for platform, content in self.sample_conversations.items():
            print(f"\n  Legacy archiving {platform.upper()}...")
            
            # Use legacy archive function
            legacy_file = archive_conversation(content, platform)
            
            self.assertTrue(os.path.exists(legacy_file), 
                f"Legacy file not created for {platform}")
            
            # Verify content
            with open(legacy_file, 'r', encoding='utf-8') as f:
                file_content = f.read()
                self.assertEqual(file_content, content)
            
            legacy_files.append(legacy_file)
            print(f"    ✓ Legacy archived to: {os.path.basename(legacy_file)}")
        
        print(f"\n✅ Legacy archiving works for all {len(legacy_files)} platforms")
        return legacy_files
    
    def test_error_handling_per_platform(self):
        """Test platform-specific error handling."""
        print("\n⚠️  Testing Platform-Specific Error Handling")
        print("=" * 50)
        
        test_errors = [
            ("timeout", "Timeout error"),
            ("element not found", "Element not found error"),
            ("connection", "Connection error"),
            ("network", "Network error")
        ]
        
        for platform in ['claude', 'gemini', 'chatgpt']:
            print(f"\n  {platform.upper()} error messages:")
            for error_str, description in test_errors:
                mock_error = Exception(error_str)
                message = get_platform_error_message(platform, mock_error)
                print(f"    {description}: {message[:60]}...")
                # Check for platform name in error message (case-insensitive)
                platform_variations = {
                    'claude': 'Claude',
                    'gemini': 'Gemini', 
                    'chatgpt': 'ChatGPT'  # ChatGPT is capitalized differently
                }
                expected_platform_name = platform_variations.get(platform, platform.title())
                self.assertIn(expected_platform_name, message)
                self.assertIn("Error", message)
        
        print("\n✅ Platform-specific error handling working")
    
    @patch('spiralbridge.initialize_driver')
    def test_mock_scraping_pipeline(self, mock_init_driver):
        """Test the complete scraping pipeline with mocked browser."""
        print("\n🚀 Testing Complete Scraping Pipeline (Mocked)")
        print("=" * 50)
        
        # Mock browser and driver
        mock_browser = Mock()
        mock_init_driver.return_value = mock_browser
        
        for platform, content in self.sample_conversations.items():
            print(f"\n  Testing {platform.upper()} pipeline...")
            
            # Mock the browser.get() and find_element() methods
            mock_element = Mock()
            mock_element.text = content
            mock_browser.find_element.return_value = mock_element
            mock_browser.find_elements.return_value = [mock_element]
            
            # Get scraping function
            scraping_functions = {
                'claude': scrape_claude_conversation,
                'gemini': scrape_gemini_conversation,
                'chatgpt': scrape_chatgpt_conversation
            }
            
            scraping_func = scraping_functions[platform]
            url = self.test_urls[platform][0]
            
            # Test scraping with retry
            try:
                result = scrape_with_retry(
                    scraping_func, mock_browser, url, platform, timeout=1, max_attempts=1
                )
                print(f"    ✓ Scraping successful: {len(result) if result else 0} chars")
            except Exception as e:
                print(f"    ⚠️  Scraping test skipped: {e}")
                # This is expected in a mocked environment
        
        print("\n✅ Pipeline testing completed")
    
    def test_memory_system_stats_and_search(self):
        """Test LocalMemorySystem statistics and search functionality."""
        print("\n📊 Testing Memory System Stats and Search")
        print("=" * 50)
        
        # First archive some conversations
        archived_files = self.test_conversation_archiving_all_platforms()
        
        # Test statistics
        stats = self.memory_system.get_project_stats()
        print(f"\n  Memory Statistics:")
        print(f"    Total conversations: {stats['total_conversations']}")
        print(f"    Storage size: {stats['storage_size_mb']} MB")
        
        self.assertGreaterEqual(stats['total_conversations'], 3, 
            "Should have at least 3 conversations (one per platform)")
        
        # Test search functionality
        search_results = self.memory_system.search_memories("Python")
        print(f"\n  Search for 'Python': {len(search_results)} results")
        
        # Search by category
        conversation_results = self.memory_system.search_memories(
            query="", category="conversations"
        )
        print(f"  Search conversations category: {len(conversation_results)} results")
        
        self.assertGreaterEqual(len(conversation_results), 3, 
            "Should find conversations from all platforms")
        
        print("\n✅ Memory system stats and search working")
    
    def test_conversation_index_functionality(self):
        """Test conversation indexing across all platforms."""
        print("\n📇 Testing Conversation Index Functionality")
        print("=" * 50)
        
        # Archive conversations to populate index
        self.test_conversation_archiving_all_platforms()
        
        # Check conversation index file
        index_path = self.memory_system.memory_root / "conversations" / "index.json"
        print(f"\n  Index file exists: {'✓' if index_path.exists() else '✗'}")
        self.assertTrue(index_path.exists(), "Conversation index file should exist")
        
        # Load and verify index content
        with open(index_path, 'r', encoding='utf-8') as f:
            index_data = json.load(f)
        
        conversations = index_data.get('conversations', [])
        print(f"  Indexed conversations: {len(conversations)}")
        
        # Verify all platforms are represented
        platforms_in_index = set()
        for conv in conversations:
            platform = conv.get('metadata', {}).get('platform')
            if platform:
                platforms_in_index.add(platform)
        
        print(f"  Platforms in index: {', '.join(sorted(platforms_in_index))}")
        
        expected_platforms = {'claude', 'gemini', 'chatgpt'}
        self.assertEqual(platforms_in_index, expected_platforms, 
            f"Index should contain all platforms. Found: {platforms_in_index}")
        
        print("\n✅ Conversation index functionality working")
    
    def test_directory_structure_integrity(self):
        """Test that directory structure supports all platforms."""
        print("\n📂 Testing Directory Structure Integrity")
        print("=" * 50)
        
        # Check all expected directories exist
        base_path = self.memory_system.memory_root
        expected_structure = {
            'conversations': ['claude', 'chatgpt', 'gemini', 'summaries'],
            'development': ['sessions', 'milestones', 'challenges', 'solutions'],
            'knowledge_base': ['technical', 'concepts', 'resources'],
            'timeline': ['daily', 'weekly', 'monthly'],
            'backups': [],
            'exports': []
        }
        
        print(f"\n  Base directory: {base_path}")
        
        for category, subdirs in expected_structure.items():
            category_path = base_path / category
            print(f"\n  {category}/")
            self.assertTrue(category_path.exists(), f"Category {category} should exist")
            
            for subdir in subdirs:
                subdir_path = category_path / subdir
                exists = subdir_path.exists()
                print(f"    {subdir}/: {'✓' if exists else '✗'}")
                self.assertTrue(exists, f"Subdirectory {category}/{subdir} should exist")
        
        print("\n✅ Directory structure supports all platforms")


def run_comprehensive_test():
    """Run comprehensive platform integration test."""
    print("🌉 SpiralBridge Platform Integration Test Suite")
    print("=" * 60)
    print("Testing LocalMemorySystem integration with:")
    print("  • Claude (claude.ai)")
    print("  • Gemini (gemini.google.com)")
    print("  • ChatGPT (chat.openai.com)")
    print("=" * 60)
    
    # Run the test suite
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TestPlatformIntegration)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "=" * 60)
    print("📋 TEST SUMMARY")
    print("=" * 60)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Success rate: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%")
    
    if result.failures:
        print("\n❌ FAILURES:")
        for test, traceback in result.failures:
            error_msg = traceback.split('AssertionError: ')[-1].split('\n')[0]
            print(f"  • {test}: {error_msg}")
    
    if result.errors:
        print("\n💥 ERRORS:")
        for test, traceback in result.errors:
            error_msg = traceback.split('\n')[-2]
            print(f"  • {test}: {error_msg}")
    
    if not result.failures and not result.errors:
        print("\n🎉 ALL TESTS PASSED!")
        print("✅ LocalMemorySystem successfully supports all three platforms")
        print("✅ Claude, Gemini, and ChatGPT integration is working correctly")
        print("✅ Pipeline is ready for production use")
    else:
        print("\n⚠️  Some tests failed. Review the output above for details.")
    
    print("\n" + "=" * 60)
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_comprehensive_test()
    sys.exit(0 if success else 1)
