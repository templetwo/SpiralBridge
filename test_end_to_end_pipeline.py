#!/usr/bin/env python3
"""
End-to-End Pipeline Test for SpiralBridge
==========================================

This script demonstrates the complete functionality of the SpiralBridge platform
integration with LocalMemorySystem. It tests the full pipeline from URL detection
through content archiving for all three supported platforms.

Features tested:
- Platform URL detection and validation
- LocalMemorySystem directory structure creation
- Content archiving and indexing
- Search and retrieval functionality
- Statistics and reporting
- Cross-platform compatibility

This serves as both a test and a demonstration of the system's capabilities.
"""

import os
import sys
import time
from pathlib import Path
from datetime import datetime

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import modules
from spiralbridge import detect_platform
from local_memory_system import LocalMemorySystem
from archive_conversation import archive_conversation

def print_header(title):
    """Print a formatted header for sections."""
    print(f"\n{'='*60}")
    print(f"🚀 {title}")
    print(f"{'='*60}")

def print_step(step_num, total_steps, description):
    """Print a formatted step indicator."""
    progress = int((step_num / total_steps) * 20)
    bar = '█' * progress + '░' * (20 - progress)
    percentage = int((step_num / total_steps) * 100)
    print(f"[{bar}] {percentage:3d}% - Step {step_num}/{total_steps}: {description}")

def demonstrate_url_detection():
    """Demonstrate URL detection for all platforms."""
    print_header("URL Detection Demonstration")
    
    # Test URLs for each platform
    test_urls = {
        'Claude': [
            'https://claude.ai/share/abc123def456',
            'https://claude.ai/chat/xyz789',
            'https://claude.ai/share/12345abcde'
        ],
        'Gemini': [
            'https://gemini.google.com/app/123abc456def',
            'https://gemini.google.com/share/xyz789',
            'https://g.co/gemini/abc123',
            'https://bard.google.com/chat/123456'  # Legacy Bard
        ],
        'ChatGPT': [
            'https://chat.openai.com/share/abc123',
            'https://chatgpt.com/share/xyz789',
            'https://chat.openai.com/c/12345abcde'
        ]
    }
    
    print(f"\n🎯 Testing platform detection for {sum(len(urls) for urls in test_urls.values())} URLs...\n")
    
    all_detected = True
    for platform_name, urls in test_urls.items():
        print(f"📋 {platform_name} URLs:")
        for url in urls:
            detected = detect_platform(url)
            expected = platform_name.lower()
            status = "✅" if detected == expected else "❌"
            print(f"  {status} {url}")
            print(f"      Detected: {detected} | Expected: {expected}")
            if detected != expected:
                all_detected = False
        print()
    
    if all_detected:
        print("🎉 All URLs correctly detected!")
    else:
        print("⚠️  Some URLs were not correctly detected.")
    
    return all_detected

def setup_memory_system():
    """Set up and demonstrate LocalMemorySystem initialization."""
    print_header("LocalMemorySystem Setup")
    
    print("🧠 Initializing LocalMemorySystem...")
    memory_system = LocalMemorySystem()
    
    # Check directory structure
    base_path = memory_system.memory_root
    print(f"📁 Base directory: {base_path}")
    
    # Expected platform directories
    platform_dirs = ['claude', 'gemini', 'chatgpt']
    print(f"\n📂 Checking platform directories:")
    
    all_dirs_exist = True
    for platform in platform_dirs:
        dir_path = base_path / 'conversations' / platform
        exists = dir_path.exists()
        status = "✅" if exists else "❌"
        print(f"  {status} conversations/{platform}/")
        if not exists:
            all_dirs_exist = False
    
    print(f"\n🏗️  Directory structure: {'✅ Complete' if all_dirs_exist else '❌ Incomplete'}")
    
    return memory_system, all_dirs_exist

