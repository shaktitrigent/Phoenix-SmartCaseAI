from pathlib import Path
from threading import Lock
from typing import Dict, Tuple


class KnowledgeBaseService:
    def __init__(self):
        base_dir = Path(__file__).resolve().parent.parent
        knowledge_dir = base_dir / "knowledge"
        self._test_case_path = knowledge_dir / "test-cases-knowledge.md"
        self._locator_path = knowledge_dir / "weblocator-knowledge.md"
        self._cache: Dict[str, Tuple[float, str]] = {}
        self._lock = Lock()

    def get_test_case_knowledge(self) -> str:
        return self._read_text(self._test_case_path)

    def get_locator_knowledge(self) -> str:
        return self._read_text(self._locator_path)

    def _read_text(self, path: Path) -> str:
        key = str(path)
        if not path.exists():
            raise ValueError(f"Knowledge file not found: {path}")

        modified_at = path.stat().st_mtime
        with self._lock:
            cached = self._cache.get(key)
            if cached and cached[0] == modified_at:
                return cached[1]

            content = path.read_text(encoding="utf-8").strip()
            if not content:
                raise ValueError(f"Knowledge file is empty: {path}")

            self._cache[key] = (modified_at, content)
            return content
