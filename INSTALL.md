# Installation Guide for Phoenix-SmartCaseAI

## 📦 Installing as a Package

### Option 1: Install from Local Directory

```bash
# Navigate to the project directory
cd Phoenix-SmartCaseAI

# Install in development mode (editable)
pip install -e .

# Or install normally
pip install .
```

### Option 2: Install with Optional Dependencies

```bash
# Install for development
pip install ".[dev]"
```

### Option 3: Build and Install Distribution

```bash
# Build the package
python -m build

# Install from wheel
pip install dist/phoenix_smartcaseai-1.0.0-py3-none-any.whl
```

## 🚀 Using in Other Projects

### Basic Usage

```python
# Import the package
from SmartCaseAI import StoryBDDGenerator

# Initialize generator
generator = StoryBDDGenerator(llm_provider="openai")

# Generate test cases
user_story = "As a user, I want to login with email and password..."

# Generate both formats and export to files
file_paths = generator.export_to_markdown(
    user_story=user_story,
    output_dir="test_cases",
    filename_prefix="login_tests",
    num_cases=5
)

print(f"Plain English: {file_paths['plain_english']}")
print(f"BDD: {file_paths['bdd']}")
```

### Command Line Interface

After installation, you can use the CLI:

```bash
# Basic usage
phoenix-smartcase --story "As a user, I want to..." --output-dir ./tests

# From file
phoenix-smartcase --story-file user_story.txt --format bdd --num-cases 10

# Interactive mode
phoenix-smartcase --interactive

# Help
phoenix-smartcase --help
```

### Advanced Usage

```python
from SmartCaseAI import StoryBDDGenerator, TestCase, BDDScenario

# Initialize with specific API key
generator = StoryBDDGenerator(
    llm_provider="openai",
    api_key="your-api-key"
)

# Generate specific format
plain_tests = generator.generate_test_cases(
    user_story="Your story here",
    output_format="plain",
    num_cases=3
)

# Access individual test cases
for test in plain_tests:
    print(f"Test: {test['title']}")
    print(f"Steps: {test['steps']}")
```

## 🔧 Environment Setup

### Required Environment Variables

```bash
# Set OpenAI API key
export OPENAI_API_KEY="your-openai-key-here"

# Windows
set OPENAI_API_KEY=your-openai-key-here
# or
$env:OPENAI_API_KEY="your-openai-key-here"
```

## 📋 Requirements

- Python 3.8+
- OpenAI API key
- Internet connection for LLM API calls

## 🔍 Verification

Test your installation:

```python
# Test import
try:
    from SmartCaseAI import StoryBDDGenerator
    print("✅ Phoenix-SmartCaseAI installed successfully")
except ImportError as e:
    print(f"❌ Installation failed: {e}")

# Test CLI
phoenix-smartcase --version
```

## 🐛 Troubleshooting

### Common Issues

1. **Import Error**: Make sure you're in the right virtual environment
2. **API Key Error**: Set your OpenAI API key as environment variable
3. **Permission Error**: Install with `--user` flag if needed

### Getting Help

- Check the main README.md for usage examples
- Run `phoenix-smartcase --help` for CLI options
- Visit the GitHub repository for issues and documentation