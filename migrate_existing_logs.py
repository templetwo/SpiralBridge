#!/usr/bin/env python3
"""
Migration Script for Existing Conversation Logs
===============================================

Migrates existing conversation logs from the old memory_logs/ directory
to the new organized memory system structure.
"""

import os
from pathlib import Path
from local_memory_system import LocalMemorySystem
import re
import datetime

def migrate_existing_logs():
    """Migrate existing conversation logs to the new memory system."""
    memory_system = LocalMemorySystem()
    old_logs_path = Path("memory_logs")
    
    if not old_logs_path.exists():
        print("❌ No existing memory_logs directory found")
        return
    
    print("=== Migrating Existing Conversation Logs ===\n")
    
    migrated_count = 0
    platforms = ["claude", "chatgpt", "gemini"]
    
    for platform in platforms:
        platform_path = old_logs_path / platform
        if not platform_path.exists():
            continue
            
        print(f"📂 Processing {platform} conversations...")
        
        for log_file in platform_path.glob("*.txt"):
            try:
                # Read the existing log
                with open(log_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                if not content.strip():
                    print(f"  ⚠️  Skipping empty file: {log_file.name}")
                    continue
                
                # Extract timestamp from filename if possible
                timestamp_match = re.search(r'(\d{8}[-_]\d{6})', log_file.name)
                session_type = "archived_conversation"
                
                # Determine tags based on content analysis
                tags = ["migrated", platform]
                if "test" in log_file.name.lower():
                    tags.append("testing")
                if "session" in log_file.name.lower():
                    tags.append("development-session")
                
                # Generate summary based on content
                summary = generate_migration_summary(content, platform)
                
                # Save to new memory system
                saved_path = memory_system.save_conversation_memory(
                    content=content,
                    platform=platform,
                    session_type=session_type,
                    tags=tags,
                    summary=summary
                )
                
                migrated_count += 1
                print(f"  ✅ Migrated: {log_file.name} -> {Path(saved_path).name}")
                
            except Exception as e:
                print(f"  ❌ Error migrating {log_file.name}: {e}")
    
    print(f"\n📊 Migration Summary:")
    print(f"   Total files migrated: {migrated_count}")
    
    # Show updated stats
    stats = memory_system.get_project_stats()
    print(f"   Total conversations in memory system: {stats['total_conversations']}")
    
    # Create migration milestone
    migration_milestone = memory_system.create_milestone_record(
        "Conversation Log Migration",
        f"Successfully migrated {migrated_count} existing conversation logs from old memory_logs structure to new organized memory system.",
        [
            f"Migrated {migrated_count} conversation files",
            "Preserved original content and timestamps where possible",
            "Added appropriate tags and generated summaries",
            "Organized by platform (Claude, ChatGPT, Gemini)",
            "Updated memory system statistics"
        ],
        ["migrate_existing_logs.py", "local_memory_system.py"]
    )
    print(f"📝 Migration milestone recorded: {Path(migration_milestone).name}")

def generate_migration_summary(content: str, platform: str) -> str:
    """Generate a summary for migrated content."""
    lines = [line.strip() for line in content.split('\n') if line.strip()]
    
    if not lines:
        return f"Empty {platform} conversation (migrated)"
    
    # Look for conversation indicators
    user_messages = len([line for line in lines if line.lower().startswith(('user:', 'human:', 'you:'))])
    assistant_messages = len([line for line in lines if line.lower().startswith((f'{platform}:', 'assistant:', 'ai:'))])
    
    # Create summary
    word_count = len(content.split())
    
    if user_messages > 0 or assistant_messages > 0:
        summary = f"Migrated {platform} conversation with ~{user_messages + assistant_messages} messages, {word_count} words"
    else:
        # Try to extract first meaningful line
        meaningful_lines = [line for line in lines if len(line) > 20 and not line.startswith('#')]
        if meaningful_lines:
            first_line = meaningful_lines[0][:100]
            summary = f"Migrated {platform} content: {first_line}..." if len(first_line) == 100 else f"Migrated {platform} content: {first_line}"
        else:
            summary = f"Migrated {platform} conversation, {word_count} words"
    
    return summary

def create_migration_report():
    """Create a detailed migration report."""
    memory_system = LocalMemorySystem()
    
    report_content = f"""# Migration Report - {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}

## Overview
This report documents the migration of existing conversation logs from the old `memory_logs/` directory structure to the new organized memory system.

## Migration Details

### Old Structure
```
memory_logs/
├── claude/
├── chatgpt/
└── gemini/
```

### New Structure
```
project_memory/
├── conversations/
│   ├── claude/
│   ├── chatgpt/
│   ├── gemini/
│   └── summaries/
├── development/
├── knowledge_base/
└── timeline/
```

## Benefits of Migration

1. **Enhanced Organization**: Structured categorization of different memory types
2. **Improved Search**: Full-text search across all memory categories
3. **Metadata Preservation**: Automatic extraction of timestamps, word counts, and content hashes
4. **Backup System**: Automated JSON-based backups
5. **Better Summaries**: Auto-generated summaries for quick reference

## Post-Migration Statistics
{memory_system.get_project_stats()}

## Next Steps

1. Verify migrated content accuracy
2. Test search functionality across migrated conversations
3. Create backup of migrated data
4. Begin using new memory system for ongoing development
5. Consider archiving old memory_logs directory

---
Generated by: migrate_existing_logs.py
"""
    
    report_file = memory_system.save_technical_knowledge(
        "Migration Report",
        report_content,
        "migration",
        ["migrate_existing_logs.py", "local_memory_system.py"]
    )
    
    return report_file

def main():
    """Main migration function."""
    migrate_existing_logs()
    
    # Create detailed migration report
    report_file = create_migration_report()
    print(f"📋 Migration report created: {Path(report_file).name}")
    
    print(f"\n🎯 Next steps:")
    print("1. Review migrated conversations for accuracy")
    print("2. Test search: python local_memory_system.py --search 'your search term'")
    print("3. Create backup: python local_memory_system.py --backup")
    print("4. Consider archiving old memory_logs/ directory")

if __name__ == "__main__":
    main()
