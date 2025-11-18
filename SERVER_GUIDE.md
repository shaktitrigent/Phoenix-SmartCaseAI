# Phoenix-SmartCaseAI Server Management Guide

Simple commands to start, stop, and manage the web server.

## Quick Start

### Windows (PowerShell/CMD)

**Start Server:**
```bash
# Option 1: Double-click
start_server.bat

# Option 2: Command line
python server_manager.py start
```

**Stop Server:**
```bash
# Option 1: Double-click
stop_server.bat

# Option 2: Command line
python server_manager.py stop
```

**Check Status:**
```bash
python server_manager.py status
```

**Restart Server:**
```bash
python server_manager.py restart
```

### Linux/Mac (Bash)

**Start Server:**
```bash
# Option 1: Make executable and run
chmod +x start_server.sh
./start_server.sh

# Option 2: Command line
python server_manager.py start
```

**Stop Server:**
```bash
# Option 1: Make executable and run
chmod +x stop_server.sh
./stop_server.sh

# Option 2: Command line
python server_manager.py stop
```

**Check Status:**
```bash
python server_manager.py status
```

**Restart Server:**
```bash
python server_manager.py restart
```

## Server Manager Commands

The `server_manager.py` script provides a unified way to manage the server:

```bash
# Start the server
python server_manager.py start

# Stop the server
python server_manager.py stop

# Restart the server
python server_manager.py restart

# Check server status
python server_manager.py status
```

## Manual Start/Stop

If you prefer to start/stop manually:

**Start:**
```bash
python -m phoenix_smartcaseai.main
```

**Stop:**
- Press `Ctrl+C` in the terminal where the server is running
- Or use `python server_manager.py stop`

## Access the Web Interface

Once the server is running, open your browser and go to:
- **Web Interface:** http://localhost:8000
- **Health Check:** http://localhost:8000/health
- **API Docs:** http://localhost:8000/docs (FastAPI auto-generated docs)

## Troubleshooting

### Port Already in Use

If port 8000 is already in use:
```bash
# Check what's using the port
python server_manager.py status

# Stop the existing server
python server_manager.py stop

# Or change the port in .env file
# APP_PORT=8001
```

### Server Won't Start

1. Check if virtual environment is activated
2. Verify dependencies are installed: `pip install -e .`
3. Check API keys are set in environment variables
4. Review error messages in the terminal

### Server Won't Stop

```bash
# Force stop using server manager
python server_manager.py stop

# Or manually find and kill the process
# Windows:
netstat -ano | findstr :8000
taskkill /F /PID <process_id>

# Linux/Mac:
lsof -ti:8000 | xargs kill -9
```

