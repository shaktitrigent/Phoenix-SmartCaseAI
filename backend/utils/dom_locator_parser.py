from __future__ import annotations

from dataclasses import dataclass, field
from html.parser import HTMLParser
import re
from typing import Dict, Iterable, List, Optional, Tuple


_TESTID_KEYS = ("data-testid", "data-test-id", "data-qa", "data-cy")
_WHITESPACE_RE = re.compile(r"\s+")
_DYNAMIC_TOKEN_RE = re.compile(r"\d{6,}")


@dataclass
class _Node:
    tag: str
    attrs: Dict[str, str]
    parent: Optional["_Node"] = None
    text: str = ""
    children: List["_Node"] = field(default_factory=list)

    def add_text(self, value: str) -> None:
        if value:
            self.text += value


class _DOMParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self._stack: List[_Node] = []
        self.nodes: List[_Node] = []

    def handle_starttag(self, tag: str, attrs: List[Tuple[str, Optional[str]]]) -> None:
        attr_map = {k.lower(): (v or "") for k, v in attrs}
        node = _Node(tag=tag.lower(), attrs=attr_map, parent=self._stack[-1] if self._stack else None)
        if node.parent:
            node.parent.children.append(node)
        self._stack.append(node)
        self.nodes.append(node)

    def handle_endtag(self, tag: str) -> None:
        if self._stack:
            self._stack.pop()

    def handle_data(self, data: str) -> None:
        if self._stack:
            self._stack[-1].add_text(data)


def extract_locators(dom: str) -> List[Dict]:
    parser = _DOMParser()
    parser.feed(dom or "")
    nodes = parser.nodes
    if not nodes:
        return []

    label_map, label_ancestor_text = _extract_label_text(nodes)
    locators: List[Dict] = []
    seen = set()

    for node in nodes:
        if not _is_candidate(node):
            continue
        candidates = _build_candidates(node, label_map, label_ancestor_text)
        if not candidates:
            continue

        element_name = _element_name(node, label_map, label_ancestor_text)
        primary = candidates[0]
        alternate = candidates[1] if len(candidates) > 1 else None

        key = (primary[0], alternate[0] if alternate else "")
        if key in seen:
            continue
        seen.add(key)

        locators.append(
            {
                "element": element_name,
                "primary_locator": primary[0],
                "alternate_locator": alternate[0] if alternate else "",
                "strategy": primary[1],
            }
        )

    return locators


def _extract_label_text(nodes: Iterable[_Node]) -> Tuple[Dict[str, str], Dict[int, str]]:
    label_map: Dict[str, str] = {}
    label_ancestor_text: Dict[int, str] = {}

    for node in nodes:
        if node.tag != "label":
            continue
        label_text = _normalize_text(_collect_text(node))
        if not label_text:
            continue
        label_for = node.attrs.get("for", "").strip()
        if label_for:
            label_map[label_for] = label_text
            continue
        for child in node.children:
            if child.tag in {"input", "select", "textarea"}:
                label_ancestor_text[id(child)] = label_text
    return label_map, label_ancestor_text


def _collect_text(node: _Node) -> str:
    parts = [node.text]
    for child in node.children:
        parts.append(_collect_text(child))
    return "".join(parts)


def _normalize_text(value: str) -> str:
    return _WHITESPACE_RE.sub(" ", str(value or "").strip())


def _is_stable_attr(value: str) -> bool:
    value = str(value or "").strip()
    if not value:
        return False
    if len(value) > 80:
        return False
    if _DYNAMIC_TOKEN_RE.search(value):
        return False
    return True


def _is_candidate(node: _Node) -> bool:
    if node.tag in {"button", "a", "input", "select", "textarea"}:
        return True
    for key in _TESTID_KEYS + ("id", "name", "aria-label", "role"):
        if _is_stable_attr(node.attrs.get(key, "")):
            return True
    return False


