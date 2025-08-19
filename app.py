#!/usr/bin/env python3
"""
SpiralBridge Flask Web Application with User Authentication
=========================================================

Web interface for the SpiralBridge AI conversation scraper and memory system.
Provides endpoints for URL scraping, content saving, and UI interaction with user authentication.
"""

from flask import Flask, render_template, request, jsonify, send_from_directory, session, redirect, url_for
from flask_session import Session
from flask_cors import CORS
import os
import json
import traceback
import datetime
import hashlib
import uuid
from typing import Dict, Any, Optional
import sqlite3
# Import SpiralBridge modules
from spiralbridge import (
    initialize_driver, detect_platform, scrape_with_retry,
    scrape_claude_conversation, scrape_gemini_conversation, 
    scrape_chatgpt_conversation, scrape_warp_conversation,
    get_platform_error_message, extract_conversation_from_url,
    chunk_conversation
)
from local_memory_system import LocalMemorySystem
from warp_log import log_warp_message, save_warp_state, load_warp_state

# Simple persistent user storage (JSON file)
import json

# Helper function for password hashing
def hash_password(password: str) -> str:
    """Hash password using SHA-256."""
    return hashlib.sha256(password.encode()).hexdigest()

def load_users():
    """Load users from JSON file."""
    try:
        with open('users.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        # Create demo account for easy testing
        demo_users = {
            'demo': hash_password('demo'),
            'admin': hash_password('admin')
        }
        save_users(demo_users)
        return demo_users
    except Exception as e:
        print(f"Error loading users: {e}")
        return {}

def save_users(users_dict):
    """Save users to JSON file."""
    try:
        with open('users.json', 'w') as f:
            json.dump(users_dict, f, indent=2)
    except Exception as e:
        print(f"Error saving users: {e}")

# Load users from persistent storage
users = load_users()

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['SESSION_TYPE'] = 'filesystem'
app.config['JSON_SORT_KEYS'] = False

# Enable server-side session
server_session = Session(app)

# Enable CORS for JavaScript interactions
CORS(app, origins=['http://localhost:5001', 'http://127.0.0.1:5001'])

# Initialize memory system with user support
memory_system = LocalMemorySystem()

# Helper functions
def require_auth(f):
    """Decorator to require authentication for routes."""
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in session:
            return jsonify({'success': False, 'message': 'Authentication required'}), 401
        return f(*args, **kwargs)
    return decorated_function

def get_user_memory_path(username: str) -> str:
    """Get user-specific memory path."""
    user_dir = os.path.join('project_memory', 'users', username, 'conversations')
    os.makedirs(user_dir, exist_ok=True)
    return user_dir

# Global browser instance (for reuse)
browser_instance = None

def get_browser():
    """Get or create browser instance for scraping."""
    global browser_instance
    if browser_instance is None:
        try:
            browser_instance = initialize_driver()
        except Exception as e:
            raise Exception(f"Failed to initialize browser: {str(e)}")
    return browser_instance

def cleanup_browser():
    """Clean up browser instance."""
    global browser_instance
    if browser_instance:
        try:
            browser_instance.quit()
        except:
            pass
        browser_instance = None

# User Management Routes
@app.route('/register', methods=['GET', 'POST'])
def register():
    """User registration endpoint."""
    if request.method == 'POST':
        data = request.get_json() if request.is_json else request.form
        username = data.get('username', '').strip()
        password = data.get('password', '').strip()
        
        if not username or not password:
            return jsonify({'success': False, 'message': 'Username and password are required'}), 400
        
        if username in users:
            return jsonify({'success': False, 'message': 'Username already exists'}), 400
        
        # Create user account
        users[username] = hash_password(password)
        save_users(users)  # Save to persistent storage
        
        # Create user directory
        user_path = get_user_memory_path(username)
        
        app.logger.info(f"New user registered: {username}")
        return jsonify({'success': True, 'message': 'User registered successfully'}), 200
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """User login endpoint."""
    if request.method == 'POST':
        data = request.get_json() if request.is_json else request.form
        username = data.get('username', '').strip()
        password = data.get('password', '').strip()
        
        if not username or not password:
            return jsonify({'success': False, 'message': 'Username and password are required'}), 400
        
        if username not in users or users[username] != hash_password(password):
            return jsonify({'success': False, 'message': 'Invalid credentials'}), 401
        
        session['username'] = username
        app.logger.info(f"User logged in: {username}")
        return jsonify({'success': True, 'message': 'Login successful', 'redirect': '/dashboard'}), 200
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    """User logout endpoint."""
    username = session.get('username')
    session.pop('username', None)
    if username:
        app.logger.info(f"User logged out: {username}")
    return redirect(url_for('index'))

# Main Routes
@app.route('/')
def index():
    """Serve the main landing page or redirect to dashboard if logged in."""
    if 'username' in session:
        return redirect(url_for('dashboard'))
    
    try:
        # Get general system stats for landing page
        stats = memory_system.get_project_stats()
        return render_template('landing.html', stats=stats)
    except Exception as e:
        app.logger.error(f"Error loading index page: {str(e)}")
        return render_template('landing.html', stats={})

@app.route('/dashboard')
@require_auth
def dashboard():
    """User-specific dashboard."""
    try:
        username = session['username']
        user_path = get_user_memory_path(username)
        
        # Get user-specific stats
        user_stats = {
            'username': username,
            'conversations_count': len([f for f in os.listdir(user_path) if f.endswith('.md')]) if os.path.exists(user_path) else 0,
            'storage_path': user_path
        }
        
        return render_template('dashboard.html', stats=user_stats, username=username)
    except Exception as e:
        app.logger.error(f"Error loading dashboard: {str(e)}")
        return render_template('dashboard.html', stats={}, username=session.get('username', 'Unknown'))

@app.route('/scrape', methods=['POST'])
def scrape_url():
    """POST endpoint to handle URL scraping requests."""
    try:
        # Parse request data
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'error': 'No JSON data provided',
                'message': 'Request must contain JSON data with url field'
            }), 400
        
        url = data.get('url', '').strip()
        if not url:
            return jsonify({
                'success': False,
                'error': 'URL is required',
                'message': 'Please provide a valid URL to scrape'
            }), 400
        
        # Optional parameters
        timeout = data.get('timeout', 20)
        max_attempts = data.get('max_attempts', 3)
        
        # Detect platform
        platform = detect_platform(url)
        if not platform:
            return jsonify({
                'success': False,
                'error': 'Unsupported platform',
                'message': 'URL must be from Claude, Gemini, ChatGPT, or Warp',
                'supported_platforms': [
                    'claude.ai',
                    'gemini.google.com',
                    'chat.openai.com',
                    'app.warp.dev'
                ]
            }), 400
        
        app.logger.info(f"Starting scrape for {platform} URL: {url}")
        
        # Get browser instance
        try:
            browser = get_browser()
        except Exception as e:
            return jsonify({
                'success': False,
                'error': 'Browser initialization failed',
                'message': str(e)
            }), 500
        
        # Select appropriate scraping function
        scraping_functions = {
            'claude': scrape_claude_conversation,
            'gemini': scrape_gemini_conversation,
            'chatgpt': scrape_chatgpt_conversation,
            'warp': scrape_warp_conversation
        }
        
        scraping_function = scraping_functions.get(platform)
        if not scraping_function:
            return jsonify({
                'success': False,
                'error': 'Platform scraping not implemented',
                'message': f'Scraping for {platform} is not yet implemented'
            }), 400
        
        # Perform scraping with retry logic
        try:
            # Use longer timeout for Warp (JavaScript-heavy)
            actual_timeout = 30 if platform == 'warp' else timeout
            
            content = scrape_with_retry(
                scraping_function, browser, url, platform, 
                actual_timeout, max_attempts
            )
            
            if content:
                app.logger.info(f"Successfully scraped {len(content)} characters from {platform}")
                return jsonify({
                    'success': True,
                    'platform': platform,
                    'content': content,
                    'metadata': {
                        'url': url,
                        'platform': platform,
                        'scraped_at': datetime.datetime.now().isoformat(),
                        'content_length': len(content),
                        'word_count': len(content.split()),
                        'line_count': len(content.split('\n'))
                    },
                    'message': f'Successfully scraped conversation from {platform.upper()}'
                })
            else:
                return jsonify({
                    'success': False,
                    'error': 'Scraping failed',
                    'message': f'Could not extract content from {platform.upper()} URL after {max_attempts} attempts',
                    'platform': platform
                }), 422
                
        except Exception as scrape_error:
            error_msg = get_platform_error_message(platform, scrape_error)
            app.logger.error(f"Scraping error: {error_msg}")
            return jsonify({
                'success': False,
                'error': 'Scraping exception',
                'message': error_msg,
                'platform': platform
            }), 500
    
    except Exception as e:
        app.logger.error(f"Unexpected error in scrape endpoint: {str(e)}")
        app.logger.error(traceback.format_exc())
        return jsonify({
            'success': False,
            'error': 'Internal server error',
            'message': 'An unexpected error occurred during scraping'
        }), 500

