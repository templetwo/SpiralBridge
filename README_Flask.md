# SpiralBridge Flask Web Application

A web interface for the SpiralBridge AI conversation scraper and memory system.

## Features

### 🔗 URL Scraping
- **Supported Platforms**: Claude, Gemini, ChatGPT, and Warp
- **Smart Detection**: Automatically detects platform from URL
- **Retry Logic**: Multiple attempts with platform-specific error handling
- **Real-time Feedback**: Progress indicators and status updates

### 💾 Memory System Integration
- **Structured Storage**: Conversations saved with metadata and tags
- **Search Functionality**: Full-text search across stored memories
- **Statistics Dashboard**: Track conversations, storage, and system health
- **Backup Support**: Export and backup conversation data

### 🌐 Web Interface
- **Modern UI**: Responsive design with smooth animations
- **Real-time Updates**: Live status indicators and progress feedback
- **Content Management**: Copy, save, and clear scraped content
- **Mobile Friendly**: Optimized for desktop and mobile devices

## Installation

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Start the Server**:
   ```bash
   python app.py
   ```

3. **Access the Web Interface**:
   Open your browser to `http://localhost:5000`

## API Endpoints

### POST /scrape
Scrape content from AI conversation URLs.

**Request Body**:
```json
{
  "url": "https://claude.ai/share/...",
  "timeout": 20,
  "max_attempts": 3
}
```

**Response**:
```json
{
  "success": true,
  "platform": "claude",
  "content": "scraped conversation content...",
  "metadata": {
    "url": "https://claude.ai/share/...",
    "platform": "claude",
    "scraped_at": "2024-01-15T10:30:00",
    "content_length": 5000,
    "word_count": 800,
    "line_count": 100
  },
  "message": "Successfully scraped conversation from CLAUDE"
}
```

### POST /save
Save content to the memory system.

**Request Body**:
```json
{
  "content": "conversation content to save...",
  "platform": "claude",
  "url": "https://claude.ai/share/...",
  "session_type": "scraped_conversation",
  "tags": ["claude", "scraped_conversation", "ai_conversation"]
}
```

**Response**:
```json
{
  "success": true,
  "memory_path": "/path/to/saved/memory.md",
  "stats": {
    "total_conversations": 15,
    "storage_size_mb": 2.5
  },
  "message": "Content successfully saved to memory system"
}
```

### GET /stats
Get memory system statistics.

**Response**:
```json
{
  "success": true,
  "stats": {
    "total_conversations": 15,
    "development_sessions": 8,
    "knowledge_entries": 12,
    "milestones": 3,
    "storage_size_mb": 2.5
  }
}
```

### GET /search
Search stored memories.

**Query Parameters**:
- `q`: Search query (required)
- `category`: Filter by category (optional)

**Response**:
```json
{
  "success": true,
  "query": "Flask development",
  "results": [
    {
      "file": "conversations/claude/scraped_conversation_20240115.md",
      "category": "claude",
      "created": "2024-01-15T10:30:00",
      "snippet": "...Flask application development..."
    }
  ],
  "count": 1
}
```

### GET /health
System health check.

**Response**:
```json
{
  "success": true,
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:00",
  "memory_system": "operational"
}
```

## Supported Platforms

| Platform | URL Pattern | Notes |
|----------|-------------|-------|
| **Claude** | `claude.ai/share/*` | Anthropic's Claude AI |
| **Gemini** | `gemini.google.com/share/*` | Google's Gemini AI |
| **ChatGPT** | `chat.openai.com/share/*` | OpenAI's ChatGPT |
| **Warp** | `app.warp.dev/session/*` | Warp Terminal sessions |

## Configuration

### Environment Variables
- `SECRET_KEY`: Flask secret key for sessions (default: dev key)
- `FLASK_ENV`: Flask environment (development/production)

### Browser Settings
The application uses undetected-chromedriver for web scraping:
- **Headless Mode**: Disabled by default (Cloudflare detection)
- **Timeout**: Configurable per request (default: 20s, Warp: 30s)
- **Retry Logic**: 3 attempts with exponential backoff

## Memory System

### Directory Structure
```
project_memory/
├── conversations/
│   ├── claude/
│   ├── gemini/
│   ├── chatgpt/
│   └── summaries/
├── development/
│   ├── sessions/
│   └── milestones/
├── knowledge_base/
│   ├── technical/
│   └── concepts/
└── timeline/
    ├── daily/
    └── weekly/
```

### File Format
Conversations are saved as Markdown with metadata:
```markdown
# Conversation Memory

**Platform:** claude
**Created:** 2024-01-15T10:30:00
**Word Count:** 800
**Tags:** claude, scraped_conversation, ai_conversation
**Summary:** Discussion about Flask development...

---

## Content

[Conversation content here...]

---
Metadata: {...}
```

## Error Handling

### Platform-Specific Errors
- **Timeouts**: Page load timeouts with platform context
- **Access Denied**: Private/expired conversation links  
- **Network Issues**: Connection and DNS problems
- **Rate Limiting**: Too many requests handling

### Recovery Strategies
- **Retry Logic**: Automatic retry with backoff
- **Browser Restart**: Fresh browser instance on failures
- **Graceful Degradation**: Partial content extraction
- **User Feedback**: Clear error messages and suggestions

## Development

### Local Development
```bash
# Start development server
python app.py

# Access debug mode at http://localhost:5000
# Debug mode enabled by default in development
```

### Production Deployment
```bash
# Set production environment
export FLASK_ENV=production
export SECRET_KEY=your-secure-secret-key

# Use a WSGI server like Gunicorn
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

### Security Considerations
- **CORS**: Configured for localhost by default
- **Input Validation**: URL format and content validation
- **Error Handling**: No sensitive information in error responses
- **Browser Security**: Isolated browser instances
- **File System**: Secure memory system storage paths

## Troubleshooting

### Common Issues

1. **Chrome Driver Issues**:
   ```bash
   # Clear Chrome driver cache
   rm -rf ~/.wdm/drivers/chromedriver/
   ```

2. **Memory System Permissions**:
   ```bash
   # Ensure write permissions
   chmod -R 755 project_memory/
   ```

3. **Port Already in Use**:
   ```bash
   # Kill existing Flask processes
   pkill -f "python app.py"
   ```

4. **Import Errors**:
   ```bash
   # Reinstall dependencies
   pip install -r requirements.txt --force-reinstall
   ```

## Performance

### Optimization Tips
- **Browser Reuse**: Single browser instance across requests
- **Memory Management**: Automatic cleanup of large content
- **Caching**: Static file serving and response caching
- **Async Operations**: Non-blocking scraping operations

### Resource Usage
- **Memory**: ~100MB base + ~50MB per browser instance
- **Storage**: Variable based on conversation length
- **Network**: Depends on target platform response times
- **CPU**: Moderate during active scraping operations

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

## License

This project is part of the SpiralBridge suite and follows the same licensing terms.
