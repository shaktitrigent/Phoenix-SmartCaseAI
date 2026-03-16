import json
from typing import Dict, List


def build_generation_prompt(
    issue_data: Dict,
    test_types: List[str],
    semantic_context: List[Dict],
    knowledge_text: str,
    output_language: str = "",
) -> str:
    attachment_blob = "\n\n".join(issue_data.get("attachments_text", []))
    semantic_blob = "\n".join([item.get("text", "") for item in semantic_context if item.get("text")])
    custom_prompt = str(issue_data.get("custom_prompt", "")).strip()

    schema = {
        "test_cases": [
            {
                "title": "string",
                "preconditions": "string",
                "steps": ["string"],
                "expected_result": "string",
                "test_type": "functional|regression|ui|security|performance",
                "priority": "Low|Medium|High",
            }
        ]
    }

    payload = {
        "issue_key": issue_data.get("issue_key", ""),
        "summary": issue_data.get("summary", ""),
        "description": issue_data.get("description", ""),
        "acceptance_criteria": issue_data.get("acceptance_criteria", ""),
        "custom_prompt": custom_prompt,
        "custom_fields": issue_data.get("custom_fields", {}),
        "attachments_text": attachment_blob,
        "semantic_context": semantic_blob,
        "test_types": test_types,
    }

    resolved_language = str(output_language or "").strip()
    instructions = [
        "You are a senior QA engineer.",
        "You MUST strictly follow the provided knowledge base policy.",
        "If user instructions conflict with the knowledge base, follow the knowledge base.",
        "Generate complete and execution-ready test cases.",
        "Each test case must include explicit preconditions, 2+ concrete steps, and a clear expected result.",
        "Cover each requested test type with practical steps and expected outcomes.",
        "Generate detailed test cases using description, acceptance criteria, and additional custom instructions when provided.",
        "Treat attachment text as requirement input; convert relevant attachment details into test conditions and checks.",
        "If attachment text conflicts with description, prioritize explicit acceptance criteria, then attachment text, then description.",
        f"Write all output fields in {resolved_language}." if resolved_language else "Write all output fields in English.",
        "Knowledge base policy (MANDATORY):",
        knowledge_text,
        "Return STRICT JSON only.",
        "Do not include markdown, comments, or explanations.",
        "Output must match this schema exactly:",
        json.dumps(schema, ensure_ascii=False),
        "Input payload:",
        json.dumps(payload, ensure_ascii=False),
    ]
    return "\n".join(instructions)


def build_locator_prompt(
    dom: str,
    framework: str,
    language: str,
    custom_prompt: str,
    knowledge_text: str,
    deterministic_locators: List[Dict],
) -> str:
    schema = {
        "locators": [
            {
                "element": "Login Button",
                "primary_locator": "string",
                "alternate_locator": "string",
                "strategy": "CSS Selector|ID|Name|XPath|Role|Text",
            }
        ],
        "test_function": "Core reusable test function/method code as plain text",
        "automation_script": "Complete runnable automation script/file as plain text",
    }

    instructions = [
        "You are a senior QA automation engineer.",
        "You MUST strictly follow the provided locator knowledge base policy.",
        "If user instructions conflict with the knowledge base, follow the knowledge base.",
        "Based on the provided DOM, generate reliable, production-ready element locators.",
        "Prefer stable attributes (id, name, data-testid).",
        "Avoid brittle absolute XPath.",
        "Provide alternate locator strategies whenever possible.",
        "Output both: (1) a reusable test function and (2) a complete runnable automation script.",
        "Ensure the test function and automation script are idiomatic for the requested framework + language.",
        "Use Playwright locators/APIs for Playwright and Selenium By.* APIs for Selenium.",
        f"Framework: {framework}",
        f"Language: {language}",
        "Custom Instructions:",
        custom_prompt or "(none)",
        "Locator knowledge base policy (MANDATORY):",
        knowledge_text,
        "Deterministic locator extraction (from HTML, for reference):",
        json.dumps(deterministic_locators, ensure_ascii=False),
        "DOM:",
        dom,
        "Return STRICT JSON only matching this schema:",
        json.dumps(schema, ensure_ascii=False),
    ]
    return "\n".join(instructions)
