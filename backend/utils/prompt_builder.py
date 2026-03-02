import json
from typing import Dict, List


def build_generation_prompt(issue_data: Dict, test_types: List[str], semantic_context: List[Dict]) -> str:
    attachment_blob = "\n\n".join(issue_data.get("attachments_text", []))
    semantic_blob = "\n".join([item.get("text", "") for item in semantic_context if item.get("text")])

    schema = {
        "test_cases": [
            {
                "title": "string",
                "preconditions": "string",
                "steps": ["string"],
                "expected_result": "string",
                "test_type": "positive|negative|edge|create|update",
                "priority": "Low|Medium|High",
            }
        ]
    }

    payload = {
        "issue_key": issue_data.get("issue_key", ""),
        "summary": issue_data.get("summary", ""),
        "description": issue_data.get("description", ""),
        "acceptance_criteria": issue_data.get("acceptance_criteria", ""),
        "custom_fields": issue_data.get("custom_fields", {}),
        "attachments_text": attachment_blob,
        "semantic_context": semantic_blob,
        "test_types": test_types,
    }

    instructions = [
        "You are a senior QA engineer.",
        "Generate complete and execution-ready test cases.",
        "Cover each requested test type with practical steps and expected outcomes.",
        "Treat attachment text as requirement input; convert relevant attachment details into test conditions and checks.",
        "If attachment text conflicts with description, prioritize explicit acceptance criteria, then attachment text, then description.",
        "Return STRICT JSON only.",
        "Do not include markdown, comments, or explanations.",
        "Output must match this schema exactly:",
        json.dumps(schema, ensure_ascii=False),
        "Input payload:",
        json.dumps(payload, ensure_ascii=False),
    ]
    return "\n".join(instructions)
