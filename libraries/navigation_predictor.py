from typing import Dict, List, Optional

from utils.logger import get_logger

logger = get_logger(__name__)

class NavigationPredictor:
    def __init__(self) -> None:
        logger.info("NavigationPredictor initialized")

    def predict_next_action(self, candidates: List[Dict]) -> Optional[Dict]:
        if not candidates:
            return None

        prioritized = sorted(
            candidates,
            key=lambda item: (
                item.get("priority", 999),
                item.get("text_length_score", 999),
            ),
        )
        selected = prioritized[0]
        logger.info("Predicted next action candidate: %s", selected.get("element_name"))
        return selected