from __future__ import annotations

import re
from typing import Dict, Iterable, List

_PLACEHOLDER_PATTERNS = [
    "tbd",
    "todo",
    "lorem",
    "dummy",
    "placeholder",
    "not provided",
    "no steps generated",
    "n/a",
]

_PLACEHOLDER_RE = re.compile("|".join(re.escape(p) for p in _PLACEHOLDER_PATTERNS), re.IGNORECASE)
_GENERIC_LOCATOR_RE = re.compile(r"^[a-z]+$", re.IGNORECASE)


def filter_test_cases(cases: Iterable[Dict]) -> List[Dict]:
    filtered: List[Dict] = []
    for case in cases or []:
        if not isinstance(case, dict):
            continue
        title = str(case.get("title", "")).strip()
        preconditions = str(case.get("preconditions", "")).strip()
        expected = str(case.get("expected_result", "")).strip()
        steps = case.get("steps", [])
        steps_list = _normalize_steps(steps)

        if not _is_valid_text(title, min_len=6):
            continue
        if not _is_valid_text(preconditions, min_len=4):
            continue
        if not _is_valid_text(expected, min_len=4):
            continue
        if len(steps_list) < 2:
            continue
        if any(not _is_valid_text(step, min_len=4) for step in steps_list):
            continue

        normalized = dict(case)
        normalized["steps"] = steps_list
        filtered.append(normalized)
    return filtered


def filter_locators(locators: Iterable[Dict]) -> List[Dict]:
    filtered: List[Dict] = []
    seen = set()
    for locator in locators or []:
        if not isinstance(locator, dict):
            continue
        primary = str(locator.get("primary_locator", "")).strip()
        strategy = str(locator.get("strategy", "")).strip()
        element = str(locator.get("element", "")).strip()
        alternate = str(locator.get("alternate_locator", "")).strip()

        if not _is_valid_text(primary, min_len=3):
            continue
        if _is_generic_locator(primary):
            continue
        if not _is_valid_text(strategy, min_len=3):
            continue

        key = (primary, alternate)
        if key in seen:
            continue
        seen.add(key)
        filtered.append(
            {
                "element": element,
                "primary_locator": primary,
                "alternate_locator": alternate,
                "strategy": strategy,
            }
        )
    return filtered


def _normalize_steps(steps) -> List[str]:
    if isinstance(steps, list):
        return [str(step).strip() for step in steps if str(step).strip()]
    if isinstance(steps, str):
        return [part.strip() for part in steps.split("\n") if part.strip()]
    return []


def _is_valid_text(value: str, min_len: int = 1) -> bool:
    if not value or len(value) < min_len:
        return False
    if _PLACEHOLDER_RE.search(value):
        return False
    return True


def _is_generic_locator(value: str) -> bool:
    if _GENERIC_LOCATOR_RE.match(value):
        return True
    if value in {"*", "button", "input", "a", "div", "span", "select", "textarea"}:
        return True
    return False
