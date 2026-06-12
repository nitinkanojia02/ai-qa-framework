from dataclasses import asdict, dataclass, field
from typing import Dict, List

@dataclass
class TestStep:
    step_number: int
    description: str
    expected_result: str = ""

    def to_dict(self) -> Dict:
        return asdict(self)

@dataclass
class TestCase:
    title: str
    objective: str
    preconditions: List[str] = field(default_factory=list)
    steps: List[TestStep] = field(default_factory=list)
    priority: str = "Medium"
    tags: List[str] = field(default_factory=list)
    source: str = "manual"

    def to_dict(self) -> Dict:
        return {
            "title": self.title,
            "objective": self.objective,
            "preconditions": self.preconditions,
            "steps": [step.to_dict() for step in self.steps],
            "priority": self.priority,
            "tags": self.tags,
            "source": self.source,
        }