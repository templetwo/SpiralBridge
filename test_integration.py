#!/usr/bin/env python3
"""
Test script for SpiralBridge integration functions
=================================================

Tests the newly integrated extract_conversation_from_url and chunk_conversation functions.
"""

import sys
from spiralbridge import extract_conversation_from_url, chunk_conversation, detect_platform

def test_platform_detection():
    """Test platform detection function."""
    print("🧪 Testing platform detection...")
    
    test_urls = [
        ("https://claude.ai/share/12345", "claude"),
        ("https://gemini.google.com/share/abcdef", "gemini"),
        ("https://chat.openai.com/share/xyz789", "chatgpt"),
        ("https://app.warp.dev/session/session123", "warp"),
        ("https://example.com/unknown", None)
    ]
    
    for url, expected in test_urls:
        result = detect_platform(url)
        status = "✅" if result == expected else "❌"
        print(f"  {status} {url} → {result} (expected: {expected})")
    
    print()

def test_chunk_conversation():
    """Test conversation chunking function."""
    print("🧪 Testing conversation chunking...")
    
    # Sample conversation content
    sample_content = (
        "User: Hello, can you help me with Python programming?\n"
        "Assistant: Sure! What do you need help with specifically?\n"
        "User: I'm trying to understand how to use loops.\n"
        "Assistant: Great! Let's go through loops together.\n"
        "User: What's the difference between a for loop and a while loop?\n"
        "Assistant: For loops iterate over a sequence.\n"
        "User: Okay, can you give me an example?\n"
        "Assistant: Certainly. Here's a basic example...\n"
        )
    
    # Test chunking
    chunks = chunk_conversation(sample_content, chunk_size=50, overlap=0, preserve_speakers=True)
    
    print("Total chunks created:", len(chunks))
    for index, chunk in enumerate(chunks):
        print(f"Chunk {index + 1}:")
        print(chunk['content'])
        print("-" * 40)
    
    print()

def main():
    test_platform_detection()
    test_chunk_conversation()
    

if __name__ == "__main__":
    main()
