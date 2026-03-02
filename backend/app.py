import io
import logging
import traceback
from threading import Lock
from urllib.parse import urlparse

import requests
from flask import Flask, jsonify, request, send_file
from flask_cors import CORS

from config import Config
from services.export_service import ExportService
from services.jirafetch import JiraFetchService
from services.llm_engine import LLMEngine
from services.testrail import TestRailService


app = Flask(__name__)
app.config["SECRET_KEY"] = Config.SECRET_KEY
CORS(app, origins=[origin.strip() for origin in Config.CORS_ORIGINS.split(",") if origin.strip()])

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
logger = logging.getLogger("jira-testcase-app")

jira_service = JiraFetchService()
llm_engine = LLMEngine()
export_service = ExportService(export_dir=Config.EXPORT_DIR)
testrail_service = TestRailService(
    base_url=Config.TESTRAIL_BASE_URL,
    username=Config.TESTRAIL_USERNAME,
    api_key=Config.TESTRAIL_API_KEY,
    password=Config.TESTRAIL_PASSWORD,
    default_project_id=Config.TESTRAIL_PROJECT_ID,
    default_suite_id=Config.TESTRAIL_SUITE_ID,
    default_section_id=Config.TESTRAIL_SECTION_ID,
)

_latest_cases = []
_latest_lock = Lock()


def _validate_test_types(test_types):
    if not isinstance(test_types, list) or not test_types:
        return False, "test_types must be a non-empty list"
    normalized = [str(x).strip().lower() for x in test_types]
    invalid = [x for x in normalized if x not in Config.DEFAULT_TEST_TYPES]
    if invalid:
        return False, f"Invalid test_types: {invalid}. Allowed: {Config.DEFAULT_TEST_TYPES}"
    return True, normalized


def _store_latest_cases(cases):
    with _latest_lock:
        _latest_cases.clear()
        _latest_cases.extend(cases)


def _read_latest_cases():
    with _latest_lock:
        return list(_latest_cases)


@app.errorhandler(Exception)
def handle_exception(exc):
    if isinstance(exc, ValueError):
        message = str(exc)
        if "(404)" in message:
            return jsonify({"error": message}), 404
        if "(401)" in message:
            return jsonify({"error": message}), 401
        return jsonify({"error": message}), 400
    logger.error("Unhandled error: %s\n%s", exc, traceback.format_exc())
    return jsonify({"error": "Internal server error", "details": str(exc)}), 500


@app.get("/health")
def health():
    return jsonify({"status": "ok"})


@app.get("/attachment/file")
def attachment_file():
    content_url = str(request.args.get("content_url", "")).strip()
    filename = str(request.args.get("filename", "attachment.bin")).strip() or "attachment.bin"
    mime_type = str(request.args.get("mime_type", "application/octet-stream")).strip()
    download = str(request.args.get("download", "0")).strip().lower() in {"1", "true", "yes"}

    if not content_url:
        return jsonify({"error": "content_url is required"}), 400

    parsed = urlparse(content_url)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        return jsonify({"error": "Invalid content_url"}), 400

    jira_host = urlparse(jira_service.base_url).hostname or ""
    host = parsed.hostname or ""
    allowed = (
        (jira_host and host == jira_host)
        or host.endswith(".atlassian.net")
        or host.endswith(".atlassian.com")
    )
    if not allowed:
        return jsonify({"error": "Attachment host is not allowed"}), 400

    response = requests.get(
        content_url,
        auth=(jira_service.username, jira_service.api_token),
        timeout=60,
    )
    if response.status_code >= 400:
        return jsonify({"error": f"Attachment fetch failed ({response.status_code})"}), response.status_code

    return send_file(
        io.BytesIO(response.content),
        as_attachment=download,
        download_name=filename,
        mimetype=mime_type or "application/octet-stream",
    )


@app.post("/generate-from-jira")
def generate_from_jira():
    payload = request.get_json(silent=True) or {}
    issue_key = str(payload.get("issue_key", "")).strip()
    test_types = payload.get("test_types", [])
    preview_only = bool(payload.get("preview_only", False))

    if not issue_key:
        return jsonify({"error": "issue_key is required"}), 400

    parsed_test_types = []
    if not preview_only:
        valid, parsed_test_types = _validate_test_types(test_types)
        if not valid:
            return jsonify({"error": parsed_test_types}), 400

    issue_data = jira_service.fetch_issue_details(issue_key=issue_key)

    if preview_only:
        return jsonify(
            {
                "issue_key": issue_data.get("issue_key", issue_key),
                "source_data": issue_data,
                "test_cases": [],
            }
        ), 200

    test_cases = llm_engine.generate_from_jira_issue(issue_data, parsed_test_types)
    _store_latest_cases(test_cases)
    return jsonify(
        {
            "issue_key": issue_data.get("issue_key", issue_key),
            "source_data": issue_data,
            "test_cases": test_cases,
        }
    ), 200


