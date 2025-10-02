# Project Structure

## 📁 **Core Components**

### **SmartCaseAI Core**
- `SmartCaseAI/` - Core test case generation logic
- `config.py` - Configuration settings
- `requirements.txt` - Python dependencies

### **API Server**
- `api-server/` - Clean Flask API server
  - `app.py` - Main API server (no HTML)
  - `requirements.txt` - API dependencies
  - `README.md` - API documentation
  - `Procfile`, `railway.json`, `render.yaml` - Deployment configs

### **Web Interfaces**
- `web-interface-two-panel/` - **Recommended** two-panel interface
- `web-interface-working/` - Alternative single-page interface

### **Examples & Testing**
- `example_*.py` - Command-line examples
- `examples/` - Generated test case outputs
- `input_files/` - Supporting files for examples

### **Utilities**
- `start_api_server.py` - Easy server startup script

## 🚀 **Quick Start**

### **Option 1: Web Interface (Recommended)**
```bash
# Start API server
python start_api_server.py

# Open web interface
web-interface-two-panel/index.html
```

### **Option 2: Command Line**
```bash
python example_gemini.py
```

## 📋 **What Was Removed**

- ❌ Old web interfaces (`web-interface/`, `web-interface-simple/`)
- ❌ All GitHub Actions workflows (simplified to local-only)
- ❌ Setup scripts (replaced by `start_api_server.py`)
- ❌ Documentation files (consolidated into main README)
- ❌ `.github/` directory (no longer needed)

## 🎯 **Current Focus**

- **Clean API server** - No HTML, pure JSON API
- **Two web interfaces** - Two-panel (recommended) + single-page
- **Simple deployment** - One working GitHub Action
- **Easy startup** - Single script to start everything
