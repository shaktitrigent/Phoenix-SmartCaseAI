import io
import json
import logging
import os
import tempfile
import traceback
from datetime import datetime
from threading import Lock
from urllib.parse import urlparse

import requests
from flask import Flask, jsonify, request, send_file, send_from_directory
from flask_cors import CORS
from werkzeug.exceptions import HTTPException

from config import Config
from services.export_service import ExportService
from services.document_parser import DocumentParser
from services.llm_engine import LLMEngine
from integrations.registry import get_issue_provider, get_publisher


app = Flask(__name__)
app.config["SECRET_KEY"] = Config.SECRET_KEY
CORS(app, origins=[origin.strip() for origin in Config.CORS_ORIGINS.split(",") if origin.strip()])

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
logger = logging.getLogger("jira-testcase-app")

issue_provider = get_issue_provider()
# Backward-compatible alias for legacy references.
jira_service = issue_provider
llm_engine = LLMEngine()
export_service = ExportService(export_dir=Config.EXPORT_DIR)
testrail_publisher = get_publisher()
document_parser = DocumentParser()
_frontend_dist = os.path.join(os.path.dirname(__file__), "..", "frontend", "dist")

_latest_cases = []
_latest_lock = Lock()
_activity_log = []
_activity_lock = Lock()
_settings_lock = Lock()
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
_framework_aliases = {
    "pw": "playwright",
    "playwright": "playwright",
    "selenium": "selenium",
    "selenium-webdriver": "selenium",
    "webdriver": "selenium",
}
_language_aliases = {
    "ts": "typescript",
    "typescript": "typescript",
    "js": "typescript",
    "javascript": "typescript",
    "java": "java",
    "py": "python",
    "python": "python",
}
_jira_include_fields = {
    "summary",
    "description",
    "acceptance_criteria",
    "attachments",
    "custom_fields",
    "issue_type",
}
_storage_dir = os.path.join(os.path.dirname(__file__), "storage")
_latest_cases_file = os.path.join(_storage_dir, "latest_cases.json")
_activity_log_file = os.path.join(_storage_dir, "activity_log.json")
_settings_file = os.path.join(_storage_dir, "settings.json")
_rejection_log_file = os.path.join(_storage_dir, "rejection_reasons.md")
_settings_cache = {}
_default_settings = {
    "jira": {
        "base_url": "",
        "username": "",
        "api_token": "",
        "attachment_download_enabled": True,
        "attachment_parse_enabled": True,
    },
    "llm": {
        "default_model_id": "",
        "auto_fallback": True,
        "cache_enabled": True,
        "api_keys": {"anthropic": "", "gemini": "", "openai": "", "openrouter": ""},
    },
    "testrail": {
        "base_url": "",
        "username": "",
        "api_key": "",
        "push_only_approved": True,
        "overwrite_duplicates": False,
    },
    "behavior": {
        "default_test_types": ["functional", "regression", "ui"],
        "max_cases_per_issue": 10,
        "output_language": "English",
        "require_review_before_export": True,
        "auto_approve_on_regenerate": False,
        "show_duplicate_hints": True,
    },
}


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
    _persist_latest_cases()


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
    review_note = str(case.get("review_note", "")).strip()

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
        "review_note": review_note,
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


def _read_cases_by_status(status: str) -> list:
    normalized = str(status or "").strip().lower()
    cases = _read_latest_cases(exportable_only=False)
    if normalized in {"approved", "pending", "rejected"}:
        return [case for case in cases if str(case.get("review_status", "")).lower() == normalized]
    return cases


def _load_persisted_state():
    with _latest_lock:
        _latest_cases.clear()
        _latest_cases.extend(_load_json(_latest_cases_file, []))
    with _activity_lock:
        _activity_log.clear()
        _activity_log.extend(_load_json(_activity_log_file, []))
    settings = _load_settings()
    _apply_runtime_settings(settings)


