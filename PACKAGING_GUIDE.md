# Phoenix-SmartCaseAI Packaging Guide

This document explains the packaging structure and all generated artifacts for Phoenix-SmartCaseAI.

## 📦 Package Structure

The project has been restructured using the modern `src/` layout:

```
Phoenix-SmartCaseAI/
├── src/
│   └── phoenix_smartcaseai/
│       ├── __init__.py          # Public API exports
│       ├── _version.py          # Version information
│       ├── generator.py         # Core BDD generation logic
│       ├── unified_file_analyzer.py  # File analysis module
│       ├── cli.py               # Command-line interface
│       ├── web_app.py           # FastAPI web application
│       └── main.py              # Web service entrypoint
├── tests/                       # Unit and integration tests
├── pyproject.toml              # Modern Python packaging config
├── setup.cfg                    # Setuptools configuration
├── requirements.txt             # Runtime dependencies
├── Dockerfile                   # Docker container definition
├── docker-compose.yml           # Docker Compose configuration
├── env.example                  # Environment variables template
└── README.md                    # Comprehensive documentation
```

## 📄 File Descriptions

### Core Package Files

#### `src/phoenix_smartcaseai/__init__.py`
- **Purpose**: Public API exports and convenience functions
- **Exports**: 
  - `generate_bdd_from_story()` - Simple function for BDD generation
  - `generate_plain_from_story()` - Simple function for plain test cases
  - `StoryBDDGenerator` - Main generator class
  - `TestCase`, `BDDScenario` - Pydantic models
  - `UnifiedFileAnalyzer` - File analysis class
  - `__version__` - Package version

#### `src/phoenix_smartcaseai/generator.py`
- **Purpose**: Core BDD generation logic using LLMs
- **Key Classes**: `StoryBDDGenerator`, `TestCase`, `BDDScenario`
- **Features**: Multi-provider support, file analysis integration

#### `src/phoenix_smartcaseai/unified_file_analyzer.py`
- **Purpose**: Analyze additional files (PDFs, images, documents) for context
- **Features**: OCR, multi-format support, intelligent LLM routing

#### `src/phoenix_smartcaseai/web_app.py`
- **Purpose**: FastAPI web application with HTML UI
- **Endpoints**:
  - `GET /` - Web interface
  - `GET /health` - Health check
  - `POST /generate-bdd` - Generate test cases
- **Features**: File upload support, multiple output formats

#### `src/phoenix_smartcaseai/main.py`
- **Purpose**: Entrypoint for running the web service
- **Usage**: `python -m phoenix_smartcaseai.main`
- **Features**: Environment variable loading, configuration

#### `src/phoenix_smartcaseai/cli.py`
- **Purpose**: Command-line interface
- **Usage**: `phoenix-smartcase --story "..." --output-dir ./tests`
- **Features**: Interactive mode, file analysis, multi-provider support

### Configuration Files

#### `pyproject.toml`
- **Purpose**: Modern Python packaging configuration (PEP 518/621)
- **Defines**: 
  - Package metadata
  - Dependencies
  - Build system
  - Entry points
  - Tool configurations (black, mypy, pytest)

#### `setup.cfg`
- **Purpose**: Setuptools configuration (for compatibility)
- **Defines**: Package metadata, entry points, find packages

#### `requirements.txt`
- **Purpose**: Runtime dependencies for the package
- **Includes**: 
  - Core LLM libraries (langchain, pydantic)
  - File processing (pdfplumber, python-docx, pandas)
  - Web framework (fastapi, uvicorn)
  - Configuration (python-dotenv)

#### `env.example`
- **Purpose**: Template for environment variables
- **Variables**:
  - `APP_HOST`, `APP_PORT`, `DEBUG` - Application settings
  - `OPENAI_API_KEY`, `GEMINI_API_KEY`, `CLAUDE_API_KEY` - LLM API keys

### Deployment Files

#### `Dockerfile`
- **Purpose**: Docker container definition
- **Base Image**: `python:3.10-slim`
- **Features**: 
  - Installs system dependencies (tesseract-ocr)
  - Installs Python dependencies
  - Builds and installs the package
  - Exposes port 8000
  - Health check included

#### `docker-compose.yml`
- **Purpose**: Docker Compose configuration for easy deployment
- **Features**:
  - Environment variable support
  - Volume mounting for outputs
  - Health checks
  - Auto-restart policy

### Testing Files

#### `tests/test_generator.py`
- **Purpose**: Unit tests for BDD generator
- **Tests**: Model validation, generator initialization

#### `tests/test_web_app.py`
- **Purpose**: Integration tests for FastAPI web app
- **Tests**: Health endpoint, API endpoints, error handling

## 🚀 Usage Examples

### As a Python Package

```python
# Install the package
pip install dist/phoenix_smartcaseai-1.0.0-py3-none-any.whl

# Use in your code
from phoenix_smartcaseai import generate_bdd_from_story

scenarios = generate_bdd_from_story(
    "As a user, I want to log in so I can access my dashboard."
)
```

### As a Web Service

```bash
# Start the web service
python -m phoenix_smartcaseai.main

# Access at http://localhost:8000
```

### As a Docker Container

```bash
# Build and run
docker-compose up -d

# Access at http://localhost:8000
```

## 🔧 Building the Package

```bash
# Install build tools
pip install build

# Build the package
python -m build

# This creates:
# - dist/phoenix_smartcaseai-1.0.0-py3-none-any.whl
# - dist/phoenix_smartcaseai-1.0.0.tar.gz

# Install the package
pip install dist/phoenix_smartcaseai-1.0.0-py3-none-any.whl
```

## ✅ Verification Checklist

After building, verify the following:

- [ ] Package builds successfully: `python -m build`
- [ ] Package installs: `pip install dist/phoenix_smartcaseai-1.0.0-py3-none-any.whl`
- [ ] Can import: `from phoenix_smartcaseai import generate_bdd_from_story`
- [ ] Web service runs: `python -m phoenix_smartcaseai.main`
- [ ] Web interface accessible: `http://localhost:8000`
- [ ] Health endpoint works: `curl http://localhost:8000/health`
- [ ] Docker builds: `docker build -t phoenix-smartcaseai:1.0.0 .`
- [ ] Docker runs: `docker-compose up -d`
- [ ] Tests pass: `pytest`

## 📝 Notes

- The package uses the modern `src/` layout for better isolation
- All core modules are in `src/phoenix_smartcaseai/`
- The old `SmartCaseAI/` directory can be kept for backward compatibility
- Environment variables are loaded from `.env` file if present
- The web interface is embedded in `web_app.py` (no external templates needed)
- Docker image includes all dependencies and is ready for cloud deployment

## 🔗 Related Documentation

- See `README.md` for comprehensive usage instructions
- See `API_KEYS_SETUP.md` for API key configuration
- See `tests/` for example test cases


