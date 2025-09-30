# 🔧 GitHub Setup Guide

## Fix GitHub Actions Permission Issues

The error you're seeing is due to GitHub Actions permissions. Here's how to fix it:

### Option 1: Enable GitHub Pages (Recommended)

1. **Go to Repository Settings:**
   - Navigate to your repository on GitHub
   - Click "Settings" tab
   - Scroll down to "Pages" section

2. **Configure GitHub Pages:**
   - Source: "GitHub Actions"
   - Save the settings

3. **Run the Workflow:**
   - Go to "Actions" tab
   - Select "Manual Web Interface" workflow
   - Click "Run workflow"
   - Choose "github-pages" as deployment method

### Option 2: Use Simple Static Hosting

If you don't want to use GitHub Pages, you can host the web interface anywhere:

1. **Download the Files:**
   - Go to "Actions" tab
   - Run "Manual Web Interface" workflow
   - Choose "download-only" as deployment method
   - Download the "web-interface-files" artifact

2. **Host Anywhere:**
   - **Netlify**: Drag & drop the files
   - **Vercel**: Connect your GitHub repository
   - **GitHub Pages**: Upload to a separate repository
   - **Any static host**: Upload the files

### Option 3: Local Development

Run the web interface locally:

```bash
# Clone the repository
git clone https://github.com/shaktitrigent/Phoenix-SmartCaseAI.git
cd Phoenix-SmartCaseAI

# Serve the web interface
cd web-interface-simple
python -m http.server 8000

# Open http://localhost:8000
```

### Option 4: Use the API Server

For full functionality with file uploads and AI processing:

```bash
# Run the API server
cd api-server
pip install -r requirements.txt
python app.py

# Open http://localhost:5000
```

## 🚀 Quick Start (No GitHub Actions Required)

### Method 1: Direct File Hosting

1. **Copy the web interface files:**
   ```bash
   # Copy web-interface-simple/index.html to any web server
   ```

2. **Host on any platform:**
   - **Netlify**: Drag & drop the `web-interface-simple` folder
   - **Vercel**: Connect your GitHub repo and select the folder
   - **GitHub Pages**: Create a new repository and upload the files

### Method 2: Use GitHub Actions (Fixed)

1. **Enable Pages in repository settings**
2. **Run the "Manual Web Interface" workflow**
3. **Choose "github-pages" deployment method**

### Method 3: API Server Deployment

1. **Deploy the API server:**
   ```bash
   ./deploy.sh
   # Choose your preferred platform
   ```

2. **Access the full web interface with AI processing**

## 🔑 Required API Keys

For full functionality, you need at least one API key:

### OpenAI
```bash
export OPENAI_API_KEY="sk-..."
```

### Google Gemini
```bash
export GOOGLE_API_KEY="..."
```

### Anthropic Claude
```bash
export ANTHROPIC_API_KEY="sk-ant-..."
```

## 📋 Troubleshooting

### GitHub Actions Permission Error
- **Solution**: Enable GitHub Pages in repository settings
- **Alternative**: Use the manual deployment workflow

### API Key Issues
- **Check**: API keys are correctly formatted
- **Verify**: Keys have sufficient quota
- **Test**: Use the local development option first

### File Upload Issues
- **Check**: File size (max 16MB)
- **Verify**: File format is supported
- **Test**: Use the API server for full functionality

## 🎯 Recommended Setup

1. **For Quick Demo**: Use `web-interface-simple/index.html` on any static host
2. **For Full Features**: Deploy the API server using `./deploy.sh`
3. **For GitHub Integration**: Enable Pages and use the workflows

## 📞 Need Help?

- **GitHub Issues**: Create an issue in the repository
- **Documentation**: Check `DEPLOYMENT.md` for detailed instructions
- **Examples**: See the `examples/` folder for usage examples

---

**The web interface is now ready to use! 🎉**
