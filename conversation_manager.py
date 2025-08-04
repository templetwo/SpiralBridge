#!/usr/bin/env python3
"""
SpiralBridge Conversation Manager
Advanced conversation archiving, indexing, and management system

Features:
- Customer vs Personal file separation
- Metadata extraction and indexing
- Search and filtering capabilities
- Privacy and security controls
- Automated organization and labeling

Created for SpiralBridge Multi-platform AI Conversation Scraper
"""

import os
import json
import hashlib
import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
import re

@dataclass
class ConversationMetadata:
    """Comprehensive metadata for archived conversations"""
    file_id: str
    original_url: str
    platform: str
    title: str
    participant_count: int
    message_count: int
    character_count: int
    created_date: str
    archived_date: str
    customer_id: Optional[str] = None
    tags: List[str] = None
    summary: str = ""
    language: str = "en"
    privacy_level: str = "personal"  # personal, customer, confidential
    file_path: str = ""
    file_size: int = 0
    content_hash: str = ""

class ConversationManager:
    """Advanced conversation management system"""
    
    def __init__(self, base_path: str = "memory_logs"):
        self.base_path = Path(base_path)
        self.index_file = self.base_path / "conversation_index.json"
        self.customer_db = self.base_path / "customer_database.json"
        
        # Create enhanced directory structure
        self._setup_directories()
        
        # Load existing indexes
        self.conversation_index = self._load_index()
        self.customer_database = self._load_customer_db()
    
    def _setup_directories(self):
        """Create comprehensive directory structure"""
        directories = [
            # Core platform directories
            "chatgpt/personal",
            "chatgpt/customers",
            "claude/personal", 
            "claude/customers",
            "gemini/personal",
            "gemini/customers",
            
            # Organization directories
            "archived/by_date",
            "archived/by_customer",
            "archived/by_topic",
            
            # System directories
            "exports/json",
            "exports/csv", 
            "exports/markdown",
            "backups",
            "temp",
            
            # Analytics
            "analytics/reports",
            "analytics/trends"
        ]
        
        for directory in directories:
            (self.base_path / directory).mkdir(parents=True, exist_ok=True)
        
        print(f"📁 Enhanced directory structure created in {self.base_path}")
    
    def _load_index(self) -> List[Dict]:
        """Load conversation index"""
        if self.index_file.exists():
            with open(self.index_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []
    
    def _load_customer_db(self) -> Dict:
        """Load customer database"""
        if self.customer_db.exists():
            with open(self.customer_db, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}
    
    def _save_index(self):
        """Save conversation index"""
        with open(self.index_file, 'w', encoding='utf-8') as f:
            json.dump(self.conversation_index, f, indent=2, ensure_ascii=False)
    
    def _save_customer_db(self):
        """Save customer database"""
        with open(self.customer_db, 'w', encoding='utf-8') as f:
            json.dump(self.customer_database, f, indent=2, ensure_ascii=False)
    
    def _generate_file_id(self, url: str, timestamp: str) -> str:
        """Generate unique file ID"""
        content = f"{url}_{timestamp}"
        return hashlib.md5(content.encode()).hexdigest()[:12]
    
    def _extract_metadata_from_file(self, file_path: Path) -> ConversationMetadata:
        """Extract metadata from existing conversation file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Extract basic info from filename
            filename = file_path.name
            platform = file_path.parent.name.split('/')[0]  # Get platform from path
            
            # Try to extract timestamp from filename
            timestamp_match = re.search(r'session-(\d{8}-\d{6})', filename)
            if timestamp_match:
                timestamp_str = timestamp_match.group(1)
                try:
                    created_date = datetime.datetime.strptime(timestamp_str, '%Y%m%d-%H%M%S').isoformat()
                except:
                    created_date = datetime.datetime.now().isoformat()
            else:
                created_date = datetime.datetime.now().isoformat()
            
            # Analyze content
            lines = content.split('\n')
            message_count = len([line for line in lines if line.strip()])
            character_count = len(content)
            
            # Try to extract title from first meaningful line
            title = "Untitled Conversation"
            for line in lines[:10]:
                if line.strip() and len(line.strip()) > 10:
                    title = line.strip()[:100] + ("..." if len(line.strip()) > 100 else "")
                    break
            
            # Generate file hash
            content_hash = hashlib.sha256(content.encode()).hexdigest()[:16]
            
            return ConversationMetadata(
                file_id=self._generate_file_id("unknown", timestamp_str if timestamp_match else ""),
                original_url="unknown",
                platform=platform,
                title=title,
                participant_count=2,  # Default assumption
                message_count=message_count,
                character_count=character_count,
                created_date=created_date,
                archived_date=datetime.datetime.now().isoformat(),
                file_path=str(file_path),
                file_size=file_path.stat().st_size,
                content_hash=content_hash,
                tags=[]
            )
            
        except Exception as e:
            print(f"⚠️  Error extracting metadata from {file_path}: {e}")
            return None
    
    def index_existing_files(self):
        """Index all existing conversation files"""
        print("🔍 Scanning existing conversation files...")
        
        indexed_count = 0
        for file_path in self.base_path.rglob("*.txt"):
            if file_path.name in ["conversation_index.json", "customer_database.json"]:
                continue
                
            # Check if already indexed
            file_hash = hashlib.md5(str(file_path).encode()).hexdigest()
            if any(conv.get('file_path_hash') == file_hash for conv in self.conversation_index):
                continue
            
            metadata = self._extract_metadata_from_file(file_path)
            if metadata:
                conv_dict = asdict(metadata)
                conv_dict['file_path_hash'] = file_hash
                self.conversation_index.append(conv_dict)
                indexed_count += 1
        
        self._save_index()
        print(f"✅ Indexed {indexed_count} conversation files")
        return indexed_count
    
    def add_conversation(self, file_path: str, url: str, platform: str, 
                        customer_id: Optional[str] = None, tags: List[str] = None) -> str:
        """Add new conversation to the system"""
        
        metadata = self._extract_metadata_from_file(Path(file_path))
        if not metadata:
            return None
        
        # Update with provided information
        metadata.original_url = url
        metadata.platform = platform.lower()
        metadata.customer_id = customer_id
        metadata.tags = tags or []
        metadata.privacy_level = "customer" if customer_id else "personal"
        
        # Move file to appropriate directory
        new_path = self._organize_file(Path(file_path), metadata)
        metadata.file_path = str(new_path)
        
        # Add to index
        self.conversation_index.append(asdict(metadata))
        self._save_index()
        
        print(f"✅ Added conversation {metadata.file_id} to archive")
        return metadata.file_id
    
    def _organize_file(self, file_path: Path, metadata: ConversationMetadata) -> Path:
        """Organize file into appropriate directory structure"""
        
        # Determine target directory
        if metadata.customer_id:
            target_dir = self.base_path / metadata.platform / "customers" / metadata.customer_id
        else:
            target_dir = self.base_path / metadata.platform / "personal"
        
        target_dir.mkdir(parents=True, exist_ok=True)
        
        # Create organized filename
        date_str = metadata.created_date[:10]  # YYYY-MM-DD
        safe_title = re.sub(r'[^\w\s-]', '', metadata.title[:50]).strip()
        safe_title = re.sub(r'[-\s]+', '-', safe_title)
        
        new_filename = f"{date_str}_{metadata.file_id}_{safe_title}.txt"
        new_path = target_dir / new_filename
        
        # Move file if different location
        if file_path != new_path:
            file_path.rename(new_path)
        
        return new_path
    
    def search_conversations(self, query: str = "", platform: str = "", 
                           customer_id: str = "", tags: List[str] = None,
                           start_date: str = "", end_date: str = "") -> List[Dict]:
        """Search conversations with multiple filters"""
        
        results = []
        for conv in self.conversation_index:
            # Text search
            if query and query.lower() not in conv.get('title', '').lower():
                continue
            
            # Platform filter
            if platform and conv.get('platform', '').lower() != platform.lower():
                continue
            
            # Customer filter
            if customer_id and conv.get('customer_id') != customer_id:
                continue
            
            # Tags filter
            if tags:
                conv_tags = conv.get('tags', [])
                if not any(tag in conv_tags for tag in tags):
                    continue
            
            # Date range filter
            if start_date and conv.get('created_date', '') < start_date:
                continue
            if end_date and conv.get('created_date', '') > end_date:
                continue
            
            results.append(conv)
        
        return sorted(results, key=lambda x: x.get('created_date', ''), reverse=True)
    
    def generate_report(self, output_format: str = "json") -> str:
        """Generate comprehensive archive report"""
        
        total_conversations = len(self.conversation_index)
        total_characters = sum(conv.get('character_count', 0) for conv in self.conversation_index)
        
        platform_stats = {}
        customer_stats = {}
        monthly_stats = {}
        
        for conv in self.conversation_index:
            # Platform statistics
            platform = conv.get('platform', 'unknown')
            if platform not in platform_stats:
                platform_stats[platform] = {'count': 0, 'characters': 0}
            platform_stats[platform]['count'] += 1
            platform_stats[platform]['characters'] += conv.get('character_count', 0)
            
            # Customer statistics
            customer = conv.get('customer_id', 'personal')
            if customer not in customer_stats:
                customer_stats[customer] = {'count': 0, 'characters': 0}
            customer_stats[customer]['count'] += 1
            customer_stats[customer]['characters'] += conv.get('character_count', 0)
            
            # Monthly statistics
            try:
                month = conv.get('created_date', '')[:7]  # YYYY-MM
                if month not in monthly_stats:
                    monthly_stats[month] = {'count': 0, 'characters': 0}
                monthly_stats[month]['count'] += 1
                monthly_stats[month]['characters'] += conv.get('character_count', 0)
            except:
                pass
        
        report = {
            "summary": {
                "total_conversations": total_conversations,
                "total_characters": total_characters,
                "total_customers": len([c for c in customer_stats.keys() if c != 'personal']),
                "generated_at": datetime.datetime.now().isoformat()
            },
            "platform_breakdown": platform_stats,
            "customer_breakdown": customer_stats,
            "monthly_trends": monthly_stats
        }
        
        # Save report
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = self.base_path / "analytics" / "reports" / f"archive_report_{timestamp}.{output_format}"
        
        if output_format == "json":
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"📊 Report generated: {report_file}")
        return str(report_file)
    
    def export_conversations(self, conversation_ids: List[str], format: str = "json") -> str:
        """Export selected conversations"""
        
        conversations = [conv for conv in self.conversation_index if conv.get('file_id') in conversation_ids]
        
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        export_file = self.base_path / "exports" / format / f"export_{timestamp}.{format}"
        
        if format == "json":
            with open(export_file, 'w', encoding='utf-8') as f:
                json.dump(conversations, f, indent=2, ensure_ascii=False)
        
        print(f"📤 Exported {len(conversations)} conversations to {export_file}")
        return str(export_file)
    
    def add_customer(self, customer_id: str, name: str, email: str = "", 
                    notes: str = "", privacy_level: str = "standard") -> bool:
        """Add new customer to database"""
        
        self.customer_database[customer_id] = {
            "name": name,
            "email": email,
            "notes": notes,
            "privacy_level": privacy_level,
            "added_date": datetime.datetime.now().isoformat(),
            "conversation_count": 0
        }
        
        self._save_customer_db()
        
        # Create customer directory
        for platform in ["chatgpt", "claude", "gemini"]:
            customer_dir = self.base_path / platform / "customers" / customer_id
            customer_dir.mkdir(parents=True, exist_ok=True)
        
        print(f"👤 Added customer: {name} ({customer_id})")
        return True
    
    def get_stats(self) -> Dict:
        """Get comprehensive archive statistics"""
        return {
            "total_conversations": len(self.conversation_index),
            "total_characters": sum(conv.get('character_count', 0) for conv in self.conversation_index),
            "platforms": len(set(conv.get('platform') for conv in self.conversation_index)),
            "customers": len(self.customer_database),
            "personal_conversations": len([c for c in self.conversation_index if not c.get('customer_id')]),
            "customer_conversations": len([c for c in self.conversation_index if c.get('customer_id')])
        }

def main():
    """CLI interface for conversation manager"""
    import argparse
    
    parser = argparse.ArgumentParser(description="SpiralBridge Conversation Manager")
    parser.add_argument("--index", action="store_true", help="Index existing files")
    parser.add_argument("--report", action="store_true", help="Generate archive report")
    parser.add_argument("--stats", action="store_true", help="Show archive statistics")
    parser.add_argument("--search", type=str, help="Search conversations")
    parser.add_argument("--platform", type=str, help="Filter by platform")
    parser.add_argument("--customer", type=str, help="Add customer (format: id:name:email)")
    
    args = parser.parse_args()
    
    manager = ConversationManager()
    
    if args.index:
        manager.index_existing_files()
    
    if args.report:
        report_file = manager.generate_report()
        print(f"📊 Report saved to: {report_file}")
    
    if args.stats:
        stats = manager.get_stats()
        print("\n📈 Archive Statistics:")
        for key, value in stats.items():
            print(f"  {key.replace('_', ' ').title()}: {value:,}")
    
    if args.search:
        results = manager.search_conversations(
            query=args.search, 
            platform=args.platform or ""
        )
        print(f"\n🔍 Found {len(results)} conversations:")
        for conv in results[:10]:  # Show first 10
            print(f"  {conv.get('created_date', '')[:10]} - {conv.get('title', 'Untitled')[:60]}")
    
    if args.customer:
        parts = args.customer.split(':')
        if len(parts) >= 2:
            customer_id, name = parts[0], parts[1]
            email = parts[2] if len(parts) > 2 else ""
            manager.add_customer(customer_id, name, email)

if __name__ == "__main__":
    main()
