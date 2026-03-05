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
