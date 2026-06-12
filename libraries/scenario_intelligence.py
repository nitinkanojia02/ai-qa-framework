from typing import Dict, List

from libraries.ai_scenario_service import AIScenarioService
from utils.logger import get_logger

logger = get_logger(__name__)


class ScenarioIntelligence:
    def __init__(self, ai_client=None) -> None:
        self.ai_client = ai_client
        self.ai_scenario_service = AIScenarioService(ai_client) if ai_client else None
        self.max_form_fields_for_positive = 5

    def build_scenarios(self, knowledge) -> List[Dict]:
        if self.ai_scenario_service:
            ai_scenarios = self._build_ai_scenarios(knowledge)
            if ai_scenarios:
                logger.info("Scenario intelligence using AI-generated scenarios: %s", len(ai_scenarios))
                return ai_scenarios

        fallback = self._build_minimal_fallback_scenarios(knowledge)
        logger.info("Scenario intelligence fallback generated %s scenarios", len(fallback))
        return fallback

    def _build_ai_scenarios(self, knowledge) -> List[Dict]:
        scenarios: List[Dict] = []
        for page in knowledge.pages:
            evidence = self._build_evidence_package(knowledge, page)
            ai_result = self.ai_scenario_service.generate_scenarios(evidence)
            default_page = {
                "page_name": page.page_name,
                "page_type": page.page_type,
            }
            page_scenarios = self.ai_scenario_service.normalize_scenarios(ai_result, default_page)
            for scenario in page_scenarios:
                scenario.setdefault("source_page", page.page_name)
                scenario.setdefault("module_name", page.module_name)
                scenario.setdefault("primary_entity", page.primary_entity)
                scenario.setdefault("linked_pages", [page.page_name])
                scenario.setdefault("generation_source", "ai_scenario_generation")
                scenario["tags"] = sorted(set((scenario.get("tags") or []) + self._base_tags(page, scenario)))
            scenarios.extend(page_scenarios)
        return self._dedupe_scenarios(scenarios)

    def _build_evidence_package(self, knowledge, page) -> Dict:
        page_elements = [element for element in knowledge.elements if element.page_name == page.page_name]
        page_locators = [locator for locator in knowledge.locators if locator.page_name == page.page_name]
        transitions = [
            transition.to_dict()
            for transition in knowledge.workflow_transitions
            if transition.source_page == page.page_name or transition.destination_page == page.page_name
        ]

        return {
            "application": {
                "name": knowledge.application_name,
                "start_url": knowledge.start_url,
            },
            "page": {
                "page_name": page.page_name,
                "title": page.title,
                "url": page.url,
                "page_type": page.page_type,
                "business_purpose": page.business_purpose,
                "module_name": page.module_name,
                "primary_entity": page.primary_entity,
                "metadata": page.metadata,
            },
            "elements": [
                {
                    "element_name": element.element_name,
                    "tag": element.tag,
                    "text": element.text,
                    "intent": element.intent,
                    "risk_class": element.risk_class,
                    "semantic_role": element.semantic_role,
                    "attributes": element.attributes,
                }
                for element in page_elements[:40]
            ],
            "locators": [
                {
                    "element_name": locator.element_name,
                    "best_locator": locator.best_locator,
                    "fallback_locators": locator.fallback_locators[:3],
                    "stability_score": locator.stability_score,
                    "success_rate": locator.success_rate,
                }
                for locator in page_locators[:20]
            ],
            "workflow_transitions": transitions[:20],
            "historical_failures": [
                failure.to_dict()
                for failure in knowledge.failures[-10:]
                if failure.metadata.get("page_name", "") == page.page_name or not failure.metadata
            ],
        }

    def _build_minimal_fallback_scenarios(self, knowledge) -> List[Dict]:
        scenarios: List[Dict] = []
        for page in knowledge.pages:
            scenarios.append(
                {
                    "title": f"Verify {page.page_name.replace('_', ' ')} page loads successfully",
                    "objective": page.business_purpose or f"Verify the {page.page_name.replace('_', ' ')} page is accessible.",
                    "scenario_type": "smoke",
                    "scenario_category": "smoke",
                    "workflow_type": page.page_type or "general",
                    "risk_level": "medium",
                    "preconditions": [
                        "Application is reachable in the target environment.",
                        f"User can access the {page.page_name.replace('_', ' ')} page.",
                    ],
                    "steps": [
                        f"Navigate to the {page.page_name.replace('_', ' ')} page.",
                        "Observe the page and verify the primary content is visible.",
                    ],
                    "expected_results": [
                        "The page loads without unexpected errors.",
                        "Primary actions, controls, and business content are visible.",
                    ],
                    "tags": self._base_tags(page, {"scenario_type": "smoke", "workflow_type": page.page_type or "general"}),
                    "source_page": page.page_name,
                    "module_name": page.module_name,
                    "primary_entity": page.primary_entity,
                    "linked_pages": [page.page_name],
                    "generation_source": "fallback_scenario_generation",
                }
            )
        return scenarios

    def _base_tags(self, page, scenario: Dict) -> List[str]:
        tags = ["ai-generated", scenario.get("scenario_type", "positive"), scenario.get("workflow_type", "general")]
        if page and page.module_name:
            tags.append(page.module_name.lower().replace(" ", "_"))
        if page and page.primary_entity:
            tags.append(page.primary_entity.lower().replace(" ", "_"))
        return [tag for tag in tags if tag]

    def _dedupe_scenarios(self, scenarios: List[Dict]) -> List[Dict]:
        deduped: List[Dict] = []
        seen = set()
        for scenario in scenarios:
            key = (
                scenario.get("title", "").strip().lower(),
                scenario.get("scenario_type", ""),
                scenario.get("source_page", ""),
            )
            if key in seen:
                continue
            seen.add(key)
            deduped.append(scenario)
        return deduped