@app.post("/preview-jira")
def preview_jira():
    payload = request.get_json(silent=True) or {}
    issue_key = str(payload.get("issue_key", "")).strip()

    if not issue_key:
        return jsonify({"error": "issue_key is required"}), 400

    issue_data = jira_service.fetch_issue_details(issue_key=issue_key)
    return jsonify(
        {
            "issue_key": issue_data.get("issue_key", issue_key),
            "source_data": issue_data,
            "test_cases": [],
        }
    ), 200


@app.post("/manual-generate-test")
def manual_generate():
    payload = request.get_json(silent=True) or {}
    description = str(payload.get("description", "")).strip()
    acceptance_criteria = str(payload.get("acceptance_criteria", "")).strip()
    attachments_text = str(payload.get("attachments_text", "")).strip()
    test_types = payload.get("test_types", [])

    if not description and not acceptance_criteria and not attachments_text:
        return (
            jsonify(
                {
                    "error": (
                        "At least one of description, acceptance_criteria, "
                        "or attachments_text is required"
                    )
                }
            ),
            400,
        )

    valid, parsed_test_types = _validate_test_types(test_types)
    if not valid:
        return jsonify({"error": parsed_test_types}), 400

    source = {
        "issue_key": "MANUAL",
        "summary": "Manual input",
        "description": description,
        "acceptance_criteria": acceptance_criteria,
        "issue_type": "Manual Input",
        "attachments_text": [attachments_text] if attachments_text else [],
        "attachments": [
            {
                "source_issue_key": "MANUAL",
                "filename": "manual_text_input.txt",
                "mime_type": "text/plain",
                "size_bytes": len(attachments_text),
                "content_url": "",
                "download_status": "provided_by_user",
                "parse_status": "parsed" if attachments_text else "not_parsed",
                "parsed_text": attachments_text,
            }
        ]
        if attachments_text
        else [],
        "custom_fields": {},
    }
    test_cases = llm_engine.generate_from_jira_issue(source, parsed_test_types)
    _store_latest_cases(test_cases)
    return jsonify({"issue_key": "MANUAL", "source_data": source, "test_cases": test_cases}), 200


@app.get("/export/excel")
def export_excel():
    cases = _read_latest_cases()
    if not cases:
        return jsonify({"error": "No generated test cases found"}), 404
    excel_bytes = export_service.export_excel_bytes(cases)
    return send_file(
        io.BytesIO(excel_bytes),
        as_attachment=True,
        download_name="generated_test_cases.xlsx",
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )


@app.get("/export/pdf")
def export_pdf():
    cases = _read_latest_cases()
    if not cases:
        return jsonify({"error": "No generated test cases found"}), 404
    pdf_bytes = export_service.export_pdf_bytes(cases)
    return send_file(
        io.BytesIO(pdf_bytes),
        as_attachment=True,
        download_name="generated_test_cases.pdf",
        mimetype="application/pdf",
    )


@app.get("/export/gherkin")
def export_gherkin():
    cases = _read_latest_cases()
    if not cases:
        return jsonify({"error": "No generated test cases found"}), 404
    gherkin_bytes = export_service.export_gherkin_bytes(cases)
    return send_file(
        io.BytesIO(gherkin_bytes),
        as_attachment=True,
        download_name="generated_test_cases.feature",
        mimetype="text/plain; charset=utf-8",
    )


@app.post("/testrail/push")
def push_testrail():
    cases = _read_latest_cases()
    if not cases:
        return jsonify({"error": "No generated test cases found"}), 404

    payload = request.get_json(silent=True) or {}
    project_id = str(payload.get("project_id", "")).strip() or None
    suite_id = str(payload.get("suite_id", "")).strip() or None
    section_id = str(payload.get("section_id", "")).strip() or None

    result = testrail_service.push_test_cases(
        test_cases=cases,
        project_id=project_id,
        suite_id=suite_id,
        section_id=section_id,
    )
    return jsonify(result), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=Config.FLASK_DEBUG)
