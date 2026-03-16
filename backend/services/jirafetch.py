import os
import re
import tempfile
import base64
from typing import Any, Dict, List

import requests

from config import Config
from services.document_parser import DocumentParser


class JiraFetchService:
    MAX_INLINE_PREVIEW_BYTES = 1_500_000

    def __init__(self):
        self.base_url = Config.JIRA_BASE_URL
        self.username = Config.JIRA_USERNAME
        self.api_token = Config.JIRA_API_TOKEN
        self.attachment_download_enabled = True
        self.attachment_parse_enabled = True
        self.parser = DocumentParser()

    def update_settings(
        self,
        base_url: str,
        username: str,
        api_token: str,
        attachment_download_enabled: bool = True,
        attachment_parse_enabled: bool = True,
    ) -> None:
        self.base_url = (base_url or "").rstrip("/")
        self.username = str(username or "").strip()
        self.api_token = str(api_token or "").strip()
        self.attachment_download_enabled = bool(attachment_download_enabled)
        self.attachment_parse_enabled = bool(attachment_parse_enabled)

    def fetch_issue_details(self, issue_key: str) -> Dict[str, Any]:
        issue_keys = self._parse_issue_keys(issue_key)
        self._validate_credentials()

        issues_data = [self._fetch_single_issue_details(key) for key in issue_keys]

        if len(issues_data) == 1:
            return issues_data[0]

        combined_issue_key = "/".join([item["issue_key"] for item in issues_data])
        combined_description = "\n\n".join(
            [f"[{item['issue_key']}] {item.get('description', '')}".strip() for item in issues_data]
        ).strip()
        combined_acceptance = "\n\n".join(
            [f"[{item['issue_key']}] {item.get('acceptance_criteria', '')}".strip() for item in issues_data]
        ).strip()
        combined_attachments_text = []
        combined_attachments = []
        combined_custom_fields = {}
        issue_types = []
        for item in issues_data:
            combined_attachments.extend(item.get("attachments", []))
            combined_attachments_text.extend(item.get("attachments_text", []))
            combined_custom_fields.update(item.get("custom_fields", {}))
            if item.get("issue_type"):
                issue_types.append(item.get("issue_type"))

        combined_issue_types = sorted(list(set(issue_types)))

        return {
            "issue_key": combined_issue_key,
            "summary": f"Combined Jira issues: {combined_issue_key}",
            "description": combined_description,
            "acceptance_criteria": combined_acceptance,
            "issue_type": ", ".join(combined_issue_types),
            "custom_fields": combined_custom_fields,
            "attachments": combined_attachments,
            "attachments_text": [txt for txt in combined_attachments_text if txt],
        }

    @staticmethod
    def _parse_issue_keys(issue_key: str) -> List[str]:
        raw = (issue_key or "").strip().upper()
        if not raw:
            raise ValueError("Invalid issue_key format. Expected format like PROJ-123.")

        # Supports:
        # - PROJ-123
        # - PROJ-123/PROJ-456
        # - PROJ-123/456 (same project shorthand)
        parts = [p.strip().upper() for p in raw.split("/") if p.strip()]
        if not parts:
            raise ValueError("Invalid issue_key format. Expected format like PROJ-123.")

        match_first = re.match(r"^([A-Z][A-Z0-9]+)-(\d+)$", parts[0])
        if not match_first:
            raise ValueError("Invalid issue_key format. Expected format like PROJ-123.")

        project = match_first.group(1)
        normalized = [f"{project}-{match_first.group(2)}"]
        for part in parts[1:]:
            full_match = re.match(r"^([A-Z][A-Z0-9]+)-(\d+)$", part)
            if full_match:
                normalized.append(f"{full_match.group(1)}-{full_match.group(2)}")
                continue
            short_match = re.match(r"^(\d+)$", part)
            if short_match:
                normalized.append(f"{project}-{short_match.group(1)}")
                continue
            raise ValueError("Invalid issue_key format. Expected format like PROJ-123.")
        return normalized

    def _validate_credentials(self):
        if not self.base_url or not self.username or not self.api_token:
            raise ValueError("Missing Jira credentials in environment variables.")

    def _fetch_single_issue_details(self, issue_key: str) -> Dict[str, Any]:
        url = f"{self.base_url}/rest/api/3/issue/{issue_key}"
        params = {"expand": "renderedFields"}
        response = requests.get(url, params=params, auth=(self.username, self.api_token), timeout=30)

        if response.status_code == 401:
            raise ValueError("Jira authentication failed (401). Check JIRA_USERNAME and JIRA_API_TOKEN.")
        if response.status_code == 404:
            raise ValueError(f"Jira issue not found: {issue_key} (404).")
        if response.status_code >= 400:
            raise ValueError(f"Jira API error {response.status_code}: {response.text}")

        issue = response.json()
        fields = issue.get("fields", {})

        summary = fields.get("summary", "") or ""
        description = self._extract_description(fields.get("description"))
        acceptance_criteria = self._extract_acceptance_criteria(fields)
        issue_type = self._extract_issue_type(fields)
        custom_fields = self._extract_custom_fields(fields)

        raw_attachments = fields.get("attachment", []) or []
        attachments = self._download_and_parse_attachments(raw_attachments, issue_key)
        attachment_texts = [
            item.get("parsed_text", "")
            for item in attachments
            if item.get("parse_status") == "parsed" and item.get("parsed_text")
        ]

        return {
            "issue_key": issue_key,
            "summary": summary.strip(),
            "description": description.strip(),
            "acceptance_criteria": acceptance_criteria.strip(),
            "issue_type": issue_type,
            "custom_fields": custom_fields,
            "attachments": attachments,
            "attachments_text": [txt for txt in attachment_texts if txt],
        }

    @staticmethod
    def _extract_description(description_node: Any) -> str:
        if not description_node:
            return ""
        if isinstance(description_node, str):
            return description_node
        if not isinstance(description_node, dict):
            return str(description_node)
        lines = []

        def walk(node):
            if isinstance(node, dict):
                if node.get("type") == "text" and node.get("text"):
                    lines.append(str(node["text"]))
                for value in node.values():
                    walk(value)
            elif isinstance(node, list):
                for item in node:
                    walk(item)

        walk(description_node)
        return " ".join(lines)

    @staticmethod
    def _extract_acceptance_criteria(fields: Dict[str, Any]) -> str:
        candidates = []
        for key, value in fields.items():
            key_lower = str(key).lower()
            if "acceptance" in key_lower and value:
                candidates.append(JiraFetchService._coerce_to_text(value))

        if candidates:
            return "\n".join(candidates)
        return ""

    @staticmethod
    def _extract_issue_type(fields: Dict[str, Any]) -> str:
        issue_type = fields.get("issuetype")
        if isinstance(issue_type, dict):
            return str(issue_type.get("name", "")).strip()
        if issue_type:
            return str(issue_type).strip()
        return ""

    @staticmethod
    def _extract_custom_fields(fields: Dict[str, Any]) -> Dict[str, Any]:
        custom = {}
        for key, value in fields.items():
            if str(key).startswith("customfield_"):
                if isinstance(value, (str, int, float, bool)):
                    custom[key] = value
                elif isinstance(value, dict):
                    custom[key] = {
                        k: v
                        for k, v in value.items()
                        if isinstance(v, (str, int, float, bool))
                    }
                elif isinstance(value, list):
                    simple_items = [x for x in value if isinstance(x, (str, int, float, bool))]
                    if simple_items:
                        custom[key] = simple_items
        return custom

    @staticmethod
    def _coerce_to_text(value: Any) -> str:
        if value is None:
            return ""
        if isinstance(value, str):
            return value
        if isinstance(value, (int, float, bool)):
            return str(value)
        if isinstance(value, dict):
            if value.get("type") == "text" and value.get("text"):
                return str(value.get("text"))
            parts = []
            for inner in value.values():
                txt = JiraFetchService._coerce_to_text(inner)
                if txt:
                    parts.append(txt)
            return " ".join(parts).strip()
        if isinstance(value, list):
            parts = [JiraFetchService._coerce_to_text(item) for item in value]
            return "\n".join([p for p in parts if p]).strip()
        return str(value)

    def _download_and_parse_attachments(
        self, attachments: List[Dict[str, Any]], issue_key: str
    ) -> List[Dict[str, Any]]:
        if not attachments:
            return []

        parsed_attachments = []
        for item in attachments:
            content_url = item.get("content")
            filename = item.get("filename", "attachment")
            attachment_record = {
                "source_issue_key": issue_key,
                "filename": filename,
                "mime_type": item.get("mimeType", ""),
                "size_bytes": item.get("size", 0),
                "content_url": content_url or "",
                "download_status": "skipped",
                "parse_status": "not_parsed",
                "parsed_text": "",
                "preview_data_url": "",
            }
            if not content_url:
                parsed_attachments.append(attachment_record)
                continue
            if not self.attachment_download_enabled:
                attachment_record["download_status"] = "download_disabled"
                parsed_attachments.append(attachment_record)
                continue
            try:
                response = requests.get(
                    content_url,
                    auth=(self.username, self.api_token),
                    timeout=30,
                )
                if response.status_code >= 400:
                    attachment_record["download_status"] = f"http_{response.status_code}"
                    parsed_attachments.append(attachment_record)
                    continue
                with tempfile.NamedTemporaryFile(
                    mode="wb",
                    delete=False,
                    suffix=os.path.splitext(filename)[1] or ".tmp",
                ) as tmp:
                    tmp.write(response.content)
                    attachment_record["download_status"] = "downloaded"

                    mime_type = str(attachment_record.get("mime_type", "")).lower()
                    if (
                        mime_type.startswith("image/")
                        and len(response.content) <= self.MAX_INLINE_PREVIEW_BYTES
                    ):
                        encoded = base64.b64encode(response.content).decode("ascii")
                        attachment_record["preview_data_url"] = f"data:{mime_type};base64,{encoded}"

                    if self.attachment_parse_enabled:
                        parsed_text = self.parser.parse_file(tmp.name)
                        if parsed_text:
                            attachment_record["parse_status"] = "parsed"
                            attachment_record["parsed_text"] = parsed_text
                        else:
                            attachment_record["parse_status"] = "empty_or_unsupported"
                    else:
                        attachment_record["parse_status"] = "parse_disabled"
                    parsed_attachments.append(attachment_record)
            except Exception:
                attachment_record["download_status"] = "download_failed"
                attachment_record["parse_status"] = "parse_failed"
                parsed_attachments.append(attachment_record)
                continue

        return parsed_attachments
