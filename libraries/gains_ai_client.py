import json
import os
from typing import Any, Dict, Optional

import requests

from utils.logger import get_logger

logger = get_logger(__name__)

class GainsAIClientError(Exception):
    """Raised when GAINS AI client operations fail."""

class GainsAIClient:
    def __init__(self, ai_config: Dict[str, Any]) -> None:
        self.ai_config = ai_config
        self.enabled = ai_config.get("enabled", False)
        self.provider = ai_config.get("provider", "gains")
        self.endpoint = ai_config.get("endpoint", "")
        raw_token_env_var = ai_config.get("token_env_var", "")
        self.token_env_var = self._normalize_env_var_name(raw_token_env_var)
        self.model = ai_config.get("model", "default")
        self.request_timeout_seconds = ai_config.get("request_timeout_seconds", 60)
        self.retry_count = ai_config.get("retry_count", 2)
        self.mock_mode = ai_config.get("mock_mode", True)

    def is_enabled(self) -> bool:
        return self.enabled

    def generate_text(
        self,
        system_prompt: str,
        user_prompt: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        if not self.enabled:
            raise GainsAIClientError("AI is disabled in configuration.")

        if self.mock_mode:
            logger.info("GAINS AI client running in mock mode")
            return self._mock_response(system_prompt, user_prompt, metadata)

        token = os.getenv(self.token_env_var, "").strip()
        if not token:
            raise GainsAIClientError(
                f"Missing AI token. Set environment variable: {self.token_env_var}"
            )

        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "metadata": metadata or {},
        }

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}",
        }

        last_error = None

        for attempt in range(1, self.retry_count + 2):
            try:
                logger.info("Calling GAINS AI endpoint | attempt=%s | model=%s", attempt, self.model)
                response = requests.post(
                    self.endpoint,
                    json=payload,
                    headers=headers,
                    timeout=self.request_timeout_seconds,
                )
                response.raise_for_status()
                data = response.json()

                text = self._extract_text(data)
                logger.info("GAINS AI call completed successfully")
                return {
                    "provider": self.provider,
                    "model": self.model,
                    "response_text": text,
                    "raw_response": data,
                }
            except Exception as exc:
                last_error = exc
                response_text = ""
                status_code = ""
                if isinstance(exc, requests.HTTPError) and exc.response is not None:
                    status_code = str(exc.response.status_code)
                    response_text = (exc.response.text or "")[:1000]
                logger.warning(
                    "GAINS AI call failed on attempt %s: %s | status=%s | response=%s",
                    attempt,
                    exc,
                    status_code,
                    response_text,
                )

        raise GainsAIClientError(f"GAINS AI call failed after retries: {last_error}")

    def _normalize_env_var_name(self, value: str) -> str:
        normalized = (value or "").strip()
        if normalized.startswith("${") and normalized.endswith("}"):
            normalized = normalized[2:-1].strip()
        return normalized

    def _extract_text(self, response_json: Dict[str, Any]) -> str:
        if isinstance(response_json, dict):
            if "response" in response_json and isinstance(response_json["response"], str):
                return response_json["response"]

            if "content" in response_json and isinstance(response_json["content"], str):
                return response_json["content"]

            if "choices" in response_json and response_json["choices"]:
                first_choice = response_json["choices"][0]
                message = first_choice.get("message", {})
                if "content" in message:
                    return message["content"]

        return str(response_json)

    def _mock_response(
        self,
        system_prompt: str,
        user_prompt: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        request_type = (metadata or {}).get("type", "")
        if request_type == "scenario_generation":
            mock_payload = {
                "page_understanding": {
                    "page_name": (metadata or {}).get("page_name", "discovered_page"),
                    "page_type": "general",
                    "business_purpose": "Mock-derived business page understanding.",
                    "module_name": "discovered_module",
                    "primary_entity": "discovered_entity",
                    "confidence": 0.55,
                },
                "scenarios": [
                    {
                        "title": "Validate discovered page loads successfully",
                        "objective": "Verify the discovered page is reachable and primary content is visible.",
                        "scenario_type": "smoke",
                        "scenario_category": "smoke",
                        "workflow_type": "general",
                        "risk_level": "medium",
                        "preconditions": ["Application is reachable in the target environment."],
                        "steps": [
                            "Navigate to the discovered page.",
                            "Observe the page and verify primary content is visible.",
                        ],
                        "expected_results": [
                            "The page loads without unexpected errors.",
                            "Primary controls and business content are visible.",
                        ],
                        "tags": ["ai-generated", "smoke", "mock-ai"],
                    }
                ],
            }
            return {
                "provider": self.provider,
                "model": self.model,
                "response_text": json.dumps(mock_payload),
                "raw_response": {"mock_mode": True, "type": request_type},
            }

        preview = user_prompt[:300].replace("\n", " ")
        mock_text = (
            "MOCK_AI_RESPONSE:\n"
            f"System prompt length: {len(system_prompt)}\n"
            f"User prompt preview: {preview}\n"
            f"Metadata: {metadata or {}}"
        )
        return {
            "provider": self.provider,
            "model": self.model,
            "response_text": mock_text,
            "raw_response": {"mock_mode": True},
        }
