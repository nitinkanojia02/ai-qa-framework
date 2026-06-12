from collections import Counter, deque
from typing import Deque

from utils.logger import get_logger

logger = get_logger(__name__)

class LoopDetector:
    def __init__(self, history_limit: int = 20, repeat_threshold: int = 3) -> None:
        self.history_limit = history_limit
        self.repeat_threshold = repeat_threshold
        self.history: Deque[str] = deque(maxlen=history_limit)

    def record(self, state_key: str) -> None:
        self.history.append(state_key)

    def is_looping(self, state_key: str) -> bool:
        counts = Counter(self.history)
        loop_detected = counts[state_key] >= self.repeat_threshold
        if loop_detected:
            logger.warning("Loop detected for state: %s", state_key)
        return loop_detected