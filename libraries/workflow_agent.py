from typing import Dict, List

from utils.logger import get_logger

logger = get_logger(__name__)

class WorkflowAgent:
    def __init__(self) -> None:
        logger.info("WorkflowAgent initialized")

    def build_action_candidates(self, locator_records: List) -> List[Dict]:
        candidates = []

        interactive_tags = {
            "button",
            "a",
            "ion-button",
            "ion-fab-button",
            "ion-chip",
            "ion-item",
            "ion-card",
            "ion-menu-button",
            "ion-icon",
        }

        for record in locator_records:
            element_name = (record.element_name or "").lower()
            tag = (record.tag or "").lower()
            original_text = (record.original_text or "").strip().lower()
            attrs = record.original_attributes or {}

            if not self._is_interactive_candidate(tag, element_name, original_text, attrs, interactive_tags):
                continue

            priority = self._derive_priority(element_name, original_text, attrs, tag)

            candidates.append(
                {
                    "element_name": record.element_name,
                    "tag": record.tag,
                    "priority": priority,
                    "text_length_score": len(record.original_text.strip()) if record.original_text else 999,
                    "locator_record": record,
                }
            )

        candidates.sort(key=lambda item: (item["priority"], item["text_length_score"]))
        logger.info("WorkflowAgent built %s exploration candidates", len(candidates))
        return candidates

    def _is_interactive_candidate(
        self,
        tag: str,
        element_name: str,
        original_text: str,
        attrs: Dict,
        interactive_tags: set,
    ) -> bool:
        if tag in interactive_tags:
            return True

        class_name = str(attrs.get("class", "")).lower()
        aria_label = str(attrs.get("aria-label", "")).lower()
        role = str(attrs.get("role", "")).lower()
        name_attr = str(attrs.get("name", "")).lower()

        if "ion-activatable" in class_name:
            return True

        if role in {"button", "link"}:
            return True

        if aria_label or name_attr:
            return True

        if any(keyword in element_name for keyword in ["home", "menu", "notification", "back", "logout", "log_out"]):
            return True

        if any(keyword in original_text for keyword in ["home", "menu", "notification", "back", "logout"]):
            return True

        return False

    def _derive_priority(self, element_name: str, original_text: str, attrs: Dict, tag: str) -> int:
        combined = " ".join(
            [
                element_name or "",
                original_text or "",
                str(attrs.get("aria-label", "") or ""),
                str(attrs.get("name", "") or ""),
                tag or "",
            ]
        ).lower()

        if "log-out" in combined or "logout" in combined or "log out" in combined:
            return 99

        if tag == "ion-icon":
            return 6

        high_priority_keywords = ["menu", "home", "notification", "next", "search", "open", "continue"]
        medium_priority_keywords = ["save", "view", "details", "go", "start", "back"]

        for keyword in high_priority_keywords:
            if keyword in combined:
                return 1

        for keyword in medium_priority_keywords:
            if keyword in combined:
                return 2

        return 5