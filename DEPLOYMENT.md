# 🚀 AI Test Case Generator - Deployment Guide

This guide covers multiple deployment options for the AI Test Case Generator, from GitHub Actions to cloud platforms.

## 📋 Table of Contents

- [GitHub Actions (On-Demand)](#github-actions-on-demand)
- [GitHub Pages (Web Interface)](#github-pages-web-interface)
- [Cloud Platform Deployment](#cloud-platform-deployment)
- [Local Development](#local-development)
- [API Documentation](#api-documentation)

## 🎯 GitHub Actions (On-Demand)

### Setup

1. **Add API Keys to Repository Secrets:**
   ```
   OPENAI_API_KEY=sk-...
   GOOGLE_API_KEY=...
   ANTHROPIC_API_KEY=sk-ant-...
   ```

2. **Run the Workflow:**
   - Go to Actions tab in your repository
   - Select "AI Test Case Generator"
   - Click "Run workflow"
   - Fill in the form:
     - **User Story:** Your requirements
     - **LLM Provider:** Choose AI provider
     - **Output Format:** Plain, BDD, or Both
     - **Number of Test Cases:** 1-50
     - **Email:** Optional for notifications

3. **Download Results:**
   - Check the workflow run
   - Download artifacts from the "Artifacts" section
   - Files include: `test_cases_plain.md`, `test_cases_bdd.md`

### Features
- ✅ No setup required
- ✅ Uses your repository's API keys
- ✅ Generates files as downloadable artifacts
- ✅ Supports file uploads via workflow inputs
- ✅ Email notifications (if configured)

## 🌐 GitHub Pages (Web Interface)

### Setup

1. **Enable GitHub Pages:**
   - Go to Settings → Pages
   - Source: "GitHub Actions"

2. **Deploy:**
   - Push to main branch
   - The web interface will be available at: `https://yourusername.github.io/Phoenix-SmartCaseAI`

3. **Custom Domain (Optional):**
   - Edit `.github/workflows/deploy-web-interface.yml`
   - Replace `your-domain.com` with your domain

### Features
- ✅ Beautiful web interface
- ✅ Drag & drop file uploads
- ✅ Real-time progress indicators
- ✅ Multiple AI provider options
- ✅ Download results as ZIP

## ☁️ Cloud Platform Deployment

### Option 1: Heroku

1. **Install Heroku CLI:**
   ```bash
   # Install from https://devcenter.heroku.com/articles/heroku-cli
   ```

2. **Deploy:**
   ```bash
   cd api-server
   heroku create your-app-name
   heroku config:set OPENAI_API_KEY=sk-...
   heroku config:set GOOGLE_API_KEY=...
   heroku config:set ANTHROPIC_API_KEY=sk-ant-...
   git subtree push --prefix=api-server heroku main
   ```

### Option 2: Railway

1. **Connect Repository:**
   - Go to [Railway.app](https://railway.app)
   - Connect your GitHub repository
   - Select the `api-server` folder

2. **Set Environment Variables:**
   ```
   OPENAI_API_KEY=sk-...
   GOOGLE_API_KEY=...
   ANTHROPIC_API_KEY=sk-ant-...
   ```

3. **Deploy:**
   - Railway automatically detects the `railway.json` config
   - Deploys with zero configuration

### Option 3: Render

1. **Create Web Service:**
   - Go to [Render.com](https://render.com)
   - Connect your GitHub repository
   - Select "Web Service"
   - Choose the `api-server` folder

2. **Configure:**
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn app:app`
   - Environment Variables:
     ```
     OPENAI_API_KEY=sk-...
     GOOGLE_API_KEY=...
     ANTHROPIC_API_KEY=sk-ant-...
     ```

### Option 4: Vercel

1. **Install Vercel CLI:**
   ```bash
   npm i -g vercel
   ```

2. **Deploy:**
   ```bash
   cd api-server
   vercel --prod
   ```

3. **Set Environment Variables:**
   - Go to Vercel dashboard
   - Add environment variables in project settings

## 🛠️ Local Development

### Quick Start

1. **Clone Repository:**
   ```bash
   git clone https://github.com/yourusername/Phoenix-SmartCaseAI.git
   cd Phoenix-SmartCaseAI
   ```

2. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   cd api-server
   pip install -r requirements.txt
   ```

3. **Set Environment Variables:**
   ```bash
   export OPENAI_API_KEY="sk-..."
   export GOOGLE_API_KEY="..."
   export ANTHROPIC_API_KEY="sk-ant-..."
   ```

4. **Run API Server:**
   ```bash
   python app.py
   ```

5. **Access Web Interface:**
   - Open http://localhost:5000
   - Use the web form to generate test cases

### Development Features
- ✅ Hot reload during development
- ✅ Debug mode with detailed error messages
- ✅ Local file storage for uploads/outputs
- ✅ CORS enabled for cross-origin requests

## 📚 API Documentation

### Endpoints

#### `GET /`
- **Description:** Web interface
- **Response:** HTML form for test case generation

#### `POST /api/generate`
- **Description:** Generate test cases
- **Content-Type:** `multipart/form-data`
- **Parameters:**
  - `user_story` (string, required): User story or requirements
  - `llm_provider` (string): AI provider (openai, gemini, claude, all)
  - `output_format` (string): Output format (plain, bdd, both)
  - `num_cases` (number): Number of test cases (1-50)
  - `files` (file[]): Supporting files (optional)
  - `email` (string): Email for results (optional)

- **Response:**
  ```json
  {
    "success": true,
    "session_id": "uuid",
    "provider": "openai",
    "num_cases": 10,
    "files_used": 3,
    "generation_time": 1.8,
    "plain_file": "session_plain.md",
    "bdd_file": "session_bdd.md",
    "preview": "Test case preview..."
  }
  ```

#### `GET /api/download/<session_id>`
- **Description:** Download all files as ZIP
- **Response:** ZIP file with all generated test cases

#### `GET /api/file/<filename>`
- **Description:** Download individual file
- **Response:** Markdown file

#### `GET /api/health`
- **Description:** Health check
- **Response:**
  ```json
  {
    "status": "healthy",
    "timestamp": "2024-01-01T00:00:00"
  }
  ```

### Example Usage

#### cURL
```bash
curl -X POST http://localhost:5000/api/generate \
  -F "user_story=As a user, I want to login" \
  -F "llm_provider=openai" \
  -F "output_format=both" \
  -F "num_cases=5" \
  -F "files=@requirements.txt"
```

#### Python
```python
import requests

response = requests.post('http://localhost:5000/api/generate', 
    data={
        'user_story': 'As a user, I want to login',
        'llm_provider': 'openai',
        'output_format': 'both',
        'num_cases': 5
    },
    files={'files': open('requirements.txt', 'rb')}
)

result = response.json()
print(f"Generated {result['num_cases']} test cases")
```

#### JavaScript
```javascript
const formData = new FormData();
formData.append('user_story', 'As a user, I want to login');
formData.append('llm_provider', 'openai');
formData.append('output_format', 'both');
formData.append('num_cases', '5');

fetch('/api/generate', {
    method: 'POST',
    body: formData
})
.then(response => response.json())
.then(data => console.log(data));
```

## 🔧 Configuration

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `OPENAI_API_KEY` | OpenAI API key | For OpenAI provider |
| `GOOGLE_API_KEY` | Google API key | For Gemini provider |
| `ANTHROPIC_API_KEY` | Anthropic API key | For Claude provider |
| `PORT` | Server port | No (default: 5000) |

### File Upload Limits

- **Max file size:** 16MB per file
- **Supported formats:** .txt, .pdf, .docx, .json, .csv, .xml, .png, .jpg, .jpeg, .webp
- **Multiple files:** Supported

### Output Formats

#### Plain English
- Step-by-step test instructions
- Clear expected results
- Easy to understand for non-technical stakeholders

#### BDD/Gherkin
- Given-When-Then format
- Feature and scenario structure
- Compatible with Cucumber, SpecFlow, etc.

## 🚨 Troubleshooting

### Common Issues

1. **API Key Errors:**
   - Verify API keys are correctly set
   - Check key format (OpenAI: sk-..., Claude: sk-ant-...)
   - Ensure keys have sufficient quota

2. **File Upload Issues:**
   - Check file size (max 16MB)
   - Verify file format is supported
   - Ensure proper multipart encoding

3. **Generation Failures:**
   - Check internet connectivity
   - Verify API provider status
   - Review error messages in response

4. **Deployment Issues:**
   - Ensure all environment variables are set
   - Check platform-specific requirements
   - Review deployment logs

### Debug Mode

Enable debug mode for detailed error messages:
```bash
export FLASK_DEBUG=1
python app.py
```

## 📈 Performance

### Optimization Tips

1. **File Processing:**
   - Use smaller files when possible
   - Compress images before upload
   - Limit number of files per request

2. **API Usage:**
   - Monitor API quotas
   - Use appropriate provider for file type
   - Cache results when possible

3. **Deployment:**
   - Use production WSGI server (gunicorn)
   - Enable compression
   - Set up monitoring

## 🔒 Security

### Best Practices

1. **API Keys:**
   - Never commit API keys to repository
   - Use environment variables
   - Rotate keys regularly

2. **File Uploads:**
   - Validate file types
   - Scan for malware
   - Limit file sizes

3. **Rate Limiting:**
   - Implement request rate limiting
   - Monitor usage patterns
   - Set up alerts

## 📞 Support

- **GitHub Issues:** [Create an issue](https://github.com/yourusername/Phoenix-SmartCaseAI/issues)
- **Documentation:** [Read the docs](https://github.com/yourusername/Phoenix-SmartCaseAI/wiki)
- **Examples:** [Check examples](https://github.com/yourusername/Phoenix-SmartCaseAI/tree/main/examples)

---

**Happy Testing! 🎉**
