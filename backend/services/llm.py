import json
import logging
import re
from typing import Dict, List, Optional

import requests

from config import Config
from utils.dom_locator_parser import extract_locators

logger = logging.getLogger(__name__)

OPENROUTER_FREE_MODELS = [
    "deepseek/deepseek-chat",
    "deepseek/deepseek-coder",
    "meta-llama/llama-3-8b-instruct",
    "meta-llama/llama-3-70b-instruct",
    "mistralai/mistral-7b-instruct",
    "mistralai/mixtral-8x7b-instruct",
]

OPENROUTER_FREE_MODEL_OPTIONS = [
    {"model_name": "deepseek/deepseek-chat", "label": "OpenRouter - DeepSeek Chat"},
    {"model_name": "deepseek/deepseek-coder", "label": "OpenRouter - DeepSeek Coder"},
    {"model_name": "meta-llama/llama-3-8b-instruct", "label": "OpenRouter - Llama 3 8B"},
    {"model_name": "meta-llama/llama-3-70b-instruct", "label": "OpenRouter - Llama 3 70B"},
    {"model_name": "mistralai/mixtral-8x7b-instruct", "label": "OpenRouter - Mixtral 8x7B"},
    {"model_name": "mistralai/mistral-7b-instruct", "label": "OpenRouter - Mistral 7B"},
]


def call_openrouter(model: str, prompt: str) -> str:
    api_key = Config.OPENROUTER_API_KEY
    if not api_key:
        return ""

    resolved_model = str(model or "").strip()
    if not resolved_model:
        return ""
    if resolved_model not in OPENROUTER_FREE_MODELS:
        logger.error("OpenRouter model rejected (not in free allowlist): %s", resolved_model)
        return ""

    url = f"{Config.OPENROUTER_BASE_URL}/chat/completions"
    payload = {
        "model": resolved_model,
        "messages": [
            {
                "role": "user",
                "content": prompt,
            }
        ],
    }
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    try:
        response = requests.post(
            url,
            headers=headers,
            json=payload,
            timeout=Config.LLM_TIMEOUT_SECONDS,
        )
    except requests.exceptions.Timeout:
        logger.error("OpenRouter request timed out for model: %s", resolved_model)
        return ""
    except requests.RequestException:
        logger.exception("OpenRouter request failed for model: %s", resolved_model)
        return ""

    if response.status_code >= 400:
        logger.error(
            "OpenRouter request failed with status %s for model: %s",
            response.status_code,
            resolved_model,
        )
        return ""

    try:
        data = response.json()
    except ValueError:
        logger.error("OpenRouter returned non-JSON response for model: %s", resolved_model)
        return ""

    choices = data.get("choices", [])
    if not choices:
        logger.error("OpenRouter returned empty choices for model: %s", resolved_model)
        return ""

    first = choices[0] if isinstance(choices[0], dict) else {}
    message = first.get("message", {}) if isinstance(first, dict) else {}
    content = message.get("content", "") if isinstance(message, dict) else ""
    if isinstance(content, str):
        return content.strip()
    if isinstance(content, list):
        chunks = []
        for item in content:
            if not isinstance(item, dict):
                continue
            text = str(item.get("text", "")).strip()
            if text:
                chunks.append(text)
        return "\n".join(chunks).strip()
    logger.error("OpenRouter returned unsupported message content format for model: %s", resolved_model)
    return ""


