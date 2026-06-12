import json
import os
from typing import Any, Dict, Optional
from urllib.parse import urlparse

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

        query = self._build_query(system_prompt, user_prompt)
        metadata = metadata or {}
        context = self._build_context(metadata)
        endpoint = self._normalize_endpoint(self.endpoint)
        data = {"query": query}
        if context:
            data["context"] = context

        logger.info(
            "Prepared GAINS AI payload | metadata_type=%s | query_len=%s | context_len=%s",
            metadata.get("type", ""),
            len(query or ""),
            len(context or ""),
        )

        headers = {
            "Authorization": f"Bearer {token}",
        }

        last_error = None

        for attempt in range(1, self.retry_count + 2):
            try:
                logger.info("Calling GAINS AI endpoint | attempt=%s | model=%s", attempt, self.model)
                response = requests.post(
                    endpoint,
                    headers=headers,
                    data=data,
                    verify=False,
                    timeout=self.request_timeout_seconds,
                )
                response.raise_for_status()
                raw_text = response.text

                text = self._extract_text(raw_text)
                logger.info("GAINS AI call completed successfully")
                return {
                    "provider": self.provider,
                    "model": self.model,
                    "response_text": text,
                    "raw_response": {
                        "response_text": raw_text,
                        "session_id": response.headers.get("sessionId", ""),
                        "status_code": response.status_code,
                    },
                }
            except Exception as exc:
                last_error = exc
                response_text = ""
                status_code = ""
                if isinstance(exc, requests.HTTPError) and exc.response is not None:
                    status_code = str(exc.response.status_code)
                    response_text = (exc.response.text or "")[:1000]
                logger.warning(
                    "GAINS AI call failed on attempt %s: %s | status=%s | response=%s | data_keys=%s | metadata_type=%s | endpoint=%s",
                    attempt,
                    exc,
                    status_code,
                    response_text,
                    list(data.keys()),
                    metadata.get("type", ""),
                    endpoint,
                )

        raise GainsAIClientError(f"GAINS AI call failed after retries: {last_error}")

    def _normalize_env_var_name(self, value: str) -> str:
        normalized = (value or "").strip()
        if normalized.startswith("${") and normalized.endswith("}"):
            normalized = normalized[2:-1].strip()
        return normalized

    def _build_query(self, system_prompt: str, user_prompt: str) -> str:
        return f"System Instructions:\n{system_prompt.strip()}\n\nUser Request:\n{user_prompt.strip()}"

    def _build_context(self, metadata: Dict[str, Any]) -> str:
        if not metadata:
            return ""
        try:
            return json.dumps(metadata, ensure_ascii=False)
        except Exception:
            return str(metadata)

    def _normalize_endpoint(self, endpoint: str) -> str:
        normalized = (endpoint or "").strip()
        if not normalized:
            raise GainsAIClientError("GAINS AI endpoint is not configured.")
        parsed = urlparse(normalized)
        if parsed.path.endswith("/chat"):
            return normalized
        return normalized.rstrip("/") + "/chat"

    def _extract_text(self, response_payload: Any) -> str:
        if isinstance(response_payload, str):
            stripped = response_payload.strip()
            if not stripped:
                return ""
            try:
                parsed = json.loads(stripped)
                return self._extract_text(parsed)
            except Exception:
                return stripped

        if isinstance(response_payload, dict):
            if "response" in response_payload and isinstance(response_payload["response"], str):
                return response_payload["response"]

            if "content" in response_payload and isinstance(response_payload["content"], str):
                return response_payload["content"]

            if "choices" in response_payload and response_payload["choices"]:
                first_choice = response_payload["choices"][0]
                message = first_choice.get("message", {})
                if "content" in message:
                    return message["content"]

        return str(response_payload)

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
