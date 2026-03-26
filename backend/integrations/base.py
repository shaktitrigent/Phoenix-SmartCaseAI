from typing import Any, Dict, List, Optional


class IssueProvider:
    name = "base"

    def update_settings(self, **_kwargs) -> None:
        return None

    def fetch_issue(self, issue_key: str) -> Dict[str, Any]:
        raise NotImplementedError


class TestCasePublisher:
    name = "base"

    def update_settings(self, **_kwargs) -> None:
        return None

    def ready_state(self, section_id: str) -> Dict[str, bool]:
        return {}

    def push_test_cases(
        self,
        test_cases: List[Dict],
        project_id: Optional[str] = None,
        suite_id: Optional[str] = None,
        section_id: Optional[str] = None,
        repository_mode: str = "single_repository",
    ) -> Dict:
        raise NotImplementedError
