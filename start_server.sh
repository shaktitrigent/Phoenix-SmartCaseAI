#!/bin/bash
echo "============================================================"
echo "Starting Phoenix-SmartCaseAI Web Service"
echo "============================================================"
echo ""

# Activate virtual environment if it exists
if [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
    python -m phoenix_smartcaseai.main
else
    echo "[WARNING] Virtual environment not found. Using system Python."
    python -m phoenix_smartcaseai.main
fi

