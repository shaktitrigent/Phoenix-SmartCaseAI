import io
import logging
import os
import tempfile
import traceback
from threading import Lock
from urllib.parse import urlparse

import requests
from flask import Flask, jsonify, request, send_file
from flask_cors import CORS

from config import Config
from services.export_service import ExportService
from services.document_parser import DocumentParser
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
document_parser = DocumentParser()

_latest_cases = []
_latest_lock = Lock()
_manual_upload_max_size_bytes = 10 * 1024 * 1024
_manual_upload_exts = {
    ".pdf",
    ".docx",
    ".txt",
    ".md",
    ".log",
    ".png",
    ".jpg",
    ".jpeg",
    ".gif",
    ".xml",
    ".json",
    ".yaml",
    ".yml",
    ".html",
    ".htm",
    ".rtf",
    ".csv",
    ".xlsx",
    ".xls",
    ".oc",
}
_testrail_repository_modes = {
    "single_repository",
    "single_repository_with_baseline",
    "multiple_test_suites",
}
_locator_frameworks = {"selenium", "playwright"}
_locator_languages = {"typescript", "java", "python"}


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


def _normalize_reviewed_case(raw_case):
    if not isinstance(raw_case, dict):
        return {}

    case = dict(raw_case)
    test_case_id = str(case.get("test_case_id", "")).strip()
    title = str(case.get("title", "")).strip()
    preconditions = str(case.get("preconditions", "")).strip()
    expected_result = str(case.get("expected_result", "")).strip()
    test_type = str(case.get("test_type", "")).strip()
    priority = str(case.get("priority", "")).strip()
    review_status = str(case.get("review_status", "approved")).strip().lower()
    if review_status not in {"approved", "rejected", "pending"}:
        review_status = "approved"

    steps = case.get("steps", [])
    if isinstance(steps, list):
        normalized_steps = [str(step).strip() for step in steps if str(step).strip()]
    elif isinstance(steps, str):
        normalized_steps = [part.strip() for part in steps.split("\n") if part.strip()]
    else:
        normalized_steps = []

    edited_fields = case.get("edited_fields", [])
    if isinstance(edited_fields, list):
        normalized_fields = [str(field).strip() for field in edited_fields if str(field).strip()]
    else:
        normalized_fields = []

    return {
        "test_case_id": test_case_id,
        "title": title,
        "preconditions": preconditions,
        "steps": normalized_steps,
        "expected_result": expected_result,
        "test_type": test_type,
        "priority": priority,
        "review_status": review_status,
        "is_edited": bool(case.get("is_edited", False)),
        "edited_fields": normalized_fields,
        "last_edited_at": str(case.get("last_edited_at", "")).strip(),
        "last_edited_by": str(case.get("last_edited_by", "")).strip(),
    }


def _read_latest_cases(exportable_only=False):
    with _latest_lock:
        snapshot = list(_latest_cases)
    if not exportable_only:
        return snapshot
    return [case for case in snapshot if str(case.get("review_status", "approved")).lower() != "rejected"]


def _extract_payload():
    if request.is_json:
        return request.get_json(silent=True) or {}
    return request.form.to_dict(flat=True)


def _extract_test_types(payload):
    raw = payload.get("test_types", [])
    if isinstance(raw, list):
        return raw
    if isinstance(raw, str):
        values = [part.strip() for part in raw.split(",") if part.strip()]
        return values
    return []


