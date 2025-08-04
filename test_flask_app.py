#!/usr/bin/env python3
"""
Simple test script for SpiralBridge Flask Application
Tests all endpoints and functionality without starting browser
"""

import json
import time
from app import create_app

def test_flask_app():
    """Test Flask application endpoints"""
    app = create_app()
    app.config['TESTING'] = True
    
    with app.test_client() as client:
        print("🧪 Testing SpiralBridge Flask Application")
        print("=" * 50)
        
        # Test 1: Index page
        print("1. Testing index page (GET /)...")
        response = client.get('/')
        assert response.status_code == 200
        assert b'SpiralBridge' in response.data
        print("   ✅ Index page loads successfully")
        
        # Test 2: Health check
        print("2. Testing health check (GET /health)...")
        response = client.get('/health')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] == True
        assert data['status'] == 'healthy'
        print("   ✅ Health check passed")
        
        # Test 3: Statistics
        print("3. Testing statistics (GET /stats)...")
        response = client.get('/stats')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] == True
        assert 'stats' in data
        print(f"   ✅ Stats retrieved: {data['stats']}")
        
        # Test 4: Search (empty query should fail)
        print("4. Testing search validation (GET /search)...")
        response = client.get('/search')
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['success'] == False
        print("   ✅ Search validation working")
        
        # Test 5: Search with query
        print("5. Testing search with query (GET /search?q=test)...")
        response = client.get('/search?q=test')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] == True
        assert 'results' in data
        print(f"   ✅ Search completed: {data['count']} results")
        
        # Test 6: Save endpoint validation
        print("6. Testing save validation (POST /save)...")
        response = client.post('/save', 
                             json={},
                             content_type='application/json')
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['success'] == False
        print("   ✅ Save validation working")
        
        # Test 7: Scrape endpoint validation
        print("7. Testing scrape validation (POST /scrape)...")
        response = client.post('/scrape',
                             json={},
                             content_type='application/json')
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['success'] == False
        print("   ✅ Scrape validation working")
        
        # Test 8: Scrape with invalid URL
        print("8. Testing scrape with invalid URL...")
        response = client.post('/scrape',
                             json={'url': 'https://invalid-platform.com/share/123'},
                             content_type='application/json')
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['success'] == False
        assert 'Unsupported platform' in data['error']
        print("   ✅ Invalid URL handling working")
        
        # Test 9: Error handlers
        print("9. Testing 404 error handler...")
        response = client.get('/nonexistent-endpoint')
        assert response.status_code == 404
        data = json.loads(response.data)
        assert data['success'] == False
        print("   ✅ 404 error handler working")
        
        print("=" * 50)
        print("🎉 All tests passed! Flask application is working correctly.")
        print("🚀 Ready to start with: python app.py")

if __name__ == '__main__':
    test_flask_app()
