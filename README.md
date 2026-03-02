# Jira LLM Test Case Generator

Production-structured full-stack application that ingests Jira issue data and generates structured QA test cases using a local LLM pipeline.

## Stack

- Backend: Flask
- Frontend: React + Vite
- Jira API: REST v3
- LLM: `llama-cpp-python` or Gemini API (`gemini-2.5-flash`)
- Embeddings: `sentence-transformers` + `faiss-cpu`
- Export: Excel (`pandas/openpyxl`), PDF (`reportlab`), and Gherkin (`.feature`)

## Project Structure

```text
backend/
  app.py
  config.py
  requirements.txt
  .env.example
  services/
  utils/
  embeddings/
frontend/
  package.json
  vite.config.js
  src/
```

## Application Flow

1. User enters a Jira issue key (or manual text) in the React UI.
2. Frontend calls Flask API (`/generate-from-jira` or `/manual-generate-test`) via axios.
3. `backend/app.py` validates input and routes request to service layer.
4. `backend/services/jirafetch.py` pulls Jira issue details using Jira REST API:
   - summary
   - description
   - acceptance criteria/custom fields
   - attachments metadata and files
5. `backend/services/document_parser.py` parses downloaded attachments:
   - PDF (`PyPDF2`)
   - DOCX (`python-docx`)
   - Excel/CSV (`pandas/openpyxl`)
   - XML (`xmlparser.py`, `multi_xml_loader.py`)
   - text files
6. `backend/embeddings/vector_store.py` builds embeddings for semantic context (SentenceTransformer + FAISS).
7. `backend/utils/prompt_builder.py` creates a strict JSON generation prompt with issue + attachment context.
8. `backend/services/llm_engine.py` calls `backend/services/llm.py`:
   - uses `llama-cpp-python` when local model exists
   - otherwise uses deterministic fallback generation
9. `backend/utils/response_parser.py` enforces normalized test-case structure.
10. Response is returned to frontend and rendered in a structured table.
11. Export endpoints (`/export/excel`, `/export/pdf`, `/export/gherkin`) convert latest generated cases into downloadable files.

## Core Files and Responsibilities

- `backend/app.py`: Flask app factory/runtime, API endpoints, validation, error handling, CORS, export streaming.
- `backend/config.py`: Centralized environment-based configuration.
- `backend/services/jirafetch.py`: Jira integration, issue fetch, custom fields extraction, attachment download.
- `backend/services/document_parser.py`: Unified parser for PDF/DOCX/XLSX/CSV/XML/TXT.
- `backend/services/xmlparser.py`: Single XML file parser.
- `backend/services/multi_xml_loader.py`: Multi-file XML aggregation.
- `backend/services/llm.py`: LLM wrapper (`llama-cpp-python`) + fallback generator.
- `backend/services/llm_engine.py`: Orchestration of embeddings, prompting, model call, and final testcase shaping.
- `backend/services/export_service.py`: Excel, PDF, and Gherkin export generation.
- `backend/services/testrail.py`: TestRail push service (live API when configured, mock fallback otherwise).
- `backend/utils/prompt_builder.py`: Prompt and schema construction for strict JSON output.
- `backend/utils/response_parser.py`: Safe JSON extraction and response normalization.
- `backend/embeddings/vector_store.py`: Sentence-transformer embedding + FAISS semantic search.
- `frontend/src/pages/Home.jsx`: Main page state, submit flow, error/loading handling.
- `frontend/src/components/JiraForm.jsx`: Input UI for Jira/manual generation and test type selection.
- `frontend/src/components/TestCaseTable.jsx`: Generated testcase rendering.
- `frontend/src/components/ExportButtons.jsx`: Export actions.
- `frontend/src/services/api.js`: Frontend API client.

## Tools, Technologies, and Libraries

### Backend

- `flask`: REST API server.
- `flask-cors`: Cross-origin access for frontend.
- `python-dotenv`: Environment variable loading from `.env`.
- `requests`: Jira HTTP API communication and attachment download.
- `llama-cpp-python`: Local LLM inference (optional runtime dependency).
- `sentence-transformers`: Embedding generation.
- `faiss-cpu`: Vector index and semantic retrieval.
- `pandas`: Tabular transformations and export preprocessing.
- `PyPDF2`: PDF text extraction.
- `python-docx`: DOCX parsing.
- `openpyxl`: Excel read/write support.
- `reportlab`: PDF report generation.
- `gunicorn`: Production WSGI serving option.

### Frontend

- `react`: UI framework.
- `vite`: Fast dev server and build tooling.
- `axios`: HTTP client for backend API calls.

## Backend Setup

1. Open terminal in `backend/`
2. Create virtual environment and install deps:
   ```bash
   python -m venv .venv
   .venv\Scripts\activate
   pip install -r requirements.txt
   ```
   Optional local llama runtime:
   ```bash
   pip install -r requirements-llama.txt
   ```
   Note: On Windows, `llama-cpp-python` may require Visual Studio C++ Build Tools and CMake/NMake.
3. Copy env template:
   ```bash
   copy .env.example .env
   ```
4. Update `.env` values (`JIRA_BASE_URL`, `JIRA_USERNAME`, `JIRA_API_TOKEN`)
   For TestRail push, also set:
   ```bash
   TESTRAIL_BASE_URL=https://your-subdomain.testrail.io
   TESTRAIL_USERNAME=your-email@example.com
   TESTRAIL_API_KEY=your-testrail-api-key
   # Optional fallback when API key auth is unavailable
   TESTRAIL_PASSWORD=your-testrail-password
   TESTRAIL_PROJECT_ID=2
   TESTRAIL_SECTION_ID=6
   # Optional: leave empty to auto-resolve first suite in project
   TESTRAIL_SUITE_ID=
   ```
   To discover suite IDs for a project:
   ```bash
   curl -u "your-email@example.com:your-testrail-api-key" \
     "https://your-subdomain.testrail.io/index.php?/api/v2/get_suites/2"
   ```
   For Gemini 2.5 Flash, also set:
   ```bash
   LLM_PROVIDER=gemini
   GEMINI_API_KEY=your-api-key
   GEMINI_MODEL=gemini-2.5-flash
   ```
5. Run server:
   ```bash
   python app.py
   ```

Server runs on `http://localhost:5000`.

## Frontend Setup

1. Open terminal in `frontend/`
2. Install dependencies:
   ```bash
   npm install
   ```
3. Optional env:
   ```bash
   copy .env.example .env
   ```
4. Run dev server:
   ```bash
   npm run dev
   ```

Frontend runs on `http://localhost:5173`.

## API Endpoints

- `POST /generate-from-jira`
- `POST /manual-generate-test`
- `GET /export/excel`
- `GET /export/pdf`
- `GET /export/gherkin`
- `POST /testrail/push`
  - Live mode response includes each created case `id` and direct `case_url` for quick verification in TestRail.
  - Live mode also includes `section_url` so you can open the target TestRail section directly.
- `GET /health`

## Notes

- Jira credentials are backend-only via environment variables.
- `LLM_PROVIDER` options: `auto`, `gemini`, `llama`, `fallback`.
- In `auto`, backend prefers Gemini if `GEMINI_API_KEY` exists, then llama (if model path exists), then rule-based fallback.
- If neither Gemini nor llama are available, app uses a deterministic fallback generator.
- Embedding search is enabled when a local sentence-transformer model is available.
