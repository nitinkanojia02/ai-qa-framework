from pathlib import Path
from typing import Dict, Optional

from utils.logger import get_logger
from utils.time_utils import utc_now_iso

logger = get_logger(__name__)


class HealingApplier:
    def apply_top_suggestion(self, resource_path: str, healing_result: Dict) -> Dict:
        suggestions = healing_result.get("suggestions", []) or []
        if not suggestions:
            return {
                "status": "skipped",
                "reason": "no_healing_suggestions",
                "applied": False,
                "generated_at": utc_now_iso(),
            }

        ranked = sorted(suggestions, key=lambda item: getattr(item, "confidence", 0.0), reverse=True)
        suggestion = ranked[0]
        if getattr(suggestion, "confidence", 0.0) < 0.6:
            return {
                "status": "skipped",
                "reason": "low_confidence_suggestion",
                "applied": False,
                "suggestion_id": suggestion.suggestion_id,
                "generated_at": utc_now_iso(),
            }

        resource_file = Path(resource_path)
        if not resource_file.exists():
            return {
                "status": "skipped",
                "reason": "resource_file_not_found",
                "applied": False,
                "suggestion_id": suggestion.suggestion_id,
                "generated_at": utc_now_iso(),
            }

        original_content = resource_file.read_text(encoding="utf-8")
        backup_path = resource_file.with_suffix(resource_file.suffix + ".bak")
        backup_path.write_text(original_content, encoding="utf-8")

        healed_content = self._inject_healing_note(original_content, suggestion)
        resource_file.write_text(healed_content, encoding="utf-8")
        logger.info("Applied healing suggestion %s to %s", suggestion.suggestion_id, resource_file)

        return {
            "status": "applied",
            "applied": True,
            "suggestion_id": suggestion.suggestion_id,
            "resource_path": resource_file.as_posix(),
            "backup_path": backup_path.as_posix(),
            "target_page": suggestion.target_page,
            "target_element": suggestion.target_element,
            "suggested_locator": suggestion.suggested_locator,
            "generated_at": utc_now_iso(),
        }

    def _inject_healing_note(self, content: str, suggestion) -> str:
        note = (
            f"# Healing Applied | suggestion_id={suggestion.suggestion_id} | "
            f"target_page={suggestion.target_page} | target_element={suggestion.target_element} | "
            f"locator={suggestion.suggested_locator}\n"
        )
        if note in content:
            return content
        return note + content
