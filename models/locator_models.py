from dataclasses import asdict, dataclass, field
from typing import Dict, List

@dataclass
class LocatorCandidate:
    by: str
    value: str
    score: float = 0.0
    strategy: str = ""
    metadata: Dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> Dict:
        return asdict(self)

@dataclass
class LocatorRecord:
    element_name: str
    tag: str
    best_locator: LocatorCandidate
    fallback_locators: List[LocatorCandidate] = field(default_factory=list)
    original_text: str = ""
    original_attributes: Dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> Dict:
        return {
            "element_name": self.element_name,
            "tag": self.tag,
            "best_locator": self.best_locator.to_dict(),
            "fallback_locators": [locator.to_dict() for locator in self.fallback_locators],
            "original_text": self.original_text,
            "original_attributes": self.original_attributes,
        }