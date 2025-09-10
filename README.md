# Phoenix-SmartCaseAI 🚀

**AI-Powered Test Case Generation for Modern QA Teams**

Phoenix-SmartCaseAI is an intelligent test case generator that leverages Large Language Models (LLMs) to automatically create comprehensive test cases from user stories. Generate both plain English test cases and BDD/Gherkin scenarios with proper JSON schema validation and export to markdown files.

## ✨ Features

- 🤖 **Multiple LLM Support**: OpenAI GPT-4, Google Gemini, Anthropic Claude
- 📝 **Dual Output Formats**: Plain English test cases and BDD/Gherkin scenarios
- 📊 **JSON Schema Validation**: Strict schema compliance for consistent output
- 📁 **Markdown Export**: Generate separate `.md` files for different test formats
- ⚙️ **Pydantic Models**: Type-safe data structures with automatic validation
- 🔗 **Extensible**: Ready for Jira and TestRail integration (coming soon)

## 🛠️ Installation

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

4. **Set up API key:**
   ```bash
   # Windows
   $env:OPENAI_API_KEY="your-openai-api-key-here"
   # Linux/Mac
   export OPENAI_API_KEY="your-openai-api-key-here"
   ```

## 🚀 Quick Start

### Basic Usage

```python
from SmartCaseAI.generator import StoryBDDGenerator

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

## 📋 Output Examples

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

## 📊 JSON Schema Support

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

## 🔧 API Reference

### StoryBDDGenerator

#### `__init__(llm_provider="openai", api_key=None)`
Initialize the generator with your preferred LLM provider.

**Parameters:**
- `llm_provider` (str): "openai", "gemini", or "claude"
- `api_key` (str, optional): Override environment variable

#### `generate_test_cases(user_story, output_format="bdd", num_cases=None)`
Generate test cases from a user story.

**Parameters:**
- `user_story` (str): The user story to generate tests for
- `output_format` (str): "plain" or "bdd"
- `num_cases` (int, optional): Limit number of generated test cases

**Returns:** List of dictionaries containing test case data

#### `export_to_markdown(user_story, output_dir=".", filename_prefix="test_cases", num_cases=None)`
Generate test cases and export to markdown files.

**Parameters:**
- `user_story` (str): The user story to generate tests for
- `output_dir` (str): Directory to save markdown files
- `filename_prefix` (str): Prefix for generated filenames
- `num_cases` (int, optional): Limit number of test cases

**Returns:** Dictionary with file paths: `{"plain_english": "path", "bdd": "path"}`

## 🧪 Testing

Run the example usage script:

```bash
python example_usage.py
```

## 🛣️ Roadmap

- [ ] **Jira Integration**: Fetch user stories directly from Jira
- [ ] **TestRail Integration**: Export test cases to TestRail
- [ ] **Google Gemini Support**: Add Gemini LLM provider
- [ ] **Anthropic Claude Support**: Add Claude LLM provider
- [ ] **Custom Templates**: User-defined test case templates
- [ ] **Batch Processing**: Process multiple user stories at once
- [ ] **Web Interface**: Simple web UI for non-technical users

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- 📧 **Email**: support@phoenixsmartcase.ai
- 📖 **Documentation**: [Full Documentation](docs/)
- 🐛 **Issues**: [GitHub Issues](https://github.com/yourusername/Phoenix-SmartCaseAI/issues)

## 🙏 Acknowledgments

- Built with [LangChain](https://langchain.com/) for LLM orchestration
- [Pydantic](https://pydantic.dev/) for data validation
- [OpenAI](https://openai.com/) for GPT models

---

**Made with ❤️ for QA Engineers who want to focus on what matters most**