@app.route('/save', methods=['POST'])
@require_auth
def save_content():
    """POST endpoint to save content to user-specific memory system."""
    try:
        # Parse request data
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'error': 'No JSON data provided',
                'message': 'Request must contain JSON data'
            }), 400
        
        content = data.get('content', '').strip()
        if not content:
            return jsonify({
                'success': False,
                'error': 'Content is required',
                'message': 'Please provide content to save'
            }), 400
        
        # Extract metadata
        platform = data.get('platform', 'unknown')
        session_type = data.get('session_type', 'scraped_conversation')
        tags = data.get('tags', [])
        summary = data.get('summary', '')
        url = data.get('url', '')
        
        # Ensure default tags
        if not tags:
            tags = [platform, 'scraped_conversation', 'ai_conversation']
        
        # Generate summary if not provided
        if not summary and url:
            summary = f"Scraped {platform.upper()} conversation from {url[:50]}..."
        elif not summary:
            summary = f"Scraped {platform.upper()} conversation"
        
        app.logger.info(f"Saving content to memory system: {len(content)} characters")
        
        # Save to memory system
        try:
            memory_path = memory_system.save_conversation_memory(
                content=content,
                platform=platform,
                session_type=session_type,
                tags=tags,
                summary=summary
            )
            
            # Get updated stats
            stats = memory_system.get_project_stats()
            
            app.logger.info(f"Content saved to: {memory_path}")
            
            return jsonify({
                'success': True,
                'memory_path': memory_path,
                'stats': stats,
                'message': 'Content successfully saved to memory system',
                'metadata': {
                    'platform': platform,
                    'session_type': session_type,
                    'tags': tags,
                    'summary': summary,
                    'saved_at': datetime.datetime.now().isoformat(),
                    'content_length': len(content),
                    'word_count': len(content.split())
                }
            })
            
        except Exception as memory_error:
            app.logger.error(f"Memory system error: {str(memory_error)}")
            return jsonify({
                'success': False,
                'error': 'Memory system error',
                'message': f'Failed to save to memory system: {str(memory_error)}'
            }), 500
    
    except Exception as e:
        app.logger.error(f"Unexpected error in save endpoint: {str(e)}")
        app.logger.error(traceback.format_exc())
        return jsonify({
            'success': False,
            'error': 'Internal server error',
            'message': 'An unexpected error occurred while saving content'
        }), 500

