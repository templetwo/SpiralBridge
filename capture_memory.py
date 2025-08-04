#!/usr/bin/env python3
"""
Quick Memory Capture Script
===========================

A simple script to quickly capture conversations, development sessions,
and project insights into the local memory system.
"""

from local_memory_system import LocalMemorySystem
import datetime
import sys

def capture_current_session():
    """Capture the current conversation/session state."""
    memory_system = LocalMemorySystem()
    
    print("=== SpiralBridge Memory Capture ===")
    print("Capturing current session state...\n")
    
    # Current session summary based on our conversation
    session_data = {
        'objectives': [
            'Set up comprehensive local memory system for SpiralBridge project',
            'Organize existing conversation logs and project knowledge',
            'Create structured approach for capturing development progress',
            'Prepare for making repository private while maintaining AI assistance capability'
        ],
        'achievements': [
            'Created LocalMemorySystem class with comprehensive memory organization',
            'Implemented structured directory system for different types of memories',
            'Added search and backup functionality for memories',
            'Created metadata extraction and auto-summarization features',
            'Built CLI interface for memory system management',
            'Designed markdown-based format for easy reading and version control'
        ],
        'challenges': [
            'Need to transition from public to private repository while maintaining AI help',
            'Managing large conversation histories and extracting key insights',
            'Balancing automated organization with manual curation needs',
            'Ensuring memory system doesn\'t become overwhelming to maintain'
        ],
        'solutions': [
            'Created local memory system to work independently of repository visibility',
            'Implemented search and filtering to make large memory collections manageable',
            'Used markdown format for human-readable but structured storage',
            'Added backup and export functionality for data preservation',
            'Created modular system that can grow with project needs'
        ],
        'code_changes': 'Created local_memory_system.py with comprehensive memory management capabilities',
        'next_steps': [
            'Initialize the memory system directory structure',
            'Migrate existing conversation logs to new organized format',
            'Test search and backup functionality',
            'Create first development session record',
            'Set up daily/weekly summary workflow',
            'Make repository private and test continued development workflow'
        ],
        'notes': '''
        The local memory system provides several key benefits:
        1. Independence from repository visibility (works with private repos)
        2. Structured organization of different types of project knowledge
        3. Search capability across all stored memories
        4. Backup and export functionality for data preservation
        5. CLI interface for easy daily use
        6. Markdown format for human readability and version control
        
        This system will allow continued AI assistance even with a private repository
        by enabling easy sharing of relevant context and project history.
        ''',
        'files_modified': [
            'local_memory_system.py (created)',
            'capture_memory.py (created)'
        ],
        'tags': ['memory-system', 'organization', 'privacy', 'knowledge-management']
    }
    
    # Save the session
    session_file = memory_system.save_development_session(session_data)
    print(f"✅ Development session saved: {session_file}")
    
    # Save key technical knowledge
    technical_knowledge = """
# Local Memory System Architecture

## Overview
The LocalMemorySystem class provides a comprehensive solution for organizing project knowledge locally, independent of repository visibility.

## Key Components

### Directory Structure
- `conversations/` - Platform-specific conversation archives (claude, chatgpt, gemini)
- `development/` - Development sessions, milestones, challenges, solutions
- `knowledge_base/` - Technical knowledge, concepts, resources
- `timeline/` - Daily, weekly, monthly summaries
- `backups/` - Automated backups in JSON format
- `exports/` - Data exports and sharing formats

### Features
1. **Metadata Extraction**: Automatic extraction of word counts, timestamps, content hashes
2. **Search Functionality**: Full-text search across all memory categories
3. **Backup System**: JSON-based backups with metadata preservation
4. **CLI Interface**: Command-line tools for daily operations
5. **Markdown Format**: Human-readable, version-control friendly format

### Usage Patterns
- Daily session recording for development progress
- Technical knowledge capture during problem-solving
- Milestone recording for project tracking
- Conversation archival with automatic summarization
- Search and retrieval for past insights

## Benefits for Private Repository Development
- Enables AI assistance without repository access
- Preserves project context and history
- Facilitates knowledge sharing through selective exports
- Maintains development continuity across privacy boundaries
"""
    
    knowledge_file = memory_system.save_technical_knowledge(
        "Local Memory System Architecture",
        technical_knowledge,
        "system-design",
        ["local_memory_system.py", "capture_memory.py"]
    )
    print(f"✅ Technical knowledge saved: {knowledge_file}")
    
    # Create milestone record
    milestone_file = memory_system.create_milestone_record(
        "Local Memory System Implementation",
        "Successfully implemented comprehensive local memory system for SpiralBridge project, enabling organized knowledge management and continued AI assistance with private repositories.",
        [
            "Created LocalMemorySystem class with full memory management capabilities",
            "Established structured directory organization for different memory types",
            "Implemented search, backup, and export functionality",
            "Built CLI interface for daily usage",
            "Designed markdown-based storage format for human readability",
            "Created capture script for easy session recording"
        ],
        ["local_memory_system.py", "capture_memory.py"]
    )
    print(f"✅ Milestone recorded: {milestone_file}")
    
    # Show stats
    stats = memory_system.get_project_stats()
    print(f"\n=== Memory System Statistics ===")
    for key, value in stats.items():
        print(f"{key.replace('_', ' ').title()}: {value}")
    
    print(f"\n🎯 Memory system location: {memory_system.memory_root}")
    print("\n📝 Next steps:")
    print("1. Run: python local_memory_system.py --init")
    print("2. Run: python local_memory_system.py --stats")
    print("3. Test search: python local_memory_system.py --search 'memory system'")
    print("4. Create backup: python local_memory_system.py --backup")

def quick_note():
    """Quickly save a development note or insight."""
    if len(sys.argv) < 2:
        print("Usage: python capture_memory.py note 'Your note content here'")
        return
    
    note_content = ' '.join(sys.argv[2:])
    memory_system = LocalMemorySystem()
    
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    knowledge_file = memory_system.save_technical_knowledge(
        f"Quick Note {timestamp}",
        note_content,
        "development-notes"
    )
    
    print(f"✅ Quick note saved: {knowledge_file}")

def main():
    """Main function for memory capture operations."""
    if len(sys.argv) > 1:
        command = sys.argv[1]
        if command == "session":
            capture_current_session()
        elif command == "note":
            quick_note()
        else:
            print("Available commands: session, note")
    else:
        capture_current_session()

if __name__ == "__main__":
    main()
