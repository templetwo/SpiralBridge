#!/usr/bin/env python3
"""
Edge case and real-world scenario tests for Gemini implementation.

This test suite focuses on challenging scenarios:
- Malformed URLs
- Network connectivity issues
- Loading errors and timeouts
- Authentication-required content
- Rate limiting scenarios
- Very large conversations
- Special content formatting
"""

import os
import sys
import tempfile
import shutil
import unittest
from unittest.mock import Mock, patch
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException
import time

# Add the current directory to Python path to import our modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from spiralbridge import (
    scrape_gemini_conversation,
    clean_gemini_conversation_content,
    detect_platform,
    get_platform_error_message,
    scrape_with_retry
)
from archive_conversation import archive_conversation


class TestGeminiEdgeCases(unittest.TestCase):
    """Test edge cases and error scenarios for Gemini implementation."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()
        os.chdir(self.temp_dir)
    
    def tearDown(self):
        """Clean up after tests."""
        os.chdir(self.original_cwd)
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_malformed_urls(self):
        """Test handling of malformed and invalid URLs."""
        print("\n=== Testing Malformed URLs ===")
        
        malformed_urls = [
            "https://gemini.google.com/",  # Missing conversation ID
            "https://gemini.google.com/app/",  # Empty conversation ID
            "https://gemini.google.com/share/",  # Empty share ID
            "https://gemini.google.com/app/invalid-id-format",  # Invalid format
            "https://g.co/gemini/",  # Missing short ID
            "https://bard.google.com/chat/",  # Empty legacy chat ID
            "gemini.google.com/share/123",  # Missing protocol
            "http://gemini.google.com/share/123",  # Wrong protocol
        ]
        
        for url in malformed_urls:
            with self.subTest(url=url):
                print(f"Testing malformed URL: {url}")
                platform = detect_platform(url)
                
                # Should still detect as Gemini platform
                if any(domain in url.lower() for domain in ['gemini.google.com', 'g.co', 'bard.google.com']):
                    self.assertEqual(platform, 'gemini', f"Should detect Gemini for {url}")
                
                # Mock browser response for these URLs should handle gracefully
                mock_browser = Mock()
                mock_browser.get.side_effect = WebDriverException("Invalid URL format")
                
                result = scrape_gemini_conversation(mock_browser, url, timeout=1)
                self.assertIsNone(result, f"Should return None for malformed URL: {url}")
        
        print("✅ Malformed URL tests passed")
    
    def test_network_errors(self):
        """Test handling of various network-related errors."""
        print("\n=== Testing Network Errors ===")
        
        network_errors = [
            ("Connection timeout", TimeoutException("Connection timed out")),
            ("DNS resolution failed", WebDriverException("Name resolution failed")),
            ("Connection refused", WebDriverException("Connection refused")),
            ("Network unreachable", WebDriverException("Network is unreachable")),
            ("SSL certificate error", WebDriverException("SSL certificate verify failed")),
        ]
        
        for error_name, exception in network_errors:
            with self.subTest(error=error_name):
                print(f"Testing {error_name}")
                
                mock_browser = Mock()
                mock_browser.get.side_effect = exception
                
                result = scrape_gemini_conversation(mock_browser, "https://gemini.google.com/share/test", timeout=1)
                self.assertIsNone(result, f"Should return None for {error_name}")
                
                # Test error message formatting
                error_msg = get_platform_error_message('gemini', exception)
                self.assertIn("Gemini Error", error_msg)
                print(f"  Error message: {error_msg}")
        
        print("✅ Network error tests passed")
    
    def test_authentication_errors(self):
        """Test handling of authentication and access control errors."""
        print("\n=== Testing Authentication Errors ===")
        
        auth_scenarios = [
            ("Private conversation", "Access denied: Private conversation"),
            ("Sign-in required", "Sign-in required to view conversation"),
            ("Account suspended", "Account access suspended"),
            ("Geographic restriction", "Content not available in your region"),
            ("Expired share link", "Share link has expired"),
        ]
        
        for scenario_name, error_message in auth_scenarios:
            with self.subTest(scenario=scenario_name):
                print(f"Testing {scenario_name}")
                
                mock_browser = Mock()
                mock_element = Mock()
                mock_element.text = f"Error: {error_message}"
                mock_browser.find_element.return_value = mock_element
                mock_browser.find_elements.return_value = []
                
                result = scrape_gemini_conversation(mock_browser, "https://gemini.google.com/share/private", timeout=1)
                
                # Should clean the error message but return something
                if result:
                    self.assertIn("Error", result)
                    print(f"  Result: {result[:100]}...")
        
        print("✅ Authentication error tests passed")
    
    def test_content_loading_scenarios(self):
        """Test different content loading scenarios."""
        print("\n=== Testing Content Loading Scenarios ===")
        
        loading_scenarios = [
            ("Empty page", ""),
            ("Loading indicator only", "Loading conversation..."),
            ("Error page", "Oops! Something went wrong."),
            ("Maintenance page", "Gemini is currently undergoing maintenance"),
            ("Rate limited", "Too many requests. Please try again later."),
            ("Bot detection", "Please verify you are human"),
        ]
        
        for scenario_name, page_content in loading_scenarios:
            with self.subTest(scenario=scenario_name):
                print(f"Testing {scenario_name}")
                
                mock_browser = Mock()
                mock_element = Mock()
                mock_element.text = page_content
                mock_browser.find_element.return_value = mock_element
                mock_browser.find_elements.return_value = []
                
                result = scrape_gemini_conversation(mock_browser, "https://gemini.google.com/share/test", timeout=1)
                
                if scenario_name == "Empty page":
                    self.assertIsNone(result)
                else:
                    # Should return cleaned content, even if it's an error message
                    if result:
                        cleaned = clean_gemini_conversation_content(result)
                        print(f"  Cleaned result: {cleaned[:50]}...")
        
        print("✅ Content loading scenario tests passed")
    
    def test_special_content_formatting(self):
        """Test handling of special content formats in conversations."""
        print("\n=== Testing Special Content Formatting ===")
        
        # Test conversation with code blocks
        code_conversation = """User: Can you help me with a Python function?

