from typing import Any, Dict, List, Optional

import requests


class TestRailService:
    def __init__(
        self,
        base_url: str,
        username: str,
        api_key: str,
        password: str = "",
        default_project_id: str = "",
        default_suite_id: str = "",
        default_section_id: str = "",
    ):
        self.base_url = (base_url or "").rstrip("/")
        self.username = (username or "").strip()
        self.api_key = (api_key or "").strip()
        self.password = (password or "").strip()
        self.default_project_id = str(default_project_id or "")
        self.default_suite_id = str(default_suite_id or "")
        self.default_section_id = str(default_section_id or "")

    def push_test_cases(
        self,
        test_cases: List[Dict],
        project_id: Optional[str] = None,
        suite_id: Optional[str] = None,
        section_id: Optional[str] = None,
        repository_mode: str = "single_repository",
    ) -> Dict:
        resolved_project = str(project_id or self.default_project_id or "").strip()
        resolved_suite = str(suite_id or self.default_suite_id or "").strip()
        resolved_section = str(section_id or self.default_section_id or "").strip()
        resolved_repository_mode = str(repository_mode or "single_repository").strip() or "single_repository"

        if not test_cases:
            raise ValueError("No test cases found to push.")

        # Keep implementation usable before credentials are provided.
        if not self._is_ready_for_live_push(resolved_section):
            return self._mock_push(
                test_cases,
                resolved_project,
                resolved_suite,
                resolved_section,
                resolved_repository_mode,
            )

        if not resolved_suite and resolved_project:
            resolved_suite = self._resolve_suite_id(resolved_project)

        created = []
        for idx, case in enumerate(test_cases, start=1):
            payload = self._map_case_payload(case)
            response = self._post(f"add_case/{resolved_section}", payload)
            case_id = response.get("id")
            created.append(
                {
                    "index": idx,
                    "id": case_id,
                    "title": response.get("title", case.get("title", "")),
                    "status": "created",
                    "case_url": self._case_url(case_id),
                }
            )

        return {
            "mode": "live",
            "repository_mode": resolved_repository_mode,
            "project_id": resolved_project,
            "suite_id": resolved_suite,
            "section_id": resolved_section,
            "section_url": self._section_url(resolved_project, resolved_suite, resolved_section),
            "created": len(created),
            "results": created,
        }

    def _is_ready_for_live_push(self, section_id: str) -> bool:
        return bool(self.base_url and self.username and self._auth_candidates() and section_id)

    def ready_state(self, section_id: str) -> Dict[str, bool]:
        return {
            "base_url": bool(self.base_url),
            "username": bool(self.username),
            "auth": bool(self._auth_candidates()),
            "section_id": bool(section_id),
        }

    def _auth_candidates(self) -> List[tuple]:
        candidates: List[tuple] = []
        if self.api_key:
            candidates.append((self.username, self.api_key))
        if self.password and self.password != self.api_key:
            candidates.append((self.username, self.password))
        return candidates

    def _post(self, endpoint: str, payload: Dict) -> Dict:
        url = f"{self.base_url}/index.php?/api/v2/{endpoint}"
        last_response = None
        for auth in self._auth_candidates():
            response = requests.post(
                url,
                auth=auth,
                json=payload,
                timeout=45,
            )
            last_response = response
            if response.status_code == 401:
                continue
            if response.status_code >= 400:
                raise ValueError(f"TestRail API error {response.status_code}: {response.text}")
            return response.json()

        if last_response is None:
            raise ValueError("TestRail API error: missing authentication credentials.")
        raise ValueError(f"TestRail API error {last_response.status_code}: {last_response.text}")

    def _get(self, endpoint: str) -> Any:
        url = f"{self.base_url}/index.php?/api/v2/{endpoint}"
        last_response = None
        for auth in self._auth_candidates():
            response = requests.get(
                url,
                auth=auth,
                timeout=45,
            )
            last_response = response
            if response.status_code == 401:
                continue
            if response.status_code >= 400:
                raise ValueError(f"TestRail API error {response.status_code}: {response.text}")
            return response.json()

        if last_response is None:
            raise ValueError("TestRail API error: missing authentication credentials.")
        raise ValueError(f"TestRail API error {last_response.status_code}: {last_response.text}")

    def _resolve_suite_id(self, project_id: str) -> str:
        try:
            suites = self._get(f"get_suites/{project_id}")
            if isinstance(suites, dict):
                suites = suites.get("suites") or suites.get("results") or []
            if isinstance(suites, list) and suites and isinstance(suites[0], dict):
                suite_id = suites[0].get("id")
                return str(suite_id).strip() if suite_id is not None else ""
        except ValueError:
            return ""
        return ""

    def _case_url(self, case_id: Any) -> str:
        case_id_str = str(case_id).strip() if case_id is not None else ""
        if not case_id_str or not self.base_url:
            return ""
        return f"{self.base_url}/index.php?/cases/view/{case_id_str}"

    def _section_url(self, project_id: str, suite_id: str, section_id: str) -> str:
        project_id = str(project_id or "").strip()
        suite_id = str(suite_id or "").strip()
        section_id = str(section_id or "").strip()
        if not self.base_url or not project_id or not section_id:
            return ""
        if suite_id:
            return (
                f"{self.base_url}/index.php?/cases/view/{project_id}"
                f"&group_by=cases:section_id&group_id={section_id}&suite_id={suite_id}"
            )
        return f"{self.base_url}/index.php?/cases/view/{project_id}&group_id={section_id}"

    @staticmethod
    def _map_case_payload(case: Dict) -> Dict:
        steps = case.get("steps", []) or []
        steps_text = "\n".join([f"{idx + 1}. {str(step).strip()}" for idx, step in enumerate(steps)]) or "-"
        expected = str(case.get("expected_result", "")).strip() or "Expected behavior is observed."
        preconditions = str(case.get("preconditions", "")).strip()
        test_type = str(case.get("test_type", "")).strip()
        priority = str(case.get("priority", "")).strip()

        title = str(case.get("title", "")).strip() or "Generated Test Case"
        if test_type:
            title = f"[{test_type}] {title}"

        refs = str(case.get("test_case_id", "")).strip()

        return {
            "title": title,
            "refs": refs,
            "custom_preconds": preconditions,
            "custom_steps": f"{steps_text}\n\nExpected:\n{expected}",
            "custom_expected": expected,
            "custom_priority": priority,
        }

    @staticmethod
    def _mock_push(
        test_cases: List[Dict], project_id: str, suite_id: str, section_id: str, repository_mode: str
    ) -> Dict:
        results = []
        for idx, case in enumerate(test_cases, start=1):
            results.append(
                {
                    "index": idx,
                    "id": f"MOCK-{idx:03d}",
                    "title": case.get("title", ""),
                    "status": "created_mock",
                    "case_url": "",
                }
            )

        return {
            "mode": "mock",
            "repository_mode": repository_mode,
            "message": (
                "TestRail credentials or section_id are missing. "
                "Returning mock push result until live configuration is provided."
            ),
            "project_id": project_id,
            "suite_id": suite_id,
            "section_id": section_id,
            "section_url": "",
            "created": len(results),
            "results": results,
        }
