from typing import Dict

from integrations.base import IssueProvider, TestCasePublisher
from integrations.jira.provider import JiraIssueProvider
from integrations.testrail.publisher import TestRailPublisher


_ISSUE_PROVIDER_FACTORIES = {
    "jira": JiraIssueProvider,
}
_PUBLISHER_FACTORIES = {
    "testrail": TestRailPublisher,
}

_issue_provider_cache: Dict[str, IssueProvider] = {}
_publisher_cache: Dict[str, TestCasePublisher] = {}


def get_issue_provider(name: str = "jira") -> IssueProvider:
    key = (name or "jira").strip().lower()
    if key not in _issue_provider_cache:
        provider_factory = _ISSUE_PROVIDER_FACTORIES.get(key)
        if not provider_factory:
            raise ValueError(f"Unknown issue provider: {name}")
        _issue_provider_cache[key] = provider_factory()
    return _issue_provider_cache[key]


def get_publisher(name: str = "testrail") -> TestCasePublisher:
    key = (name or "testrail").strip().lower()
    if key not in _publisher_cache:
        publisher_factory = _PUBLISHER_FACTORIES.get(key)
        if not publisher_factory:
            raise ValueError(f"Unknown publisher: {name}")
        _publisher_cache[key] = publisher_factory()
    return _publisher_cache[key]