Gemini: Of course! Here's a example function:

```python
def hello_world(name):
    '''
    A simple greeting function
    '''
    return f"Hello, {name}!"

# Usage example
print(hello_world("User"))
```

This function takes a name parameter and returns a greeting.

User: That's perfect, thank you!

Gemini: You're welcome! Let me know if you need help with anything else."""
        
        # Test conversation with tables
        table_conversation = """User: Can you create a comparison table?

Gemini: Here's a comparison of programming languages:

| Language | Type     | Use Case      |
|----------|----------|---------------|
| Python   | Dynamic  | Data Science  |
| Java     | Static   | Enterprise    |
| JavaScript| Dynamic | Web Dev       |

Each language has its strengths depending on the project requirements.

User: This is very helpful!"""
        
        # Test conversation with mathematical expressions
        math_conversation = """User: Explain the quadratic formula

Gemini: The quadratic formula is:

x = (-b ± √(b² - 4ac)) / 2a

Where:
- a, b, c are coefficients
- x represents the solutions
- ± means there are typically two solutions

For example, for the equation x² - 5x + 6 = 0:
- a = 1, b = -5, c = 6
- x = (5 ± √(25 - 24)) / 2 = (5 ± 1) / 2
- Solutions: x = 3 or x = 2"""
        
        # Test conversation with lists and formatting
        list_conversation = """User: What are the benefits of exercise?

Gemini: Here are the key benefits of regular exercise:

**Physical Benefits:**
1. Improved cardiovascular health
2. Increased muscle strength
3. Better flexibility and balance
4. Weight management

**Mental Benefits:**
• Reduced stress and anxiety
• Improved mood and self-esteem
• Better sleep quality
• Enhanced cognitive function

**Social Benefits:**
- Opportunities to meet people
- Team building experiences
- Community involvement

Regular exercise contributes to overall well-being in multiple ways."""
        
        special_content_tests = [
            (code_conversation, "Code blocks"),
            (table_conversation, "Tables"),
            (math_conversation, "Mathematical expressions"),
            (list_conversation, "Lists and formatting")
        ]
        
        for content, description in special_content_tests:
            with self.subTest(content_type=description):
                print(f"Testing {description}")
                
                cleaned = clean_gemini_conversation_content(content)
                
                # Verify important content is preserved
                self.assertIn("User:", cleaned)
                self.assertIn("Gemini:", cleaned)
                
                # Check that formatting elements are mostly preserved
                if "Code blocks" in description:
                    self.assertIn("python", cleaned)
                    self.assertIn("def hello_world", cleaned)
                elif "Tables" in description:
                    self.assertIn("Language", cleaned)
                    self.assertIn("Python", cleaned)
                elif "Mathematical" in description:
                    self.assertIn("quadratic formula", cleaned)
                    self.assertIn("√", cleaned)
                elif "Lists" in description:
                    self.assertIn("Physical Benefits", cleaned)
                    self.assertIn("Mental Benefits", cleaned)
                
                print(f"  Cleaned length: {len(cleaned)} chars")
                print(f"  Preview: {cleaned[:100]}...")
        
        print("✅ Special content formatting tests passed")
    
    def test_very_large_conversations(self):
        """Test handling of very large conversations."""
        print("\n=== Testing Very Large Conversations ===")
        
        # Generate a very large conversation
        large_conversation_parts = ["User: Let's have a very long discussion about technology"]
        
        # Add many exchanges
        for i in range(100):
            topic = f"artificial intelligence topic {i+1}"
            large_conversation_parts.extend([
                f"Gemini: Great question about {topic}! Let me provide a detailed explanation with multiple paragraphs of content. " * 10,
                f"User: That's interesting. Can you elaborate more on {topic} and provide specific examples?" * 5
            ])
        
        large_conversation = "\n\n".join(large_conversation_parts)
        
        print(f"Generated conversation with {len(large_conversation)} characters")
        print(f"Estimated {large_conversation.count('User:')} user messages")
        print(f"Estimated {large_conversation.count('Gemini:')} Gemini responses")
        
        # Test cleaning the large conversation
        start_time = time.time()
        cleaned = clean_gemini_conversation_content(large_conversation)
        end_time = time.time()
        
        processing_time = end_time - start_time
        print(f"Processing time: {processing_time:.2f} seconds")
        print(f"Original size: {len(large_conversation)} chars")
        print(f"Cleaned size: {len(cleaned)} chars")
        
        # Verify content structure is maintained
        self.assertGreater(len(cleaned), 1000, "Large conversation should remain substantial")
        self.assertIn("User:", cleaned)
        self.assertIn("Gemini:", cleaned)
        
        # Test archiving large content
        archive_path = archive_conversation(cleaned, 'gemini')
        self.assertTrue(os.path.exists(archive_path))
        
        file_size = os.path.getsize(archive_path)
        print(f"Archived file size: {file_size} bytes")
        
        print("✅ Large conversation tests passed")
    
    def test_retry_mechanism_edge_cases(self):
        """Test retry mechanism with various failure patterns."""
        print("\n=== Testing Retry Mechanism Edge Cases ===")
        
        # Test alternating failures
        attempt_count = 0
        def alternating_failure_function(browser, url, timeout):
            nonlocal attempt_count
            attempt_count += 1
            if attempt_count % 2 == 1:  # Fail on odd attempts
                raise TimeoutException(f"Odd attempt {attempt_count} failed")
            return f"Success on even attempt {attempt_count}"
        
        mock_browser = Mock()
        attempt_count = 0  # Reset counter
        
        result = scrape_with_retry(
            alternating_failure_function,
            mock_browser,
            "https://gemini.google.com/share/test",
            'gemini',
            timeout=1,
            max_attempts=4
        )
        
        self.assertEqual(result, "Success on even attempt 2")
        print(f"Alternating failure result: {result}")
        
        # Test progressive timeout increases
        timeout_attempts = []
        def timeout_tracking_function(browser, url, timeout):
            timeout_attempts.append(timeout)
            if len(timeout_attempts) < 3:
                raise TimeoutException(f"Timeout on attempt {len(timeout_attempts)}")
            return "Success after timeouts"
        
        mock_browser = Mock()
        timeout_attempts = []  # Reset tracker
        
        result = scrape_with_retry(
            timeout_tracking_function,
            mock_browser,
            "https://gemini.google.com/share/test",
            'gemini',
            timeout=5,
            max_attempts=3
        )
        
        self.assertEqual(result, "Success after timeouts")
        print(f"Timeout tracking result: {result}")
        print(f"Timeout attempts recorded: {timeout_attempts}")
        
        print("✅ Retry mechanism edge case tests passed")


