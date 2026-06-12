import json
from typing import Any, Dict, List

from utils.file_utils import read_text_file
from utils.logger import get_logger

logger = get_logger(__name__)


class AIScenarioService:
    def __init__(self, ai_client) -> None:
        self.ai_client = ai_client

    def generate_scenarios(self, evidence: Dict[str, Any]) -> Dict[str, Any]:
        system_prompt = read_text_file("data/prompts/scenario_generation_prompt.txt")
        user_prompt = self._build_prompt(evidence)

        response = self.ai_client.generate_text(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            metadata={
                "type": "scenario_generation",
                "page_name": evidence.get("page", {}).get("page_name", ""),
                "workflow_transition_count": len(evidence.get("workflow_transitions", [])),
            },
        )

        parsed = self._extract_json_payload(response.get("response_text", ""))
        if not parsed:
            logger.warning("AI scenario generation returned non-JSON or invalid payload; using empty scenario result")
            return {
                "page_understanding": {},
                "scenarios": [],
                "provider": response.get("provider", ""),
                "model": response.get("model", ""),
                "raw_response_text": response.get("response_text", ""),
            }

        parsed["provider"] = response.get("provider", "")
        parsed["model"] = response.get("model", "")
        parsed["raw_response_text"] = response.get("response_text", "")
        return parsed

    def _build_prompt(self, evidence: Dict[str, Any]) -> str:
        return json.dumps(evidence, indent=2, ensure_ascii=False)

    def _extract_json_payload(self, text: str) -> Dict[str, Any]:
        if not text:
            return {}
        stripped = text.strip()
        try:
            return json.loads(stripped)
        except json.JSONDecodeError:
            pass

        start = stripped.find("{")
        end = stripped.rfind("}")
        if start != -1 and end != -1 and end > start:
            candidate = stripped[start : end + 1]
            try:
                return json.loads(candidate)
            except json.JSONDecodeError:
                return {}
        return {}

    def normalize_scenarios(self, ai_result: Dict[str, Any], default_page: Dict[str, Any]) -> List[Dict[str, Any]]:
        scenarios = ai_result.get("scenarios", []) or []
        normalized: List[Dict[str, Any]] = []
        for scenario in scenarios:
            title = (scenario.get("title") or "").strip()
            if not title:
                continue
            normalized.append(
                {
                    "title": title,
                    "objective": scenario.get("objective", "Verify the generated scenario based on discovered evidence."),
                    "scenario_type": scenario.get("scenario_type", "positive"),
                    "scenario_category": scenario.get("scenario_category", "general"),
                    "workflow_type": scenario.get("workflow_type", default_page.get("page_type", "general") or "general"),
                    "risk_level": scenario.get("risk_level", "medium"),
                    "preconditions": scenario.get("preconditions", ["Application is reachable in the target environment."]),
                    "steps": scenario.get("steps", [f"Navigate to the {default_page.get('page_name', 'discovered')} page."]),
                    "expected_results": scenario.get("expected_results", ["The workflow completes without unexpected errors."]),
                    "tags": scenario.get("tags", []),
                }
            )
        return normalized
