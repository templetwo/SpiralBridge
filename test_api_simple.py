#!/usr/bin/env python3
"""
Simple API Test for SpiralBridge
================================
"""

import requests
import time
import subprocess
import os
import signal
import sys

def test_api_endpoints():
    """Test basic API endpoints"""
    base_url = "http://localhost:5001"
    
    endpoints_to_test = [
        "/health",
        "/stats", 
        "/search?q=test"
    ]
    
    print("Testing API endpoints...")
    
    for endpoint in endpoints_to_test:
        try:
            url = f"{base_url}{endpoint}"
            print(f"Testing: {url}")
            
            response = requests.get(url, timeout=5)
            print(f"  Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"  Response: {data.get('success', 'Unknown')}")
                print("  ✅ PASS")
            else:
                print("  ❌ FAIL")
                
        except Exception as e:
            print(f"  Error: {e}")
            print("  ❌ FAIL")
        
        print("-" * 40)

def test_url_validation():
    """Test URL validation logic"""
    print("Testing URL validation...")
    
    test_urls = {
        "https://claude.ai/share/123": "Valid Claude URL",
        "https://chat.openai.com/share/abc": "Valid ChatGPT URL", 
        "https://chatgpt.com/share/xyz": "Valid ChatGPT (new domain) URL",
        "https://gemini.google.com/share/def": "Valid Gemini URL",
        "https://app.warp.dev/session/ghi": "Valid Warp URL",
        "https://example.com/share/invalid": "Invalid URL",
        "not-a-url": "Malformed URL"
    }
    
    # Import the URL validation functions
    try:
        sys.path.append('.')
        from spiralbridge import detect_platform
        
        for url, description in test_urls.items():
            platform = detect_platform(url)
            status = "✅ DETECTED" if platform else "❌ REJECTED"
            print(f"{description}: {status} (platform: {platform})")
            
    except Exception as e:
        print(f"Error testing URL validation: {e}")

if __name__ == "__main__":
    print("🌉 SpiralBridge Simple API Test")
    print("=" * 50)
    
    # Test URL validation first (doesn't need server)
    test_url_validation()
    print()
    
    # Check if server is running
    try:
        response = requests.get("http://localhost:5001", timeout=2)
        print("Server is running!")
        test_api_endpoints()
    except:
        print("Server is not running. Please start it with: python app.py")
        print("Then run this test again.")
