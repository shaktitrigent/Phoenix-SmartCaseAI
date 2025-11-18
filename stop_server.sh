#!/bin/bash
echo "============================================================"
echo "Stopping Phoenix-SmartCaseAI Web Service"
echo "============================================================"
echo ""

# Find and kill processes on port 8000
lsof -ti:8000 | xargs kill -9 2>/dev/null
pkill -f "phoenix_smartcaseai.main" 2>/dev/null

echo "Server stopped."

