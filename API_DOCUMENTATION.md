# SpiralBridge API Documentation

A comprehensive web interface for AI conversation scraping and memory system integration with specialized Warp logging capabilities.

## Table of Contents
- [Supported Platforms](#supported-platforms)
- [REST API Endpoints](#rest-api-endpoints)
- [Request/Response Formats](#requestresponse-formats)
- [Error Codes and Handling](#error-codes-and-handling)
- [Performance Characteristics](#performance-characteristics)
- [Resource Usage](#resource-usage)
- [Warp Logging Subsystem](#warp-logging-subsystem)

## Supported Platforms

### Platform Support Matrix

| Platform | URL Pattern | Status | Notes |
|----------|-------------|--------|-------|
| **Claude** | `claude.ai/share/*` | ✅ Active | Anthropic's Claude AI conversations |
| **Gemini** | `gemini.google.com/share/*`, `g.co/gemini/*`, `bard.google.com/*` | ✅ Active | Google's Gemini/Bard AI |
| **ChatGPT** | `chat.openai.com/share/*`, `chatgpt.com/share/*` | ✅ Active | OpenAI's ChatGPT conversations |
| **Warp** | `app.warp.dev/session/*` | ✅ Active | Warp Terminal sessions with specialized logging |

### URL Detection Algorithm
The system automatically detects platforms using the `detect_platform()` function:
```python
def detect_platform(url):
    url = url.lower()
    if 'claude.ai' in url:
        return 'claude'
    elif 'gemini.google.com' in url or 'g.co' in url or 'bard.google.com' in url:
        return 'gemini'
    elif 'chat.openai.com' in url or 'chatgpt.com' in url:
        return 'chatgpt'
    elif 'app.warp.dev' in url:
        return 'warp'
    else:
        return None
```

## REST API Endpoints

### Core Scraping Endpoints

#### `POST /scrape` (Legacy)
**Description**: Scrape content from AI conversation URLs with retry logic.

**Request Body**:
```json
{
  "url": "https://claude.ai/share/12345",
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
    "url": "https://claude.ai/share/12345",
    "platform": "claude",
    "scraped_at": "2024-01-15T10:30:00",
    "content_length": 5000,
    "word_count": 800,
    "line_count": 100
  },
  "message": "Successfully scraped conversation from CLAUDE"
}
```

#### `POST /extract` (Enhanced)
**Description**: Enhanced conversation extraction with optional chunking support.

**Request Body**:
```json
{
  "url": "https://claude.ai/share/12345",
  "timeout": 20,
  "max_attempts": 3,
  "chunk_size": 4000,
  "enable_chunking": true,
  "preserve_speakers": true
}
```

**Response**:
```json
{
  "success": true,
  "platform": "claude",
  "content": "extracted conversation content...",
  "metadata": {
    "url": "https://claude.ai/share/12345",
    "platform": "claude",
    "scraped_at": "2024-01-15T10:30:00",
    "content_length": 5000,
    "word_count": 800
  },
  "chunks": [
    {
      "content": "first chunk content...",
      "metadata": {
        "chunk_index": 1,
        "chunk_size": 1500,
        "total_chunks": 4
      }
    }
  ],
  "chunking": {
    "enabled": true,
    "total_chunks": 4,
    "chunk_size": 4000,
    "preserve_speakers": true
  },
  "message": "Successfully extracted conversation from CLAUDE and split into 4 chunks"
}
```

#### `POST /chunk`
**Description**: Chunk conversation content into manageable pieces.

**Request Body**:
```json
{
  "content": "long conversation content...",
  "chunk_size": 4000,
  "overlap": 200,
  "preserve_speakers": true
}
```

**Response**:
```json
{
  "success": true,
  "chunks": [
    {
      "content": "chunk content...",
      "metadata": {
        "chunk_index": 1,
        "chunk_size": 3950,
        "overlap_start": 0,
        "overlap_end": 200
      }
    }
  ],
  "metadata": {
    "original_length": 15000,
    "total_chunks": 4,
    "chunk_size_limit": 4000,
    "overlap": 200,
    "preserve_speakers": true,
    "average_chunk_size": 3750.0,
    "chunked_at": "2024-01-15T10:30:00"
  },
  "message": "Successfully chunked content into 4 pieces"
}
```

### Memory System Endpoints

#### `POST /save`
**Description**: Save content to the memory system with metadata.

**Request Body**:
```json
{
  "content": "conversation content to save...",
  "platform": "claude",
  "url": "https://claude.ai/share/12345",
  "session_type": "scraped_conversation",
  "tags": ["claude", "scraped_conversation", "ai_conversation"],
  "summary": "Discussion about Flask development"
}
```

**Response**:
```json
{
  "success": true,
  "memory_path": "/path/to/saved/memory.md",
  "stats": {
    "total_conversations": 16,
    "development_sessions": 8,
    "knowledge_entries": 12,
    "milestones": 3,
    "storage_size_mb": 2.7
  },
  "message": "Content successfully saved to memory system",
  "metadata": {
    "platform": "claude",
    "session_type": "scraped_conversation",
    "tags": ["claude", "scraped_conversation", "ai_conversation"],
    "summary": "Discussion about Flask development",
    "saved_at": "2024-01-15T10:30:00",
    "content_length": 5000,
    "word_count": 800
  }
}
```

#### `GET /stats`
**Description**: Retrieve memory system statistics.

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
  },
  "message": "Statistics retrieved successfully"
}
```

#### `GET /search`
**Description**: Search stored memories with optional category filtering.

**Query Parameters**:
- `q` (required): Search query string
- `category` (optional): Filter by category

**Example**: `GET /search?q=Flask%20development&category=claude`

**Response**:
```json
{
  "success": true,
  "query": "Flask development",
  "category": "claude",
  "results": [
    {
      "file": "conversations/claude/scraped_conversation_20240115.md",
      "category": "claude",
      "created": "2024-01-15T10:30:00",
      "snippet": "...Flask application development..."
    }
  ],
  "count": 1,
  "message": "Found 1 results for \"Flask development\""
}
```

### System Health Endpoints

#### `GET /health`
**Description**: System health check with comprehensive status.

**Response**:
```json
{
  "success": true,
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:00",
  "memory_system": "operational",
  "stats": {
    "total_conversations": 15,
    "storage_size_mb": 2.5
  }
}
```

### Warp Logging Endpoints

#### `GET /warp-status`
**Description**: Get current Warp session state and logging status.

**Response**:
```json
{
  "success": true,
  "warp_state": {
    "tone": "grounding",
    "glyph": "⟁",
    "field": "restabilizing"
  },
  "timestamp": "2024-01-15T10:30:00"
}
```

#### `POST /warp-log`
**Description**: Log Warp messages and update session state.

**Request Body**:
```json
{
  "message": "Initiating field reset due to flow interruption",
  "tone": "confused",
  "glyph": "🜃",
  "state": {
    "tone": "grounding",
    "glyph": "⟁",
    "field": "restabilizing"
  }
}
```

**Response**:
```json
{
  "success": true,
  "message": "Warp entry logged successfully",
  "logged_at": "2024-01-15T10:30:00"
}
```

## Error Codes and Handling

### HTTP Status Codes

| Code | Description | Common Causes |
|------|-------------|---------------|
| `200` | Success | Request completed successfully |
| `400` | Bad Request | Missing required fields, invalid JSON, unsupported platform |
| `401` | Unauthorized | Authentication required (for save endpoint) |
| `404` | Not Found | Endpoint doesn't exist |
| `405` | Method Not Allowed | Wrong HTTP method used |
| `422` | Unprocessable Entity | Valid request but scraping failed |
| `500` | Internal Server Error | Unexpected server errors |

### Platform-Specific Error Handling

#### Claude Errors
```json
{
  "success": false,
  "error": "Scraping failed",
  "message": "Claude Error: Page took too long to load. Claude may be experiencing high traffic or the shared link may be invalid.",
  "platform": "claude"
}
```

#### Gemini Errors
```json
{
  "success": false,
  "error": "Scraping failed", 
  "message": "Gemini Error: Access denied. The conversation may be private or require Google account sign-in.",
  "platform": "gemini"
}
```

#### ChatGPT Errors
```json
{
  "success": false,
  "error": "Scraping failed",
  "message": "ChatGPT Error: Rate limit exceeded. Please wait a few minutes before trying again.",
  "platform": "chatgpt"
}
```

#### Warp Errors
```json
{
  "success": false,
  "error": "Scraping failed",
  "message": "Warp Error: Session load timeout. The session may be expired or you may need to sign in.",
  "platform": "warp"
}
```

### Error Recovery Strategies

1. **Retry Logic**: Automatic retry with exponential backoff (up to 3 attempts)
2. **Browser Restart**: Fresh browser instance on critical failures
3. **Graceful Degradation**: Partial content extraction when possible
4. **User Feedback**: Clear error messages with actionable suggestions
5. **Platform Detection**: Fallback to generic scraping if platform detection fails

## Performance Characteristics

### Timeout Configuration
```python
# Platform-specific timeouts
TIMEOUTS = {
    'claude': 20,    # seconds
    'gemini': 20,    # seconds  
    'chatgpt': 20,   # seconds
    'warp': 30       # longer for JavaScript-heavy content
}
```

### Retry Strategy
- **Max Attempts**: 3 attempts per request
- **Backoff**: 2-3 seconds between attempts
- **Timeout Escalation**: Increases timeout by 50% on each retry

### Browser Management
- **Instance Reuse**: Single browser instance across requests
- **Memory Cleanup**: Automatic cleanup of large content
- **Session Isolation**: Separate sessions for different platforms

### Caching Strategy
- **Static Files**: Cached browser assets
- **Response Caching**: Memory system statistics cached for 30 seconds
- **Content Deduplication**: Prevents saving duplicate conversations

## Resource Usage

### Memory Requirements
- **Base Application**: ~100MB
- **Browser Instance**: ~50MB per instance
- **Content Buffer**: Variable (5-50MB depending on conversation length)
- **Total Typical**: ~200-300MB under normal load

### Storage Requirements
- **Log Files**: ~1-10MB per day (depending on activity)
- **Memory System**: Variable based on conversation count and length
- **Warp Logs**: ~1MB per day for active sessions
- **Browser Cache**: ~50-100MB

### Network Usage
- **Platform Requests**: Depends on target platform response times
- **Typical Latency**: 2-10 seconds per scraping request
- **Bandwidth**: Low (mainly text content)

### CPU Usage
- **Idle**: Low (~1-5% CPU)
- **Active Scraping**: Moderate (~20-40% CPU)
- **Peak Load**: High during multiple concurrent requests (~60-80% CPU)

## Warp Logging Subsystem

### Overview
Specialized logging system for Warp sessions to maintain continuity and prevent tone resets.

### File Structure
```
memory_logs/warp/
├── warp-session-YYYYMMDD-HHMM.txt  # Raw session logs
└── warp-state.json                 # Persistent state tracking
```

### Log Entry Format
```
[HH:MM:SS] glyph tone message content
```

### State Tracking
```json
{
  "tone": "grounding",
  "glyph": "⟁", 
  "field": "restabilizing"
}
```

### Integration Points
- Automatic logging during Warp scraping operations
- State persistence across browser sessions
- Visual status indicators in web interface
- CLI integration for direct logging

### Usage Examples
```python
from warp_log import log_warp_message, save_warp_state

# Log activity
log_warp_message("Field reset initiated", tone="confused", glyph="🜃")

# Update persistent state
save_warp_state({
    "tone": "grounding",
    "glyph": "⟁",
    "field": "restabilizing"
})
```

## Development Notes

### Environment Variables
- `SECRET_KEY`: Flask secret key for sessions
- `FLASK_ENV`: Environment (development/production)

### Security Considerations
- CORS configured for localhost development
- Input validation on all endpoints
- No sensitive information in error responses
- Isolated browser instances for scraping

### Production Deployment
```bash
# Use WSGI server
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5001 app:app
```

---

*This documentation reflects the current state of SpiralBridge API as of the implementation review. For the most up-to-date information, consult the source code and test files.*
