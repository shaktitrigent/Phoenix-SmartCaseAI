# API Keys Setup Guide

## Environment Variables Required

To use the AI Test Case Generator, you need to set up the following environment variables:

### Required API Keys

1. **OpenAI API Key** (for OpenAI provider)
   - Get your key from: https://platform.openai.com/api-keys
   - Set as: `OPENAI_API_KEY`

2. **Google Gemini API Key** (for Gemini provider)
   - Get your key from: https://makersuite.google.com/app/apikey
   - Set as: `GEMINI_API_KEY`

3. **Anthropic Claude API Key** (for Claude provider)
   - Get your key from: https://console.anthropic.com/
   - Set as: `CLAUDE_API_KEY`

### Setting Environment Variables

#### Windows (PowerShell)
```powershell
$env:OPENAI_API_KEY="your_openai_key_here"
$env:GEMINI_API_KEY="your_gemini_key_here"
$env:CLAUDE_API_KEY="your_claude_key_here"
```

#### Windows (Command Prompt)
```cmd
set OPENAI_API_KEY=your_openai_key_here
set GEMINI_API_KEY=your_gemini_key_here
set CLAUDE_API_KEY=your_claude_key_here
```

#### Linux/Mac
```bash
export OPENAI_API_KEY="your_openai_key_here"
export GEMINI_API_KEY="your_gemini_key_here"
export CLAUDE_API_KEY="your_claude_key_here"
```

### Using .env File (Recommended)

Create a `.env` file in the project root with:
```
OPENAI_API_KEY=your_openai_key_here
GEMINI_API_KEY=your_gemini_key_here
CLAUDE_API_KEY=your_claude_key_here
```

**Important**: Never commit `.env` files to version control!

### Security Notes

- Keep your API keys secure and never share them
- Use environment variables instead of hardcoding keys
- Add `.env` to your `.gitignore` file
- Rotate your API keys regularly
