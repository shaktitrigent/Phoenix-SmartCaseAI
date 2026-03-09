# QA Automation Suite

Production-ready full-stack application to:
- fetch issue context (Jira or manual input),
- generate intelligent QA test cases with LLMs,
- generate automation locators and runnable test templates,
- review/edit/approve/reject generated test cases,
- export outputs,
- push generated test cases to TestRail.

## Tech Stack

- Backend: Flask
- Frontend: React + Vite
- LLM Providers: Gemini, OpenAI, Anthropic, OpenRouter, local llama (`llama-cpp-python`), fallback
- Embeddings/RAG: `sentence-transformers` + `faiss-cpu`
- Exports: Excel, PDF, Gherkin, Plain Text, CSV, JSON

## Key Features

### 1. Test Case Generation

- **Tab 1: Jira Issue**
  - Fetches Jira issue details + attachments
  - Generates structured test cases by selected test types
- **Tab 2: Manual Input**
  - Accepts description, acceptance criteria, optional prompt, and file uploads
  - Generates structured test cases without Jira dependency

### 2. Locator Generation

- **Tab 3: Generate Locators**
  - Input DOM/HTML
  - Select automation framework (`Selenium` or `Playwright`)
  - Select language (`Python`, `TypeScript`, `Java`)
  - Optional custom locator instructions
  - Returns:
    - structured locator JSON
    - generated runnable test template

### 3. Review, Export, and TestRail

- Review workflow:
  - Inline edit for generated test cases
  - Per-case status: `approved`, `pending`, `rejected`
  - Manual edit metadata tracked (`is_edited`, `edited_fields`, `last_edited_at`, `last_edited_by`)
  - Rejected cases are excluded from export and TestRail push
- Export dropdown:
  - Export All
  - Export as Plain Text
  - Export as Gherkin
  - Export as PDF
  - Export as Excel
- Push to TestRail dropdown modes:
  - `single_repository`
  - `single_repository_with_baseline`
  - `multiple_test_suites`

### 4. UX

- Sticky top navigation
- Dark/Light mode toggle (persisted to `localStorage`)
- Toast notifications
- Loading overlay
- Validation states for required fields

## Supported Upload Formats

### Primary formats shown in UI

- `.pdf`, `.docx`, `.txt`, `.png`, `.jpg`, `.jpeg`, `.gif`, `.xml`, `.csv`, `.xlsx`

### Additional formats shown under "More supported formats"

- `.json`, `.md`, `.log`, `.yaml`, `.yml`, `.html`, `.htm`, `.rtf`, `.xls`, `.oc`

Notes:
- Images are used as metadata context for generation.
- Some accepted extensions may parse as empty/unsupported depending on file content.

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

## Architecture Diagram

### Component View

```text
+---------------------------+              +---------------------------+
| React + Vite Frontend     |   HTTP/JSON  | Flask Backend             |
|                           +------------->|                           |
| - Jira/Manual forms       |              | - app.py routes           |
| - Locator form            |              | - validation + orchestrat |
| - Review table            |              | - latest cases store      |
| - Export / TestRail UI    |              |                           |
+-------------+-------------+              +-------------+-------------+
              |                                            |
              |                                            |
              v                                            v
  +-----------+-----------+                   +------------+------------+
  | Browser download APIs |                   | LLMEngine / LLMService  |
  | (export files)        |                   | - provider routing       |
  +-----------------------+                   | - fallback handling      |
                                              +------------+------------+
                                                           |
                                                           v
                                    +----------------------+----------------------+
                                    | External Integrations                       |
                                    | - Jira API                                  |
                                    | - OpenRouter / OpenAI / Gemini / Anthropic |
                                    | - TestRail API                              |
                                    +---------------------------------------------+
```

### Request Flow (Test Case Path)

```text
User -> Frontend Form -> /generate-from-jira or /manual-generate-test
     -> Flask app.py -> LLMEngine -> LLMService(provider/model)
     -> Parsed test cases -> Frontend editable review table
     -> /review-testcases (sync edits + statuses)
     -> /export-testcases OR /testrail/push (rejected excluded)
```

## Backend Setup (Windows)

1. Open terminal in `backend/`
2. Create and activate venv:
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
6. Fill environment values (minimum):
   - `JIRA_BASE_URL`
   - `JIRA_USERNAME`
   - `JIRA_API_TOKEN`
7. Run backend:
   ```bash
   python app.py
   ```

Backend default: `http://localhost:5000`

## Frontend Setup

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

## Environment Templates

Use templates only, and never commit real keys/tokens.

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

### Knowledge Base Files (Mandatory)

The app injects these files into prompts and treats them as mandatory policy for generation:

- `backend/knowledge/test-cases-knowledge.md` for test case generation
- `backend/knowledge/weblocator-knowledge.md` for locator generation

To update behavior later, edit/replace these two files directly. No code changes are required.

If either file is missing/empty, generation returns an error.

### Frontend `.env` template

```env
VITE_API_BASE_URL=http://localhost:5000
```