def _parse_manual_attachments(uploaded_files):
    parsed_chunks = []
    attachment_records = []

    for file_storage in uploaded_files:
        if not file_storage:
            continue

        filename = str(file_storage.filename or "").strip() or "attachment"
        extension = os.path.splitext(filename)[1].lower()
        mime_type = str(file_storage.mimetype or "application/octet-stream").strip()

        if extension not in _manual_upload_exts:
            attachment_records.append(
                {
                    "source_issue_key": "MANUAL",
                    "filename": filename,
                    "mime_type": mime_type,
                    "size_bytes": 0,
                    "content_url": "",
                    "download_status": "uploaded_by_user",
                    "parse_status": "unsupported_type",
                    "parsed_text": "",
                }
            )
            continue

        file_storage.stream.seek(0, os.SEEK_END)
        size_bytes = int(file_storage.stream.tell() or 0)
        file_storage.stream.seek(0)

        if size_bytes > _manual_upload_max_size_bytes:
            attachment_records.append(
                {
                    "source_issue_key": "MANUAL",
                    "filename": filename,
                    "mime_type": mime_type,
                    "size_bytes": size_bytes,
                    "content_url": "",
                    "download_status": "uploaded_by_user",
                    "parse_status": "file_too_large",
                    "parsed_text": "",
                }
            )
            continue

        parsed_text = ""
        parse_status = "empty_or_unsupported"

        if extension in {".png", ".jpg", ".jpeg", ".gif"}:
            parsed_text = (
                f"Image attachment provided: {filename}. "
                "Use this image as input for visual/UI related test scenarios."
            )
            parse_status = "metadata_only"
        else:
            temp_path = ""
            try:
                with tempfile.NamedTemporaryFile(suffix=extension, delete=False) as tmp_file:
                    temp_path = tmp_file.name
                    file_storage.save(tmp_file)
                parsed_text = document_parser.parse_file(temp_path)
                parse_status = "parsed" if parsed_text else "empty_or_unsupported"
            except Exception:
                parsed_text = ""
                parse_status = "parse_failed"
            finally:
                if temp_path and os.path.exists(temp_path):
                    try:
                        os.remove(temp_path)
                    except OSError:
                        logger.warning("Failed to remove temp file: %s", temp_path)

        attachment_records.append(
            {
                "source_issue_key": "MANUAL",
                "filename": filename,
                "mime_type": mime_type,
                "size_bytes": size_bytes,
                "content_url": "",
                "download_status": "uploaded_by_user",
                "parse_status": parse_status,
                "parsed_text": parsed_text,
            }
        )
        if parsed_text:
            parsed_chunks.append(parsed_text)

    return parsed_chunks, attachment_records