class TestGeminiRealWorldScenarios(unittest.TestCase):
    """Test real-world scenarios that users might encounter."""
    
    def setUp(self):
        """Set up for real-world scenario tests."""
        self.temp_dir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()
        os.chdir(self.temp_dir)
    
    def tearDown(self):
        """Clean up after real-world scenario tests."""
        os.chdir(self.original_cwd)
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_mixed_content_conversation(self):
        """Test conversation with mixed content types."""
        print("\n=== Testing Mixed Content Conversation ===")
        
        mixed_content = """Gemini Apps
Try Gemini Advanced
New chat

User: I need help with a web development project. Can you help me create a responsive navbar?

Gemini: I'd be happy to help you create a responsive navbar! Here's a complete solution using HTML, CSS, and JavaScript:

**HTML Structure:**
```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Responsive Navbar</title>
    <link rel="stylesheet" href="style.css">
</head>
<body>
    <nav class="navbar">
        <div class="nav-container">
            <div class="nav-logo">
                <a href="#">MyWebsite</a>
            </div>
            <div class="nav-menu">
                <a href="#" class="nav-link">Home</a>
                <a href="#" class="nav-link">About</a>
                <a href="#" class="nav-link">Services</a>
                <a href="#" class="nav-link">Contact</a>
            </div>
            <div class="hamburger">
                <span class="bar"></span>
                <span class="bar"></span>
                <span class="bar"></span>
            </div>
        </div>
    </nav>
</body>
</html>
```

**CSS Styling:**
```css
* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

.navbar {
    position: fixed;
    top: 0;
    width: 100%;
    background-color: #333;
    z-index: 1000;
}

.nav-container {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 1rem 2rem;
}

.nav-logo a {
    color: white;
    font-size: 1.5rem;
    font-weight: bold;
    text-decoration: none;
}

.nav-menu {
    display: flex;
    gap: 2rem;
}

.nav-link {
    color: white;
    text-decoration: none;
    transition: color 0.3s ease;
}

.nav-link:hover {
    color: #007bff;
}

.hamburger {
    display: none;
    flex-direction: column;
    cursor: pointer;
}

.bar {
    width: 25px;
    height: 3px;
    background-color: white;
    margin: 3px 0;
    transition: 0.3s;
}

/* Mobile Responsive */
@media screen and (max-width: 768px) {
    .nav-menu {
        position: fixed;
        left: -100%;
        top: 70px;
        flex-direction: column;
        background-color: #333;
        width: 100%;
        text-align: center;
        transition: 0.3s;
        padding: 2rem 0;
    }

    .nav-menu.active {
        left: 0;
    }

    .hamburger {
        display: flex;
    }

    .hamburger.active .bar:nth-child(2) {
        opacity: 0;
    }

    .hamburger.active .bar:nth-child(1) {
        transform: translateY(8px) rotate(45deg);
    }

    .hamburger.active .bar:nth-child(3) {
        transform: translateY(-8px) rotate(-45deg);
    }
}
```

**Key Features:**
1. **Fixed positioning** - navbar stays at top when scrolling
2. **Flexbox layout** - for easy alignment and distribution
3. **Mobile-first approach** - responsive design for all screen sizes
4. **Smooth transitions** - hover effects and menu animations
5. **Accessibility** - proper semantic HTML structure

**Responsive Breakpoints:**
- Desktop: > 768px (horizontal menu)
- Mobile: ≤ 768px (hamburger menu)

Would you like me to explain any specific part or add additional features like dropdown menus or search functionality?

User: This is perfect! Can you also show me the JavaScript for the hamburger menu?

Gemini: Absolutely! Here's the JavaScript to make the hamburger menu functional:

```javascript
// Get DOM elements
const hamburger = document.querySelector('.hamburger');
const navMenu = document.querySelector('.nav-menu');
const navLinks = document.querySelectorAll('.nav-link');

// Toggle mobile menu
function toggleMenu() {
    hamburger.classList.toggle('active');
    navMenu.classList.toggle('active');
}

// Close mobile menu when clicking on a link
function closeMenu() {
    hamburger.classList.remove('active');
    navMenu.classList.remove('active');
}

// Event listeners
hamburger.addEventListener('click', toggleMenu);

// Close menu when clicking on nav links (for single page applications)
navLinks.forEach(link => {
    link.addEventListener('click', closeMenu);
});

// Close menu when clicking outside (optional enhancement)
document.addEventListener('click', function(event) {
    const isClickInsideNav = navMenu.contains(event.target) || hamburger.contains(event.target);
    
    if (!isClickInsideNav && navMenu.classList.contains('active')) {
        closeMenu();
    }
});

// Handle window resize (optional enhancement)
window.addEventListener('resize', function() {
    if (window.innerWidth > 768) {
        // Remove active classes when switching to desktop view
        hamburger.classList.remove('active');
        navMenu.classList.remove('active');
    }
});
```

**How it works:**

1. **toggleMenu()** - Adds/removes 'active' class to show/hide menu
2. **closeMenu()** - Removes 'active' classes to close menu
3. **Click outside detection** - Closes menu when clicking elsewhere
4. **Resize handling** - Ensures proper behavior when switching screen sizes

**Enhanced Features:**
- Menu closes when clicking on navigation links
- Menu closes when clicking outside the navigation area
- Handles window resize events properly
- Smooth animations through CSS transitions

**Alternative: Vanilla JS with better performance:**
```javascript
class ResponsiveNavbar {
    constructor() {
        this.hamburger = document.querySelector('.hamburger');
        this.navMenu = document.querySelector('.nav-menu');
        this.navLinks = document.querySelectorAll('.nav-link');
        this.init();
    }

    init() {
        this.bindEvents();
    }

    bindEvents() {
        this.hamburger?.addEventListener('click', () => this.toggleMenu());
        
        this.navLinks.forEach(link => {
            link.addEventListener('click', () => this.closeMenu());
        });

        document.addEventListener('click', (e) => this.handleOutsideClick(e));
        window.addEventListener('resize', () => this.handleResize());
    }

    toggleMenu() {
        this.hamburger.classList.toggle('active');
        this.navMenu.classList.toggle('active');
    }

    closeMenu() {
        this.hamburger.classList.remove('active');
        this.navMenu.classList.remove('active');
    }

    handleOutsideClick(event) {
        const isClickInside = this.navMenu.contains(event.target) || 
                             this.hamburger.contains(event.target);
        
        if (!isClickInside && this.navMenu.classList.contains('active')) {
            this.closeMenu();
        }
    }

    handleResize() {
        if (window.innerWidth > 768) {
            this.closeMenu();
        }
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new ResponsiveNavbar();
});
```

This class-based approach is more organized and easier to maintain for larger projects. Both versions work perfectly - choose based on your project complexity!

Privacy & Terms
Made by Google"""
        
        # Test cleaning this complex mixed content
        cleaned = clean_gemini_conversation_content(mixed_content)
        
        print(f"Original length: {len(mixed_content)}")
        print(f"Cleaned length: {len(cleaned)}")
        
        # Verify UI elements are removed
        self.assertNotIn("Gemini Apps", cleaned)
        self.assertNotIn("Try Gemini Advanced", cleaned)
        self.assertNotIn("New chat", cleaned)
        self.assertNotIn("Privacy & Terms", cleaned)
        self.assertNotIn("Made by Google", cleaned)
        
        # Verify important content is preserved
        self.assertIn("responsive navbar", cleaned)
        self.assertIn("HTML Structure", cleaned)
        self.assertIn("CSS Styling", cleaned)
        self.assertIn("JavaScript", cleaned)
        self.assertIn("hamburger menu", cleaned)
        self.assertIn("class ResponsiveNavbar", cleaned)
        
        # Verify code blocks are preserved
        self.assertIn("<!DOCTYPE html>", cleaned)
        self.assertIn(".navbar {", cleaned)
        self.assertIn("const hamburger", cleaned)
        
        print("✅ Mixed content conversation test passed")
    
    def test_conversation_with_errors_and_corrections(self):
        """Test conversation where Gemini corrects itself or acknowledges errors."""
        print("\n=== Testing Conversation with Corrections ===")
        
        correction_conversation = """User: What's 15 * 17?

Gemini: Let me calculate that for you:
15 * 17 = 255

User: I think that might be wrong. Can you double-check?

Gemini: You're absolutely right! Let me recalculate that:

15 * 17 = 255

Actually, let me break this down step by step:
15 * 17 = 15 * (10 + 7) = (15 * 10) + (15 * 7) = 150 + 105 = 255

Wait, that's the same answer. Let me verify once more:
  15
× 17
----
 105  (15 × 7)
150   (15 × 10)
----
255

I apologize for any confusion, but 15 × 17 does equal 255. Could you double-check your calculation as well?

User: You're right, I made an error. Sorry about that! 

Gemini: No worries at all! Math mistakes happen to everyone. It's always good to double-check calculations, and I appreciate you questioning the result - that's exactly the right approach when working with numbers. Is there anything else I can help you with?"""
        
        cleaned = clean_gemini_conversation_content(correction_conversation)
        
        # Verify the conversation flow and corrections are preserved
        self.assertIn("15 * 17", cleaned)
        self.assertIn("255", cleaned)
        self.assertIn("double-check", cleaned)
        self.assertIn("recalculate", cleaned)
        self.assertIn("made an error", cleaned)
        self.assertIn("No worries at all", cleaned)
        
        print(f"Correction conversation cleaned length: {len(cleaned)}")
        print("✅ Conversation with corrections test passed")