def _compute_counts(cases):
    counts = {"total": 0, "pending": 0, "approved": 0, "rejected": 0}
    for case in cases:
        counts["total"] += 1
        status = str(case.get("review_status", "approved")).lower()
        if status not in counts:
            status = "approved"
        counts[status] += 1
    return counts


def _log_activity(message, category="system"):
    entry = {"message": str(message).strip(), "category": category}
    if not entry["message"]:
        return
    with _activity_lock:
        _activity_log.insert(0, entry)
        del _activity_log[50:]
    _persist_activity_log()


def _ensure_storage_dir():
    if not os.path.isdir(_storage_dir):
        os.makedirs(_storage_dir, exist_ok=True)


def _load_json(path, fallback):
    try:
        if not os.path.isfile(path):
            return fallback
        with open(path, "r", encoding="utf-8") as handle:
            return json.load(handle)
    except (OSError, json.JSONDecodeError):
        return fallback


def _save_json(path, payload):
    try:
        _ensure_storage_dir()
        temp_path = f"{path}.tmp"
        with open(temp_path, "w", encoding="utf-8") as handle:
            json.dump(payload, handle, ensure_ascii=True, indent=2)
        os.replace(temp_path, path)
    except OSError:
        logger.warning("Failed to persist data to %s", path)


def _persist_latest_cases():
    with _latest_lock:
        snapshot = list(_latest_cases)
    _save_json(_latest_cases_file, snapshot)


def _persist_activity_log():
    with _activity_lock:
        snapshot = list(_activity_log)
    _save_json(_activity_log_file, snapshot)


def _log_rejection(test_case_id, reason):
    if not reason.strip():
        return
    try:
        with open(_rejection_log_file, "a", encoding="utf-8") as f:
            f.write(f"## Test Case {test_case_id}\n")
            f.write(f"**Date:** {datetime.now().isoformat()}\n")
            f.write(f"**Reason:** {reason}\n\n")
    except Exception as e:
        logger.warning(f"Failed to log rejection for {test_case_id}: {e}")


def _deep_merge(base, updates):
    merged = dict(base)
    for key, value in (updates or {}).items():
        if isinstance(value, dict) and isinstance(merged.get(key), dict):
            merged[key] = _deep_merge(merged.get(key, {}), value)
        else:
            merged[key] = value
    return merged


def _load_settings():
    with _settings_lock:
        if _settings_cache:
            return dict(_settings_cache)
        stored = _load_json(_settings_file, {})
        merged = _deep_merge(_default_settings, stored)
        _settings_cache.update(merged)
        return dict(_settings_cache)


def _save_settings(updates):
    with _settings_lock:
        if _settings_cache:
            base = dict(_settings_cache)
        else:
            stored = _load_json(_settings_file, {})
            base = _deep_merge(_default_settings, stored)
        merged = _deep_merge(base, updates or {})
        _settings_cache.clear()
        _settings_cache.update(merged)
        _save_json(_settings_file, merged)
        return dict(_settings_cache)


def _setting_value(value, fallback):
    return value if str(value or "").strip() else fallback


