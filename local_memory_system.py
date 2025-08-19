#!/usr/bin/env python3
"""
Local Memory System for SpiralBridge Project
============================================

A comprehensive system for organizing project knowledge, conversation history,
development notes, and technical documentation locally.

Features:
- Structured memory storage with categories
- Auto-tagging and metadata extraction
- Search and retrieval system
- Timeline tracking of project evolution
- Knowledge base with technical insights
- Session summaries and key learnings
"""

import os
import json
import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
import re
import hashlib

class LocalMemorySystem:
    """Manages local memory storage and organization for the SpiralBridge project."""
    
    def __init__(self, base_path: str = None):
        self.base_path = Path(base_path) if base_path else Path.cwd()
        self.memory_root = self.base_path / "project_memory"
        self.setup_directory_structure()
        
    def setup_directory_structure(self):
        """Create the organized directory structure for local memory."""
        directories = [
            "conversations/claude",
            "conversations/chatgpt", 
            "conversations/gemini",
            "conversations/summaries",
            "development/sessions",
            "development/milestones",
            "development/challenges",
            "development/solutions",
            "knowledge_base/technical",
            "knowledge_base/concepts",
            "knowledge_base/resources",
            "timeline/daily",
            "timeline/weekly",
            "timeline/monthly",
            "backups",
            "exports"
        ]
        
        for directory in directories:
            (self.memory_root / directory).mkdir(parents=True, exist_ok=True)
    
    def save_conversation_memory(self, content: str, platform: str, 
                                session_type: str = "development", 
                                tags: List[str] = None,
                                summary: str = None,
                                title: str = None,
                                date: str = None,
                                notes: str = None,
                                url: str = None,
                                metadata: Dict[str, Any] = None) -> str:
        """Save a conversation with enhanced metadata and return the file path."""
        # Use custom date if provided, otherwise use current timestamp
        if date:
            try:
                # Parse the date if it's a string
                if isinstance(date, str):
                    parsed_date = datetime.datetime.fromisoformat(date.replace('Z', '+00:00'))
                else:
                    parsed_date = date
                timestamp = parsed_date.strftime("%Y%m%d_%H%M%S")
            except (ValueError, TypeError):
                timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        else:
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            
        # Create filename with title if provided
        if title:
            safe_title = re.sub(r'[^\w\-_]', '_', title.lower())[:50]  # Limit length
            filename = f"{session_type}_{timestamp}_{safe_title}.md"
        else:
            filename = f"{session_type}_{timestamp}.md"
            
        file_path = self.memory_root / "conversations" / platform / filename
        
        # Extract and enhance metadata
        enhanced_metadata = self._extract_conversation_metadata(
            content, platform, tags, summary, title, date, notes, url, metadata
        )
        
        # Create markdown format with enhanced metadata header
        markdown_content = self._create_enhanced_markdown_memory(content, enhanced_metadata)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(markdown_content)
        
        # Update index with enhanced metadata
        self._update_conversation_index(file_path, enhanced_metadata)
        
        return str(file_path)
    
    def save_development_session(self, session_data: Dict[str, Any]) -> str:
        """Save a development session with achievements, challenges, and next steps."""
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"session_{timestamp}.md"
        file_path = self.memory_root / "development" / "sessions" / filename
        
        session_md = f"""# Development Session - {datetime.datetime.now().strftime("%Y-%m-%d %H:%M")}

## Objectives
{session_data.get('objectives', 'Not specified')}

## Achievements
{self._format_list(session_data.get('achievements', []))}

## Challenges Encountered
{self._format_list(session_data.get('challenges', []))}

## Solutions Implemented
{self._format_list(session_data.get('solutions', []))}

## Code Changes
{session_data.get('code_changes', 'None recorded')}

## Next Steps
{self._format_list(session_data.get('next_steps', []))}

## Notes
{session_data.get('notes', 'No additional notes')}

## Files Modified
{self._format_list(session_data.get('files_modified', []))}

---
Tags: {', '.join(session_data.get('tags', []))}
"""
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(session_md)
        
        return str(file_path)
    
    def save_technical_knowledge(self, topic: str, content: str, 
                                category: str = "general",
                                related_files: List[str] = None) -> str:
        """Save technical knowledge and insights."""
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_topic = re.sub(r'[^\w\-_]', '_', topic.lower())
        filename = f"{safe_topic}_{timestamp}.md"
        file_path = self.memory_root / "knowledge_base" / "technical" / filename
        
        knowledge_md = f"""# {topic}

**Category:** {category}  
**Created:** {datetime.datetime.now().strftime("%Y-%m-%d %H:%M")}  
**Related Files:** {', '.join(related_files or [])}

## Content
{content}

## Context
This knowledge was captured during development of the SpiralBridge project.

---
Category: {category}
"""
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(knowledge_md)
        
        return str(file_path)
    
    def create_milestone_record(self, milestone: str, description: str, 
                               achievements: List[str] = None,
                               files_involved: List[str] = None) -> str:
        """Record a project milestone."""
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_milestone = re.sub(r'[^\w\-_]', '_', milestone.lower())
        filename = f"{safe_milestone}_{timestamp}.md"
        file_path = self.memory_root / "development" / "milestones" / filename
        
        milestone_md = f"""# Milestone: {milestone}

**Date:** {datetime.datetime.now().strftime("%Y-%m-%d %H:%M")}

## Description
{description}

## Key Achievements
{self._format_list(achievements or [])}

## Files Involved
{self._format_list(files_involved or [])}

## Impact
This milestone represents significant progress in the SpiralBridge project development.

---
Milestone: {milestone}
"""
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(milestone_md)
        
        return str(file_path)
    
    def create_daily_summary(self, summary_data: Dict[str, Any]) -> str:
        """Create a daily summary of activities and progress."""
        today = datetime.date.today().strftime("%Y%m%d")
        filename = f"daily_summary_{today}.md"
        file_path = self.memory_root / "timeline" / "daily" / filename
        
        summary_md = f"""# Daily Summary - {datetime.date.today().strftime("%B %d, %Y")}

## Overview
{summary_data.get('overview', 'No overview provided')}

## Key Activities
{self._format_list(summary_data.get('activities', []))}

## Progress Made
{self._format_list(summary_data.get('progress', []))}

## Challenges
{self._format_list(summary_data.get('challenges', []))}

## Learnings
{self._format_list(summary_data.get('learnings', []))}

## Tomorrow's Plan
{self._format_list(summary_data.get('tomorrow_plan', []))}

---
Date: {today}
"""
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(summary_md)
        
        return str(file_path)
    
    def search_memories(self, query: str, category: str = None, 
                       date_range: tuple = None) -> List[Dict[str, Any]]:
        """Search through stored memories."""
        results = []
        search_dirs = []
        
        if category:
            if category in ["conversations", "development", "knowledge_base", "timeline"]:
                search_dirs = [self.memory_root / category]
        else:
            search_dirs = [
                self.memory_root / "conversations",
                self.memory_root / "development", 
                self.memory_root / "knowledge_base",
                self.memory_root / "timeline"
            ]
        
        for search_dir in search_dirs:
            if search_dir.exists():
                for file_path in search_dir.rglob("*.md"):
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                            if query.lower() in content.lower():
                                results.append({
                                    'file': str(file_path),
                                    'category': file_path.parent.name,
                                    'created': datetime.datetime.fromtimestamp(
                                        file_path.stat().st_mtime
                                    ).isoformat(),
                                    'snippet': self._extract_snippet(content, query)
                                })
                    except Exception as e:
                        continue
        
        return results
    
    def get_project_stats(self) -> Dict[str, Any]:
        """Get statistics about the stored memories."""
        stats = {
            'total_conversations': 0,
            'development_sessions': 0,
            'knowledge_entries': 0,
            'milestones': 0,
            'daily_summaries': 0,
            'storage_size_mb': 0
        }
        
        # Count files in each category
        categories = {
            'total_conversations': 'conversations',
            'development_sessions': 'development/sessions',
            'knowledge_entries': 'knowledge_base',
            'milestones': 'development/milestones',
            'daily_summaries': 'timeline/daily'
        }
        
        total_size = 0
        for stat_key, dir_path in categories.items():
            full_path = self.memory_root / dir_path
            if full_path.exists():
                files = list(full_path.rglob("*.md"))
                stats[stat_key] = len(files)
                for file_path in files:
                    total_size += file_path.stat().st_size
        
        stats['storage_size_mb'] = round(total_size / (1024 * 1024), 2)
        return stats
    
    def export_memory_backup(self, backup_name: str = None) -> str:
        """Create a backup export of all memories."""
        if not backup_name:
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_name = f"memory_backup_{timestamp}"
        
        backup_path = self.memory_root / "backups" / f"{backup_name}.json"
        
        backup_data = {
            'created': datetime.datetime.now().isoformat(),
            'stats': self.get_project_stats(),
            'memories': []
        }
        
        # Collect all markdown files
        for md_file in self.memory_root.rglob("*.md"):
            if "backups" not in str(md_file):
                try:
                    with open(md_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                        backup_data['memories'].append({
                            'file_path': str(md_file.relative_to(self.memory_root)),
                            'content': content,
                            'created': datetime.datetime.fromtimestamp(
                                md_file.stat().st_mtime
                            ).isoformat()
                        })
                except Exception as e:
                    continue
        
        with open(backup_path, 'w', encoding='utf-8') as f:
            json.dump(backup_data, f, indent=2, ensure_ascii=False)
        
        return str(backup_path)
    
    # Helper methods
    def _extract_conversation_metadata(self, content: str, platform: str, 
                                     tags: List[str] = None, 
                                     summary: str = None,
                                     title: str = None,
                                     date: str = None,
                                     notes: str = None,
                                     url: str = None,
                                     metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """Extract enhanced metadata from conversation content."""
        word_count = len(content.split())
        lines = content.split('\n')
        
        # Base metadata
        enhanced_metadata = {
            'platform': platform,
            'word_count': word_count,
            'line_count': len(lines),
            'created': datetime.datetime.now().isoformat(),
            'tags': tags or [],
            'summary': summary or self._auto_generate_summary(content),
            'content_hash': hashlib.md5(content.encode()).hexdigest()[:8],
            'title': title or self._extract_title_from_content(content),
            'custom_date': date,
            'notes': notes or '',
            'source_url': url or '',
            'file_size': len(content.encode('utf-8'))
        }
        
        # Merge any additional metadata
        if metadata:
            enhanced_metadata.update(metadata)
        
        # Extract conversation participants if detectable
        participants = self._detect_conversation_participants(content)
        if participants:
            enhanced_metadata['participants'] = participants
        
        # Detect conversation topics/themes
        topics = self._extract_topics(content)
        if topics:
            enhanced_metadata['topics'] = topics
            
        return enhanced_metadata
    
    def _create_markdown_memory(self, content: str, metadata: Dict[str, Any]) -> str:
        """Create formatted markdown with metadata header."""
        return f"""# Conversation Memory

**Platform:** {metadata['platform']}  
**Created:** {metadata['created']}  
**Word Count:** {metadata['word_count']}  
**Tags:** {', '.join(metadata['tags'])}  
**Summary:** {metadata['summary']}

---

## Content

{content}

---
Metadata: {json.dumps(metadata, indent=2)}
"""
    
    def _auto_generate_summary(self, content: str) -> str:
        """Generate a basic summary from content."""
        lines = [line.strip() for line in content.split('\n') if line.strip()]
        if not lines:
            return "Empty conversation"
        
        # Take first few meaningful lines as summary
        summary_lines = []
        for line in lines:
            if len(line) > 20 and not line.startswith('#'):
                summary_lines.append(line)
                if len(summary_lines) >= 2:
                    break
        
        summary = ' '.join(summary_lines)
        return summary[:200] + '...' if len(summary) > 200 else summary
    
    def _format_list(self, items: List[str]) -> str:
        """Format a list as markdown bullets."""
        if not items:
            return "- None recorded"
        return '\n'.join(f"- {item}" for item in items)
    
    def _extract_snippet(self, content: str, query: str, context_chars: int = 200) -> str:
        """Extract a snippet around the search query."""
        lower_content = content.lower()
        lower_query = query.lower()
        
        pos = lower_content.find(lower_query)
        if pos == -1:
            return content[:context_chars] + '...'
        
        start = max(0, pos - context_chars // 2)
        end = min(len(content), pos + len(query) + context_chars // 2)
        
        snippet = content[start:end]
        if start > 0:
            snippet = '...' + snippet
        if end < len(content):
            snippet = snippet + '...'
        
        return snippet
    
    def _create_enhanced_markdown_memory(self, content: str, metadata: Dict[str, Any]) -> str:
        """Create enhanced markdown with comprehensive metadata header."""
        # Format the display date
        display_date = metadata.get('custom_date', metadata.get('created', ''))
        if display_date:
            try:
                if 'T' in display_date:
                    date_obj = datetime.datetime.fromisoformat(display_date.replace('Z', '+00:00'))
                    display_date = date_obj.strftime("%B %d, %Y at %I:%M %p")
            except (ValueError, TypeError):
                display_date = str(display_date)
        
        # Create platform emoji mapping
        platform_emojis = {
            'claude': '🧠',
            'gemini': '✨', 
            'chatgpt': '💬',
            'warp': '⚡',
            'other': '🤖'
        }
        
        platform_emoji = platform_emojis.get(metadata['platform'], '🤖')
        
        return f"""# {metadata['title']}

{platform_emoji} **Platform:** {metadata['platform'].title()}  
📅 **Date:** {display_date}  
📊 **Stats:** {metadata['word_count']} words, {metadata['line_count']} lines  
🏷️ **Tags:** {', '.join(metadata.get('tags', []))}  
📝 **Summary:** {metadata.get('summary', 'No summary available')}

{('🔗 **Source:** ' + metadata['source_url']) if metadata.get('source_url') else ''}
{('📋 **Notes:** ' + metadata['notes']) if metadata.get('notes') else ''}
{('👥 **Participants:** ' + ', '.join(metadata['participants'])) if metadata.get('participants') else ''}
{('🎯 **Topics:** ' + ', '.join(metadata['topics'])) if metadata.get('topics') else ''}

---

## Conversation Content

{content}

---

### Metadata
```json
{json.dumps(metadata, indent=2, ensure_ascii=False)}
```

**File Hash:** `{metadata['content_hash']}`  
**Size:** {metadata.get('file_size', 0)} bytes  
**Archived:** {metadata['created']}
"""
    
    def _extract_title_from_content(self, content: str) -> str:
        """Extract or generate a meaningful title from content."""
        lines = [line.strip() for line in content.split('\n') if line.strip()]
        
        if not lines:
            return "Empty Conversation"
        
        # Look for title-like patterns
        for line in lines[:5]:  # Check first 5 lines
            # Skip very short lines or lines with only symbols
            if len(line) < 10 or line.count('#') > 2:
                continue
                
            # Clean up common artifacts
            clean_line = re.sub(r'^[#*\-\s]+', '', line)
            clean_line = re.sub(r'[#*\-\s]+$', '', clean_line)
            
            # If it looks like a reasonable title, use it
            if 20 <= len(clean_line) <= 100 and not clean_line.lower().startswith(('user:', 'assistant:', 'human:')):
                return clean_line
        
        # Fallback: use first substantial line
        for line in lines[:10]:
            if len(line) > 15 and ':' not in line[:20]:  # Avoid role indicators
                title = line[:80] + ('...' if len(line) > 80 else '')
                return title
        
        return "Untitled Conversation"
    
    def _detect_conversation_participants(self, content: str) -> List[str]:
        """Detect conversation participants from content."""
        participants = set()
        
        # Common role patterns
        role_patterns = [
            r'^(User|Human|You):\s*',
            r'^(Assistant|AI|Claude|Gemini|ChatGPT|GPT|Warp):\s*',
            r'^\*\*(User|Human|Assistant|AI|Claude|Gemini|ChatGPT|GPT|Warp)\*\*:\s*'
        ]
        
        lines = content.split('\n')
        for line in lines:
            line = line.strip()
            for pattern in role_patterns:
                match = re.match(pattern, line, re.IGNORECASE)
                if match:
                    role = match.group(1).lower()
                    # Normalize role names
                    if role in ['user', 'human', 'you']:
                        participants.add('User')
                    elif role in ['assistant', 'ai']:
                        participants.add('Assistant')
                    else:
                        participants.add(role.title())
        
        return sorted(list(participants))
    
    def _extract_topics(self, content: str) -> List[str]:
        """Extract key topics/themes from conversation content."""
        topics = set()
        
        # Simple keyword-based topic extraction
        topic_keywords = {
            'Programming': ['code', 'programming', 'development', 'coding', 'software', 'function', 'class', 'variable'],
            'Web Development': ['html', 'css', 'javascript', 'react', 'vue', 'angular', 'web', 'frontend', 'backend'],
            'Data Science': ['data', 'analysis', 'machine learning', 'ai', 'model', 'dataset', 'statistics'],
            'Database': ['sql', 'database', 'query', 'table', 'mysql', 'postgresql', 'mongodb'],
            'DevOps': ['docker', 'kubernetes', 'deployment', 'cloud', 'aws', 'azure', 'server'],
            'Testing': ['test', 'testing', 'unit test', 'integration', 'debugging', 'bug'],
            'API': ['api', 'rest', 'graphql', 'endpoint', 'http', 'request', 'response'],
            'UI/UX': ['design', 'user interface', 'user experience', 'ui', 'ux', 'layout', 'styling']
        }
        
        content_lower = content.lower()
        
        for topic, keywords in topic_keywords.items():
            keyword_count = sum(1 for keyword in keywords if keyword in content_lower)
            # If multiple keywords from a topic are found, include the topic
            if keyword_count >= 2:
                topics.add(topic)
        
        return sorted(list(topics))
    
    def _update_conversation_index(self, file_path: Path, metadata: Dict[str, Any]):
        """Update the conversation index for faster searching."""
        index_path = self.memory_root / "conversations" / "index.json"
        
        try:
            if index_path.exists():
                with open(index_path, 'r', encoding='utf-8') as f:
                    index = json.load(f)
            else:
                index = {'conversations': []}
            
            # Create index entry with enhanced metadata
            index_entry = {
                'file': str(file_path.relative_to(self.memory_root)),
                'file_path': str(file_path),
                'metadata': metadata,
                'indexed_at': datetime.datetime.now().isoformat()
            }
            
            index['conversations'].append(index_entry)
            
            # Sort by date (newest first)
            index['conversations'].sort(
                key=lambda x: x['metadata'].get('custom_date', x['metadata'].get('created', '')),
                reverse=True
            )
            
            with open(index_path, 'w', encoding='utf-8') as f:
                json.dump(index, f, indent=2, ensure_ascii=False)
        
        except Exception as e:
            print(f"Warning: Could not update conversation index: {e}")


def main():
    """CLI interface for the local memory system."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Local Memory System for SpiralBridge")
    parser.add_argument('--init', action='store_true', help='Initialize memory system')
    parser.add_argument('--stats', action='store_true', help='Show memory statistics')
    parser.add_argument('--search', type=str, help='Search memories')
    parser.add_argument('--backup', action='store_true', help='Create backup')
    parser.add_argument('--session', action='store_true', help='Start development session recording')
    
    args = parser.parse_args()
    
    memory_system = LocalMemorySystem()
    
    if args.init:
        memory_system.setup_directory_structure()
        print(f"Memory system initialized at: {memory_system.memory_root}")
    
    elif args.stats:
        stats = memory_system.get_project_stats()
        print("\n=== Project Memory Statistics ===")
        for key, value in stats.items():
            print(f"{key.replace('_', ' ').title()}: {value}")
    
    elif args.search:
        results = memory_system.search_memories(args.search)
        print(f"\n=== Search Results for '{args.search}' ===")
        for result in results:
            print(f"\nFile: {result['file']}")
            print(f"Category: {result['category']}")
            print(f"Created: {result['created']}")
            print(f"Snippet: {result['snippet']}")
            print("-" * 50)
    
    elif args.backup:
        backup_path = memory_system.export_memory_backup()
        print(f"Backup created: {backup_path}")
    
    elif args.session:
        print("Development session recording mode - implement interactive session...")
    
    else:
        print("Use --help for available commands")


if __name__ == "__main__":
    main()