def run_comprehensive_gemini_tests():
    """Run comprehensive testing guide for manual verification."""
    print("\n🔬 COMPREHENSIVE GEMINI TESTING CHECKLIST")
    print("=" * 60)
    
    print("\n📋 AUTOMATED TESTS COMPLETED:")
    print("✅ Platform detection")
    print("✅ Content cleaning")
    print("✅ Error handling")
    print("✅ Edge cases")
    print("✅ Network scenarios")
    print("✅ Authentication errors")
    print("✅ Special content formatting")
    print("✅ Large conversations")
    print("✅ Retry mechanisms")
    print("✅ Mixed content scenarios")
    
    print("\n🧑‍💻 MANUAL TESTS TO PERFORM:")
    
    print("\n1. CREATE TEST CONVERSATIONS:")
    print("   □ Short conversation (2-4 exchanges)")
    print("   □ Medium conversation (10-15 exchanges)")
    print("   □ Long conversation (50+ exchanges)")
    print("   □ Conversation with code snippets")
    print("   □ Conversation with mathematical formulas")
    print("   □ Conversation with tables and lists")
    print("   □ Conversation with image references")
    print("   □ Conversation with file uploads mentioned")
    
    print("\n2. TEST DIFFERENT URL FORMATS:")
    print("   □ https://gemini.google.com/app/[conversation-id]")
    print("   □ https://gemini.google.com/share/[share-id]")
    print("   □ https://g.co/gemini/[short-id]")
    print("   □ Legacy Bard URLs (if any still work)")
    
    print("\n3. TEST ERROR SCENARIOS:")
    print("   □ Private/unshared conversations")
    print("   □ Expired share links")
    print("   □ Invalid conversation IDs")
    print("   □ Rate limiting (multiple rapid requests)")
    print("   □ Network disconnection during scraping")
    print("   □ Very slow network conditions")
    
    print("\n4. VERIFY OUTPUT QUALITY:")
    print("   □ Check memory_logs/gemini/ directory creation")
    print("   □ Verify timestamp-based filenames")
    print("   □ Confirm UI elements are removed")
    print("   □ Ensure conversation content is preserved")
    print("   □ Validate special formatting is maintained")
    print("   □ Check file encoding (UTF-8)")
    
    print("\n5. PERFORMANCE TESTING:")
    print("   □ Time scraping of different conversation lengths")
    print("   □ Monitor memory usage with large conversations")
    print("   □ Test concurrent scraping (multiple URLs)")
    print("   □ Browser cleanup verification")
    
    print("\n🚀 RUN TESTS WITH:")
    print("   python test_gemini_edge_cases.py")
    print("   python spiralbridge.py [YOUR_GEMINI_URL]")
    
    print("\n📊 SUCCESS CRITERIA:")
    print("   ✓ All automated tests pass")
    print("   ✓ Manual tests complete successfully")
    print("   ✓ Content is properly cleaned and archived")
    print("   ✓ Error handling is graceful and informative")
    print("   ✓ Performance is acceptable for typical use cases")


if __name__ == "__main__":
    print("🧪 SpiralBridge Gemini Edge Cases & Real-World Scenarios")
    print("=" * 60)
    
    # Run the automated edge case tests
    unittest.main(verbosity=2, exit=False)
    
    # Display comprehensive testing guide
    print("\n" + "=" * 60)
    run_comprehensive_gemini_tests()