def _apply_runtime_settings(settings):
    jira = settings.get("jira", {}) if isinstance(settings, dict) else {}
    llm = settings.get("llm", {}) if isinstance(settings, dict) else {}
    testrail = settings.get("testrail", {}) if isinstance(settings, dict) else {}

    issue_provider.update_settings(
        base_url=_setting_value(jira.get("base_url"), Config.JIRA_BASE_URL),
        username=_setting_value(jira.get("username"), Config.JIRA_USERNAME),
        api_token=_setting_value(jira.get("api_token"), Config.JIRA_API_TOKEN),
        attachment_download_enabled=bool(jira.get("attachment_download_enabled", True)),
        attachment_parse_enabled=bool(jira.get("attachment_parse_enabled", True)),
    )

    api_keys = llm.get("api_keys", {}) if isinstance(llm.get("api_keys", {}), dict) else {}
    llm_engine.llm.gemini_api_key = _setting_value(api_keys.get("gemini"), Config.GEMINI_API_KEY)
    llm_engine.llm.openai_api_key = _setting_value(api_keys.get("openai"), Config.OPENAI_API_KEY)
    llm_engine.llm.anthropic_api_key = _setting_value(api_keys.get("anthropic"), Config.ANTHROPIC_API_KEY)
    llm_engine.llm.openrouter_api_key = _setting_value(api_keys.get("openrouter"), Config.OPENROUTER_API_KEY)
    llm_engine.llm.default_model_id = _setting_value(llm.get("default_model_id"), Config.LLM_DEFAULT_MODEL_ID)
    llm_engine.llm.auto_fallback = bool(llm.get("auto_fallback", True))
    llm_engine.llm.cache_enabled = bool(llm.get("cache_enabled", True))

    testrail_publisher.update_settings(
        base_url=_setting_value(testrail.get("base_url"), Config.TESTRAIL_BASE_URL),
        username=_setting_value(testrail.get("username"), Config.TESTRAIL_USERNAME),
        api_key=_setting_value(testrail.get("api_key"), Config.TESTRAIL_API_KEY),
        password=_setting_value(testrail.get("password"), Config.TESTRAIL_PASSWORD),
        project_id=_setting_value(testrail.get("project_id"), Config.TESTRAIL_PROJECT_ID),
        suite_id=_setting_value(testrail.get("suite_id"), Config.TESTRAIL_SUITE_ID),
        section_id=_setting_value(testrail.get("section_id"), Config.TESTRAIL_SECTION_ID),
    )


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


def _behavior_setting(key, fallback=None):
    settings = _load_settings()
    behavior = settings.get("behavior", {}) if isinstance(settings, dict) else {}
    if key in behavior:
        return behavior.get(key)
    return fallback


def _extract_include_fields(payload):
    raw = payload.get("include_fields", [])
    if isinstance(raw, list):
        values = [str(item).strip().lower() for item in raw if str(item).strip()]
    elif isinstance(raw, str):
        values = [part.strip().lower() for part in raw.split(",") if part.strip()]
    else:
        values = []

    if not values:
        return sorted(list(_jira_include_fields))
    normalized = [value for value in values if value in _jira_include_fields]
    return normalized or sorted(list(_jira_include_fields))


def _apply_include_fields(issue_data, include_fields):
    selected = set(include_fields or [])
    filtered = dict(issue_data)
    if "summary" not in selected:
        filtered["summary"] = ""
    if "description" not in selected:
        filtered["description"] = ""
    if "acceptance_criteria" not in selected:
        filtered["acceptance_criteria"] = ""
    if "issue_type" not in selected:
        filtered["issue_type"] = ""
    if "custom_fields" not in selected:
        filtered["custom_fields"] = {}
    if "attachments" not in selected:
        filtered["attachments"] = []
        filtered["attachments_text"] = []
    return filtered


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
    if isinstance(exc, HTTPException):
        return jsonify({"error": exc.name, "details": exc.description}), exc.code
    if isinstance(exc, ValueError):
        message = str(exc)
        if "(404)" in message:
            return jsonify({"error": message}), 404
        if "(401)" in message:
            return jsonify({"error": message}), 401
        return jsonify({"error": message}), 400
    logger.error("Unhandled error: %s\n%s", exc, traceback.format_exc())
    return jsonify({"error": "Internal server error", "details": str(exc)}), 500


@app.get("/")
def serve_root():
    if os.path.isdir(_frontend_dist):
        return send_from_directory(_frontend_dist, "index.html")
    return jsonify({"error": "Frontend build not found"}), 404


@app.get("/health")
def health():
    return jsonify({"status": "ok"})


@app.get("/llm-models")
def llm_models():
    models = llm_engine.llm.list_models()
    return jsonify(
        {
            "default_model_id": llm_engine.llm.default_model_id,
            "models": models,
        }
    ), 200


@app.get("/settings")
def get_settings():
    return jsonify(_load_settings()), 200


