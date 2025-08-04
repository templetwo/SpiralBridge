#!/usr/bin/env python3
"""
Basic Web UI Test Suite for SpiralBridge
========================================

Tests the core functionality without requiring Selenium setup.
"""

import requests
import json
import time
import logging
from typing import Dict, List

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class BasicWebUITests:
    """Basic test suite for SpiralBridge Web UI"""
    
    def __init__(self, base_url="http://localhost:5001"):
        self.base_url = base_url
        self.test_results = []
        
        # Test URLs for different platforms
        self.test_urls = {
            'claude': [
                'https://claude.ai/share/12345',
                'https://claude.ai/share/test-conversation'
            ],
            'gemini': [
                'https://gemini.google.com/share/abc123',
                'https://g.co/gemini/xyz789'
            ],
            'chatgpt': [
                'https://chat.openai.com/share/valid-id',
                'https://chatgpt.com/share/new-format'
            ],
            'warp': [
                'https://app.warp.dev/session/test-session'
            ],
            'invalid': [
                'https://example.com/share/test',
                'not-a-url'
            ]
        }
    
    def test_server_availability(self):
        """Test if server is responding"""
        logger.info("Testing server availability...")
        
        try:
            response = requests.get(self.base_url, timeout=5)
            success = response.status_code == 200
            
            if success:
                logger.info("✅ Server is responding")
                # Check if it returns HTML
                content_type = response.headers.get('content-type', '')
                if 'text/html' in content_type:
                    logger.info("✅ Server returns HTML content")
                else:
                    logger.warning("❌ Server not returning HTML")
                    success = False
            else:
                logger.error(f"❌ Server returned status {response.status_code}")
            
            self.test_results.append({
                'test': 'server_availability',
                'passed': success,
                'details': {'status_code': response.status_code}
            })
            
            return success
            
        except Exception as e:
            logger.error(f"❌ Server not available: {e}")
            self.test_results.append({
                'test': 'server_availability',
                'passed': False,
                'details': {'error': str(e)}
            })
            return False
    
    def test_api_endpoints(self):
        """Test API endpoints"""
        logger.info("Testing API endpoints...")
        
        endpoints = [
            {'path': '/health', 'method': 'GET', 'expected_success': True},
            {'path': '/stats', 'method': 'GET', 'expected_success': True},
            {'path': '/search?q=test', 'method': 'GET', 'expected_success': True}
        ]
        
        results = []
        all_passed = True
        
        for endpoint in endpoints:
            try:
                url = f"{self.base_url}{endpoint['path']}"
                
                if endpoint['method'] == 'GET':
                    response = requests.get(url, timeout=10)
                
                success = response.status_code == 200
                
                if success:
                    try:
                        data = response.json()
                        api_success = data.get('success', False)
                        if api_success == endpoint['expected_success']:
                            logger.info(f"✅ {endpoint['path']}: API success")
                        else:
                            logger.warning(f"⚠️ {endpoint['path']}: Unexpected API response")
                            success = False
                    except json.JSONDecodeError:
                        logger.warning(f"⚠️ {endpoint['path']}: Non-JSON response")
                        success = False
                else:
                    logger.error(f"❌ {endpoint['path']}: HTTP {response.status_code}")
                
                results.append({
                    'endpoint': endpoint['path'],
                    'success': success,
                    'status_code': response.status_code
                })
                
                if not success:
                    all_passed = False
                    
            except Exception as e:
                logger.error(f"❌ {endpoint['path']}: {e}")
                results.append({
                    'endpoint': endpoint['path'],
                    'success': False,
                    'error': str(e)
                })
                all_passed = False
        
        self.test_results.append({
            'test': 'api_endpoints',
            'passed': all_passed,
            'details': results
        })
        
        return all_passed
    
    def test_url_validation_backend(self):
        """Test URL validation on the backend"""
        logger.info("Testing URL validation (backend)...")
        
        # Import the backend validation function
        try:
            import sys
            sys.path.append('.')
            from spiralbridge import detect_platform
            
            validation_results = []
            all_passed = True
            
            # Test valid URLs
            for platform, urls in self.test_urls.items():
                if platform == 'invalid':
                    continue
                    
                for url in urls:
                    detected_platform = detect_platform(url)
                    success = detected_platform == platform
                    
                    if success:
                        logger.info(f"✅ {url}: Correctly detected as {platform}")
                    else:
                        logger.error(f"❌ {url}: Expected {platform}, got {detected_platform}")
                        all_passed = False
                    
                    validation_results.append({
                        'url': url,
                        'expected': platform,
                        'detected': detected_platform,
                        'success': success
                    })
            
            # Test invalid URLs
            for url in self.test_urls['invalid']:
                detected_platform = detect_platform(url)
                success = detected_platform is None
                
                if success:
                    logger.info(f"✅ {url}: Correctly rejected")
                else:
                    logger.error(f"❌ {url}: Should be rejected, got {detected_platform}")
                    all_passed = False
                
                validation_results.append({
                    'url': url,
                    'expected': None,
                    'detected': detected_platform,
                    'success': success
                })
            
            self.test_results.append({
                'test': 'url_validation_backend',
                'passed': all_passed,
                'details': validation_results
            })
            
            return all_passed
            
        except Exception as e:
            logger.error(f"❌ URL validation test failed: {e}")
            self.test_results.append({
                'test': 'url_validation_backend',
                'passed': False,
                'details': {'error': str(e)}
            })
            return False
    
    def test_scraping_error_handling(self):
        """Test scraping with invalid URLs to check error handling"""
        logger.info("Testing scraping error handling...")
        
        test_cases = [
            {'url': 'https://example.com/share/invalid', 'should_fail': True},
            {'url': 'not-a-url', 'should_fail': True},
            {'url': '', 'should_fail': True}
        ]
        
        results = []
        all_passed = True
        
        for case in test_cases:
            try:
                response = requests.post(
                    f"{self.base_url}/scrape",
                    json={'url': case['url']},
                    timeout=10
                )
                
                data = response.json()
                
                # For invalid URLs, we expect the API to return success=False
                if case['should_fail']:
                    success = not data.get('success', True)
                    if success:
                        logger.info(f"✅ {case['url']}: Properly rejected")
                    else:
                        logger.error(f"❌ {case['url']}: Should have been rejected")
                        all_passed = False
                else:
                    success = data.get('success', False)
                    if success:
                        logger.info(f"✅ {case['url']}: Properly accepted")
                    else:
                        logger.error(f"❌ {case['url']}: Should have been accepted")
                        all_passed = False
                
                results.append({
                    'url': case['url'],
                    'should_fail': case['should_fail'],
                    'api_success': data.get('success'),
                    'test_passed': success,
                    'message': data.get('message', '')
                })
                
            except Exception as e:
                logger.error(f"❌ Error testing {case['url']}: {e}")
                results.append({
                    'url': case['url'],
                    'should_fail': case['should_fail'],
                    'test_passed': False,
                    'error': str(e)
                })
                all_passed = False
        
        self.test_results.append({
            'test': 'scraping_error_handling',
            'passed': all_passed,
            'details': results
        })
        
        return all_passed
    
    def test_memory_system_integration(self):
        """Test basic memory system integration"""
        logger.info("Testing memory system integration...")
        
        try:
            # Test save functionality with mock data
            test_content = "Test conversation content for memory system integration"
            
            response = requests.post(
                f"{self.base_url}/save",
                json={
                    'content': test_content,
                    'platform': 'test',
                    'session_type': 'test_conversation',
                    'tags': ['test', 'integration'],
                    'summary': 'Test save functionality'
                },
                timeout=10
            )
            
            data = response.json()
            success = data.get('success', False)
            
            if success:
                logger.info("✅ Memory system save: Success")
                
                # Test if stats were updated
                stats_response = requests.get(f"{self.base_url}/stats", timeout=5)
                if stats_response.status_code == 200:
                    stats_data = stats_response.json()
                    if stats_data.get('success'):
                        logger.info("✅ Memory system stats: Accessible")
                    else:
                        success = False
                        logger.error("❌ Memory system stats: Failed")
                else:
                    success = False
                    logger.error("❌ Memory system stats: HTTP error")
            else:
                logger.error(f"❌ Memory system save: {data.get('message', 'Unknown error')}")
            
            self.test_results.append({
                'test': 'memory_system_integration',
                'passed': success,
                'details': {
                    'save_success': data.get('success'),
                    'save_message': data.get('message')
                }
            })
            
            return success
            
        except Exception as e:
            logger.error(f"❌ Memory system integration test failed: {e}")
            self.test_results.append({
                'test': 'memory_system_integration',
                'passed': False,
                'details': {'error': str(e)}
            })
            return False
    
    def run_all_tests(self):
        """Run all basic tests"""
        logger.info("🌉 Starting SpiralBridge Basic Web UI Tests")
        logger.info("=" * 60)
        
        test_functions = [
            ('Server Availability', self.test_server_availability),
            ('API Endpoints', self.test_api_endpoints),
            ('URL Validation (Backend)', self.test_url_validation_backend),
            ('Scraping Error Handling', self.test_scraping_error_handling),
            ('Memory System Integration', self.test_memory_system_integration)
        ]
        
        results_summary = {'total': 0, 'passed': 0, 'failed': 0}
        
        for test_name, test_func in test_functions:
            logger.info(f"\n{'─' * 50}")
            logger.info(f"Running: {test_name}")
            logger.info(f"{'─' * 50}")
            
            try:
                success = test_func()
                results_summary['total'] += 1
                
                if success:
                    results_summary['passed'] += 1
                    logger.info(f"✅ {test_name}: PASSED")
                else:
                    results_summary['failed'] += 1
                    logger.error(f"❌ {test_name}: FAILED")
                    
            except Exception as e:
                logger.error(f"💥 {test_name}: CRASHED - {e}")
                results_summary['total'] += 1
                results_summary['failed'] += 1
        
        self.generate_report(results_summary)
        return results_summary
    
    def generate_report(self, summary):
        """Generate test report"""
        logger.info("\n" + "=" * 60)
        logger.info("BASIC WEB UI TEST REPORT")
        logger.info("=" * 60)
        
        logger.info(f"Total Tests: {summary['total']}")
        logger.info(f"Passed: {summary['passed']}")
        logger.info(f"Failed: {summary['failed']}")
        
        if summary['total'] > 0:
            success_rate = (summary['passed'] / summary['total']) * 100
            logger.info(f"Success Rate: {success_rate:.1f}%")
        
        logger.info("\nDetailed Results:")
        logger.info("-" * 40)
        
        for result in self.test_results:
            status = "✅ PASS" if result['passed'] else "❌ FAIL"
            logger.info(f"{result['test']}: {status}")
        
        # Save detailed results
        with open('basic_web_ui_test_results.json', 'w') as f:
            json.dump(self.test_results, f, indent=2)
        
        logger.info(f"\nDetailed results saved to: basic_web_ui_test_results.json")
        logger.info("=" * 60)

def main():
    """Main function"""
    import sys
    
    base_url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:5001"
    
    # Check if server is running
    try:
        response = requests.get(base_url, timeout=5)
        if response.status_code != 200:
            logger.error(f"Server not responding correctly at {base_url}")
            logger.info("Please start the server with: python app.py")
            sys.exit(1)
    except Exception as e:
        logger.error(f"Cannot connect to server at {base_url}: {e}")
        logger.info("Please start the server with: python app.py")
        sys.exit(1)
    
    # Run tests
    test_suite = BasicWebUITests(base_url)
    results = test_suite.run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if results['failed'] == 0 else 1)

if __name__ == "__main__":
    main()
