# SpiralBridge Local Memory System - Quick Guide

## Overview
The local memory system provides organized storage and retrieval of project knowledge, conversations, and development progress. It works independently of repository visibility, making it perfect for private repositories while maintaining AI assistance capabilities.

## Directory Structure
```
project_memory/
├── conversations/          # AI conversation archives
│   ├── claude/            # Claude conversations
│   ├── chatgpt/           # ChatGPT conversations  
│   ├── gemini/            # Gemini conversations
│   └── summaries/         # Conversation summaries
├── development/           # Development tracking
│   ├── sessions/          # Daily development sessions
│   ├── milestones/        # Project milestones
│   ├── challenges/        # Problems encountered
│   └── solutions/         # Solutions implemented
├── knowledge_base/        # Technical knowledge
│   ├── technical/         # Technical insights
│   ├── concepts/          # Conceptual knowledge
│   └── resources/         # External resources
├── timeline/             # Time-based organization
│   ├── daily/            # Daily summaries
│   ├── weekly/           # Weekly reviews
│   └── monthly/          # Monthly reviews
├── backups/              # Automated backups
└── exports/              # Data exports
```

## Quick Commands

### Basic Operations
```bash
# Show memory statistics
python local_memory_system.py --stats

# Search all memories
python local_memory_system.py --search "your search term"

# Create backup
python local_memory_system.py --backup

# Initialize (if needed)
python local_memory_system.py --init
```

### Capture Operations
```bash
# Capture current session
python capture_memory.py session

# Quick note capture
python capture_memory.py note "Your insight or note here"
```

## Daily Workflow

### 1. Start of Development Session
```bash
# Capture session objectives and plan
python capture_memory.py session
```

### 2. During Development
```bash
# Quick notes for insights
python capture_memory.py note "Discovered that X approach works better because Y"

# Save technical knowledge
# (Use the Python API for more detailed technical knowledge)
```

### 3. End of Session
```bash
# Update session with achievements and next steps
# Create backup
python local_memory_system.py --backup
```

### 4. Weekly Review
```bash
# Search recent work
python local_memory_system.py --search "this week"

# Review statistics
python local_memory_system.py --stats
```

## Python API Usage

### Save Conversation
```python
from local_memory_system import LocalMemorySystem

memory_system = LocalMemorySystem()

# Save a conversation
file_path = memory_system.save_conversation_memory(
    content="Your conversation content here",
    platform="claude",  # or "chatgpt", "gemini"
    session_type="development",
    tags=["debugging", "api-integration"],
    summary="Session focused on fixing API integration issues"
)
```

### Save Development Session
```python
session_data = {
    'objectives': ['Fix bug in scraper', 'Add error handling'],
    'achievements': ['Implemented retry logic', 'Added user feedback'],
    'challenges': ['Complex CSS selectors', 'Rate limiting'],
    'solutions': ['Used multiple selectors', 'Added delays'],
    'next_steps': ['Test with more URLs', 'Add logging'],
    'tags': ['bug-fix', 'scraping']
}

session_file = memory_system.save_development_session(session_data)
```

### Save Technical Knowledge
```python
knowledge_file = memory_system.save_technical_knowledge(
    topic="Selenium Best Practices",
    content="Key insights about web scraping with Selenium...",
    category="web-scraping",
    related_files=["spiralbridge.py", "test_scraper.py"]
)
```

### Search Memories
```python
results = memory_system.search_memories(
    query="selenium",
    category="knowledge_base"  # optional filter
)

for result in results:
    print(f"Found in: {result['file']}")
    print(f"Snippet: {result['snippet']}")
```

## Working with Private Repositories

### When Repository is Private
1. **Before making private**: Run backup and ensure all memories are captured
2. **During development**: Use memory system to share context with AI
3. **For AI assistance**: Copy relevant memories to share specific context

### Sharing Context with AI
```bash
# Find relevant memories
python local_memory_system.py --search "error handling"

# Copy specific files to share with AI
cat project_memory/knowledge_base/technical/selenium_best_practices_*.md
```

## Best Practices

### Daily Habits
- Start each session with `capture_memory.py session`
- Capture insights immediately with quick notes
- End sessions with updated achievements and next steps
- Weekly backup and review

### Organization Tips
- Use consistent tagging for easy retrieval
- Write meaningful summaries for future reference
- Keep technical knowledge focused and actionable
- Regular cleanup of outdated information

### Search Strategies
- Use specific technical terms for precise results
- Search by category when looking for specific types of content
- Combine multiple searches to narrow down results
- Review snippets to find most relevant memories

## Migration and Backup

### Migrating Existing Logs
```bash
# One-time migration of existing conversation logs
python migrate_existing_logs.py
```

### Regular Backups
```bash
# Create timestamped backup
python local_memory_system.py --backup

# Backups are saved as JSON in project_memory/backups/
```

### Exporting for Sharing
```python
# Create backup for sharing specific knowledge
backup_path = memory_system.export_memory_backup("client_project_context")
```

## Troubleshooting

### Common Issues
- **Permission errors**: Ensure write access to project directory
- **Import errors**: Make sure you're in the correct directory
- **Search not working**: Check file encoding and content format

### Recovery
- Backups are stored in JSON format for easy restoration
- Original conversation logs are preserved during migration
- All operations create timestamped files to avoid overwrites

## Integration with Development

### Version Control
- Memory system works alongside Git
- Markdown format is version-control friendly
- Can be included in repository or kept separate

### AI Assistant Workflow
1. Use memory system to maintain project context
2. Share relevant memories when asking for help
3. Capture insights and solutions back into memory system
4. Build cumulative knowledge base over time

---

**Files**: `local_memory_system.py`, `capture_memory.py`, `migrate_existing_logs.py`
**Created**: 2025-08-02  
**Last Updated**: 2025-08-02