@app.put("/settings")
def update_settings():
    payload = request.get_json(silent=True) or {}
    if not isinstance(payload, dict):
        return jsonify({"error": "Settings payload must be a JSON object"}), 400

    allowed_sections = set(_default_settings.keys())
    invalid_sections = [key for key in payload.keys() if key not in allowed_sections]
    if invalid_sections:
        return (
            jsonify(
                {
                    "error": (
                        "Invalid settings section(s): "
                        + ", ".join(sorted(invalid_sections))
                        + f". Allowed: {', '.join(sorted(allowed_sections))}."
                    )
                }
            ),
            400,
        )

    merged = _save_settings(payload)
    _apply_runtime_settings(merged)
    return jsonify(merged), 200


@app.get("/attachment/file")
def attachment_file():
    _apply_runtime_settings(_load_settings())
    settings = _load_settings()
    jira_settings = settings.get("jira", {}) if isinstance(settings, dict) else {}
    if not bool(jira_settings.get("attachment_download_enabled", True)):
        return jsonify({"error": "Attachment download is disabled in Settings."}), 403
    content_url = str(request.args.get("content_url", "")).strip()
    filename = str(request.args.get("filename", "attachment.bin")).strip() or "attachment.bin"
    mime_type = str(request.args.get("mime_type", "application/octet-stream")).strip()
    download = str(request.args.get("download", "0")).strip().lower() in {"1", "true", "yes"}

    if not content_url:
        return jsonify({"error": "content_url is required"}), 400

    parsed = urlparse(content_url)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        return jsonify({"error": "Invalid content_url"}), 400

    jira_host = urlparse(issue_provider.base_url).hostname or ""
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
        auth=(issue_provider.username, issue_provider.api_token),
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
    _apply_runtime_settings(_load_settings())
    payload = _extract_payload()
    issue_key = str(payload.get("issue_key", "")).strip()
    model_id = str(payload.get("model_id", "")).strip() or "stepfun/step-3.5-flash:free"
    custom_prompt = str(payload.get("custom_prompt", "")).strip()
    test_types = _extract_test_types(payload)
    if not test_types:
        test_types = _behavior_setting("default_test_types", Config.DEFAULT_TEST_TYPES)
    include_fields = _extract_include_fields(payload)
    preview_only = bool(payload.get("preview_only", False))

    if not issue_key:
        return jsonify({"error": "issue_key is required"}), 400

    parsed_test_types = []
    if not preview_only:
        valid, parsed_test_types = _validate_test_types(test_types)
        if not valid:
            return jsonify({"error": parsed_test_types}), 400

    issue_data = issue_provider.fetch_issue(issue_key=issue_key)
    if custom_prompt:
        issue_data["custom_prompt"] = custom_prompt
    issue_data_for_llm = _apply_include_fields(issue_data, include_fields)

    if not (
        issue_data_for_llm.get("summary")
        or issue_data_for_llm.get("description")
        or issue_data_for_llm.get("acceptance_criteria")
        or issue_data_for_llm.get("attachments_text")
        or custom_prompt
    ):
        return jsonify({"error": "Selected fields contain no usable content for generation."}), 400

    if preview_only:
        return jsonify(
            {
                "issue_key": issue_data.get("issue_key", issue_key),
                "source_data": issue_data,
                "test_cases": [],
            }
        ), 200

    output_language = str(_behavior_setting("output_language", "English") or "English")
    test_cases = llm_engine.generate_from_jira_issue(
        issue_data_for_llm,
        parsed_test_types,
        model_id=model_id,
        output_language=output_language,
    )
    auto_approve = bool(_behavior_setting("auto_approve_on_regenerate", False))
    for case in test_cases:
        case.setdefault("review_status", "approved" if auto_approve else "pending")
    max_cases = int(_behavior_setting("max_cases_per_issue", 0) or 0)
    if max_cases > 0:
        test_cases = test_cases[:max_cases]
    _store_latest_cases(test_cases)
    _log_activity(
        f"Generated {len(test_cases)} test case(s) from {issue_data.get('issue_key', issue_key)}.",
        category="generation",
    )
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
    _apply_runtime_settings(_load_settings())
    payload = request.get_json(silent=True) or {}
    issue_key = str(payload.get("issue_key", "")).strip()

    if not issue_key:
        return jsonify({"error": "issue_key is required"}), 400

    issue_data = issue_provider.fetch_issue(issue_key=issue_key)
    return jsonify(
        {
            "issue_key": issue_data.get("issue_key", issue_key),
            "source_data": issue_data,
            "test_cases": [],
        }
    ), 200