def _element_name(node: _Node, label_map: Dict[str, str], label_ancestor_text: Dict[int, str]) -> str:
    attrs = node.attrs
    label_text = _label_text(node, label_map, label_ancestor_text)
    for value in (
        attrs.get("aria-label", ""),
        label_text,
        _normalize_text(_collect_text(node)),
        attrs.get("placeholder", ""),
        attrs.get("title", ""),
        attrs.get("alt", ""),
        attrs.get("name", ""),
        attrs.get("id", ""),
    ):
        if _is_stable_attr(value):
            return value.strip()
    return f"{node.tag} element"


def _build_candidates(
    node: _Node, label_map: Dict[str, str], label_ancestor_text: Dict[int, str]
) -> List[Tuple[str, str]]:
    attrs = node.attrs
    candidates: List[Tuple[str, str]] = []

    for key in _TESTID_KEYS:
        value = attrs.get(key, "")
        if _is_stable_attr(value):
            candidates.append((_css_attr_selector(key, value), "CSS Selector"))
            break

    value = attrs.get("id", "")
    if _is_stable_attr(value):
        candidates.append((f"#{value}", "ID"))

    value = attrs.get("aria-label", "")
    if _is_stable_attr(value):
        candidates.append((_css_attr_selector("aria-label", value), "CSS Selector"))

    value = attrs.get("name", "")
    if _is_stable_attr(value):
        candidates.append((_css_attr_selector("name", value), "Name"))

    label_text = _label_text(node, label_map, label_ancestor_text)
    if label_text:
        candidates.append((f'label="{_escape_quotes(label_text)}"', "Text"))

    role_value = attrs.get("role", "") or _infer_role(node)
    name_value = _accessible_name(node, label_text)
    if role_value and name_value:
        candidates.append(
            (f'role={role_value} name="{_escape_quotes(name_value)}"', "Role")
        )

    if node.tag in {"button", "a"}:
        text_value = _normalize_text(_collect_text(node))
        if _is_stable_attr(text_value):
            candidates.append((f'text="{_escape_quotes(text_value)}"', "Text"))

    return _dedupe_candidates(candidates)


def _label_text(node: _Node, label_map: Dict[str, str], label_ancestor_text: Dict[int, str]) -> str:
    node_id = node.attrs.get("id", "").strip()
    if node_id and node_id in label_map:
        return label_map[node_id]
    return label_ancestor_text.get(id(node), "")


def _accessible_name(node: _Node, label_text: str) -> str:
    attrs = node.attrs
    for value in (
        attrs.get("aria-label", ""),
        label_text,
        _normalize_text(_collect_text(node)),
        attrs.get("title", ""),
        attrs.get("alt", ""),
        attrs.get("placeholder", ""),
        attrs.get("value", ""),
    ):
        if _is_stable_attr(value):
            return value.strip()
    return ""


def _infer_role(node: _Node) -> str:
    if node.tag == "button":
        return "button"
    if node.tag == "a" and node.attrs.get("href"):
        return "link"
    if node.tag == "input":
        input_type = node.attrs.get("type", "").lower()
        if input_type in {"submit", "button", "reset"}:
            return "button"
        if input_type in {"checkbox"}:
            return "checkbox"
        if input_type in {"radio"}:
            return "radio"
        return "textbox"
    if node.tag == "select":
        return "combobox"
    if node.tag == "textarea":
        return "textbox"
    return ""


def _css_attr_selector(name: str, value: str) -> str:
    value = str(value or "")
    if "'" in value and '"' in value:
        value = value.replace('"', '\\"')
        return f'[{name}="{value}"]'
    if "'" in value:
        return f'[{name}="{value}"]'
    return f"[{name}='{value}']"


def _escape_quotes(value: str) -> str:
    return str(value or "").replace('"', '\\"')


def _dedupe_candidates(items: List[Tuple[str, str]]) -> List[Tuple[str, str]]:
    seen = set()
    result = []
    for locator, strategy in items:
        key = (locator, strategy)
        if not locator or key in seen:
            continue
        seen.add(key)
        result.append((locator, strategy))
    return result
