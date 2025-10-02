# SmartCaseAI API Server - Local Usage

A clean Flask-based API server for generating test cases using AI. **This guide is for local development only - no deployment needed.**

## 🚀 Quick Start (Local Only)

### **Option 1: Easy Startup (Recommended)**
```bash
# From the main project directory
python start_api_server.py
```

### **Option 2: Manual Startup**
```bash
# 1. Navigate to API server directory
cd api-server

# 2. Install dependencies
pip install -r requirements.txt

# 3. Set API keys (at least one required)
set GOOGLE_API_KEY=your-google-key        # For Gemini
set OPENAI_API_KEY=your-openai-key        # For OpenAI  
set ANTHROPIC_API_KEY=your-anthropic-key  # For Claude

# 4. Start the server
python app.py
```

### **Option 3: PowerShell (Windows)**
```powershell
# Set API keys
$env:GOOGLE_API_KEY="your-google-key"
$env:OPENAI_API_KEY="your-openai-key"

# Start server
cd api-server
python app.py
```

## 🌐 Using the Web Interface

Once the server is running:

1. **Open your browser**
2. **Go to:** `http://localhost:5000`
3. **Or use the web interfaces:**
   - `../web-interface-two-panel/index.html` - **Two-panel interface (Recommended)**
   - `../web-interface-working/index.html` - Single-page interface

## 📋 What You'll See

### **Server Status:**
- **API Server:** `http://localhost:5000` - JSON API endpoints
- **Web Interface:** Open the HTML files in your browser
- **Generated Files:** Saved in `api-server/outputs/` directory

### **API Endpoints (for developers):**
- `GET /` - Server status and documentation
- `POST /api/generate` - Generate test cases
- `GET /api/download/<session_id>` - Download ZIP files
- `GET /api/health` - Health check

## 🔑 API Keys Setup

You need at least **one** API key to generate test cases:

### **Google Gemini (Recommended - You have this key):**
```bash
set GOOGLE_API_KEY=AIzaSyAR***************************Xi7E
```

### **OpenAI (Optional):**
```bash
set OPENAI_API_KEY=sk-your-openai-key-here
```

### **Anthropic Claude (Optional):**
```bash
set ANTHROPIC_API_KEY=sk-ant-your-anthropic-key-here
```

## 🎯 How to Use

### **Step 1: Start the Server**
```bash
python start_api_server.py
```

### **Step 2: Open Web Interface**
- Open `web-interface-two-panel/index.html` in your browser
- You'll see a two-panel interface:
  - **Left Panel:** Input user story, select AI provider, upload files
  - **Right Panel:** View generated test cases, copy, export

### **Step 3: Generate Test Cases**
1. **Enter your user story** in the left panel
2. **Select AI provider** (recommend Gemini since you have that key)
3. **Upload supporting files** (optional)
4. **Click "Generate Test Cases"**
5. **View results** in the right panel
6. **Copy or export** the generated test cases

## 🔧 Troubleshooting

### **"API Disconnected" Error:**
- Make sure the server is running: `python start_api_server.py`
- Check that the server is accessible at `http://localhost:5000`

### **"No API keys found" Error:**
- Set at least one API key (see API Keys Setup above)
- Restart the server after setting keys

### **"Failed to generate test cases" Error:**
- Check your API key is valid and has quota
- Try a different AI provider
- Check the server logs for detailed error messages

## 📁 File Locations

- **API Server:** `api-server/app.py`
- **Web Interfaces:** `web-interface-two-panel/` and `web-interface-working/`
- **Generated Files:** `api-server/outputs/`
- **Supporting Files:** `input_files/` (for examples)

## 🎉 That's It!

No deployment, no cloud setup, no complex configuration. Just run the server locally and use the web interface to generate test cases!
