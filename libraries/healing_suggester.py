from pathlib import Path
from typing import Dict, List

from models.knowledge_models import KnowledgeHealingSuggestion
from utils.json_utils import write_json
from utils.logger import get_logger
from utils.time_utils import utc_now_iso

logger = get_logger(__name__)


class HealingSuggester:
    def generate(self, knowledge, run_id: str, artifact_output_path: str) -> Dict:
        locator_failures = [
            failure for failure in knowledge.failures
            if failure.run_id == run_id and (
                failure.suspected_locator_issue or failure.classification == "locator_failure"
            )
        ]

        suggestions: List[KnowledgeHealingSuggestion] = []
        suggestion_index = 1

        for failure in locator_failures:
            related_locators = sorted(
                knowledge.locators,
                key=lambda item: (item.success_rate, item.stability_score),
                reverse=True,
            )
            for locator in related_locators[:3]:
                candidates = locator.fallback_locators or []
                suggested_locator = ""
                if candidates:
                    top_candidate = candidates[0]
                    suggested_locator = f"{top_candidate.get('locator_type', '')}:{top_candidate.get('locator_value', '')}"
                else:
                    suggested_locator = f"{locator.best_locator.get('locator_type', '')}:{locator.best_locator.get('locator_value', '')}"

                current_locator = f"{locator.best_locator.get('locator_type', '')}:{locator.best_locator.get('locator_value', '')}"
                suggestion = KnowledgeHealingSuggestion(
                    suggestion_id=f"HEAL-{run_id}-{suggestion_index:03d}",
                    run_id=run_id,
                    related_test_name=failure.test_name,
                    target_page=locator.page_name,
                    target_element=locator.element_name,
                    current_locator=current_locator,
                    suggested_locator=suggested_locator,
                    suggestion_type="locator_replacement",
                    confidence=round(min(0.95, 0.5 + locator.success_rate + (locator.stability_score / 2)), 2),
                    reason=(
                        "Generated from locator-related failure using highest-ranked known fallback "
                        "or best known locator candidate."
                    ),
                    status="proposed",
                    created_at=utc_now_iso(),
                    metadata={
                        "failure_classification": failure.classification,
                        "failure_message": failure.message[:500],
                    },
                )
                suggestions.append(suggestion)
                suggestion_index += 1

        payload = {
            "generated_at": utc_now_iso(),
            "run_id": run_id,
            "count": len(suggestions),
            "suggestions": [item.to_dict() for item in suggestions],
        }

        output_path = Path(artifact_output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        write_json(output_path.as_posix(), payload)
        logger.info("Generated %s healing suggestions", len(suggestions))

        return {
            "count": len(suggestions),
            "artifact_path": output_path.as_posix(),
            "suggestions": suggestions,
        }