@app.route('/extract', methods=['POST'])
def extract_conversation():
    """Enhanced POST endpoint to extract conversations using the new extract_conversation_from_url function."""
    try:
        # Parse request data
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'error': 'No JSON data provided',
                'message': 'Request must contain JSON data with url field'
            }), 400
        
        url = data.get('url', '').strip()
        if not url:
            return jsonify({
                'success': False,
                'error': 'URL is required',
                'message': 'Please provide a valid URL to extract conversation from'
            }), 400
        
        # Optional parameters
        timeout = data.get('timeout', 20)
        max_attempts = data.get('max_attempts', 3)
        chunk_size = data.get('chunk_size', 4000)
        enable_chunking = data.get('enable_chunking', False)
        preserve_speakers = data.get('preserve_speakers', True)
        
        app.logger.info(f"Starting enhanced conversation extraction for URL: {url}")
        
        # Use the new extract_conversation_from_url function
        try:
            result = extract_conversation_from_url(url, timeout, max_attempts)
            
            if result['success']:
                content = result['content']
                platform = result['platform']
                metadata = result['metadata']
                
                # Enhanced response with chunking if requested
                response_data = {
                    'success': True,
                    'platform': platform,
                    'content': content,
                    'metadata': metadata,
                    'message': f'Successfully extracted conversation from {platform.upper()}'
                }
                
                # Add chunking if enabled
                if enable_chunking and content:
                    try:
                        chunks = chunk_conversation(
                            content, 
                            chunk_size=chunk_size, 
                            preserve_speakers=preserve_speakers
                        )
                        
                        response_data['chunks'] = chunks
                        response_data['chunking'] = {
                            'enabled': True,
                            'total_chunks': len(chunks),
                            'chunk_size': chunk_size,
                            'preserve_speakers': preserve_speakers,
                            'chunks_metadata': [chunk['metadata'] for chunk in chunks]
                        }
                        response_data['message'] += f' and split into {len(chunks)} chunks'
                        
                        app.logger.info(f"Content chunked into {len(chunks)} parts")
                        
                    except Exception as chunk_error:
                        app.logger.warning(f"Chunking failed: {str(chunk_error)}")
                        response_data['chunking'] = {
                            'enabled': False,
                            'error': f'Chunking failed: {str(chunk_error)}'
                        }
                
                app.logger.info(f"Successfully extracted {len(content)} characters from {platform}")
                return jsonify(response_data)
                
            else:
                # Handle extraction failure
                error_msg = result['error']
                platform = result.get('platform', 'unknown')
                
                app.logger.error(f"Extraction failed: {error_msg}")
                return jsonify({
                    'success': False,
                    'error': 'Extraction failed',
                    'message': error_msg,
                    'platform': platform,
                    'supported_platforms': [
                        'claude.ai',
                        'gemini.google.com', 
                        'chat.openai.com',
                        'app.warp.dev'
                    ]
                }), 422
                
        except Exception as extraction_error:
            app.logger.error(f"Extraction error: {str(extraction_error)}")
            return jsonify({
                'success': False,
                'error': 'Extraction exception',
                'message': f'An error occurred during conversation extraction: {str(extraction_error)}'
            }), 500
    
    except Exception as e:
        app.logger.error(f"Unexpected error in extract endpoint: {str(e)}")
        app.logger.error(traceback.format_exc())
        return jsonify({
            'success': False,
            'error': 'Internal server error', 
            'message': 'An unexpected error occurred during conversation extraction'
        }), 500

