from typing import Any, Dict

from integrations.base import IssueProvider
from services.jirafetch import JiraFetchService


class JiraIssueProvider(IssueProvider):
    name = "jira"

    def __init__(self) -> None:
        self._service = JiraFetchService()

    def update_settings(
        self,
        base_url: str,
        username: str,
        api_token: str,
        attachment_download_enabled: bool = True,
        attachment_parse_enabled: bool = True,
    ) -> None:
        self._service.update_settings(
            base_url=base_url,
            username=username,
            api_token=api_token,
            attachment_download_enabled=attachment_download_enabled,
            attachment_parse_enabled=attachment_parse_enabled,
        )

    def fetch_issue(self, issue_key: str) -> Dict[str, Any]:
        return self._service.fetch_issue_details(issue_key)

    # Backward-compatible alias for legacy callers.
    def fetch_issue_details(self, issue_key: str) -> Dict[str, Any]:
        return self.fetch_issue(issue_key)

    @property
    def base_url(self) -> str:
        return self._service.base_url

    @property
    def username(self) -> str:
        return self._service.username

    @property
    def api_token(self) -> str:
        return self._service.api_token
