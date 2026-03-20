# Phoenix SmartCaseAI

Production-ready QA automation suite to generate, review, export, and publish test cases using LLMs.

## Contents

- Overview
- Features
- Tech Stack
- Project Structure
- Setup
- Configuration
- API Reference
- Notes

## Overview

This app helps QA teams:
- Generate test cases from Jira issues or manual input
- Generate automation locators and runnable templates
- Review, edit, approve, and reject test cases
- Export outputs in multiple formats
- Push approved cases to TestRail
- Track review and dashboard metrics

## Features

### Test Case Generation
- **Jira Issue**: fetch issue details and attachments
- **Manual Input**: description, acceptance criteria, and attachments
- Configurable test types and model selection

### Locator Generation
- Input DOM/HTML
- Framework: `Selenium` or `Playwright`
- Language: `Python`, `TypeScript`, `Java`
- Optional custom instructions
- Outputs structured locators + runnable template

### Review Workflow
- Inline edits with per-case status: `approved`, `pending`, `rejected`
- Review Queue with bulk approve and reviewer notes
- Rejected cases are excluded from export and TestRail push

### Export & TestRail
- Export: Excel, PDF, Gherkin, Plain Text, CSV, JSON
- TestRail push modes:
  - `single_repository`
  - `single_repository_with_baseline`
  - `multiple_test_suites`

### UX
- Sticky top navigation
- Dark/Light mode toggle (persisted)
- Toast notifications + loading overlay
- Dashboard metrics and recent activity

## Tech Stack

- Backend: Flask
- Frontend: React + Vite
- LLM providers: Gemini, OpenAI, Anthropic, OpenRouter, local llama (`llama-cpp-python`), fallback
- Embeddings/RAG: `sentence-transformers` + `faiss-cpu`
- Exports: Excel, PDF, Gherkin, Plain Text, CSV, JSON

## Project Structure

```text
backend/
  app.py
  config.py
  requirements.txt
  requirements-llama.txt
  services/
  utils/
  embeddings/
frontend/
  package.json
  vite.config.js
  index.html
  src/
```

## Setup

### Backend (Windows)

1. Open terminal in `backend/`
2. Create and activate a venv:
   ```bash
   python -m venv .venv
   .venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Optional local llama runtime:
   ```bash
   pip install -r requirements-llama.txt
   ```
5. Create `.env` from template:
   ```bash
   copy .env.example .env
   ```
6. Fill required environment values:
   - `JIRA_BASE_URL`
   - `JIRA_USERNAME`
   - `JIRA_API_TOKEN`
7. Run backend:
   ```bash
   python app.py
   ```

Backend default: `http://localhost:5000`

### Frontend

1. Open terminal in `frontend/`
2. Install dependencies:
   ```bash
   npm install
   ```
3. Run dev server:
   ```bash
   npm run dev
   ```

Frontend default: `http://localhost:5173`

### Dev Proxy

The Vite dev server proxies API routes to Flask. If you add new endpoints, update `frontend/vite.config.js`.

## Configuration

### Backend `.env` template

```env
FLASK_ENV=development
FLASK_DEBUG=true
SECRET_KEY=your_secret_key

JIRA_BASE_URL=https://your-domain.atlassian.net
JIRA_USERNAME=your-jira-email@example.com
JIRA_API_TOKEN=your-jira-api-token

CORS_ORIGINS=http://localhost:5173
EXPORT_DIR=exports

LLM_PROVIDER=auto
LLM_DEFAULT_MODEL_ID=gemini-2.5-flash
LLM_MODEL_PATH=
LLM_N_CTX=4096
LLM_MAX_TOKENS=1200
LLM_TEMPERATURE=0.1
LLM_TIMEOUT_SECONDS=60

GEMINI_API_KEY=your_gemini_api_key
GEMINI_MODEL=gemini-2.5-flash
GEMINI_MINI_MODEL=gemini-2.0-flash-lite
GEMINI_BASE_URL=https://generativelanguage.googleapis.com/v1beta

OPENAI_API_KEY=your_openai_api_key
OPENAI_BASE_URL=your_openai_base_url
OPENAI_MINI_MODEL=gpt-4.1-mini
OPENAI_NANO_MODEL=gpt-4.1-nano
OPENAI_4O_MINI_MODEL=gpt-4o-mini

ANTHROPIC_API_KEY=your_anthropic_api_key
ANTHROPIC_BASE_URL=your_anthropic_base_url
CLAUDE_SONNET_MODEL=claude-3-7-sonnet-latest
CLAUDE_HAIKU_MODEL=claude-3-5-haiku-latest

OPENROUTER_API_KEY=your_openrouter_api_key
OPENROUTER_BASE_URL=your_openrouter_base_url

TESTRAIL_BASE_URL=your_testrail_base_url
TESTRAIL_USERNAME=your_testrail_username
TESTRAIL_API_KEY=your_testrail_api_key
TESTRAIL_PASSWORD=your_testrail_password
TESTRAIL_PROJECT_ID=your_testrail_project_id
TESTRAIL_SUITE_ID=your_testrail_suite_id
TESTRAIL_SECTION_ID=your_testrail_section_id

EMBEDDING_MODEL_NAME=sentence-transformers/all-MiniLM-L6-v2
```