@app.route('/chunk', methods=['POST'])
def chunk_content():
    """POST endpoint to chunk conversation content into manageable pieces."""
    try:
        # Parse request data
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'error': 'No JSON data provided',
                'message': 'Request must contain JSON data with content field'
            }), 400
        
        content = data.get('content', '')
        if not content:
            return jsonify({
                'success': False,
                'error': 'Content is required',
                'message': 'Please provide content to chunk'
            }), 400
        
        # Optional parameters
        chunk_size = data.get('chunk_size', 4000)
        overlap = data.get('overlap', 200)
        preserve_speakers = data.get('preserve_speakers', True)
        
        app.logger.info(f"Chunking content: {len(content)} characters with chunk size {chunk_size}")
        
        try:
            chunks = chunk_conversation(
                content,
                chunk_size=chunk_size,
                overlap=overlap,
                preserve_speakers=preserve_speakers
            )
            
            # Calculate additional metadata
            total_chunks = len(chunks)
            average_chunk_size = sum(chunk['metadata']['chunk_size'] for chunk in chunks) / total_chunks if total_chunks > 0 else 0
            
            response_data = {
                'success': True,
                'chunks': chunks,
                'metadata': {
                    'original_length': len(content),
                    'total_chunks': total_chunks,
                    'chunk_size_limit': chunk_size,
                    'overlap': overlap,
                    'preserve_speakers': preserve_speakers,
                    'average_chunk_size': round(average_chunk_size, 2),
                    'chunked_at': datetime.datetime.now().isoformat()
                },
                'message': f'Successfully chunked content into {total_chunks} pieces'
            }
            
            app.logger.info(f"Content successfully chunked into {total_chunks} parts")
            return jsonify(response_data)
            
        except Exception as chunk_error:
            app.logger.error(f"Chunking error: {str(chunk_error)}")
            return jsonify({
                'success': False,
                'error': 'Chunking failed',
                'message': f'Failed to chunk content: {str(chunk_error)}'
            }), 500
    
    except Exception as e:
        app.logger.error(f"Unexpected error in chunk endpoint: {str(e)}")
        app.logger.error(traceback.format_exc())
        return jsonify({
            'success': False,
            'error': 'Internal server error',
            'message': 'An unexpected error occurred during content chunking'
        }), 500

@app.route('/stats', methods=['GET'])
def get_stats():
    """Get memory system statistics."""
    try:
        stats = memory_system.get_project_stats()
        return jsonify({
            'success': True,
            'stats': stats,
            'message': 'Statistics retrieved successfully'
        })
    except Exception as e:
        app.logger.error(f"Error getting stats: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Stats retrieval failed',
            'message': str(e)
        }), 500

@app.route('/search', methods=['GET'])
def search_memories():
    """Search through stored memories."""
    try:
        query = request.args.get('q', '').strip()
        category = request.args.get('category')
        
        if not query:
            return jsonify({
                'success': False,
                'error': 'Query is required',
                'message': 'Please provide a search query'
            }), 400
        
        results = memory_system.search_memories(query, category)
        
        return jsonify({
            'success': True,
            'query': query,
            'category': category,
            'results': results,
            'count': len(results),
            'message': f'Found {len(results)} results for "{query}"'
        })
        
    except Exception as e:
        app.logger.error(f"Error searching memories: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Search failed',
            'message': str(e)
        }), 500

