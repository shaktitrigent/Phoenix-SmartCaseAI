from typing import Dict, List, Optional

from embeddings.vector_store import EmbeddingVectorStore
from services.knowledge_base import KnowledgeBaseService
from services.llm import LLMService
from utils.dom_locator_parser import extract_locators
from utils.output_validator import filter_locators, filter_test_cases
from utils.prompt_builder import build_generation_prompt, build_locator_prompt
from utils.response_parser import parse_locator_response, parse_test_case_response


class LLMEngine:
    def __init__(self):
        self.llm = LLMService()
        self.vector_store = EmbeddingVectorStore()
        self.knowledge_base = KnowledgeBaseService()

    def _ensure_strict_model_used(self):
        if not str(self.llm.last_model_used or "").strip():
            raise ValueError(
                "Strict knowledge mode requires a cloud LLM provider/model. "
                "Configure an API key (Gemini/OpenAI/Anthropic/OpenRouter)."
            )

    def generate_from_jira_issue(
        self,
        issue_data: Dict,
        test_types: List[str],
        model_id: Optional[str] = None,
        output_language: str = "",
    ) -> List[Dict]:
        searchable_chunks = []
        summary = issue_data.get("summary", "")
        description = issue_data.get("description", "")
        acceptance_criteria = issue_data.get("acceptance_criteria", "")
        custom_prompt = str(issue_data.get("custom_prompt", "")).strip()
        attachments = issue_data.get("attachments_text", []) or []

        if summary:
            searchable_chunks.append(summary)
        if description:
            searchable_chunks.append(description)
        if acceptance_criteria:
            searchable_chunks.append(acceptance_criteria)
        if custom_prompt:
            searchable_chunks.append(custom_prompt)
        attachment_chunks = [x for x in attachments if x]
        searchable_chunks.extend(attachment_chunks)

        metadatas = []
        if summary:
            metadatas.append({"source": "summary"})
        if description:
            metadatas.append({"source": "description"})
        if acceptance_criteria:
            metadatas.append({"source": "acceptance_criteria"})
        if custom_prompt:
            metadatas.append({"source": "custom_prompt"})
        metadatas.extend([{"source": "attachment"} for _ in attachment_chunks])

        self.vector_store.add_texts(
            searchable_chunks,
            metadatas=metadatas,
        )

        attachment_query = "\n".join(attachment_chunks[:2])
        semantic_context = self.vector_store.search(
            query=f"{summary}\n{description}\n{acceptance_criteria}\n{custom_prompt}\n{attachment_query}",
            top_k=3,
        )

        knowledge_text = self.knowledge_base.get_test_case_knowledge()
        prompt = build_generation_prompt(
            issue_data=issue_data,
            test_types=test_types,
            semantic_context=semantic_context,
            knowledge_text=knowledge_text,
            output_language=output_language,
        )
        seed_payload = {
            "mode": "test_case_generation",
            "summary": summary or "Generated Test Cases",
            "source": "\n".join(searchable_chunks),
            "test_types": test_types,
        }
        raw_response = self.llm.generate_json(prompt, seed_payload, model_id=model_id)
        self._ensure_strict_model_used()
        cases = parse_test_case_response(raw_response)
        cases = filter_test_cases(cases)
        if not cases:
            raise ValueError("LLM returned no valid test cases.")

        final_cases = []
        for idx, case in enumerate(cases, start=1):
            normalized = dict(case)
            normalized["test_case_id"] = f"TC-{idx:03d}"
            final_cases.append(normalized)
        return final_cases

    def generate_locators(
        self,
        dom: str,
        framework: str,
        language: str,
        custom_prompt: str = "",
        model_id: Optional[str] = None,
    ) -> Dict:
        deterministic_locators = extract_locators(dom)
        prompt = build_locator_prompt(
            dom=dom,
            framework=framework,
            language=language,
            custom_prompt=custom_prompt,
            knowledge_text=self.knowledge_base.get_locator_knowledge(),
            deterministic_locators=deterministic_locators,
        )
        seed_payload = {
            "mode": "locator_generation",
            "dom": dom,
            "framework": framework,
            "language": language,
            "custom_prompt": custom_prompt,
        }
        try:
            raw_response = self.llm.generate_json(prompt, seed_payload, model_id=model_id)
            parsed = parse_locator_response(raw_response)
            automation_script = parsed.get("automation_script", "")
            test_function = parsed.get("test_function", "") or automation_script

            if not str(self.llm.last_model_used or "").strip():
                raise ValueError("No LLM model was used.")
            if not parsed.get("locators") and not automation_script and not test_function:
                raise ValueError("LLM returned an empty locator response.")

            merged_locators = _merge_locators(parsed.get("locators", []), deterministic_locators)
            filtered_locators = filter_locators(merged_locators)
            if not filtered_locators:
                raise ValueError("LLM returned no valid locators.")
            return {
                "locators": filtered_locators,
                "test_function": test_function,
                "automation_script": automation_script,
                # Backward compatibility for existing frontend/client consumers.
                "test_template": automation_script,
                "model_used": self.llm.last_model_used,
            }
        except Exception:
            fallback = LLMService._rule_based_locator_generator(seed_payload)
            automation_script = fallback.get("automation_script", "")
            test_function = fallback.get("test_function", "") or automation_script
            merged_locators = _merge_locators(fallback.get("locators", []), deterministic_locators)
            filtered_locators = filter_locators(merged_locators)
            if not filtered_locators:
                raise ValueError("No valid locators could be generated from the provided DOM.")
            return {
                "locators": filtered_locators,
                "test_function": test_function,
                "automation_script": automation_script,
                "test_template": automation_script,
                "model_used": "rule_based",
            }


def _merge_locators(primary: List[Dict], fallback: List[Dict]) -> List[Dict]:
    merged: List[Dict] = []
    seen = set()

    for items in (primary, fallback):
        for item in items or []:
            if not isinstance(item, dict):
                continue
            primary_locator = str(item.get("primary_locator", "")).strip()
            alternate_locator = str(item.get("alternate_locator", "")).strip()
            key = (primary_locator, alternate_locator)
            if not primary_locator or key in seen:
                continue
            seen.add(key)
            merged.append(
                {
                    "element": str(item.get("element", "")).strip(),
                    "primary_locator": primary_locator,
                    "alternate_locator": alternate_locator,
                    "strategy": str(item.get("strategy", "")).strip(),
                }
            )

    return merged