def demonstrate_conversation_archiving(memory_system):
    """Demonstrate conversation archiving for all platforms."""
    print_header("Conversation Archiving Demonstration")
    
    # Sample conversations for each platform
    sample_conversations = {
        'claude': {
            'content': """Human: Hello Claude, I'm working on a Python project and need help with error handling. Can you explain try/except blocks?

Claude: I'd be happy to help you with Python error handling! Try/except blocks are essential for managing errors gracefully in your code.

Here's the basic structure:

```python
try:
    # Code that might raise an exception
    result = 10 / 0
except ZeroDivisionError:
    # Handle specific exception
    print("Cannot divide by zero!")
except Exception as e:
    # Handle any other exception
    print(f"An error occurred: {e}")
else:
    # Executes if no exception occurred
    print("Operation successful!")
finally:
    # Always executes
    print("Cleanup code here")
```""",
            "summary":"Python error handling example with try/except blocks",
            "tags":["python","error handling","example"]
        },
        'gemini': {
            'content': """User: Hi Gemini, what are the main topics in deep learning?

Gemini: Deep learning focuses on artificial neural networks and many layers of processing units for feature extraction and transformation. Key topics include:

1. Neural networks and architecture
2. Convolutional networks for image data
3. Recurrent networks for sequence data
4. Generative models for creative tasks

These fundamentals are crucial for understanding advances in AI.

User: Can you elaborate on convolutional networks?

Gemini: Convolutional Neural Networks (CNNs) are designed for processing structured grid data like images. They use layers of convolution, pooling, and fully connected layers to automatically learn spatial hierarchies in images.""",
            "summary":"Deep learning fundamentals overview with focus on CNNs",
            "tags":["deep learning","cnn","ai"]
        },
        'chatgpt': {
            'content': """User: Hello ChatGPT, tell me about the benefits of functional programming.

ChatGPT: Functional programming offers several advantages:

- **Immutability**: Variables do not change state or value, promoting safer and more predictable code.
- **First-class functions**: Functions are treated as first-class citizens and can be passed as arguments, returned from other functions, and assigned to variables.
- **Pure functions**: These functions have no side effects, and their output depends solely on their input, enhancing testability and reusability.

User: How does that compare to object-oriented programming?

ChatGPT: While object-oriented programming organizes code using objects to encapsulate data and behavior, functional programming emphasizes computation avoiding mutable state and changing data, leading to simpler, more reliable code.""",
            "summary":"Functional programming benefits compared to OOP",
            "tags":["functional programming","oop","programming paradigms"]
        }
    }
    
    print(f"\nArchiving {len(sample_conversations)} conversations to LocalMemorySystem...")
    
    archived_files = []
    for platform, details in sample_conversations.items():
        print(f"Archiving {platform.upper()} conversation...")
        memory_file = memory_system.save_conversation_memory(
            content=details['content'],
            platform=platform,
            session_type="end_to_end_demo",
            tags=details['tags'],
            summary=details['summary']
        )
        
        archived_files.append(memory_file)
        print(f"Archived to: {os.path.basename(memory_file)}")
    
    return archived_files

def demonstrate_memory_search_and_statistics(memory_system, archived_files):
    """Demonstrate search and statistics functionality."""
    print_header("Memory Search and Statistics Demonstration")
    
    # Show basic statistics
    stats = memory_system.get_project_stats()
    print(f"\n📊 Memory Statistics:")
    print(f"  Total conversations: {stats['total_conversations']}")
    print(f"  Storage size: {stats['storage_size_mb']} MB")
    
    # Perform a search
    search_query = "CNNs"
    print(f"\n🔍 Searching for '{search_query}'...")
    search_results = memory_system.search_memories(search_query)
    
    print(f"\nSearch results for '{search_query}': {len(search_results)} found")
    for result in search_results:
        print(f"- {result['file']}: {result['snippet'][:50]}...")
    
    return len(search_results)

def main():
    """Main function to run the demonstration."""
    print_header("SpiralBridge End-to-End Pipeline Demonstration")
    
    num_steps = 4
    step = 1
    print_step(step, num_steps, "Detecting URLs")
    if not demonstrate_url_detection():
        print("❌ URL detection failed. Exiting...")
        return
    
    step += 1
    print_step(step, num_steps, "Setting up LocalMemorySystem")
    memory_system, dirs_ok = setup_memory_system()
    if not dirs_ok:
        print("❌ Directory setup incomplete. Exiting...")
        return
    
    step += 1
    print_step(step, num_steps, "Archiving conversations")
    archived_files = demonstrate_conversation_archiving(memory_system)
    
    step += 1
    print_step(step, num_steps, "Searching and showing statistics")
    found_results = demonstrate_memory_search_and_statistics(memory_system, archived_files)
    
    if found_results:
        print("🎉 End-to-end demonstration completed successfully!")
    else:
        print("⚠️  End-to-end demonstration encountered issues.")

if __name__ == "__main__":
    main()
