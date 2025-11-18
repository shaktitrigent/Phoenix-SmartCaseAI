# Phoenix-SmartCaseAI

**AI-Powered Test Case Generation for Modern QA Teams**

Phoenix-SmartCaseAI is an intelligent test case generator that leverages Large Language Models (LLMs) to automatically create comprehensive test cases from user stories. Generate both plain English test cases and BDD/Gherkin scenarios with proper JSON schema validation and export to markdown files.

## 🚀 Quick Start

### Prerequisites
1. **Set up API Keys** (Required):
   - Set environment variables: `OPENAI_API_KEY`, `GEMINI_API_KEY` (or `GOOGLE_API_KEY`), `ANTHROPIC_API_KEY` (or `CLAUDE_API_KEY`)
   - At minimum, you need one API key for the provider you want to use
   - See the [API Keys Setup Guide](#api-keys-setup-guide) section below for detailed instructions

### Option 1: Web Interface (Recommended)
1. **Start the API server:**
   ```bash
   # Windows
   python server_manager.py start
   # Or use the batch script
   start_server.bat
   
   # Linux/Mac
   python server_manager.py start
   # Or use the shell script
   ./start_server.sh
   
   # Or run directly
   python -m phoenix_smartcaseai.main
   ```

2. **Access the web interface:**
   - Open your browser and navigate to: `http://localhost:8000`
   - The interface features a modern two-panel layout:
     - **Input Panel**: Enter user story, select format, choose LLM provider, upload files
     - **Output Panel**: View generated test cases with Copy and Export functionality
   - Supports both light and dark modes

### Option 2: Python Package Usage
Use Phoenix-SmartCaseAI as an importable Python package:

```python
from phoenix_smartcaseai import generate_bdd_from_story, StoryBDDGenerator

# Quick function call
scenarios = generate_bdd_from_story(
    "As a user, I want to log in so I can access my dashboard.",
    llm_provider="openai",
    num_cases=5
)

# Or use the class for more control
generator = StoryBDDGenerator(llm_provider="openai")
test_cases = generator.generate_test_cases(
    user_story="As a user, I want to reset my password.",
    output_format="bdd",
    num_cases=5
)
```

### Option 3: Command Line Examples
Ready-to-run examples focusing on a comprehensive Payment Portal user story:

```bash
# 1. Set up API keys (at least one required):
# Windows PowerShell
$env:OPENAI_API_KEY="sk-..."        # OpenAI GPT models
$env:GOOGLE_API_KEY="..."           # Google Gemini models  
$env:ANTHROPIC_API_KEY="sk-ant-..."  # Anthropic Claude models

# Linux/Mac
export OPENAI_API_KEY="sk-..."
export GOOGLE_API_KEY="..."
export ANTHROPIC_API_KEY="sk-ant-..."

# 2. Run comparison examples:
python example_openai.py    # OpenAI-generated test cases
python example_gemini.py    # Gemini-generated test cases
python example_claude.py    # Claude-generated test cases
python example_all.py       # Combined multi-provider approach

# 3. View outputs in examples/payment_portal/[provider]/
```

**Supporting Files**: All examples automatically use comprehensive supporting files from `input_files/` including API specs, requirements, test data, security guidelines, and business rules.

## Features

- **Multi-Provider Support**: OpenAI GPT, Google Gemini, Claude (Anthropic), or all together for enhanced accuracy
- **Dual Output Formats**: Plain English test cases and BDD/Gherkin scenarios
- **JSON Schema Validation**: Strict schema compliance for consistent output
- **Markdown Export**: Generate separate `.md` files for different test formats
- **Pydantic Models**: Type-safe data structures with automatic validation
- **File Analysis**: Analyze additional files (PDFs, images, documents, spreadsheets) for enhanced context
- **OCR & Vision**: Extract text from images and analyze UI mockups/wireframes
- **Multi-format Support**: Handle text, PDF, Word, Excel, CSV, JSON, XML, images, and videos


## Installation

### Method 1: Install as a Python Package (Recommended)

1. **Clone the repository:**
   ```bash
   git clone https://github.com/shaktitrigent/Phoenix-SmartCaseAI.git
   cd Phoenix-SmartCaseAI
   ```

2. **Create and activate virtual environment:**
   ```bash
   python -m venv venv
   # Windows
   .\venv\Scripts\activate
   # Linux/Mac
   source venv/bin/activate
   ```

3. **Install the package in development mode:**
   ```bash
   pip install -e .
   ```

   This installs the package and all dependencies, allowing you to import it as `phoenix_smartcaseai`.

### Method 2: Install from Requirements

1. **Follow steps 1-2 from Method 1**

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up API keys:**
   ```bash
   # For OpenAI (required for OpenAI provider)
   # Windows PowerShell
   $env:OPENAI_API_KEY="your-openai-api-key-here"
   # Linux/Mac
   export OPENAI_API_KEY="your-openai-api-key-here"
   
   # For Google Gemini (required for Gemini provider)
   # Windows PowerShell
   $env:GOOGLE_API_KEY="your-google-api-key-here"
   # Linux/Mac
   export GOOGLE_API_KEY="your-google-api-key-here"
   
   # For Claude/Anthropic (required for Claude provider)
   # Windows PowerShell
   $env:ANTHROPIC_API_KEY="your-anthropic-api-key-here"
   # Linux/Mac
   export ANTHROPIC_API_KEY="your-anthropic-api-key-here"
   ```

### Method 3: Using .env File (Recommended for Development)

1. **Copy the example environment file:**
   ```bash
   cp env.example .env
   ```

2. **Edit `.env` and add your API keys:**
   ```bash
   OPENAI_API_KEY=your-openai-api-key-here
   GOOGLE_API_KEY=your-google-api-key-here
   ANTHROPIC_API_KEY=your-anthropic-api-key-here
   APP_HOST=0.0.0.0
   APP_PORT=8000
   DEBUG=False
   ```

   The application will automatically load these variables when starting.

## Quick Start

### Basic Usage

```python
from phoenix_smartcaseai import StoryBDDGenerator, generate_bdd_from_story

# Method 1: Simple function call
scenarios = generate_bdd_from_story(
    "As a user, I want to reset my password so that I can regain access to my account.",
    llm_provider="openai",
    num_cases=5
)
print(f"Generated {len(scenarios)} BDD scenarios")

# Method 2: Using the class directly
generator = StoryBDDGenerator(llm_provider="openai")

# Generate and export test cases to markdown files
user_story = """
As a user, I want to reset my password so that I can regain 
access to my account if I forget my current password.
"""

file_paths = generator.export_to_markdown(
    user_story=user_story,
    output_dir="test_cases",
    filename_prefix="password_reset",
    num_cases=5
)

print(f"Plain English tests: {file_paths['plain_english']}")
print(f"BDD tests: {file_paths['bdd']}")
```

### Enhanced Usage with File Analysis

```python
from phoenix_smartcaseai import StoryBDDGenerator

# Initialize the generator
generator = StoryBDDGenerator(llm_provider="openai")

# User story
user_story = """
As a user, I want to be able to log into the system using my email and password
so that I can access my personal dashboard and manage my account.
"""

# Additional files for context (requirements, UI mockups, API specs, etc.)
additional_files = [
    "requirements.pdf",
    "ui_mockup.png", 
    "api_spec.json",
    "test_data.csv"
]

# Generate test cases with file analysis
test_cases = generator.generate_test_cases(
    user_story=user_story,
    output_format="bdd",
    num_cases=5,
    additional_files=additional_files
)

# Or export directly to markdown with file analysis
file_paths = generator.export_to_markdown(
    user_story=user_story,
    output_dir="test_cases",
    filename_prefix="login_tests",
    num_cases=5,
    additional_files=additional_files
)
```

### AI Provider Options

Phoenix-SmartCaseAI supports multiple AI providers for enhanced test case generation:

#### Single Provider Usage

```python
# Using OpenAI only (GPT models)
gen_openai = StoryBDDGenerator(llm_provider="openai")

# Using Google Gemini only  
gen_gemini = StoryBDDGenerator(llm_provider="gemini")

# Using Claude (Anthropic) only
gen_claude = StoryBDDGenerator(llm_provider="claude")

# Generate with specific provider
test_cases = gen_openai.generate_test_cases(user_story, output_format="bdd")
```

#### Multi-Provider Mode

```python
# Use all providers and combine all results
gen_all = StoryBDDGenerator(llm_provider="all")

# Generate test cases using all providers
# Results will be combined and labeled by source provider
file_paths = gen_all.export_to_markdown(
    user_story=user_story,
    output_dir="multi_provider_tests",
    filename_prefix="comprehensive_tests",
    num_cases=15  # Gets more diverse test cases from all providers
)
```

#### Custom API Keys

```python
# Pass custom API keys
custom_keys = {
    "openai": "your-openai-key-here",
    "gemini": "your-google-api-key-here",
    "claude": "your-anthropic-api-key-here"
}

gen = StoryBDDGenerator(
    llm_provider="all",  # for multi-provider
    api_keys=custom_keys
)
```

#### Provider Comparison & Benefits

| Provider | Strengths | Best Use Cases |
|----------|-----------|----------------|
| **OpenAI GPT** | Detailed, structured test cases | Complex business logic, detailed workflows |
| **Google Gemini** | Excellent edge cases, boundary testing | Security testing, error handling scenarios |
| **Claude (Anthropic)** | Strong logical reasoning, safety-focused | Critical systems, compliance testing |
| **All** | Maximum coverage and diversity | Comprehensive test suites, comparison studies |

**Benefits of Multi-Provider Generation:**
- **Enhanced Coverage**: Different LLMs catch different edge cases
- **Redundancy**: Fallback if one provider has issues  
- **Diverse Perspectives**: Each LLM brings unique testing insights
- **Provider Tracking**: Each test case labeled with source provider
- **Comprehensive Results**: Combined output from multiple AI providers

### Generate Individual Formats

```python
# Generate only plain English test cases
plain_tests = gen.generate_test_cases(
    user_story=user_story,
    output_format="plain",
    num_cases=6
)

# Generate only BDD scenarios
bdd_tests = gen.generate_test_cases(
    user_story=user_story,
    output_format="bdd",
    num_cases=4
)
```

## Output Examples

### Plain English Test Cases
```markdown
# Test Cases - Plain English Format

## Test Case 1: Login with valid credentials
**Description:** Verify that a user can successfully log in with valid username and password
**Type:** positive
**Preconditions:** User has a valid account in the system
**Steps:**
1. Navigate to the login page
2. Enter valid username in the username field
3. Enter valid password in the password field
4. Click the 'Login' button
**Expected Result:** User should be successfully logged in and redirected to the dashboard
```

### BDD/Gherkin Scenarios
```markdown
# BDD Test Scenarios - Gherkin Format

## Scenario 1: Successful login with valid credentials
**Feature:** User Authentication

```gherkin
Feature: User Authentication
Scenario: Successful login with valid credentials
  Given the user is on the login page
  Given the user has valid account credentials
  When the user enters their valid username
  When the user enters their valid password
  When the user clicks the login button
  Then the user should be logged in successfully
  Then the user should be redirected to the dashboard
  Then the user session should be active
```
```

## JSON Schema Support

Phoenix-SmartCaseAI uses strict JSON schemas to ensure consistent output:

### TestCase Schema (Plain English)
```json
{
  "title": "List[TestCase]",
  "description": "A list of TestCase objects.",
  "type": "array",
  "items": {
    "type": "object",
    "properties": {
      "id": {"type": "integer"},
      "title": {"type": "string"},
      "description": {"type": "string"},
      "preconditions": {"type": "string", "default": null},
      "steps": {"type": "array", "items": {"type": "string"}},
      "expected": {"type": "string"},
      "type": {"type": "string"}
    },
    "required": ["id", "title", "description", "steps", "expected", "type"]
  }
}
```

### BDDScenario Schema
```json
{
  "title": "List[BDDScenario]",
  "description": "A list of BDDScenario objects.",
  "type": "array",
  "items": {
    "type": "object",
    "properties": {
      "feature": {"type": "string"},
      "scenario": {"type": "string"},
      "given": {"type": "array", "items": {"type": "string"}},
      "when": {"type": "array", "items": {"type": "string"}},
      "then": {"type": "array", "items": {"type": "string"}}
    },
    "required": ["feature", "scenario", "given", "when", "then"]
  }
}
```

## API Reference

### StoryBDDGenerator

#### `__init__(llm_provider="openai", api_keys=None)`
Initialize the generator with your preferred LLM provider.

**Parameters:**
- `llm_provider` (str): "openai", "gemini", "claude", or "all" (for multi-provider)
- `api_keys` (dict, optional): Dictionary with keys "openai", "gemini", "claude" to override environment variables

#### `generate_test_cases(user_story, output_format="bdd", num_cases=None, additional_files=None)`
Generate test cases from a user story with optional file analysis.

**Parameters:**
- `user_story` (str): The user story to generate tests for
- `output_format` (str): "plain" or "bdd"
- `num_cases` (int, optional): Limit number of generated test cases
- `additional_files` (list, optional): List of file paths to analyze for additional context

**Returns:** List of dictionaries containing test case data

#### `export_to_markdown(user_story, output_dir=".", filename_prefix="test_cases", num_cases=None, additional_files=None)`
Generate test cases and export to markdown files.

**Parameters:**
- `user_story` (str): The user story to generate tests for
- `output_dir` (str): Directory to save markdown files
- `filename_prefix` (str): Prefix for generated filenames
- `num_cases` (int, optional): Limit number of test cases
- `additional_files` (list, optional): List of file paths to analyze for additional context

**Returns:** Dictionary with file paths: `{"plain_english": "path", "bdd": "path"}`

### FileAnalyzer

#### `analyze_file(file_path)`
Analyze a single file and extract relevant information.

**Parameters:**
- `file_path` (str/Path): Path to the file to analyze

**Returns:** FileAnalysisResult object with extracted content and metadata

#### `analyze_multiple_files(file_paths)`
Analyze multiple files and return results.

**Parameters:**
- `file_paths` (list): List of file paths to analyze

**Returns:** List of FileAnalysisResult objects

#### Supported File Types:
- **Text**: `.txt`, `.md`, `.markdown`
- **Documents**: `.pdf`, `.docx`, `.doc`
- **Spreadsheets**: `.xlsx`, `.xls`, `.csv`
- **Data**: `.json`, `.xml`
- **Images**: `.png`, `.jpg`, `.jpeg`, `.gif`, `.bmp`, `.tiff`
- **Videos**: `.mp4`, `.avi`, `.mov`, `.wmv`

## Server Management

Phoenix-SmartCaseAI includes a unified server management script for easy start/stop/restart operations:

### Server Management Commands

```bash
# Start the web server
python server_manager.py start

# Stop the web server
python server_manager.py stop

# Restart the web server
python server_manager.py restart

# Check server status
python server_manager.py status
```

### Convenience Scripts

**Windows:**
```bash
# Start server
start_server.bat

# Stop server
stop_server.bat
```

**Linux/Mac:**
```bash
# Start server
./start_server.sh

# Stop server
./stop_server.sh
```

The server manager automatically:
- Detects and uses the virtual environment's Python executable
- Finds and manages the server process
- Provides status information including health check
- Handles port conflicts gracefully

## Testing

Run the example usage scripts:

```bash
# Basic example
python example_usage.py

# File analysis demonstration
python example_file_analysis.py

# Multi-provider demonstration
python example_multi_provider.py
```

## Roadmap

- [x] **Google Gemini Support**: Multi-provider support with OpenAI + Gemini
- [x] **Anthropic Claude Support**: Add Claude LLM provider
- [x] **Web Interface**: Modern two-panel web UI with file upload support
- [x] **Python Package**: Installable package with `src/` layout
- [x] **Docker Support**: Containerized deployment with Docker and Docker Compose
- [x] **Server Management**: Unified scripts for start/stop/restart operations
- [x] **File Analysis**: Support for PDFs, images, documents, spreadsheets
- [x] **API Endpoints**: FastAPI-based REST API for programmatic access

- [ ] **TestRail Integration**: Export test cases to TestRail
- [ ] **Custom Templates**: User-defined test case templates
- [ ] **Batch Processing**: Process multiple user stories at once
- [ ] **Test Case Comparison**: Advanced comparison between provider results
- [ ] **Real-time Progress**: Server-Sent Events (SSE) for live generation updates

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

- **Email**: support@phoenixsmartcase.ai
- **Documentation**: [Full Documentation](docs/)
- **Issues**: [GitHub Issues](https://github.com/yourusername/Phoenix-SmartCaseAI/issues)

## API Keys Setup Guide

### Getting Your API Keys

#### OpenAI API Key
1. Visit [OpenAI Platform](https://platform.openai.com/)
2. Sign up or log in to your account
3. Navigate to **API Keys** section
4. Click **"Create new secret key"**
5. Copy your key (starts with `sk-...`)

#### Google Gemini API Key  
1. Go to [Google AI Studio](https://aistudio.google.com/)
2. Sign in with your Google account
3. Click **"Get API Key"**
4. Create a new API key or use existing one
5. Copy your key

#### Claude (Anthropic) API Key
1. Visit [Anthropic Console](https://console.anthropic.com/)
2. Sign up or log in to your account
3. Navigate to **API Keys** section
4. Click **"Create Key"**
5. Copy your key (starts with `sk-ant-...`)

### Setting Up Environment Variables

#### Windows (PowerShell)
```powershell
# Set temporarily (current session only)
$env:OPENAI_API_KEY="your-openai-api-key-here"
$env:GOOGLE_API_KEY="your-google-api-key-here"
$env:ANTHROPIC_API_KEY="your-anthropic-api-key-here"

# Set permanently (all sessions)
[System.Environment]::SetEnvironmentVariable("OPENAI_API_KEY", "your-openai-api-key-here", "User")
[System.Environment]::SetEnvironmentVariable("GOOGLE_API_KEY", "your-google-api-key-here", "User")  
[System.Environment]::SetEnvironmentVariable("ANTHROPIC_API_KEY", "your-anthropic-api-key-here", "User")
```

#### Linux/Mac (Bash/Zsh)
```bash
# Set temporarily (current session only)
export OPENAI_API_KEY="your-openai-api-key-here"
export GOOGLE_API_KEY="your-google-api-key-here"
export ANTHROPIC_API_KEY="your-anthropic-api-key-here"

# Set permanently (add to ~/.bashrc or ~/.zshrc)
echo 'export OPENAI_API_KEY="your-openai-api-key-here"' >> ~/.bashrc
echo 'export GOOGLE_API_KEY="your-google-api-key-here"' >> ~/.bashrc
echo 'export ANTHROPIC_API_KEY="your-anthropic-api-key-here"' >> ~/.bashrc
source ~/.bashrc
```

### Verify Your Setup
```bash
# Test your configuration
python -c "
from phoenix_smartcaseai import StoryBDDGenerator
import os

# Check which API keys are available
print('OpenAI Key:', '[OK]' if os.getenv('OPENAI_API_KEY') else '[MISSING]')
print('Gemini Key:', '[OK]' if os.getenv('GOOGLE_API_KEY') or os.getenv('GEMINI_API_KEY') else '[MISSING]') 
print('Claude Key:', '[OK]' if os.getenv('ANTHROPIC_API_KEY') or os.getenv('CLAUDE_API_KEY') else '[MISSING]')

# Test generator initialization
try:
    gen = StoryBDDGenerator(llm_provider='openai')
    print('[OK] Generator initialized successfully!')
except Exception as e:
    print(f'[ERROR] Setup issue: {e}')
"
```

### Provider Requirements by Mode

| Mode | Required API Keys |
|------|-------------------|
| `openai` | `OPENAI_API_KEY` |
| `gemini` | `GOOGLE_API_KEY` or `GEMINI_API_KEY` |
| `claude` | `ANTHROPIC_API_KEY` or `CLAUDE_API_KEY` |
| `all` | **All three keys** (at least one for each provider) |

### Pro Tips
- **Multi-provider mode** (`all`) requires all three API keys but provides the most comprehensive results
- You can use any single provider if you only have one API key
- API keys are never stored - only used for API calls
- Each provider has different rate limits and pricing
- For production use, consider setting up billing alerts

## 📦 Package Installation & Usage

### Install as a Python Package

Phoenix-SmartCaseAI is a fully installable Python package with a modern `src/` layout, following Python packaging best practices.

#### Build the Package

```bash
# Install build tools
pip install build wheel

# Build the package
python -m build

# This creates:
# - dist/phoenix_smartcaseai-<version>-py3-none-any.whl (wheel)
# - dist/phoenix_smartcaseai-<version>.tar.gz (source distribution)
```

#### Install the Package

```bash
# Install from wheel file
pip install dist/phoenix_smartcaseai-*.whl

# Or install in development mode (recommended for development)
pip install -e .

# Or install from source
pip install .
```

#### Use as a Python Module

```python
# Import convenience functions
from phoenix_smartcaseai import (
    generate_bdd_from_story,
    generate_plain_from_story,
    StoryBDDGenerator,
    TestCase,
    BDDScenario
)

# Simple function call for BDD scenarios
scenarios = generate_bdd_from_story(
    "As a user, I want to log in so I can access my dashboard.",
    llm_provider="openai",
    num_cases=5
)
print(f"Generated {len(scenarios)} scenarios")
print(scenarios[0]['scenario'])

# Simple function call for plain English test cases
test_cases = generate_plain_from_story(
    "As a user, I want to reset my password.",
    llm_provider="openai",
    num_cases=5
)

# Or use the class directly for more control
generator = StoryBDDGenerator(llm_provider="openai")
test_cases = generator.generate_test_cases(
    user_story="As a user, I want to reset my password.",
    output_format="bdd",
    num_cases=5,
    additional_files=["requirements.pdf", "ui_mockup.png"]
)
```

## 🌐 Web Interface & API

### Run as a Web Service

Phoenix-SmartCaseAI includes a FastAPI-based web interface with a modern two-panel layout for easy access.

#### Start the Web Service

```bash
# Method 1: Using the server manager (Recommended)
python server_manager.py start

# Method 2: Using the package entrypoint
python -m phoenix_smartcaseai.main

# Method 3: Using uvicorn directly
uvicorn phoenix_smartcaseai.web_app:app --host 0.0.0.0 --port 8000

# Method 4: Using convenience scripts
# Windows
start_server.bat

# Linux/Mac
./start_server.sh
```

#### Server Management

The `server_manager.py` script provides easy server management:

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

#### Access the Web Interface

1. Open your browser and navigate to: `http://localhost:8000`
2. You'll see a modern two-panel web interface:
   - **Input Panel**: 
     - Paste your user story
     - Select output format (Plain English, BDD, or Both)
     - Choose LLM provider (OpenAI, Gemini, Claude)
     - Upload additional files for context
     - Generate test cases with a single click
   - **Output Panel**:
     - View generated test cases in both formats
     - Switch between Plain English and BDD/Gherkin tabs
     - Copy test cases to clipboard
     - Export test cases as `.txt` files
     - Progress animation during generation
   - **Features**:
     - Light/Dark mode toggle
     - Responsive design
     - Real-time generation status

#### API Endpoints

- `GET /` - Web interface (HTML) - Two-panel interface
- `GET /health` - Health check endpoint (returns `{"status": "ok"}`)
- `POST /generate-bdd` - Generate test cases (accepts form data with file uploads)

#### Example API Usage

```bash
# Using curl (with file upload)
curl -X POST "http://localhost:8000/generate-bdd" \
  -F "user_story=As a user, I want to log in so I can access my dashboard." \
  -F "output_format=bdd" \
  -F "llm_provider=openai" \
  -F "num_cases=5" \
  -F "files=@requirements.pdf" \
  -F "files=@ui_mockup.png"

# Using Python requests
import requests

# Without file upload
response = requests.post(
    "http://localhost:8000/generate-bdd",
    data={
        "user_story": "As a user, I want to log in so I can access my dashboard.",
        "output_format": "bdd",
        "llm_provider": "openai",
        "num_cases": 5
    }
)
result = response.json()
print(result['bdd_content'])

# With file upload
files = [
    ('files', open('requirements.pdf', 'rb')),
    ('files', open('ui_mockup.png', 'rb'))
]
response = requests.post(
    "http://localhost:8000/generate-bdd",
    data={
        "user_story": "As a user, I want to log in so I can access my dashboard.",
        "output_format": "bdd",
        "llm_provider": "openai",
        "num_cases": 5
    },
    files=files
)
result = response.json()
print(result['bdd_content'])
```

#### API Response Format

```json
{
  "success": true,
  "bdd_content": "# BDD Test Scenarios...",
  "plain_content": "# Test Cases - Plain English...",
  "num_scenarios": 5,
  "num_cases": 5,
  "generation_time": "12.34s",
  "llm_provider": "openai"
}
```

## ☁️ Cloud Deployment

### Docker Deployment

Phoenix-SmartCaseAI includes Docker support for easy cloud deployment.

#### Build Docker Image

```bash
docker build -t phoenix-smartcaseai:1.0.0 .
```

#### Run with Docker

```bash
docker run -d \
  -p 8000:8000 \
  -e OPENAI_API_KEY=your-key-here \
  -e GEMINI_API_KEY=your-key-here \
  -e ANTHROPIC_API_KEY=your-key-here \
  --name phoenix-smartcaseai \
  phoenix-smartcaseai:1.0.0
```

#### Docker Compose (Recommended)

```bash
# Copy environment file
cp env.example .env

# Edit .env and add your API keys
# Then run:
docker-compose up -d

# View logs
docker-compose logs -f

# Stop the service
docker-compose down
```

### Environment Configuration

Create a `.env` file in the project root:

```bash
# Application Settings
APP_HOST=0.0.0.0
APP_PORT=8000
DEBUG=False

# LLM API Keys
OPENAI_API_KEY=your-openai-api-key-here
GEMINI_API_KEY=your-google-api-key-here
CLAUDE_API_KEY=your-anthropic-api-key-here
```

### Cloud Platform Deployment

#### AWS EC2 / DigitalOcean / Linode

1. **SSH into your server:**
   ```bash
   ssh user@your-server-ip
   ```

2. **Clone the repository:**
   ```bash
   git clone https://github.com/shaktitrigent/Phoenix-SmartCaseAI.git
   cd Phoenix-SmartCaseAI
   ```

3. **Build and run with Docker:**
   ```bash
   docker-compose up -d
   ```

4. **Access the service:**
   - Open `http://your-server-ip:8000` in your browser
   - Make sure port 8000 is open in your firewall

#### Render / Railway / Heroku

1. **Connect your GitHub repository**
2. **Set environment variables** in the platform dashboard:
   - `OPENAI_API_KEY`
   - `GEMINI_API_KEY` (optional)
   - `ANTHROPIC_API_KEY` (optional)
   - `APP_PORT=8000`
3. **Deploy** - The platform will automatically build and deploy

#### Kubernetes Deployment

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: phoenix-smartcaseai
spec:
  replicas: 2
  selector:
    matchLabels:
      app: phoenix-smartcaseai
  template:
    metadata:
      labels:
        app: phoenix-smartcaseai
    spec:
      containers:
      - name: phoenix-smartcaseai
        image: phoenix-smartcaseai:1.0.0
        ports:
        - containerPort: 8000
        env:
        - name: OPENAI_API_KEY
          valueFrom:
            secretKeyRef:
              name: api-keys
              key: openai-key
        - name: APP_PORT
          value: "8000"
---
apiVersion: v1
kind: Service
metadata:
  name: phoenix-smartcaseai-service
spec:
  selector:
    app: phoenix-smartcaseai
  ports:
  - protocol: TCP
    port: 80
    targetPort: 8000
  type: LoadBalancer
```

## 🧪 Testing

### Run Unit Tests

```bash
# Install test dependencies
pip install -e ".[dev]"

# Run all tests
pytest

# Run with coverage
pytest --cov=phoenix_smartcaseai --cov-report=html

# Run specific test file
pytest tests/test_generator.py

# Run integration tests (requires API keys)
pytest tests/test_web_app.py -m integration
```

### Test the Web API

```bash
# Start the service
python -m phoenix_smartcaseai.main

# In another terminal, test the health endpoint
curl http://localhost:8000/health

# Test the generation endpoint
curl -X POST http://localhost:8000/generate-bdd \
  -F "user_story=As a user, I want to log in." \
  -F "output_format=bdd" \
  -F "llm_provider=openai" \
  -F "num_cases=2"
```

## Production Ready

### Production Features
- **Environment Validation**: Automatic checks for API keys and system requirements
- **Configuration Management**: Production/development configuration profiles
- **Version Management**: Centralized version control with semantic versioning
- **Error Handling**: Comprehensive error handling with retry logic
- **Logging**: Configurable logging levels for production monitoring
- **Rate Limiting**: Built-in protection against API rate limits
- **Docker Support**: Containerized deployment for consistency
- **Health Checks**: Built-in health check endpoints for monitoring

### Example Production Usage
```python
from phoenix_smartcaseai import StoryBDDGenerator

# Simple usage
generator = StoryBDDGenerator(llm_provider="openai")
test_cases = generator.generate_test_cases(
    user_story="As a user, I want to log in.",
    output_format="bdd",
    num_cases=5
)
```

## 🙏 Acknowledgments

- Built with [LangChain](https://langchain.com/) for LLM orchestration
- [Pydantic](https://pydantic.dev/) for data validation
- [OpenAI](https://openai.com/) for GPT models

---

**Made for QA Engineers who want to focus on what matters most**
