#!/usr/bin/env python3
"""
Setup environment variables for API keys.
"""

import os
import sys

def setup_environment():
    """Setup environment variables for API keys."""
    print("Setting up API Key Environment Variables...")
    print("=" * 50)
    
    # Check current environment
    current_keys = {
        'OPENAI_API_KEY': os.getenv('OPENAI_API_KEY'),
        'GEMINI_API_KEY': os.getenv('GEMINI_API_KEY'),
        'CLAUDE_API_KEY': os.getenv('CLAUDE_API_KEY')
    }
    
    print("Current API Keys:")
    for key_name, key_value in current_keys.items():
        if key_value:
            masked_key = key_value[:8] + "*" * (len(key_value) - 12) + key_value[-4:] if len(key_value) > 12 else "*" * len(key_value)
            print(f"  {key_name}: {masked_key}")
        else:
            print(f"  {key_name}: Not set")
    
    print("\n" + "=" * 50)
    print("To set up your API keys, you have several options:")
    print("\n1. Set environment variables in your system:")
    print("   Windows (PowerShell):")
    print("   $env:OPENAI_API_KEY='your-openai-key-here'")
    print("   $env:GOOGLE_API_KEY='your-google-key-here'")
    print("   $env:ANTHROPIC_API_KEY='your-anthropic-key-here'")
    print("\n   Windows (Command Prompt):")
    print("   set OPENAI_API_KEY=your-openai-key-here")
    print("   set GOOGLE_API_KEY=your-google-key-here")
    print("   set ANTHROPIC_API_KEY=your-anthropic-key-here")
    
    print("\n2. Create a .env file in the api-server directory:")
    print("   OPENAI_API_KEY=your-openai-key-here")
    print("   GOOGLE_API_KEY=your-google-key-here")
    print("   ANTHROPIC_API_KEY=your-anthropic-key-here")
    
    print("\n3. Set them in your IDE/editor environment")
    
    print("\n" + "=" * 50)
    print("API Key Formats:")
    print("  - OpenAI: Starts with 'sk-'")
    print("  - Google: Starts with 'AIzaSy'")
    print("  - Anthropic: Starts with 'sk-ant-'")
    
    print("\n" + "=" * 50)
    print("After setting the keys, restart the API server:")
    print("  python start_api_server.py")

if __name__ == "__main__":
    setup_environment()
