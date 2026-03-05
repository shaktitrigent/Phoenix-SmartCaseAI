import os
from dataclasses import dataclass
from pathlib import Path
from dotenv import load_dotenv


load_dotenv(Path(__file__).resolve().parent / ".env")


@dataclass
class Config:
    FLASK_ENV: str = os.getenv("FLASK_ENV", "development")
    FLASK_DEBUG: bool = os.getenv("FLASK_DEBUG", "false").lower() == "true"
    SECRET_KEY: str = os.getenv("SECRET_KEY", "change-me")

    JIRA_BASE_URL: str = os.getenv("JIRA_BASE_URL", "").rstrip("/")
    JIRA_USERNAME: str = os.getenv("JIRA_USERNAME", "")
    JIRA_API_TOKEN: str = os.getenv("JIRA_API_TOKEN", "")

    CORS_ORIGINS: str = os.getenv("CORS_ORIGINS", "http://localhost:5173")
    EXPORT_DIR: str = os.getenv("EXPORT_DIR", "exports")

    LLM_MODEL_PATH: str = os.getenv("LLM_MODEL_PATH", "")
    LLM_N_CTX: int = int(os.getenv("LLM_N_CTX", "4096"))
    LLM_MAX_TOKENS: int = int(os.getenv("LLM_MAX_TOKENS", "1200"))
    LLM_TEMPERATURE: float = float(os.getenv("LLM_TEMPERATURE", "0.1"))
    LLM_PROVIDER: str = os.getenv("LLM_PROVIDER", "auto").lower()
    LLM_TIMEOUT_SECONDS: int = int(os.getenv("LLM_TIMEOUT_SECONDS", "60"))

    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
    GEMINI_MINI_MODEL: str = os.getenv("GEMINI_MINI_MODEL", "gemini-2.0-flash-lite")
    GEMINI_BASE_URL: str = os.getenv(
        "GEMINI_BASE_URL",
        "https://generativelanguage.googleapis.com/v1beta",
    ).rstrip("/")

    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    OPENAI_BASE_URL: str = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1").rstrip("/")
    OPENAI_MINI_MODEL: str = os.getenv("OPENAI_MINI_MODEL", "gpt-4.1-mini")
    OPENAI_NANO_MODEL: str = os.getenv("OPENAI_NANO_MODEL", "gpt-4.1-nano")
    OPENAI_4O_MINI_MODEL: str = os.getenv("OPENAI_4O_MINI_MODEL", "gpt-4o-mini")
    ANTHROPIC_API_KEY: str = os.getenv("ANTHROPIC_API_KEY", "")
    ANTHROPIC_BASE_URL: str = os.getenv("ANTHROPIC_BASE_URL", "https://api.anthropic.com").rstrip("/")
    CLAUDE_SONNET_MODEL: str = os.getenv("CLAUDE_SONNET_MODEL", "claude-3-7-sonnet-latest")
    CLAUDE_HAIKU_MODEL: str = os.getenv("CLAUDE_HAIKU_MODEL", "claude-3-5-haiku-latest")
    OPENROUTER_API_KEY: str = os.getenv("OPENROUTER_API_KEY", "")
    OPENROUTER_BASE_URL: str = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1").rstrip("/")
    LLM_DEFAULT_MODEL_ID: str = os.getenv("LLM_DEFAULT_MODEL_ID", "gemini-2.5-flash")

    TESTRAIL_BASE_URL: str = os.getenv("TESTRAIL_BASE_URL", "").rstrip("/")
    TESTRAIL_USERNAME: str = os.getenv("TESTRAIL_USERNAME", "")
    TESTRAIL_API_KEY: str = os.getenv("TESTRAIL_API_KEY", "")
    TESTRAIL_PASSWORD: str = os.getenv("TESTRAIL_PASSWORD", "")
    TESTRAIL_PROJECT_ID: str = os.getenv("TESTRAIL_PROJECT_ID", "")
    TESTRAIL_SUITE_ID: str = os.getenv("TESTRAIL_SUITE_ID", "")
    TESTRAIL_SECTION_ID: str = os.getenv("TESTRAIL_SECTION_ID", "")

    EMBEDDING_MODEL_NAME: str = os.getenv(
        "EMBEDDING_MODEL_NAME", "sentence-transformers/all-MiniLM-L6-v2"
    )

    DEFAULT_TEST_TYPES = [
        "functional",
        "regression",
        "ui",
        "security",
        "performance",
        "create",
        "update",
        "edge",
    ]