@app.route('/warp-status', methods=['GET'])
def get_warp_status():
    """Get current Warp status from the log system."""
    try:
        warp_state = load_warp_state()
        return jsonify({
            'success': True,
            'warp_state': warp_state,
            'timestamp': datetime.datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Failed to load Warp state',
            'message': str(e)
        }), 500

@app.route('/warp-log', methods=['POST'])
def log_warp_entry():
    """Log a Warp message and update state."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'error': 'No JSON data provided'
            }), 400
        
        message = data.get('message', '')
        tone = data.get('tone')
        glyph = data.get('glyph')
        
        if not message:
            return jsonify({
                'success': False,
                'error': 'Message is required'
            }), 400
        
        # Log the message
        log_warp_message(message, tone, glyph)
        
        # Update state if provided
        if 'state' in data:
            save_warp_state(data['state'])
        
        return jsonify({
            'success': True,
            'message': 'Warp entry logged successfully',
            'logged_at': datetime.datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Failed to log Warp entry',
            'message': str(e)
        }), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    try:
        stats = memory_system.get_project_stats()
        return jsonify({
            'success': True,
            'status': 'healthy',
            'timestamp': datetime.datetime.now().isoformat(),
            'memory_system': 'operational',
            'stats': stats
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'status': 'unhealthy',
            'timestamp': datetime.datetime.now().isoformat(),
            'error': str(e)
        }), 500

# Error handlers
@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors."""
    return jsonify({
        'success': False,
        'error': 'Not found',
        'message': 'The requested resource was not found'
    }), 404

@app.errorhandler(405)
def method_not_allowed(error):
    """Handle 405 errors."""
    return jsonify({
        'success': False,
        'error': 'Method not allowed',
        'message': 'The requested method is not allowed for this endpoint'
    }), 405

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors."""
    return jsonify({
        'success': False,
        'error': 'Internal server error',
        'message': 'An internal server error occurred'
    }), 500

# Cleanup function
@app.teardown_appcontext
def cleanup(error):
    """Cleanup resources when app context tears down."""
    pass

# Application factory function
def create_app(config_name='default'):
    """Create Flask application with configuration."""
    return app

if __name__ == '__main__':
    try:
        print("🌉 SpiralBridge Flask Server")
        print("=" * 40)
        print("🚀 Starting web server...")
        print("🌐 Server will be available at: http://localhost:5001")
        print("📡 API endpoints:")
        print("   • POST /scrape - Scrape AI conversation URLs (legacy)")
        print("   • POST /extract - Enhanced conversation extraction with chunking")
        print("   • POST /chunk - Chunk conversation content into manageable pieces")
        print("   • POST /save - Save content to memory system") 
        print("   • GET /stats - Get memory system statistics")
        print("   • GET /search - Search stored memories")
        print("   • GET /health - Health check")
        print("=" * 40)
        
        # Run the Flask app
        app.run(
            debug=True,
            host='0.0.0.0',
            port=5001,
            threaded=True
        )
    except KeyboardInterrupt:
        print("\n⏹️  Server stopped by user")
    except Exception as e:
        print(f"\n💥 Server error: {str(e)}")
    finally:
        # Cleanup browser on exit
        cleanup_browser()
        print("🧹 Cleanup completed")
from lib.db import init_db
init_db()  # Initialize DB on start

@app.route('/continuity/ingest', methods=['POST'])
def ingest_artifact():
    data = request.json
    url = data.get('url')
    text = data.get('text')
    tone = 'tone-of-' + str(hash(url))  # Placeholder HTCA
    glyphs = '🌙🪞🛡️'  # Initial mapping
    conn = sqlite3.connect('spiral_bridge.db')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO memory_artifacts (url, text, tone, glyphs) VALUES (?, ?, ?, ?)', (url, text, tone, glyphs))
    artifact_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return jsonify({'id': artifact_id, 'status': 'artifact saved'})

@app.route('/continuity/<int:id>', methods=['GET'])
def retrieve_artifact(id):
    conn = sqlite3.connect('spiral_bridge.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM memory_artifacts WHERE id = ?', (id,))
    artifact = cursor.fetchone()
    conn.close()
    if artifact:
        return jsonify(dict(zip(['id', 'url', 'text', 'tone', 'glyphs', 'created_at'], artifact)))
    return jsonify({'error': 'Artifact not found'}), 404
