# Payment Portal Test Case Examples

This directory contains test case generation examples focused on a comprehensive Payment Portal user story.

## Directory Structure

```
examples/
└── payment_portal/
    ├── openai/         # OpenAI GPT-generated test cases
    ├── gemini/         # Google Gemini-generated test cases  
    ├── claude/         # Anthropic Claude-generated test cases
    └── all_providers/  # Combined multi-provider test cases
```

## Usage

Run the comparison scripts from the project root:

```bash
# Individual provider examples
python example_openai.py    # Generate using OpenAI GPT
python example_gemini.py    # Generate using Google Gemini
python example_claude.py    # Generate using Anthropic Claude

# Combined multi-provider approach
python example_all.py       # Generate using all available providers
```

## Payment Portal User Story

All examples use the same comprehensive Payment Portal user story:

> As a customer of an e-commerce platform, I want to securely process my payment through a comprehensive payment portal, so that I can complete my purchase quickly and safely with multiple payment options.

## Supporting Files

All examples automatically use supporting files from `input_files/`:
- payment_portal_user_story.txt
- payment_api_specification.json  
- payment_requirements.txt
- payment_test_data.csv
- payment_ui_mockup.txt
- security_guidelines.txt
- business_rules.xml

## Comparison Focus

Compare the outputs to evaluate:
- Test case coverage and completeness
- Edge case identification  
- Security scenario depth
- Regulatory compliance considerations
- User experience focus
- Technical accuracy

Each provider brings unique strengths to test case generation, and the combined approach leverages all available AI capabilities for comprehensive test coverage.