@app.post("/manual-generate-test")
def manual_generate():
    _apply_runtime_settings(_load_settings())
    payload = _extract_payload()
    description = str(payload.get("description", "")).strip()
    acceptance_criteria = str(payload.get("acceptance_criteria", "")).strip()
    custom_prompt = str(payload.get("custom_prompt", "")).strip()
    manual_attachments_text = str(payload.get("attachments_text", "")).strip()
    model_id = str(payload.get("model_id", "")).strip() or "stepfun/step-3.5-flash:free"
    test_types = _extract_test_types(payload)
    if not test_types:
        test_types = _behavior_setting("default_test_types", Config.DEFAULT_TEST_TYPES)
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
    output_language = str(_behavior_setting("output_language", "English") or "English")
    test_cases = llm_engine.generate_from_jira_issue(
        source,
        parsed_test_types,
        model_id=model_id,
        output_language=output_language,
    )
    auto_approve = bool(_behavior_setting("auto_approve_on_regenerate", False))
    for case in test_cases:
        case.setdefault("review_status", "approved" if auto_approve else "pending")
    max_cases = int(_behavior_setting("max_cases_per_issue", 0) or 0)
    if max_cases > 0:
        test_cases = test_cases[:max_cases]
    _store_latest_cases(test_cases)
    _log_activity(
        f"Generated {len(test_cases)} test case(s) from manual input.",
        category="generation",
    )
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
    _apply_runtime_settings(_load_settings())
    payload = _extract_payload()
    dom = str(payload.get("dom", "")).strip()
    framework = str(payload.get("framework", "")).strip()
    language = str(payload.get("language", "")).strip()
    custom_prompt = str(payload.get("custom_prompt", "")).strip()
    model_id = str(payload.get("model_id", "")).strip() or "qwen/qwen3-coder:free"
    uploaded_files = request.files.getlist("attachments") if request.files else []
    parsed_upload_chunks, _uploaded_attachment_records = _parse_manual_attachments(uploaded_files)
    uploaded_text = "\n\n".join([chunk for chunk in parsed_upload_chunks if chunk]).strip()

    if not dom and not uploaded_text:
        return jsonify({"error": "dom or at least one supported attachment is required"}), 400
    if not framework:
        return jsonify({"error": "framework is required"}), 400
    if not language:
        return jsonify({"error": "language is required"}), 400

    framework_key = _framework_aliases.get(framework.lower(), framework.lower())
    language_key = _language_aliases.get(language.lower(), language.lower())
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
        framework=framework_key.title(),
        language=("TypeScript" if language_key == "typescript" else language_key.title()),
        custom_prompt=custom_prompt,
        model_id=model_id,
    )
    _log_activity("Generated locators from provided DOM.", category="locators")
    return jsonify(result), 200


@app.get("/testcases/latest")
def latest_testcases():
    cases = _read_latest_cases(exportable_only=False)
    return jsonify({"counts": _compute_counts(cases), "test_cases": cases}), 200


@app.get("/review-queue")
def review_queue():
    status = str(request.args.get("status", "all")).strip().lower()
    cases = _read_latest_cases(exportable_only=False)
    if status in {"approved", "pending", "rejected"}:
        cases = [case for case in cases if str(case.get("review_status", "")).lower() == status]
    counts = _compute_counts(_read_latest_cases(exportable_only=False))
    counts["all"] = counts["total"]
    return jsonify({"test_cases": cases, "counts": counts}), 200