### Frontend `.env` template

```env
VITE_API_BASE_URL=http://localhost:5000
```

### Required Knowledge Base Files

The app injects these files into prompts and treats them as mandatory policy for generation:
- `backend/knowledge/test-cases-knowledge.md` for test case generation
- `backend/knowledge/weblocator-knowledge.md` for locator generation

If either file is missing or empty, generation returns an error.

### Store API Keys in GitHub Secrets

Do not store real keys in the repo. Use GitHub secrets and generate `backend/.env` at runtime.

Example GitHub Actions step:

```yaml
- name: Create backend .env from GitHub Secrets
  shell: bash
  run: |
    cat > backend/.env << 'EOF'
    FLASK_ENV=production
    FLASK_DEBUG=false
    SECRET_KEY=${{ secrets.SECRET_KEY }}
    JIRA_BASE_URL=${{ secrets.JIRA_BASE_URL }}
    JIRA_USERNAME=${{ secrets.JIRA_USERNAME }}
    JIRA_API_TOKEN=${{ secrets.JIRA_API_TOKEN }}
    CORS_ORIGINS=${{ secrets.CORS_ORIGINS }}
    EXPORT_DIR=exports
    LLM_PROVIDER=auto
    LLM_DEFAULT_MODEL_ID=gemini-2.5-flash
    LLM_TIMEOUT_SECONDS=60
    GEMINI_API_KEY=${{ secrets.GEMINI_API_KEY }}
    OPENAI_API_KEY=${{ secrets.OPENAI_API_KEY }}
    ANTHROPIC_API_KEY=${{ secrets.ANTHROPIC_API_KEY }}
    OPENROUTER_API_KEY=${{ secrets.OPENROUTER_API_KEY }}
    TESTRAIL_BASE_URL=${{ secrets.TESTRAIL_BASE_URL }}
    TESTRAIL_USERNAME=${{ secrets.TESTRAIL_USERNAME }}
    TESTRAIL_API_KEY=${{ secrets.TESTRAIL_API_KEY }}
    EOF
```

## API Reference

### Health and metadata
- `GET /health`
- `GET /llm-models`
- `GET /dashboard/metrics`
- `GET /testcases/latest`
- `GET /review-queue?status=all|pending|approved|rejected`

### Generation
- `POST /generate-from-jira`
- `POST /manual-generate-test`
- `POST /generate-locators`
- `POST /review-testcases`
- `POST /review-queue/update`
- `POST /review-queue/approve-all`

### Exports
- `POST /export-testcases` with body `{ "format": "<format>" }`
  - supported: `excel`, `pdf`, `gherkin`, `plain`, `csv`, `json`
  - exports only non-rejected cases
- Legacy GET exports still available:
  - `GET /export/excel`
  - `GET /export/pdf`
  - `GET /export/gherkin`
  - `GET /export/plain`

### Attachments
- `GET /attachment/file`

### TestRail
- `POST /testrail/push`
  - pushes only non-rejected cases
  - requires TestRail configuration (base URL, username, API key/password, section_id)

## Notes

- Credentials and API keys stay backend-side only.
- In `auto` mode, the backend tries the provider chain and falls back if needed.
- If no model/API key is available, deterministic fallback generation is used.
