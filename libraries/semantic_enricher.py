from typing import Dict, List

from utils.logger import get_logger

logger = get_logger(__name__)


class SemanticEnricher:
    def __init__(self) -> None:
        logger.info("SemanticEnricher initialized")

    def enrich_page_analysis(self, page_analysis) -> Dict[str, str]:
        page_type = self._infer_page_type(page_analysis)
        business_purpose = self._infer_business_purpose(page_analysis, page_type)
        module_name = self._infer_module_name(page_analysis)
        primary_entity = self._infer_primary_entity(page_analysis)

        semantic_metadata = {
            "semantic_page_type": page_type,
            "business_purpose": business_purpose,
            "module_name": module_name,
            "primary_entity": primary_entity,
            "high_risk_action_count": str(self._count_high_risk_actions(page_analysis)),
        }
        logger.info(
            "Semantic enrichment complete | page=%s | type=%s | module=%s | entity=%s",
            page_analysis.page_name,
            page_type,
            module_name,
            primary_entity,
        )
        return semantic_metadata

    def infer_element_intent(self, element) -> str:
        signal = self._element_signal_text(element)
        if any(word in signal for word in ["login", "sign in", "log in", "authenticate"]):
            return "authentication"
        if any(word in signal for word in ["search", "filter", "find", "lookup"]):
            return "search"
        if any(word in signal for word in ["save", "submit", "create", "add", "register"]):
            return "data_submission"
        if any(word in signal for word in ["edit", "update", "modify"]):
            return "edit"
        if any(word in signal for word in ["delete", "remove", "terminate", "reject"]):
            return "destructive"
        if any(word in signal for word in ["approve", "confirm"]):
            return "approval"
        if any(word in signal for word in ["cancel", "close", "back"]):
            return "navigation_cancel"
        if element.tag in {"input", "textarea", "select", "ion-input", "ion-select"}:
            return "data_entry"
        if element.tag in {"a", "button", "ion-button", "ion-item", "ion-card"}:
            return "navigation_or_action"
        return "generic"

    def classify_action_risk(self, element) -> str:
        signal = self._element_signal_text(element)
        restricted_keywords = ["delete", "remove", "terminate", "reject", "approve", "submit", "pay", "deactivate"]
        caution_keywords = ["save", "update", "edit", "upload", "create", "add"]
        if any(word in signal for word in restricted_keywords):
            return "restricted"
        if any(word in signal for word in caution_keywords):
            return "caution"
        return "safe"

    def infer_transition_semantics(self, transition: Dict) -> Dict[str, str]:
        target = (transition.get("target") or "").replace("_", " ").lower()
        action = (transition.get("action") or "").lower()
        source_page = (transition.get("source_page") or "").lower()
        destination_page = (transition.get("destination_page") or "").lower()

        workflow_type = "navigation"
        if any(word in target for word in ["login", "sign in"]):
            workflow_type = "authentication"
        elif any(word in target for word in ["search", "filter", "find"]):
            workflow_type = "search"
        elif any(word in target for word in ["create", "add", "save", "submit"]):
            workflow_type = "data_entry"
        elif any(word in target for word in ["approve", "reject"]):
            workflow_type = "approval"

        business_context = destination_page or source_page or target
        return {
            "workflow_type": workflow_type,
            "transition_intent": f"{action}_{workflow_type}" if action else workflow_type,
            "business_context": business_context,
        }

    def _infer_page_type(self, page_analysis) -> str:
        title = (page_analysis.title or "").lower()
        page_name = (page_analysis.page_name or "").lower()
        text_signals = f"{title} {page_name}"

        if any(word in text_signals for word in ["login", "sign in", "authentication"]):
            return "authentication"
        if page_analysis.forms and page_analysis.inputs:
            return "form"
        if len(page_analysis.links) >= max(len(page_analysis.inputs), 1) and len(page_analysis.links) >= 5:
            return "navigation_hub"
        if page_analysis.inputs and not page_analysis.buttons:
            return "data_entry"
        if any(word in text_signals for word in ["dashboard", "home", "landing"]):
            return "dashboard"
        return "general"

    def _infer_business_purpose(self, page_analysis, page_type: str) -> str:
        title = (page_analysis.title or page_analysis.page_name or "page").replace("_", " ").strip()
        if page_type == "authentication":
            return "Authenticate user access into the application"
        if page_type == "dashboard":
            return f"Provide summary access and navigation for {title}"
        if page_type == "form":
            return f"Capture or update business data on {title}"
        if page_type == "navigation_hub":
            return f"Allow navigation across business options from {title}"
        if page_type == "data_entry":
            return f"Collect business input on {title}"
        return f"Support business interaction on {title}"

    def _infer_module_name(self, page_analysis) -> str:
        url = (page_analysis.url or "").rstrip("/")
        path_parts = [part for part in url.split("/") if part and not part.startswith("http")]
        if path_parts:
            return path_parts[-1].replace("-", "_")
        return page_analysis.page_name or "unknown_module"

    def _infer_primary_entity(self, page_analysis) -> str:
        candidates: List[str] = []
        for element in page_analysis.inputs + page_analysis.buttons + page_analysis.links:
            signal = self._element_signal_text(element)
            candidates.extend([part for part in signal.replace("/", " ").split() if len(part) > 3])
        if candidates:
            frequency = {}
            for item in candidates:
                frequency[item] = frequency.get(item, 0) + 1
            return sorted(frequency.items(), key=lambda pair: (-pair[1], pair[0]))[0][0]
        return page_analysis.page_name or "entity"

    def _count_high_risk_actions(self, page_analysis) -> int:
        count = 0
        for element in page_analysis.buttons + page_analysis.links:
            if self.classify_action_risk(element) == "restricted":
                count += 1
        return count

    def _element_signal_text(self, element) -> str:
        parts = [
            element.text or "",
            element.name or "",
            element.element_id or "",
            element.placeholder or "",
            element.role or "",
            element.attributes.get("aria-label", "") if getattr(element, "attributes", None) else "",
            element.attributes.get("title", "") if getattr(element, "attributes", None) else "",
        ]
        return " ".join(parts).strip().lower()