@app.post("/review-queue/update")
def review_queue_update():
    payload = request.get_json(silent=True) or {}
    test_case_id = str(payload.get("test_case_id", "")).strip()
    review_status = str(payload.get("review_status", "")).strip().lower()
    review_note = str(payload.get("note", "")).strip()
    if not test_case_id:
        return jsonify({"error": "test_case_id is required"}), 400
    if review_status not in {"approved", "pending", "rejected"}:
        return jsonify({"error": "review_status must be approved, pending, or rejected"}), 400

    updated = None
    with _latest_lock:
        for idx, case in enumerate(_latest_cases):
            if str(case.get("test_case_id", "")).strip() == test_case_id:
                updated = dict(case)
                updated["review_status"] = review_status
                updated["review_note"] = review_note
                _latest_cases[idx] = updated
                break

    if not updated:
        return jsonify({"error": "test case not found"}), 404

    if review_status == "rejected":
        _log_rejection(test_case_id, review_note)

    _persist_latest_cases()
    _log_activity(f"{test_case_id} marked {review_status}.", category="review")
    counts = _compute_counts(_read_latest_cases(exportable_only=False))
    counts["all"] = counts["total"]
    return jsonify({"updated": updated, "counts": counts}), 200


@app.post("/review-queue/approve-all")
def review_queue_approve_all():
    updated = 0
    with _latest_lock:
        for idx, case in enumerate(_latest_cases):
            status = str(case.get("review_status", "approved")).lower()
            if status == "pending":
                updated_case = dict(case)
                updated_case["review_status"] = "approved"
                _latest_cases[idx] = updated_case
                updated += 1
    if updated:
        _persist_latest_cases()
        _log_activity(f"Approved {updated} pending test case(s).", category="review")
    counts = _compute_counts(_read_latest_cases(exportable_only=False))
    counts["all"] = counts["total"]
    return jsonify({"updated": updated, "counts": counts}), 200




@app.get("/dashboard/metrics")
def dashboard_metrics():
    cases = _read_latest_cases(exportable_only=False)
    counts = _compute_counts(cases)
    approval_rate = 0
    if counts["total"]:
        approval_rate = round((counts["approved"] / counts["total"]) * 100)

    type_breakdown = {}
    priority_breakdown = {}
    for case in cases:
        ttype = str(case.get("test_type", "unspecified")).lower() or "unspecified"
        priority = str(case.get("priority", "unspecified")).lower() or "unspecified"
        type_breakdown[ttype] = type_breakdown.get(ttype, 0) + 1
        priority_breakdown[priority] = priority_breakdown.get(priority, 0) + 1

    with _activity_lock:
        recent_activity = list(_activity_log)

    return jsonify(
        {
            "counts": counts,
            "approval_rate": approval_rate,
            "type_breakdown": type_breakdown,
            "priority_breakdown": priority_breakdown,
            "recent_activity": recent_activity,
        }
    ), 200


@app.post("/export-testcases")
def export_testcases():
    settings = _load_settings()
    behavior = settings.get("behavior", {}) if isinstance(settings, dict) else {}
    if bool(behavior.get("require_review_before_export", True)):
        pending_cases = _read_cases_by_status("pending")
        if pending_cases:
            return jsonify({"error": "Pending review cases must be approved or rejected before export."}), 400
    payload = _extract_payload()
    export_format = str(payload.get("format", "")).strip().lower()

    cases = _read_latest_cases(exportable_only=True)
    if not cases:
        return jsonify({"error": "No exportable test cases found"}), 404

    return _export_response_for_format(export_format, cases)


