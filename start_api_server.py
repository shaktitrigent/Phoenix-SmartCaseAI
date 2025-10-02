#!/usr/bin/env python3
"""
SmartCaseAI API Server Startup Script
"""

import os
import sys
import subprocess
from pathlib import Path

def check_environment():
    """Check if required environment variables are set."""
    print("Checking environment variables...")
    
    keys = {
        'OPENAI_API_KEY': os.getenv('OPENAI_API_KEY'),
        'GOOGLE_API_KEY': os.getenv('GOOGLE_API_KEY'), 
        'ANTHROPIC_API_KEY': os.getenv('ANTHROPIC_API_KEY')
    }
    
    has_keys = False
    for key_name, key_value in keys.items():
        if key_value:
            masked_key = key_value[:8] + "*" * (len(key_value) - 12) + key_value[-4:] if len(key_value) > 12 else "*" * len(key_value)
            print(f"[OK] {key_name}: {masked_key}")
            has_keys = True
        else:
            print(f"[MISSING] {key_name}: Not set")
    
    if not has_keys:
        print("\n[WARNING] No API keys found!")
        print("[INFO] Set at least one API key:")
        print("  export OPENAI_API_KEY='your-openai-key'")
        print("  export GOOGLE_API_KEY='your-google-key'")
        print("  export ANTHROPIC_API_KEY='your-anthropic-key'")
        print("\n[INFO] Or create a .env file in api-server/ directory")
        return False
    
    return True

def start_server():
    """Start the API server."""
    print("\nStarting SmartCaseAI API Server...")
    print("=" * 50)
    
    # Change to api-server directory
    api_server_dir = Path(__file__).parent / "api-server"
    if not api_server_dir.exists():
        print("[ERROR] api-server directory not found!")
        return False
    
    os.chdir(api_server_dir)
    print(f"[INFO] Working directory: {api_server_dir}")
    
    # Check if requirements are installed
    try:
        import flask
        print("[OK] Flask is installed")
    except ImportError:
        print("[ERROR] Flask not installed. Installing requirements...")
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
    
    # Start the server
    print("\n[INFO] Starting API server...")
    print("[INFO] Server will be available at: http://localhost:5000")
    print("[INFO] Press Ctrl+C to stop the server")
    print("=" * 50)
    
    try:
        subprocess.run([sys.executable, "app.py"])
    except KeyboardInterrupt:
        print("\n[INFO] Server stopped by user")
    except Exception as e:
        print(f"[ERROR] Failed to start server: {e}")
        return False
    
    return True

def main():
    """Main function."""
    print("SmartCaseAI API Server Startup")
    print("=" * 50)
    
    # Check environment
    if not check_environment():
        print("\n[INFO] You can still start the server, but test case generation will fail without API keys.")
        response = input("Continue anyway? (y/N): ")
        if response.lower() != 'y':
            return
    
    # Start server
    start_server()

if __name__ == "__main__":
    main()
