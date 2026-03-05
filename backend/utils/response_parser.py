import json
import re
from typing import Dict, List


def parse_test_case_response(raw_text: str) -> List[Dict]:
    if not raw_text:
        return []

    payload = _safe_json_load(raw_text)
    if payload is None:
        json_fragment = _extract_json_fragment(raw_text)
        payload = _safe_json_load(json_fragment) if json_fragment else None
    if payload is None or not isinstance(payload, dict):
        return []

    cases = payload.get("test_cases", [])
    if not isinstance(cases, list):
        return []
    return [_normalize_case(item) for item in cases if isinstance(item, dict)]


def parse_locator_response(raw_text: str) -> Dict:
    fallback = {"locators": [], "test_template": ""}
    if not raw_text:
        return fallback

    payload = _safe_json_load(raw_text)
    if payload is None:
        json_fragment = _extract_json_fragment(raw_text)
        payload = _safe_json_load(json_fragment) if json_fragment else None
    if payload is None or not isinstance(payload, dict):
        return fallback

    locators = payload.get("locators", [])
    if not isinstance(locators, list):
        locators = []

    normalized_locators = []
    for item in locators:
        if not isinstance(item, dict):
            continue
        normalized_locators.append(
            {
                "element": str(item.get("element", "")).strip(),
                "primary_locator": str(item.get("primary_locator", "")).strip(),
                "alternate_locator": str(item.get("alternate_locator", "")).strip(),
                "strategy": str(item.get("strategy", "")).strip(),
            }
        )

    return {
        "locators": normalized_locators,
        "test_template": str(payload.get("test_template", "")).strip(),
    }


def _safe_json_load(value: str):
    try:
        return json.loads(value)
    except Exception:
        return None


def _extract_json_fragment(text: str):
    match = re.search(r"\{.*\}", text, re.DOTALL)
    return match.group(0) if match else None


def _normalize_case(case: Dict) -> Dict:
    steps = case.get("steps", [])
    if isinstance(steps, str):
        steps = [s.strip() for s in re.split(r"[\n;]+", steps) if s.strip()]
    if not isinstance(steps, list):
        steps = []

    return {
        "title": str(case.get("title", "")).strip(),
        "preconditions": str(case.get("preconditions", "")).strip(),
        "steps": [str(s).strip() for s in steps if str(s).strip()],
        "expected_result": str(case.get("expected_result", "")).strip(),
        "test_type": str(case.get("test_type", "functional")).strip().lower(),
        "priority": str(case.get("priority", "Medium")).strip().title(),
    }