def _export_response_for_format(format_name, cases):
    normalized = str(format_name or "").strip().lower()

    if normalized == "excel":
        content = export_service.export_excel_bytes(cases)
        return send_file(
            io.BytesIO(content),
            as_attachment=True,
            download_name="generated_test_cases.xlsx",
            mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
    if normalized == "csv":
        content = export_service.export_csv_bytes(cases)
        return send_file(
            io.BytesIO(content),
            as_attachment=True,
            download_name="generated_test_cases.csv",
            mimetype="text/csv; charset=utf-8",
        )
    if normalized == "json":
        content = export_service.export_json_bytes(cases)
        return send_file(
            io.BytesIO(content),
            as_attachment=True,
            download_name="generated_test_cases.json",
            mimetype="application/json; charset=utf-8",
        )
    if normalized == "pdf":
        content = export_service.export_pdf_bytes(cases)
        return send_file(
            io.BytesIO(content),
            as_attachment=True,
            download_name="generated_test_cases.pdf",
            mimetype="application/pdf",
        )
    if normalized == "gherkin":
        content = export_service.export_gherkin_bytes(cases)
        return send_file(
            io.BytesIO(content),
            as_attachment=True,
            download_name="generated_test_cases.feature",
            mimetype="text/plain; charset=utf-8",
        )
    if normalized == "plain":
        content = export_service.export_plain_text_bytes(cases)
        return send_file(
            io.BytesIO(content),
            as_attachment=True,
            download_name="generated_test_cases.txt",
            mimetype="text/plain; charset=utf-8",
        )

    return jsonify({"error": "Invalid format. Allowed: excel, csv, json, pdf, gherkin, plain"}), 400


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


@app.get("/llm-models")
def llm_models():
    models = llm_engine.llm.list_models()
    return jsonify(
        {
            "default_model_id": Config.LLM_DEFAULT_MODEL_ID,
            "models": models,
        }
    ), 200


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
    payload = _extract_payload()
    issue_key = str(payload.get("issue_key", "")).strip()
    model_id = str(payload.get("model_id", "")).strip() or None
    custom_prompt = str(payload.get("custom_prompt", "")).strip()
    test_types = _extract_test_types(payload)
    preview_only = bool(payload.get("preview_only", False))

    if not issue_key:
        return jsonify({"error": "issue_key is required"}), 400

    parsed_test_types = []
    if not preview_only:
        valid, parsed_test_types = _validate_test_types(test_types)
        if not valid:
            return jsonify({"error": parsed_test_types}), 400

    issue_data = jira_service.fetch_issue_details(issue_key=issue_key)
    if custom_prompt:
        issue_data["custom_prompt"] = custom_prompt

    if preview_only:
        return jsonify(
            {
                "issue_key": issue_data.get("issue_key", issue_key),
                "source_data": issue_data,
                "test_cases": [],
            }
        ), 200

    test_cases = llm_engine.generate_from_jira_issue(
        issue_data,
        parsed_test_types,
        model_id=model_id,
    )
    _store_latest_cases(test_cases)
    return jsonify(
        {
            "issue_key": issue_data.get("issue_key", issue_key),
            "source_data": issue_data,
            "test_cases": test_cases,
            "model_used": llm_engine.llm.last_model_used,
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
    payload = _extract_payload()
    description = str(payload.get("description", "")).strip()
    acceptance_criteria = str(payload.get("acceptance_criteria", "")).strip()
    custom_prompt = str(payload.get("custom_prompt", "")).strip()
    manual_attachments_text = str(payload.get("attachments_text", "")).strip()
    model_id = str(payload.get("model_id", "")).strip() or None
    test_types = _extract_test_types(payload)
    uploaded_files = request.files.getlist("attachments") if request.files else []
    parsed_upload_chunks, uploaded_attachment_records = _parse_manual_attachments(uploaded_files)

    attachment_chunks = []
    if manual_attachments_text:
        attachment_chunks.append(manual_attachments_text)
    attachment_chunks.extend(parsed_upload_chunks)
    attachments_text = "\n\n".join([chunk for chunk in attachment_chunks if chunk]).strip()

    if not description and not acceptance_criteria and not attachments_text and not custom_prompt:
        return (
            jsonify(
                {
                    "error": (
                        "At least one of description, acceptance_criteria, "
                        "attachments_text, or custom_prompt is required"
                    )
                }
            ),
            400,
        )

    valid, parsed_test_types = _validate_test_types(test_types)
    if not valid:
        return jsonify({"error": parsed_test_types}), 400

    manual_text_attachment = (
        [
            {
                "source_issue_key": "MANUAL",
                "filename": "manual_text_input.txt",
                "mime_type": "text/plain",
                "size_bytes": len(manual_attachments_text),
                "content_url": "",
                "download_status": "provided_by_user",
                "parse_status": "parsed" if manual_attachments_text else "not_parsed",
                "parsed_text": manual_attachments_text,
            }
        ]
        if manual_attachments_text
        else []
    )

    source = {
        "issue_key": "MANUAL",
        "summary": "Manual input",
        "description": description,
        "acceptance_criteria": acceptance_criteria,
        "custom_prompt": custom_prompt,
        "issue_type": "Manual Input",
        "attachments_text": [attachments_text] if attachments_text else [],
        "attachments": manual_text_attachment + uploaded_attachment_records,
        "custom_fields": {},
    }
    test_cases = llm_engine.generate_from_jira_issue(
        source,
        parsed_test_types,
        model_id=model_id,
    )
    _store_latest_cases(test_cases)
    return jsonify(
        {
            "issue_key": "MANUAL",
            "source_data": source,
            "test_cases": test_cases,
            "model_used": llm_engine.llm.last_model_used,
        }
    ), 200


@app.post("/generate-locators")
def generate_locators():
    payload = _extract_payload()
    dom = str(payload.get("dom", "")).strip()
    framework = str(payload.get("framework", "")).strip()
    language = str(payload.get("language", "")).strip()
    custom_prompt = str(payload.get("custom_prompt", "")).strip()
    model_id = str(payload.get("model_id", "")).strip() or None
    uploaded_files = request.files.getlist("attachments") if request.files else []
    parsed_upload_chunks, _uploaded_attachment_records = _parse_manual_attachments(uploaded_files)
    uploaded_text = "\n\n".join([chunk for chunk in parsed_upload_chunks if chunk]).strip()

    if not dom and not uploaded_text:
        return jsonify({"error": "dom or at least one supported attachment is required"}), 400
    if not framework:
        return jsonify({"error": "framework is required"}), 400
    if not language:
        return jsonify({"error": "language is required"}), 400

    framework_key = framework.lower()
    language_key = language.lower()
    if framework_key not in _locator_frameworks:
        return jsonify({"error": "framework must be one of: Selenium, Playwright"}), 400
    if language_key not in _locator_languages:
        return jsonify({"error": "language must be one of: TypeScript, Java, Python"}), 400

    merged_dom = dom
    if uploaded_text:
        merged_dom = (
            f"{dom}\n\n[Attachment-derived context]\n{uploaded_text}"
            if dom
            else f"[Attachment-derived context]\n{uploaded_text}"
        )

    result = llm_engine.generate_locators(
        dom=merged_dom,
        framework=framework,
        language=language,
        custom_prompt=custom_prompt,
        model_id=model_id,
    )
    return jsonify(result), 200


@app.post("/export-testcases")
def export_testcases():
    payload = _extract_payload()
    export_format = str(payload.get("format", "")).strip().lower()

    cases = _read_latest_cases(exportable_only=True)
    if not cases:
        return jsonify({"error": "No exportable test cases found"}), 404

    return _export_response_for_format(export_format, cases)


@app.get("/export/excel")
def export_excel():
    cases = _read_latest_cases(exportable_only=True)
    if not cases:
        return jsonify({"error": "No exportable test cases found"}), 404
    return _export_response_for_format("excel", cases)


@app.get("/export/pdf")
def export_pdf():
    cases = _read_latest_cases(exportable_only=True)
    if not cases:
        return jsonify({"error": "No exportable test cases found"}), 404
    return _export_response_for_format("pdf", cases)


@app.get("/export/gherkin")
def export_gherkin():
    cases = _read_latest_cases(exportable_only=True)
    if not cases:
        return jsonify({"error": "No exportable test cases found"}), 404
    return _export_response_for_format("gherkin", cases)


@app.get("/export/plain")
def export_plain():
    cases = _read_latest_cases(exportable_only=True)
    if not cases:
        return jsonify({"error": "No exportable test cases found"}), 404
    return _export_response_for_format("plain", cases)


@app.post("/review-testcases")
def review_testcases():
    payload = request.get_json(silent=True) or {}
    cases = payload.get("test_cases", [])
    if not isinstance(cases, list):
        return jsonify({"error": "test_cases must be a list"}), 400

    normalized_cases = [_normalize_reviewed_case(case) for case in cases if isinstance(case, dict)]
    if not normalized_cases:
        return jsonify({"error": "No valid test cases provided"}), 400

    _store_latest_cases(normalized_cases)
    exportable_count = len(_read_latest_cases(exportable_only=True))
    return jsonify({"status": "ok", "stored": len(normalized_cases), "exportable": exportable_count}), 200


@app.post("/testrail/push")
def push_testrail():
    cases = _read_latest_cases(exportable_only=True)
    if not cases:
        return jsonify({"error": "No exportable test cases found"}), 404

    payload = request.get_json(silent=True) or {}
    selected_test_case_ids_raw = payload.get("selected_test_case_ids")
    project_id = str(payload.get("project_id", "")).strip() or None
    suite_id = str(payload.get("suite_id", "")).strip() or None
    section_id = str(payload.get("section_id", "")).strip() or None
    repository_mode = str(payload.get("repository_mode", "")).strip() or "single_repository"

    if selected_test_case_ids_raw is not None:
        if isinstance(selected_test_case_ids_raw, list):
            selected_test_case_ids = [
                str(item).strip()
                for item in selected_test_case_ids_raw
                if str(item).strip()
            ]
        elif isinstance(selected_test_case_ids_raw, str):
            selected_test_case_ids = [
                part.strip()
                for part in selected_test_case_ids_raw.split(",")
                if part.strip()
            ]
        else:
            return jsonify({"error": "selected_test_case_ids must be a list or comma-separated string"}), 400

        if not selected_test_case_ids:
            return jsonify({"error": "No selected test cases provided"}), 400

        selected_id_set = set(selected_test_case_ids)
        cases = [
            case
            for case in cases
            if str(case.get("test_case_id", "")).strip() in selected_id_set
        ]
        if not cases:
            return jsonify({"error": "No matching exportable selected test cases found"}), 404

    if repository_mode not in _testrail_repository_modes:
        return (
            jsonify(
                {
                    "error": (
                        "Invalid repository_mode. Allowed: "
                        "single_repository, single_repository_with_baseline, multiple_test_suites"
                    )
                }
            ),
            400,
        )

    result = testrail_service.push_test_cases(
        test_cases=cases,
        project_id=project_id,
        suite_id=suite_id,
        section_id=section_id,
        repository_mode=repository_mode,
    )
    return jsonify(result), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=Config.FLASK_DEBUG)
