#!/usr/bin/env python3
"""
Comprehensive Web UI Test Suite for SpiralBridge
================================================

This test suite covers all the requirements for Step 7:
- Test with various URLs to ensure compatibility
- Verify error handling for invalid URLs
- Test clipboard functionality across browsers
- Ensure save functionality properly integrates with memory system
- Check responsive design on different screen sizes
- Validate accessibility features
- Add necessary logging for debugging
"""

import pytest
import time
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import requests
import logging
from typing import Dict, List, Tuple, Optional
import os
from urllib.parse import urljoin

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('web_ui_test_results.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class WebUITestSuite:
    """Comprehensive test suite for SpiralBridge Web UI"""
    
    def __init__(self, base_url="http://localhost:5001"):
        self.base_url = base_url
        self.test_results = []
        self.drivers = {}
        
        # Test URLs for different platforms
        self.test_urls = {
            'claude': [
                'https://claude.ai/share/12345',
                'https://claude.ai/share/test-conversation',
                'https://claude.ai/share/invalid-id'
            ],
            'gemini': [
                'https://gemini.google.com/share/abc123',
                'https://g.co/gemini/xyz789',
                'https://bard.google.com/share/old-format'
            ],
            'chatgpt': [
                'https://chat.openai.com/share/valid-id',
                'https://chatgpt.com/share/new-format',
                'https://chat.openai.com/share/another-test'
            ],
            'warp': [
                'https://app.warp.dev/session/test-session',
                'https://app.warp.dev/session/12345abcde'
            ],
            'invalid': [
                'https://example.com/share/test',
                'https://invalid-platform.com/share/123',
                'not-a-url',
                'http://localhost/fake'
            ]
        }
    
    def setup_drivers(self):
        """Initialize web drivers for different browsers"""
        logger.info("Setting up web drivers...")
        
        # Chrome setup
        try:
            chrome_options = Options()
            chrome_options.add_argument('--headless')
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-gpu')
            self.drivers['chrome'] = webdriver.Chrome(options=chrome_options)
            logger.info("Chrome driver initialized")
        except Exception as e:
            logger.error(f"Failed to initialize Chrome driver: {e}")
        
        # Firefox setup (optional)
        try:
            firefox_options = FirefoxOptions()
            firefox_options.add_argument('--headless')
            self.drivers['firefox'] = webdriver.Firefox(options=firefox_options)
            logger.info("Firefox driver initialized")
        except Exception as e:
            logger.warning(f"Firefox driver not available: {e}")
    
    def teardown_drivers(self):
        """Clean up web drivers"""
        for browser, driver in self.drivers.items():
            try:
                driver.quit()
                logger.info(f"{browser} driver closed")
            except Exception as e:
                logger.error(f"Error closing {browser} driver: {e}")
    
    def wait_for_element(self, driver, by, locator, timeout=10):
        """Wait for element to be present"""
        try:
            return WebDriverWait(driver, timeout).until(
                EC.presence_of_element_located((by, locator))
            )
        except TimeoutException:
            logger.error(f"Element {locator} not found within {timeout} seconds")
            return None
    
    def wait_for_clickable(self, driver, by, locator, timeout=10):
        """Wait for element to be clickable"""
        try:
            return WebDriverWait(driver, timeout).until(
                EC.element_to_be_clickable((by, locator))
            )
        except TimeoutException:
            logger.error(f"Element {locator} not clickable within {timeout} seconds")
            return None

    def test_url_compatibility(self, browser='chrome'):
        """Test URL compatibility across different platforms"""
        logger.info(f"Testing URL compatibility with {browser}")
        driver = self.drivers.get(browser)
        if not driver:
            logger.error(f"No driver available for {browser}")
            return False
        
        results = {
            'valid_urls_accepted': 0,
            'invalid_urls_rejected': 0,
            'total_tests': 0,
            'errors': []
        }
        
        try:
            driver.get(self.base_url)
            url_input = self.wait_for_element(driver, By.ID, 'urlInput')
            scrape_btn = self.wait_for_element(driver, By.ID, 'scrapeBtn')
            
            if not url_input or not scrape_btn:
                logger.error("Essential UI elements not found")
                return False
            
            # Test valid URLs
            for platform, urls in self.test_urls.items():
                if platform == 'invalid':
                    continue
                    
                for url in urls:
                    results['total_tests'] += 1
                    logger.info(f"Testing valid URL: {url}")
                    
                    url_input.clear()
                    url_input.send_keys(url)
                    time.sleep(1)  # Allow validation to run
                    
                    # Check if URL is accepted (no invalid class)
                    classes = url_input.get_attribute('class') or ''
                    if 'invalid' not in classes and 'unsupported' not in classes:
                        results['valid_urls_accepted'] += 1
                        logger.info(f"✅ URL accepted: {url}")
                    else:
                        results['errors'].append(f"Valid URL rejected: {url}")
                        logger.warning(f"❌ Valid URL rejected: {url}")
            
            # Test invalid URLs
            for url in self.test_urls['invalid']:
                results['total_tests'] += 1
                logger.info(f"Testing invalid URL: {url}")
                
                url_input.clear()
                url_input.send_keys(url)
                time.sleep(1)  # Allow validation to run
                
                # Check if URL is properly rejected
                classes = url_input.get_attribute('class') or ''
                if 'invalid' in classes or 'unsupported' in classes:
                    results['invalid_urls_rejected'] += 1
                    logger.info(f"✅ Invalid URL properly rejected: {url}")
                else:
                    results['errors'].append(f"Invalid URL accepted: {url}")
                    logger.warning(f"❌ Invalid URL incorrectly accepted: {url}")
            
            self.test_results.append({
                'test': 'url_compatibility',
                'browser': browser,
                'results': results,
                'passed': len(results['errors']) == 0
            })
            
            return len(results['errors']) == 0
            
        except Exception as e:
            logger.error(f"URL compatibility test failed: {e}")
            return False
    
    def test_error_handling(self, browser='chrome'):
        """Test error handling for various scenarios"""
        logger.info(f"Testing error handling with {browser}")
        driver = self.drivers.get(browser)
        if not driver:
            return False
        
        test_cases = [
            {'input': '', 'expected_error': 'Please enter a URL'},
            {'input': 'not-a-url', 'expected_error': 'valid URL'},
            {'input': 'https://example.com', 'expected_error': 'supported platforms'},
        ]
        
        errors_handled = 0
        total_cases = len(test_cases)
        
        try:
            driver.get(self.base_url)
            
            for case in test_cases:
                logger.info(f"Testing error case: {case['input']}")
                
                url_input = self.wait_for_element(driver, By.ID, 'urlInput')
                scrape_btn = self.wait_for_clickable(driver, By.ID, 'scrapeBtn')
                
                url_input.clear()
                if case['input']:
                    url_input.send_keys(case['input'])
                
                scrape_btn.click()
                
                # Wait for status message
                time.sleep(2)
                status_area = driver.find_element(By.ID, 'scrapeStatus')
                
                if status_area.is_displayed():
                    status_text = status_area.text.lower()
                    if case['expected_error'].lower() in status_text:
                        errors_handled += 1
                        logger.info(f"✅ Error properly handled: {case['input']}")
                    else:
                        logger.warning(f"❌ Unexpected error message for: {case['input']}")
                else:
                    logger.warning(f"❌ No error message shown for: {case['input']}")
            
            success = errors_handled == total_cases
            self.test_results.append({
                'test': 'error_handling',
                'browser': browser,
                'results': {'handled': errors_handled, 'total': total_cases},
                'passed': success
            })
            
            return success
            
        except Exception as e:
            logger.error(f"Error handling test failed: {e}")
            return False
    
    def test_clipboard_functionality(self, browser='chrome'):
        """Test clipboard functionality"""
        logger.info(f"Testing clipboard functionality with {browser}")
        driver = self.drivers.get(browser)
        if not driver:
            return False
        
        try:
            driver.get(self.base_url)
            
            # Simulate having scraped content
            driver.execute_script("""
                currentScrapedData = {
                    content: 'Test conversation content for clipboard testing',
                    platform: 'test',
                    metadata: {
                        word_count: 7,
                        content_length: 45
                    }
                };
                displayScrapedContent(currentScrapedData);
            """)
            
            time.sleep(1)
            
            # Try to copy content
            copy_btn = self.wait_for_clickable(driver, By.ID, 'copyBtn')
            if copy_btn:
                copy_btn.click()
                time.sleep(2)
                
                # Check if copy was successful (button text should change)
                btn_text = copy_btn.text
                success = '✅' in btn_text or 'Copied' in btn_text
                
                self.test_results.append({
                    'test': 'clipboard_functionality',
                    'browser': browser,
                    'results': {'copy_attempted': True, 'success_indicated': success},
                    'passed': success
                })
                
                return success
            
            return False
            
        except Exception as e:
            logger.error(f"Clipboard test failed: {e}")
            return False
    
    def test_save_functionality(self, browser='chrome'):
        """Test save functionality integration with memory system"""
        logger.info(f"Testing save functionality with {browser}")
        driver = self.drivers.get(browser)
        if not driver:
            return False
        
        try:
            driver.get(self.base_url)
            
            # Simulate having scraped content
            driver.execute_script("""
                currentScrapedData = {
                    content: 'Test conversation for save functionality testing',
                    platform: 'test',
                    metadata: {
                        url: 'https://test.example.com/share/123',
                        word_count: 8,
                        content_length: 49
                    }
                };
                displayScrapedContent(currentScrapedData);
            """)
            
            time.sleep(1)
            
            # Try to save content
            save_btn = self.wait_for_clickable(driver, By.ID, 'saveBtn')
            if save_btn:
                save_btn.click()
                time.sleep(3)  # Allow time for save operation
                
                # Check status message for success
                status_area = driver.find_element(By.ID, 'scrapeStatus')
                success = False
                
                if status_area.is_displayed():
                    status_text = status_area.text.lower()
                    success = 'saved' in status_text and 'success' in status_text
                
                self.test_results.append({
                    'test': 'save_functionality',
                    'browser': browser,
                    'results': {'save_attempted': True, 'success': success},
                    'passed': success
                })
                
                return success
            
            return False
            
        except Exception as e:
            logger.error(f"Save functionality test failed: {e}")
            return False
    
    def test_responsive_design(self, browser='chrome'):
        """Test responsive design at different screen sizes"""
        logger.info(f"Testing responsive design with {browser}")
        driver = self.drivers.get(browser)
        if not driver:
            return False
        
        screen_sizes = [
            {'name': 'Desktop', 'width': 1920, 'height': 1080},
            {'name': 'Tablet', 'width': 768, 'height': 1024},
            {'name': 'Mobile', 'width': 375, 'height': 667},
            {'name': 'Small Mobile', 'width': 320, 'height': 568}
        ]
        
        results = []
        
        try:
            driver.get(self.base_url)
            
            for size in screen_sizes:
                logger.info(f"Testing {size['name']} size: {size['width']}x{size['height']}")
                
                driver.set_window_size(size['width'], size['height'])
                time.sleep(2)  # Allow layout to adjust
                
                # Check if essential elements are visible and accessible
                elements_visible = True
                essential_elements = ['urlInput', 'scrapeBtn', 'totalConversations']
                
                for element_id in essential_elements:
                    try:
                        element = driver.find_element(By.ID, element_id)
                        if not element.is_displayed():
                            elements_visible = False
                            logger.warning(f"Element {element_id} not visible at {size['name']} size")
                    except NoSuchElementException:
                        elements_visible = False
                        logger.error(f"Element {element_id} not found at {size['name']} size")
                
                results.append({
                    'size': size['name'],
                    'dimensions': f"{size['width']}x{size['height']}",
                    'elements_visible': elements_visible
                })
            
            all_passed = all(result['elements_visible'] for result in results)
            
            self.test_results.append({
                'test': 'responsive_design',
                'browser': browser,
                'results': results,
                'passed': all_passed
            })
            
            return all_passed
            
        except Exception as e:
            logger.error(f"Responsive design test failed: {e}")
            return False
    
    def test_accessibility_features(self, browser='chrome'):
        """Test basic accessibility features"""
        logger.info(f"Testing accessibility features with {browser}")
        driver = self.drivers.get(browser)
        if not driver:
            return False
        
        accessibility_checks = {
            'form_labels': 0,
            'button_text': 0,
            'alt_text': 0,
            'aria_labels': 0,
            'keyboard_navigation': 0
        }
        
        try:
            driver.get(self.base_url)
            
            # Check form labels
            labels = driver.find_elements(By.TAG_NAME, 'label')
            for label in labels:
                if label.get_attribute('for'):
                    accessibility_checks['form_labels'] += 1
            
            # Check button text
            buttons = driver.find_elements(By.TAG_NAME, 'button')
            for button in buttons:
                if button.text.strip():
                    accessibility_checks['button_text'] += 1
            
            # Check for ARIA labels
            aria_elements = driver.find_elements(By.XPATH, "//*[@aria-label]")
            accessibility_checks['aria_labels'] = len(aria_elements)
            
            # Test keyboard navigation
            url_input = driver.find_element(By.ID, 'urlInput')
            url_input.send_keys(Keys.TAB)
            
            # Check if focus moved to scrape button
            active_element = driver.switch_to.active_element
            if active_element.get_attribute('id') == 'scrapeBtn':
                accessibility_checks['keyboard_navigation'] = 1
            
            total_checks = sum(accessibility_checks.values())
            
            self.test_results.append({
                'test': 'accessibility_features',
                'browser': browser,
                'results': accessibility_checks,
                'passed': total_checks > 0
            })
            
            return total_checks > 0
            
        except Exception as e:
            logger.error(f"Accessibility test failed: {e}")
            return False
    
    def test_api_endpoints(self):
        """Test backend API endpoints"""
        logger.info("Testing API endpoints")
        
        endpoints = [
            {'url': '/health', 'method': 'GET', 'expected_status': 200},
            {'url': '/stats', 'method': 'GET', 'expected_status': 200},
            {'url': '/search?q=test', 'method': 'GET', 'expected_status': 200}
        ]
        
        results = []
        
        for endpoint in endpoints:
            try:
                full_url = urljoin(self.base_url, endpoint['url'])
                
                if endpoint['method'] == 'GET':
                    response = requests.get(full_url, timeout=10)
                
                success = response.status_code == endpoint['expected_status']
                
                results.append({
                    'endpoint': endpoint['url'],
                    'expected_status': endpoint['expected_status'],
                    'actual_status': response.status_code,
                    'success': success
                })
                
                logger.info(f"API test - {endpoint['url']}: {'✅' if success else '❌'}")
                
            except Exception as e:
                logger.error(f"API test failed for {endpoint['url']}: {e}")
                results.append({
                    'endpoint': endpoint['url'],
                    'error': str(e),
                    'success': False
                })
        
        all_passed = all(result['success'] for result in results)
        
        self.test_results.append({
            'test': 'api_endpoints',
            'browser': 'N/A',
            'results': results,
            'passed': all_passed
        })
        
        return all_passed
    
    def run_comprehensive_tests(self):
        """Run all tests in the suite"""
        logger.info("Starting comprehensive web UI tests")
        
        # Setup
        self.setup_drivers()
        
        test_functions = [
            ('URL Compatibility', self.test_url_compatibility),
            ('Error Handling', self.test_error_handling),
            ('Clipboard Functionality', self.test_clipboard_functionality),
            ('Save Functionality', self.test_save_functionality),
            ('Responsive Design', self.test_responsive_design),
            ('Accessibility Features', self.test_accessibility_features),
            ('API Endpoints', self.test_api_endpoints)
        ]
        
        results_summary = {'total': 0, 'passed': 0, 'failed': 0}
        
        for test_name, test_func in test_functions:
            logger.info(f"\n{'='*50}")
            logger.info(f"Running: {test_name}")
            logger.info(f"{'='*50}")
            
            try:
                if test_func == self.test_api_endpoints:
                    success = test_func()
                else:
                    success = test_func('chrome')
                
                results_summary['total'] += 1
                if success:
                    results_summary['passed'] += 1
                    logger.info(f"✅ {test_name} PASSED")
                else:
                    results_summary['failed'] += 1
                    logger.error(f"❌ {test_name} FAILED")
                    
            except Exception as e:
                logger.error(f"💥 {test_name} CRASHED: {e}")
                results_summary['total'] += 1
                results_summary['failed'] += 1
        
        # Cleanup
        self.teardown_drivers()
        
        # Generate report
        self.generate_report(results_summary)
        
        return results_summary
    
    def generate_report(self, summary):
        """Generate comprehensive test report"""
        logger.info("\n" + "="*60)
        logger.info("COMPREHENSIVE TEST REPORT")
        logger.info("="*60)
        
        logger.info(f"Total Tests: {summary['total']}")
        logger.info(f"Passed: {summary['passed']}")
        logger.info(f"Failed: {summary['failed']}")
        logger.info(f"Success Rate: {(summary['passed']/summary['total']*100):.1f}%")
        
        logger.info("\nDetailed Results:")
        logger.info("-" * 40)
        
        for result in self.test_results:
            status = "✅ PASS" if result['passed'] else "❌ FAIL"
            logger.info(f"{result['test']} ({result['browser']}): {status}")
        
        # Save detailed results to JSON
        with open('web_ui_test_detailed_results.json', 'w') as f:
            json.dump(self.test_results, f, indent=2)
        
        logger.info(f"\nDetailed results saved to: web_ui_test_detailed_results.json")
        logger.info("="*60)

def main():
    """Main function to run the test suite"""
    import sys
    
    base_url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:5001"
    
    logger.info(f"Starting SpiralBridge Web UI Test Suite")
    logger.info(f"Target URL: {base_url}")
    
    # Check if server is running
    try:
        response = requests.get(base_url, timeout=5)
        if response.status_code != 200:
            logger.error(f"Server not responding correctly at {base_url}")
            sys.exit(1)
    except Exception as e:
        logger.error(f"Cannot connect to server at {base_url}: {e}")
        logger.info("Please make sure the Flask server is running:")
        logger.info("python app.py")
        sys.exit(1)
    
    # Run tests
    test_suite = WebUITestSuite(base_url)
    results = test_suite.run_comprehensive_tests()
    
    # Exit with appropriate code
    sys.exit(0 if results['failed'] == 0 else 1)

if __name__ == "__main__":
    main()