@app.get("/export/excel")
def export_excel():
    settings = _load_settings()
    behavior = settings.get("behavior", {}) if isinstance(settings, dict) else {}
    if bool(behavior.get("require_review_before_export", True)):
        pending_cases = _read_cases_by_status("pending")
        if pending_cases:
            return jsonify({"error": "Pending review cases must be approved or rejected before export."}), 400
    cases = _read_latest_cases(exportable_only=True)
    if not cases:
        return jsonify({"error": "No exportable test cases found"}), 404
    return _export_response_for_format("excel", cases)


@app.get("/export/pdf")
def export_pdf():
    settings = _load_settings()
    behavior = settings.get("behavior", {}) if isinstance(settings, dict) else {}
    if bool(behavior.get("require_review_before_export", True)):
        pending_cases = _read_cases_by_status("pending")
        if pending_cases:
            return jsonify({"error": "Pending review cases must be approved or rejected before export."}), 400
    cases = _read_latest_cases(exportable_only=True)
    if not cases:
        return jsonify({"error": "No exportable test cases found"}), 404
    return _export_response_for_format("pdf", cases)


@app.get("/export/gherkin")
def export_gherkin():
    settings = _load_settings()
    behavior = settings.get("behavior", {}) if isinstance(settings, dict) else {}
    if bool(behavior.get("require_review_before_export", True)):
        pending_cases = _read_cases_by_status("pending")
        if pending_cases:
            return jsonify({"error": "Pending review cases must be approved or rejected before export."}), 400
    cases = _read_latest_cases(exportable_only=True)
    if not cases:
        return jsonify({"error": "No exportable test cases found"}), 404
    return _export_response_for_format("gherkin", cases)


@app.get("/export/plain")
def export_plain():
    settings = _load_settings()
    behavior = settings.get("behavior", {}) if isinstance(settings, dict) else {}
    if bool(behavior.get("require_review_before_export", True)):
        pending_cases = _read_cases_by_status("pending")
        if pending_cases:
            return jsonify({"error": "Pending review cases must be approved or rejected before export."}), 400
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
    _apply_runtime_settings(_load_settings())
    settings = _load_settings()
    behavior = settings.get("behavior", {}) if isinstance(settings, dict) else {}
    testrail_settings = settings.get("testrail", {}) if isinstance(settings, dict) else {}
    pending_cases = _read_cases_by_status("pending")
    review_gate = bool(behavior.get("require_review_before_export", True))
    warning_message = ""
    if review_gate and pending_cases:
        warning_message = (
            "Pending review cases exist. Please review them in Review Queue. "
            "Only approved cases will be pushed."
        )
    cases = _read_latest_cases(exportable_only=True)
    if not cases:
        return jsonify({"error": "No exportable test cases found"}), 404

    if bool(testrail_settings.get("push_only_approved", True)):
        cases = [case for case in cases if str(case.get("review_status", "")).lower() == "approved"]
        if not cases:
            return jsonify({"error": "No approved test cases available to push."}), 404

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

    ready = testrail_publisher.ready_state(section_id or Config.TESTRAIL_SECTION_ID)
    if not all(ready.values()):
        return (
            jsonify(
                {
                    "error": (
                        "TestRail configuration is incomplete. "
                        "Provide base_url, username, API key/password, and section_id."
                    ),
                    "missing": [key for key, value in ready.items() if not value],
                }
            ),
            400,
        )

    result = testrail_publisher.push_test_cases(
        test_cases=cases,
        project_id=project_id,
        suite_id=suite_id,
        section_id=section_id,
        repository_mode=repository_mode,
    )
    if warning_message:
        result["warning"] = warning_message
        result["pending_review_count"] = len(pending_cases)
    return jsonify(result), 200


@app.get("/<path:asset_path>")
def serve_frontend_assets(asset_path: str):
    if not os.path.isdir(_frontend_dist):
        return jsonify({"error": "Not found"}), 404

    requested = os.path.join(_frontend_dist, asset_path)
    if os.path.isfile(requested):
        return send_from_directory(_frontend_dist, asset_path)
    return send_from_directory(_frontend_dist, "index.html")


_load_persisted_state()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=Config.FLASK_DEBUG)
