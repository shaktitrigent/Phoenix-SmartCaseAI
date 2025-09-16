# Changelog

All notable changes to Phoenix-SmartCaseAI will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2025-09-15

### Added
- ✨ **Core AI Test Case Generation**: Generate comprehensive test cases from user stories using OpenAI's GPT models
- 📝 **Dual Format Support**: Support for both Plain English and BDD/Gherkin format test case generation
- 📄 **Markdown Export**: Export generated test cases to well-formatted markdown files with timestamps
- 🎯 **Pydantic Data Models**: Robust data validation using Pydantic for `TestCase` and `BDDScenario` models
- 🔧 **Command Line Interface**: Production-ready CLI with comprehensive options and help
- 📦 **Python Package**: Installable package with proper entry points and dependencies
- 🔑 **OpenAI Integration**: Seamless integration with OpenAI API using langchain-openai
- ⚙️ **JSON Schema Validation**: Ensure generated test cases conform to specified JSON structures
- 📚 **Comprehensive Documentation**: Complete README, installation guide, and usage examples
- 🛡️ **Error Handling**: Robust error handling with informative error messages
- 🏗️ **Production Configuration**: Professional project structure with proper packaging

### Technical Features
- **LLM Integration**: Built on LangChain framework for reliable LLM interactions
- **Type Safety**: Full type hints and Pydantic validation throughout
- **Configurable Output**: Customizable number of test cases and output directories
- **Extensible Design**: Clean architecture for easy future enhancements
- **Cross-Platform**: Works on Windows, macOS, and Linux

### Supported Use Cases
- Generate positive, negative, edge, and boundary test scenarios
- Convert user stories into actionable test cases
- Export test cases for integration with testing frameworks
- Standardize test case documentation across teams
- Accelerate QA processes with AI-powered test generation

### Dependencies
- `pydantic>=2.11.0` - Data validation and settings management
- `langchain-core>=0.3.70` - Core LangChain functionality
- `langchain-openai>=0.3.30` - OpenAI integration for LangChain

### CLI Commands
- `phoenix-smartcase --story "..."` - Generate from story text
- `phoenix-smartcase --story-file story.txt` - Generate from file
- `phoenix-smartcase --interactive` - Interactive mode
- `phoenix-smartcase --help` - Show all available options

## [Unreleased]

### Planned Features
- 🔌 **Multi-LLM Support**: Google Gemini, Anthropic Claude, and other LLM providers
- 🎯 **JIRA Integration**: Direct integration with JIRA for fetching user stories
- 🧪 **TestRail Integration**: Export test cases directly to TestRail
- 🔄 **Template System**: Customizable test case templates
- 📊 **Analytics**: Test case generation analytics and reporting
- 🎨 **Custom Formats**: Support for additional test case formats
- 🔍 **Advanced Filtering**: Filter test cases by type, complexity, or other criteria
