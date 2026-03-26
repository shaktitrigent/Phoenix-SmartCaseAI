from typing import Dict, List, Optional

from config import Config
from integrations.base import TestCasePublisher
from services.testrail import TestRailService


class TestRailPublisher(TestCasePublisher):
    name = "testrail"

    def __init__(self) -> None:
        self._service = TestRailService(
            base_url=Config.TESTRAIL_BASE_URL,
            username=Config.TESTRAIL_USERNAME,
            api_key=Config.TESTRAIL_API_KEY,
            password=Config.TESTRAIL_PASSWORD,
            default_project_id=Config.TESTRAIL_PROJECT_ID,
            default_suite_id=Config.TESTRAIL_SUITE_ID,
            default_section_id=Config.TESTRAIL_SECTION_ID,
        )

    def update_settings(
        self,
        base_url: str,
        username: str,
        api_key: str,
        password: str,
        project_id: str,
        suite_id: str,
        section_id: str,
    ) -> None:
        self._service.base_url = (base_url or "").rstrip("/")
        self._service.username = str(username or "").strip()
        self._service.api_key = str(api_key or "").strip()
        self._service.password = str(password or "").strip()
        self._service.default_project_id = str(project_id or "")
        self._service.default_suite_id = str(suite_id or "")
        self._service.default_section_id = str(section_id or "")

    def ready_state(self, section_id: str) -> Dict[str, bool]:
        return self._service.ready_state(section_id)

    def push_test_cases(
        self,
        test_cases: List[Dict],
        project_id: Optional[str] = None,
        suite_id: Optional[str] = None,
        section_id: Optional[str] = None,
        repository_mode: str = "single_repository",
    ) -> Dict:
        return self._service.push_test_cases(
            test_cases=test_cases,
            project_id=project_id,
            suite_id=suite_id,
            section_id=section_id,
            repository_mode=repository_mode,
        )
