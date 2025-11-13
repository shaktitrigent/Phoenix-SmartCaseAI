# Phoenix-SmartCaseAI

**AI-Powered Test Case Generation for Modern QA Teams**

Phoenix-SmartCaseAI is an intelligent test case generator that leverages Large Language Models (LLMs) to automatically create comprehensive test cases from user stories. Generate both plain English test cases and BDD/Gherkin scenarios with proper JSON schema validation and export to markdown files.

## 🚀 Quick Start

### Prerequisites
1. **Set up API Keys** (Required):
   - See `API_KEYS_SETUP.md` for detailed instructions
   - Set environment variables: `OPENAI_API_KEY`, `GEMINI_API_KEY`, `CLAUDE_API_KEY`
   - At minimum, you need one API key for the provider you want to use

### Option 1: Web Interface (Recommended)
1. **Start the API server:**
   ```bash
   python start_api_server.py
   ```

2. **Open the web interface:**
   - **Two-panel interface**: `web-interface-two-panel/index.html` (Recommended - Input panel + Output panel)
   - **Single-page interface**: `web-interface-working/index.html` (Alternative - All-in-one)

### Option 2: Command Line Examples
Ready-to-run examples focusing on a comprehensive Payment Portal user story:

```bash
# 1. Set up API keys (at least one required):
$env:OPENAI_API_KEY="sk-..."        # OpenAI GPT models
$env:GOOGLE_API_KEY="..."           # Google Gemini models  
$env:ANTHROPIC_API_KEY="sk-ant-..."  # Anthropic Claude models

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

1. **Clone the repository:**
   ```bash
   git clone https://github.com/yourusername/Phoenix-SmartCaseAI.git
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

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up API keys:**
   ```bash
   # For OpenAI (required for OpenAI provider)
   # Windows
   $env:OPENAI_API_KEY="your-openai-api-key-here"
   # Linux/Mac
   export OPENAI_API_KEY="your-openai-api-key-here"
   
   # For Google Gemini (required for Gemini provider)
   # Windows
   $env:GOOGLE_API_KEY="your-google-api-key-here"
   # Linux/Mac
   export GOOGLE_API_KEY="your-google-api-key-here"
   
   # For Claude/Anthropic (required for Claude provider)
   # Windows
   $env:ANTHROPIC_API_KEY="your-anthropic-api-key-here"
   # Linux/Mac
   export ANTHROPIC_API_KEY="your-anthropic-api-key-here"
   ```

## Quick Start

### Basic Usage

```python
from SmartCaseAI import StoryBDDGenerator

# Initialize the generator
gen = StoryBDDGenerator(llm_provider="openai")

# Generate and export test cases to markdown files
user_story = """
As a user, I want to reset my password so that I can regain 
access to my account if I forget my current password.
"""

file_paths = gen.export_to_markdown(
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
from SmartCaseAI import StoryBDDGenerator

# Initialize the generator
gen = StoryBDDGenerator(llm_provider="openai")

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
test_cases = gen.generate_test_cases(
    user_story=user_story,
    output_format="bdd",
    num_cases=5,
    additional_files=additional_files
)

# Or export directly to markdown with file analysis
file_paths = gen.export_to_markdown(
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

#### `__init__(llm_provider="openai", api_key=None)`
Initialize the generator with your preferred LLM provider.

**Parameters:**
- `llm_provider` (str): "openai", "gemini", or "claude"
- `api_key` (str, optional): Override environment variable

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

## Command Line Interface

Phoenix-SmartCaseAI includes a powerful CLI for easy integration into your workflow:

### Basic CLI Usage

```bash
# Generate test cases from a user story (OpenAI default)
phoenix-smartcase --story "As a user, I want to login..." --output-dir ./tests

# Use Google Gemini provider
phoenix-smartcase --story "As a user, I want to login..." --provider gemini

# Multi-provider generation (OpenAI + Gemini)
phoenix-smartcase --story "As a user, I want to login..." --provider all

# Generate with additional files for context
phoenix-smartcase --story "As a user, I want to login..." \
                  --files requirements.pdf ui_mockup.png api_spec.json \
                  --provider all

