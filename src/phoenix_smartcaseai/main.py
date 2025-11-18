"""
Main entry point for running Phoenix-SmartCaseAI as a web service.
"""

import os
import sys
import uvicorn
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
env_path = Path(__file__).parent.parent.parent / ".env"
if env_path.exists():
    load_dotenv(env_path)
else:
    # Also try loading from current directory
    load_dotenv()


def main():
    """Run the FastAPI web service."""
    # Get configuration from environment variables
    host = os.getenv("APP_HOST", "0.0.0.0")
    port = int(os.getenv("APP_PORT", "8000"))
    debug = os.getenv("DEBUG", "False").lower() == "true"
    reload = debug  # Auto-reload in debug mode
    
    print("=" * 60)
    print("Phoenix-SmartCaseAI Web Service")
    print("=" * 60)
    print(f"Host: {host}")
    print(f"Port: {port}")
    print(f"Debug: {debug}")
    print(f"Access the web interface at: http://localhost:{port}")
    print("=" * 60)
    
    # Import here to avoid issues if dependencies aren't installed
    from .web_app import app
    
    # Run the server
    uvicorn.run(
        app,
        host=host,
        port=port,
        reload=reload,
        log_level="debug" if debug else "info"
    )


if __name__ == "__main__":
    main()

