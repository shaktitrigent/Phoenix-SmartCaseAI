#!/usr/bin/env python3
"""
Simple server manager for Phoenix-SmartCaseAI
Usage:
    python server_manager.py start    - Start the server
    python server_manager.py stop     - Stop the server
    python server_manager.py restart  - Restart the server
    python server_manager.py status   - Check server status
"""

import sys
import subprocess
import time
import os
from pathlib import Path

def get_python_executable():
    """Get the correct Python executable, preferring venv if available."""
    project_root = Path(__file__).parent
    
    # Check for virtual environment
    if sys.platform == "win32":
        venv_python = project_root / "venv" / "Scripts" / "python.exe"
    else:
        venv_python = project_root / "venv" / "bin" / "python"
    
    if venv_python.exists():
        return str(venv_python)
    
    # Fallback to system Python
    return sys.executable

def find_server_process():
    """Find the server process running on port 8000."""
    try:
        if sys.platform == "win32":
            # Windows: Use netstat to find process on port 8000
            result = subprocess.run(
                ['netstat', '-ano'],
                capture_output=True,
                text=True
            )
            for line in result.stdout.split('\n'):
                if ':8000' in line and 'LISTENING' in line:
                    parts = line.split()
                    if len(parts) > 4:
                        return parts[-1]
        else:
            # Linux/Mac: Use lsof
            result = subprocess.run(
                ['lsof', '-ti:8000'],
                capture_output=True,
                text=True
            )
            if result.returncode == 0 and result.stdout.strip():
                return result.stdout.strip().split('\n')[0]
    except Exception:
        pass
    return None

def start_server():
    """Start the web server."""
    print("=" * 60)
    print("Starting Phoenix-SmartCaseAI Web Service")
    print("=" * 60)
    print()
    
    # Check if server is already running
    pid = find_server_process()
    if pid:
        print(f"[WARNING] Server is already running (PID: {pid})")
        print("   Use 'python server_manager.py stop' to stop it first")
        return
    
    try:
        # Get the correct Python executable
        python_exe = get_python_executable()
        
        # Start the server
        subprocess.Popen([
            python_exe, "-m", "phoenix_smartcaseai.main"
        ], cwd=Path(__file__).parent)
        
        # Wait a moment and check if it started
        time.sleep(3)
        pid = find_server_process()
        if pid:
            print(f"[OK] Server started successfully!")
            print(f"   Process ID: {pid}")
            print(f"   Access at: http://localhost:8000")
        else:
            print("[INFO] Server may be starting...")
            print("   Check http://localhost:8000 in a few seconds")
    except Exception as e:
        print(f"[ERROR] Failed to start server: {e}")

def stop_server():
    """Stop the web server."""
    print("=" * 60)
    print("Stopping Phoenix-SmartCaseAI Web Service")
    print("=" * 60)
    print()
    
    pid = find_server_process()
    if not pid:
        print("[INFO] No server process found on port 8000")
        return
    
    try:
        if sys.platform == "win32":
            subprocess.run(['taskkill', '/F', '/PID', pid], 
                         capture_output=True)
        else:
            subprocess.run(['kill', '-9', pid], capture_output=True)
        
        time.sleep(1)
        
        # Verify it's stopped
        if not find_server_process():
            print("[OK] Server stopped successfully")
        else:
            print("[WARNING] Server may still be running")
    except Exception as e:
        print(f"[ERROR] Failed to stop server: {e}")

def restart_server():
    """Restart the web server."""
    print("=" * 60)
    print("Restarting Phoenix-SmartCaseAI Web Service")
    print("=" * 60)
    print()
    
    stop_server()
    time.sleep(2)
    start_server()

def check_status():
    """Check server status."""
    print("=" * 60)
    print("Phoenix-SmartCaseAI Server Status")
    print("=" * 60)
    print()
    
    pid = find_server_process()
    if pid:
        print(f"[OK] Server is RUNNING")
        print(f"   Process ID: {pid}")
        print(f"   Port: 8000")
        print(f"   URL: http://localhost:8000")
        
        # Try to check health endpoint
        try:
            import urllib.request
            response = urllib.request.urlopen('http://localhost:8000/health', timeout=2)
            if response.status == 200:
                print("   Health: [OK] Healthy")
        except:
            print("   Health: [WARNING] Not responding")
    else:
        print("[ERROR] Server is NOT running")
        print("   Use 'python server_manager.py start' to start it")

def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    
    command = sys.argv[1].lower()
    
    if command == "start":
        start_server()
    elif command == "stop":
        stop_server()
    elif command == "restart":
        restart_server()
    elif command == "status":
        check_status()
    else:
        print(f"Unknown command: {command}")
        print(__doc__)
        sys.exit(1)

if __name__ == "__main__":
    main()