# Use a directory of files with multi-provider
phoenix-smartcase --story "As a user, I want to login..." \
                  --file-dir ./project_docs --provider all

# Interactive mode with custom API keys
phoenix-smartcase --interactive \
                  --provider all \
                  --openai-key sk-xxx \
                  --gemini-key yyy

# Generate only BDD format with Gemini
phoenix-smartcase --story "As a user, I want to login..." \
                  --format bdd --provider gemini

# Custom output directory and prefix with multi-provider
phoenix-smartcase --story "As a user, I want to login..." \
                  --output-dir ./my_tests \
                  --prefix login_feature \
                  --provider all \
                  --files requirements.pdf
```

### CLI Options

- `--story`, `-s`: User story text directly as argument
- `--story-file`, `-f`: Path to file containing user story
- `--interactive`, `-i`: Interactive mode - enter story via prompt
- `--format`: Output format ("plain", "bdd", or "both")
- `--provider`: LLM provider ("openai", "gemini", or "all") 
- `--num-cases`, `-n`: Number of test cases to generate
- `--output-dir`, `-o`: Directory to save generated files
- `--prefix`, `-p`: Filename prefix for generated files
- `--files`, `-F`: Additional files to analyze for context
- `--file-dir`: Directory containing files to analyze
- `--openai-key`: OpenAI API key (or set OPENAI_API_KEY env var)
- `--gemini-key`: Google API key for Gemini (or set GOOGLE_API_KEY env var)
- `--api-key`: OpenAI API key (legacy - use --openai-key instead)
- `--quiet`, `-q`: Suppress output except errors

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

- [ ] **TestRail Integration**: Export test cases to TestRail
- [ ] **Anthropic Claude Support**: Add Claude LLM provider
- [ ] **Custom Templates**: User-defined test case templates
- [ ] **Batch Processing**: Process multiple user stories at once
- [ ] **Web Interface**: Simple web UI for non-technical users
- [ ] **Test Case Comparison**: Advanced comparison between provider results

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
from SmartCaseAI.generator import StoryBDDGenerator
from config import Config

# Check which API keys are available
print('OpenAI Key:', '[OK]' if Config.get_api_key('openai') else '[MISSING]')
print('Gemini Key:', '[OK]' if Config.get_api_key('gemini') else '[MISSING]') 
print('Claude Key:', '[OK]' if Config.get_api_key('claude') else '[MISSING]')

# Test generator initialization
try:
    gen = StoryBDDGenerator(llm_provider='all')
    print('[OK] All providers ready!')
except Exception as e:
    print(f'[ERROR] Setup issue: {e}')
"
```

### Provider Requirements by Mode

| Mode | Required API Keys |
|------|-------------------|
| `openai` | `OPENAI_API_KEY` |
| `gemini` | `GOOGLE_API_KEY` |
| `claude` | `ANTHROPIC_API_KEY` |
| `all` | **All three keys** |

### Pro Tips
- **Multi-provider mode** (`all`) requires all three API keys but provides the most comprehensive results
- You can use any single provider if you only have one API key
- API keys are never stored - only used for API calls
- Each provider has different rate limits and pricing
- For production use, consider setting up billing alerts

## Production Ready

### Package Installation
```bash
# Install as a package
pip install -e .

# Use CLI anywhere
phoenix-smartcase --version
```

### Production Features
- **Environment Validation**: Automatic checks for API keys and system requirements
- **Configuration Management**: Production/development configuration profiles
- **Version Management**: Centralized version control with semantic versioning
- **Error Handling**: Comprehensive error handling with retry logic
- **Logging**: Configurable logging levels for production monitoring
- **Rate Limiting**: Built-in protection against API rate limits

### Example Production Usage
```python
from SmartCaseAI import StoryBDDGenerator
from config import get_config

# Load production configuration and validate environment
config = get_config("production")
validation = config.validate_environment()

if validation['valid']:
    generator = StoryBDDGenerator(llm_provider="openai")
    # Generate test cases for production use
```

## 🙏 Acknowledgments

- Built with [LangChain](https://langchain.com/) for LLM orchestration
- [Pydantic](https://pydantic.dev/) for data validation
- [OpenAI](https://openai.com/) for GPT models

---

**Made for QA Engineers who want to focus on what matters most**