class LLMService:
    def __init__(self):
        self.provider = Config.LLM_PROVIDER
        self.max_tokens = Config.LLM_MAX_TOKENS
        self.temperature = Config.LLM_TEMPERATURE
        self.n_ctx = Config.LLM_N_CTX
        self.timeout_seconds = Config.LLM_TIMEOUT_SECONDS

        self.gemini_api_key = Config.GEMINI_API_KEY
        self.gemini_base_url = Config.GEMINI_BASE_URL

        self.openai_api_key = Config.OPENAI_API_KEY
        self.openai_base_url = Config.OPENAI_BASE_URL
        self.anthropic_api_key = Config.ANTHROPIC_API_KEY
        self.anthropic_base_url = Config.ANTHROPIC_BASE_URL
        self.openrouter_api_key = Config.OPENROUTER_API_KEY

        self.default_model_id = Config.LLM_DEFAULT_MODEL_ID
        self.last_model_used = ""

    @staticmethod
    def _dedupe(values: List[str]) -> List[str]:
        seen = set()
        result = []
        for value in values:
            item = str(value or "").strip()
            if not item or item in seen:
                continue
            seen.add(item)
            result.append(item)
        return result

    def _try_gemini_models(self, prompt: str, models: List[str]) -> Optional[str]:
        for model_name in self._dedupe(models):
            result = self._generate_with_gemini(prompt, model_name)
            if result:
                self.last_model_used = f"gemini:{model_name}"
                return result
        return None

    def _try_openai_models(self, prompt: str, models: List[str]) -> Optional[str]:
        for model_name in self._dedupe(models):
            result = self._generate_with_openai(prompt, model_name)
            if result:
                self.last_model_used = f"openai:{model_name}"
                return result
        return None

    def _try_anthropic_models(self, prompt: str, models: List[str]) -> Optional[str]:
        for model_name in self._dedupe(models):
            result = self._generate_with_anthropic(prompt, model_name)
            if result:
                self.last_model_used = f"anthropic:{model_name}"
                return result
        return None

    def _try_openrouter_models(self, prompt: str, models: List[str]) -> Optional[str]:
        for model_name in self._dedupe(models):
            result = call_openrouter(model_name, prompt)
            if result:
                self.last_model_used = f"openrouter:{model_name}"
                return result
        return None

    def list_models(self) -> List[Dict]:
        models = [
            {
                "id": "gemini-2.5-flash",
                "label": "Gemini 2.5 Flash",
                "provider": "gemini",
                "model_name": Config.GEMINI_MODEL,
                "available": bool(self.gemini_api_key),
                "requires_api_key": True,
            },
            {
                "id": "openai-gpt-4.1-mini",
                "label": "OpenAI GPT-4.1 Mini",
                "provider": "openai",
                "model_name": Config.OPENAI_MINI_MODEL,
                "available": bool(self.openai_api_key),
                "requires_api_key": True,
            },
            {
                "id": "claude-3-7-sonnet",
                "label": "Claude 3.7 Sonnet",
                "provider": "anthropic",
                "model_name": Config.CLAUDE_SONNET_MODEL,
                "available": bool(self.anthropic_api_key),
                "requires_api_key": True,
            },
        ]
        for option in OPENROUTER_FREE_MODEL_OPTIONS:
            model_name = option["model_name"]
            models.append(
                {
                    "id": f"openrouter:{model_name}",
                    "label": option["label"],
                    "provider": "openrouter",
                    "model_name": model_name,
                    "available": bool(self.openrouter_api_key),
                    "requires_api_key": True,
                }
            )
        return models

    def generate_json(self, prompt: str, seed_payload: Dict, model_id: Optional[str] = None) -> str:
        if self.provider not in {"auto", "gemini", "openai", "anthropic", "openrouter"}:
            raise ValueError(
                "Invalid LLM_PROVIDER. Allowed values: auto, gemini, openai, anthropic, openrouter."
            )

        selected_model_id = (model_id or self.default_model_id or "").strip()
        selected = (
            self._find_model(selected_model_id)
            or self._parse_provider_model(selected_model_id)
            or self._find_model("gemini-2.5-flash")
        )

        if selected and selected.get("provider") == "gemini":
            result = self._try_gemini_models(
                prompt,
                [selected.get("model_name", ""), Config.GEMINI_MODEL, Config.GEMINI_MINI_MODEL],
            )
            if result:
                return result

        if selected and selected.get("provider") == "openai":
            result = self._try_openai_models(
                prompt,
                [selected.get("model_name", ""), Config.OPENAI_MINI_MODEL, Config.OPENAI_4O_MINI_MODEL, Config.OPENAI_NANO_MODEL],
            )
            if result:
                return result

        if selected and selected.get("provider") == "anthropic":
            result = self._try_anthropic_models(
                prompt,
                [selected.get("model_name", ""), Config.CLAUDE_SONNET_MODEL, Config.CLAUDE_HAIKU_MODEL],
            )
            if result:
                return result

        if selected and selected.get("provider") == "openrouter":
            result = self._try_openrouter_models(
                prompt,
                [selected.get("model_name", "")] + OPENROUTER_FREE_MODELS,
            )
            if result:
                return result

        if self.provider == "auto":
            if self.gemini_api_key:
                result = self._try_gemini_models(prompt, [Config.GEMINI_MODEL, Config.GEMINI_MINI_MODEL])
                if result:
                    return result
            if self.openai_api_key:
                result = self._try_openai_models(
                    prompt, [Config.OPENAI_MINI_MODEL, Config.OPENAI_4O_MINI_MODEL, Config.OPENAI_NANO_MODEL]
                )
                if result:
                    return result
            if self.anthropic_api_key:
                result = self._try_anthropic_models(prompt, [Config.CLAUDE_SONNET_MODEL, Config.CLAUDE_HAIKU_MODEL])
                if result:
                    return result
            if self.openrouter_api_key:
                result = self._try_openrouter_models(prompt, OPENROUTER_FREE_MODELS)
                if result:
                    return result

        if self.provider == "gemini":
            result = self._try_gemini_models(prompt, [Config.GEMINI_MODEL, Config.GEMINI_MINI_MODEL])
            if result:
                return result

        if self.provider == "openai":
            result = self._try_openai_models(
                prompt, [Config.OPENAI_MINI_MODEL, Config.OPENAI_4O_MINI_MODEL, Config.OPENAI_NANO_MODEL]
            )
            if result:
                return result

        if self.provider == "anthropic":
            result = self._try_anthropic_models(prompt, [Config.CLAUDE_SONNET_MODEL, Config.CLAUDE_HAIKU_MODEL])
            if result:
                return result

        if self.provider == "openrouter":
            result = self._try_openrouter_models(prompt, OPENROUTER_FREE_MODELS)
            if result:
                return result

        raise ValueError(
            "No cloud LLM available for this request. Configure at least one API key "
            "(Gemini/OpenAI/Anthropic/OpenRouter) and select an available model."
        )

    def _find_model(self, model_id: str) -> Optional[Dict]:
        if not model_id:
            return None
        for model in self.list_models():
            if model.get("id") == model_id:
                return model
        return None

    @staticmethod
    def _parse_provider_model(model_id: str) -> Optional[Dict]:
        value = str(model_id or "").strip()
        if ":" not in value:
            return None
        provider, model_name = value.split(":", 1)
        provider = provider.strip().lower()
        model_name = model_name.strip()
        if not provider or not model_name:
            return None
        if provider not in {"gemini", "openai", "anthropic", "openrouter"}:
            return None
        return {
            "id": value,
            "label": value,
            "provider": provider,
            "model_name": model_name,
            "available": True,
            "requires_api_key": True,
        }

    def _generate_with_gemini(self, prompt: str, model_name: str) -> str:
        if not self.gemini_api_key:
            return ""

        resolved_model = model_name or Config.GEMINI_MODEL
        url = f"{self.gemini_base_url}/models/{resolved_model}:generateContent"
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
            parts = candidates[0].get("content", {}).get("parts", [])
            text_chunks = [str(part.get("text", "")).strip() for part in parts if part.get("text")]
            return "\n".join([x for x in text_chunks if x]).strip()
        except Exception:
            return ""

    def _generate_with_openai(self, prompt: str, model_name: str) -> str:
        if not self.openai_api_key:
            return ""

        resolved_model = model_name or Config.OPENAI_MINI_MODEL
        url = f"{self.openai_base_url}/chat/completions"
        payload = {
            "model": resolved_model,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "response_format": {"type": "json_object"},
            "messages": [
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
        }
        headers = {
            "Authorization": f"Bearer {self.openai_api_key}",
            "Content-Type": "application/json",
        }

        try:
            response = requests.post(
                url,
                headers=headers,
                json=payload,
                timeout=self.timeout_seconds,
            )
            if response.status_code >= 400:
                return ""

            data = response.json()
            choices = data.get("choices", [])
            if not choices:
                return ""
            message = choices[0].get("message", {})
            content = message.get("content", "")
            if isinstance(content, str):
                return content.strip()
            return ""
        except Exception:
            return ""

    def _generate_with_anthropic(self, prompt: str, model_name: str) -> str:
        if not self.anthropic_api_key:
            return ""

        resolved_model = model_name or Config.CLAUDE_SONNET_MODEL
        url = f"{self.anthropic_base_url}/v1/messages"
        payload = {
            "model": resolved_model,
            "max_tokens": self.max_tokens,
            "temperature": self.temperature,
            "messages": [
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
        }
        headers = {
            "x-api-key": self.anthropic_api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        }

        try:
            response = requests.post(
                url,
                headers=headers,
                json=payload,
                timeout=self.timeout_seconds,
            )
            if response.status_code >= 400:
                return ""

            data = response.json()
            content_items = data.get("content", [])
            text_chunks = []
            if isinstance(content_items, list):
                for item in content_items:
                    if not isinstance(item, dict):
                        continue
                    if item.get("type") == "text":
                        text = str(item.get("text", "")).strip()
                        if text:
                            text_chunks.append(text)
            return "\n".join(text_chunks).strip()
        except Exception:
            return ""

    @staticmethod
    def _rule_based_generator(seed_payload: Dict) -> Dict:
        mode = str(seed_payload.get("mode", "")).strip().lower()
        if mode == "locator_generation":
            return LLMService._rule_based_locator_generator(seed_payload)

        source = str(seed_payload.get("source", "")).strip()
        summary = str(seed_payload.get("summary", "Generated Test Cases")).strip() or "Generated Test Cases"
        test_types = seed_payload.get("test_types", []) or ["functional", "regression", "ui"]
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
            if ttype == "regression":
                expected = "Existing user journeys continue to work without regressions."
            elif ttype == "ui":
                expected = "UI elements render correctly and interaction flow is consistent."
            elif ttype == "security":
                expected = "System prevents unauthorized access and rejects malicious input."
            elif ttype == "performance":
                expected = "System responds within acceptable thresholds under expected load."

            cases.append(
                {
                    "title": f"{summary} - {ttype.title()} Scenario {i}",
                    "preconditions": "User has required permissions and test data is available.",
                    "steps": steps,
                    "expected_result": expected,
                    "test_type": ttype,
                    "priority": "High" if ttype in ["security", "performance"] else "Medium",
                }
            )

        return {"test_cases": cases}

    @staticmethod
    def _rule_based_locator_generator(seed_payload: Dict) -> Dict:
        framework = str(seed_payload.get("framework", "Selenium")).strip() or "Selenium"
        language = str(seed_payload.get("language", "Python")).strip() or "Python"
        custom_prompt = str(seed_payload.get("custom_prompt", "")).strip()
        dom = str(seed_payload.get("dom", "")).strip()

        locators = extract_locators(dom)

        automation_script = LLMService._fallback_locator_template(framework, language, custom_prompt)
        test_function = LLMService._fallback_test_function(framework, language)
        return {
            "locators": locators,
            "test_function": test_function,
            "automation_script": automation_script,
            "test_template": automation_script,
        }

    @staticmethod
    def _fallback_test_function(framework: str, language: str) -> str:
        framework_norm = framework.lower()
        language_norm = language.lower()

        if framework_norm == "playwright" and language_norm == "typescript":
            return (
                "async function loginSmoke(page: Page): Promise<void> {\n"
                "  await page.locator(\"input[name='username'], #username\").fill('demo');\n"
                "  await page.locator(\"input[name='password'], #password\").fill('demo-password');\n"
                "  await page.getByRole('button', { name: /login|sign in|submit/i }).click();\n"
                "}\n"
            )
        if framework_norm == "playwright" and language_norm == "java":
            return (
                "private static void loginSmoke(Page page) {\n"
                "  page.locator(\"input[name='username'], #username\").fill(\"demo\");\n"
                "  page.locator(\"input[name='password'], #password\").fill(\"demo-password\");\n"
                "  page.getByRole(AriaRole.BUTTON, new Page.GetByRoleOptions().setName(\"Sign in\")).click();\n"
                "}\n"
            )
        if framework_norm == "selenium" and language_norm == "java":
            return (
                "private static void loginSmoke(WebDriver driver) {\n"
                "  driver.findElement(By.cssSelector(\"input[name='username'], #username\")).sendKeys(\"demo\");\n"
                "  driver.findElement(By.cssSelector(\"input[name='password'], #password\")).sendKeys(\"demo-password\");\n"
                "  driver.findElement(By.cssSelector(\"[data-testid='submit'], button[type='submit']\")).click();\n"
                "}\n"
            )
        if framework_norm == "selenium" and language_norm == "typescript":
            return (
                "async function loginSmoke(driver: WebDriver): Promise<void> {\n"
                "  await driver.findElement(By.css(\"input[name='username'], #username\")).sendKeys('demo');\n"
                "  await driver.findElement(By.css(\"input[name='password'], #password\")).sendKeys('demo-password');\n"
                "  await driver.findElement(By.css(\"[data-testid='submit'], button[type='submit']\")).click();\n"
                "}\n"
            )
        return (
            "def login_smoke(driver) -> None:\n"
            "    driver.find_element(By.CSS_SELECTOR, \"input[name='username'], #username\").send_keys('demo')\n"
            "    driver.find_element(By.CSS_SELECTOR, \"input[name='password'], #password\").send_keys('demo-password')\n"
            "    driver.find_element(By.CSS_SELECTOR, \"[data-testid='submit'], button[type='submit']\").click()\n"
        )

    @staticmethod
    def _fallback_locator_template(framework: str, language: str, custom_prompt: str) -> str:
        framework_norm = framework.lower()
        language_norm = language.lower()
        hint = f"# Custom instructions: {custom_prompt}" if custom_prompt else "# Custom instructions: none"

        if framework_norm == "playwright" and language_norm == "typescript":
            return (
                "import { test, expect } from '@playwright/test';\n\n"
                f"// Framework: {framework} | Language: {language}\n"
                f"// {hint.replace('# ', '')}\n"
                "test('example locator smoke test', async ({ page }) => {\n"
                "  await page.goto('https://example.com');\n"
                "  const username = page.locator(\"input[name='username'], #username\");\n"
                "  const password = page.locator(\"input[name='password'], #password\");\n"
                "  const submit = page.getByRole('button', { name: /login|sign in|submit/i });\n"
                "  await username.fill('demo');\n"
                "  await password.fill('demo-password');\n"
                "  await submit.click();\n"
                "  await expect(page).not.toHaveURL(/login/);\n"
                "});\n"
            )

        if framework_norm == "playwright" and language_norm == "python":
            return (
                "from playwright.sync_api import Playwright, sync_playwright, expect\n\n"
                f"# Framework: {framework} | Language: {language}\n"
                f"{hint}\n\n"
                "def test_locator_smoke() -> None:\n"
                "    with sync_playwright() as playwright:\n"
                "        browser = playwright.chromium.launch(headless=True)\n"
                "        page = browser.new_page()\n"
                "        page.goto('https://example.com')\n"
                "        page.locator(\"input[name='username'], #username\").fill('demo')\n"
                "        page.locator(\"input[name='password'], #password\").fill('demo-password')\n"
                "        page.get_by_role('button', name='Sign in').click()\n"
                "        expect(page).not_to_have_url(re.compile('login'))\n"
                "        browser.close()\n"
            )

        if framework_norm == "playwright" and language_norm == "java":
            return (
                "import com.microsoft.playwright.*;\n"
                "import static com.microsoft.playwright.assertions.PlaywrightAssertions.assertThat;\n\n"
                "public class LocatorSmokeTest {\n"
                "  public static void main(String[] args) {\n"
                f"    // Framework: {framework} | Language: {language}\n"
                f"    // {hint.replace('# ', '')}\n"
                "    try (Playwright playwright = Playwright.create()) {\n"
                "      Browser browser = playwright.chromium().launch(new BrowserType.LaunchOptions().setHeadless(true));\n"
                "      Page page = browser.newPage();\n"
                "      page.navigate(\"https://example.com\");\n"
                "      page.locator(\"input[name='username'], #username\").fill(\"demo\");\n"
                "      page.locator(\"input[name='password'], #password\").fill(\"demo-password\");\n"
                "      page.getByRole(AriaRole.BUTTON, new Page.GetByRoleOptions().setName(\"Sign in\")).click();\n"
                "      assertThat(page).not().hasURL(\".*login.*\");\n"
                "      browser.close();\n"
                "    }\n"
                "  }\n"
                "}\n"
            )

        if framework_norm == "selenium" and language_norm == "java":
            return (
                "import org.openqa.selenium.By;\n"
                "import org.openqa.selenium.WebDriver;\n"
                "import org.openqa.selenium.chrome.ChromeDriver;\n\n"
                "public class LocatorSmokeTest {\n"
                "  public static void main(String[] args) {\n"
                f"    // Framework: {framework} | Language: {language}\n"
                f"    // {hint.replace('# ', '')}\n"
                "    WebDriver driver = new ChromeDriver();\n"
                "    try {\n"
                "      driver.get(\"https://example.com\");\n"
                "      driver.findElement(By.cssSelector(\"input[name='username'], #username\")).sendKeys(\"demo\");\n"
                "      driver.findElement(By.cssSelector(\"input[name='password'], #password\")).sendKeys(\"demo-password\");\n"
                "      driver.findElement(By.id(\"submit\")).click();\n"
                "    } finally {\n"
                "      driver.quit();\n"
                "    }\n"
                "  }\n"
                "}\n"
            )

        if framework_norm == "selenium" and language_norm == "typescript":
            return (
                "import { Builder, By, until } from 'selenium-webdriver';\n\n"
                f"// Framework: {framework} | Language: {language}\n"
                f"// {hint.replace('# ', '')}\n"
                "async function run(): Promise<void> {\n"
                "  const driver = await new Builder().forBrowser('chrome').build();\n"
                "  try {\n"
                "    await driver.get('https://example.com');\n"
                "    await driver.findElement(By.css(\"input[name='username'], #username\")).sendKeys('demo');\n"
                "    await driver.findElement(By.css(\"input[name='password'], #password\")).sendKeys('demo-password');\n"
                "    await driver.findElement(By.css(\"[data-testid='submit'], button[type='submit']\")).click();\n"
                "    await driver.wait(until.urlIs('https://example.com/dashboard'), 10000);\n"
                "  } finally {\n"
                "    await driver.quit();\n"
                "  }\n"
                "}\n\n"
                "run();\n"
            )

        return (
            "from selenium import webdriver\n"
            "from selenium.webdriver.common.by import By\n\n"
            f"# Framework: {framework} | Language: {language}\n"
            f"{hint}\n\n"
            "def test_locator_smoke() -> None:\n"
            "    driver = webdriver.Chrome()\n"
            "    try:\n"
            "        driver.get('https://example.com')\n"
            "        driver.find_element(By.CSS_SELECTOR, \"input[name='username'], #username\").send_keys('demo')\n"
            "        driver.find_element(By.CSS_SELECTOR, \"input[name='password'], #password\").send_keys('demo-password')\n"
            "        driver.find_element(By.CSS_SELECTOR, \"[data-testid='submit'], button[type='submit']\").click()\n"
            "    finally:\n"
            "        driver.quit()\n"
        )