## Store API Keys in GitHub Secrets

Do not store real API keys in tracked files. Keep secrets in GitHub repository secrets:

1. Open GitHub repo -> `Settings` -> `Secrets and variables` -> `Actions`.
2. Add secrets for your backend keys, for example:
   - `JIRA_BASE_URL`
   - `JIRA_USERNAME`
   - `JIRA_API_TOKEN`
   - `GEMINI_API_KEY`
   - `OPENAI_API_KEY`
   - `ANTHROPIC_API_KEY`
   - `OPENROUTER_API_KEY`
   - `TESTRAIL_BASE_URL`
   - `TESTRAIL_USERNAME`
   - `TESTRAIL_API_KEY`
3. In GitHub Actions workflow, generate `backend/.env` from secrets at runtime.

Example step:

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

## Environment Variables (Backend)

### Core

- `FLASK_ENV`, `FLASK_DEBUG`, `SECRET_KEY`
- `CORS_ORIGINS`
- `EXPORT_DIR`

### Jira

- `JIRA_BASE_URL`
- `JIRA_USERNAME`
- `JIRA_API_TOKEN`

### LLM

- `LLM_PROVIDER` (`auto|gemini|openai|anthropic|openrouter|llama|fallback`)
- `LLM_DEFAULT_MODEL_ID`
- `LLM_TIMEOUT_SECONDS`
- `LLM_MODEL_PATH` (for local llama)

### Provider keys/models

- Gemini: `GEMINI_API_KEY`, `GEMINI_MODEL`
- OpenAI: `OPENAI_API_KEY`, `OPENAI_MINI_MODEL`
- Anthropic: `ANTHROPIC_API_KEY`, `CLAUDE_SONNET_MODEL`
- OpenRouter: `OPENROUTER_API_KEY`, `OPENROUTER_BASE_URL` (free-tier model allowlist enforced in backend)
  - Allowed free models: `deepseek/deepseek-chat`, `deepseek/deepseek-coder`, `meta-llama/llama-3-8b-instruct`, `meta-llama/llama-3-70b-instruct`, `mistralai/mistral-7b-instruct`, `mistralai/mixtral-8x7b-instruct`

### Active model catalog (UI)

- Gemini 2.5 Flash
- OpenAI GPT-4.1 Mini
- Claude 3.7 Sonnet
- OpenRouter free models (allowlist above)
- Local Llama (GGUF)
- Rule-based fallback

### TestRail

- `TESTRAIL_BASE_URL`
- `TESTRAIL_USERNAME`
- `TESTRAIL_API_KEY` (or fallback `TESTRAIL_PASSWORD`)
- `TESTRAIL_PROJECT_ID`
- `TESTRAIL_SUITE_ID` (optional)
- `TESTRAIL_SECTION_ID`

## API Endpoints

### Health and metadata

- `GET /health`
- `GET /llm-models`

### Generation

- `POST /generate-from-jira`
- `POST /manual-generate-test`
- `POST /generate-locators`
- `POST /review-testcases`

### Exports

- `POST /export-testcases` with body `{ "format": "<format>" }`
  - supported: `excel`, `pdf`, `gherkin`, `plain`, `csv`, `json`
  - exports only non-rejected cases
- Legacy GET exports still available:
  - `GET /export/excel`
  - `GET /export/pdf`
  - `GET /export/gherkin`
  - `GET /export/plain`
  - each exports only non-rejected cases

### Attachments

- `GET /attachment/file`

### TestRail

- `POST /testrail/push`
  - pushes only non-rejected cases

## Review Workflow API

### Request (`POST /review-testcases`)

```json
{
  "test_cases": [
    {
      "test_case_id": "TC-001",
      "title": "Updated title",
      "preconditions": "User has valid account",
      "steps": ["Open page", "Perform action", "Validate output"],
      "expected_result": "Expected behavior is observed",
      "test_type": "functional",
      "priority": "High",
      "review_status": "approved",
      "is_edited": true,
      "edited_fields": ["title", "steps"],
      "last_edited_at": "2026-03-05T11:00:00Z",
      "last_edited_by": "manual"
    }
  ]
}
```

### Response

```json
{
  "status": "ok",
  "stored": 1,
  "exportable": 1
}
```

## Locator Generation Request/Response

### Request (`POST /generate-locators`)

```json
{
  "dom": "<html>...</html>",
  "framework": "Selenium",
  "language": "Python",
  "custom_prompt": "Prefer data-testid",
  "model_id": "gemini-2.5-flash"
}
```

### Response

```json
{
  "locators": [
    {
      "element": "Login Button",
      "primary_locator": "...",
      "alternate_locator": "...",
      "strategy": "CSS Selector"
    }
  ],
  "test_template": "Complete runnable test file",
  "model_used": "gemini:gemini-2.5-flash"
}
```

## Notes

- Credentials and API keys stay backend-side only.
- In `auto` mode, backend tries available provider chain then fallback.
- If no model/API key is available, deterministic fallback generation is used.
