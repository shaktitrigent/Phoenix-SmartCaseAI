import json
import os
import re
from typing import Dict, List

import requests

from config import Config


class LLMService:
    def __init__(self):
        self.model = None
        self.provider = Config.LLM_PROVIDER
        self.model_path = Config.LLM_MODEL_PATH
        self.max_tokens = Config.LLM_MAX_TOKENS
        self.temperature = Config.LLM_TEMPERATURE
        self.n_ctx = Config.LLM_N_CTX
        self.timeout_seconds = Config.LLM_TIMEOUT_SECONDS

        self.gemini_api_key = Config.GEMINI_API_KEY
        self.gemini_model = Config.GEMINI_MODEL
        self.gemini_base_url = Config.GEMINI_BASE_URL

        self._load_llama_if_available()

    def _load_llama_if_available(self):
        if not self.model_path or not os.path.exists(self.model_path):
            return
        try:
            from llama_cpp import Llama

            self.model = Llama(model_path=self.model_path, n_ctx=self.n_ctx, verbose=False)
        except Exception:
            self.model = None

    def generate_json(self, prompt: str, seed_payload: Dict) -> str:
        if self._should_use_gemini():
            gemini_result = self._generate_with_gemini(prompt)
            if gemini_result:
                return gemini_result
            if self.provider == "gemini":
                return json.dumps(self._rule_based_generator(seed_payload), ensure_ascii=False)

        if self._should_use_llama():
            try:
                output = self.model.create_completion(
                    prompt=prompt,
                    max_tokens=self.max_tokens,
                    temperature=self.temperature,
                    stop=["```", "\n\n\n"],
                )
                text = output["choices"][0]["text"].strip()
                if text:
                    return text
            except Exception:
                pass

        return json.dumps(self._rule_based_generator(seed_payload), ensure_ascii=False)

    def _should_use_gemini(self) -> bool:
        if self.provider == "gemini":
            return True
        if self.provider == "auto":
            return bool(self.gemini_api_key)
        return False

    def _should_use_llama(self) -> bool:
        if self.provider == "llama":
            return self.model is not None
        if self.provider == "auto":
            return self.model is not None and not self.gemini_api_key
        return False

    def _generate_with_gemini(self, prompt: str) -> str:
        if not self.gemini_api_key:
            return ""

        url = f"{self.gemini_base_url}/models/{self.gemini_model}:generateContent"
        payload = {
            "generationConfig": {
                "temperature": self.temperature,
                "responseMimeType": "application/json",
            },
            "contents": [
                {
                    "role": "user",
                    "parts": [{"text": prompt}],
                }
            ],
        }
        try:
            response = requests.post(
                url,
                params={"key": self.gemini_api_key},
                json=payload,
                timeout=self.timeout_seconds,
            )
            if response.status_code >= 400:
                return ""

            data = response.json()
            candidates = data.get("candidates", [])
            if not candidates:
                return ""
            parts = (
                candidates[0]
                .get("content", {})
                .get("parts", [])
            )
            text_chunks = [str(part.get("text", "")).strip() for part in parts if part.get("text")]
            return "\n".join([x for x in text_chunks if x]).strip()
        except Exception:
            return ""

    @staticmethod
    def _rule_based_generator(seed_payload: Dict) -> Dict:
        source = str(seed_payload.get("source", "")).strip()
        summary = str(seed_payload.get("summary", "Generated Test Cases")).strip() or "Generated Test Cases"
        test_types = seed_payload.get("test_types", []) or ["positive", "negative", "edge"]
        test_types = [str(t).lower().strip() for t in test_types]

        sentences = [
            s.strip()
            for s in re.split(r"[.\n]+", source)
            if s and len(s.strip()) > 10
        ]
        if not sentences:
            sentences = [summary]

        cases: List[Dict] = []
        for i, ttype in enumerate(test_types, start=1):
            base = sentences[min(i - 1, len(sentences) - 1)]
            steps = [
                "Open the relevant application screen.",
                f"Prepare data required for {ttype} validation.",
                f"Perform action aligned with scenario: {base}",
                "Observe system behavior and collect output.",
            ]
            expected = "System behaves according to acceptance criteria without data integrity issues."
            if ttype == "negative":
                expected = "System blocks invalid input and returns clear validation feedback."
            elif ttype == "edge":
                expected = "System handles boundary values without crash or inconsistent state."
            elif ttype == "create":
                expected = "System creates a new entity and persists correct values."
            elif ttype == "update":
                expected = "System updates existing entity and audit/history remains correct."

            cases.append(
                {
                    "title": f"{summary} - {ttype.title()} Scenario {i}",
                    "preconditions": "User has required permissions and test data is available.",
                    "steps": steps,
                    "expected_result": expected,
                    "test_type": ttype,
                    "priority": "High" if ttype in ["negative", "edge"] else "Medium",
                }
            )

        return {"test_cases": cases}
