from dataclasses import asdict, dataclass, field
from typing import Dict, List

@dataclass
class WorkflowStep:
    action: str
    target: str
    source_page: str = ""
    destination_page: str = ""
    locator: Dict[str, str] = field(default_factory=dict)
    status: str = "pending"
    metadata: Dict = field(default_factory=dict)

    def to_dict(self) -> Dict:
        return asdict(self)

@dataclass
class WorkflowGraph:
    application_name: str
    start_url: str
    steps: List[WorkflowStep] = field(default_factory=list)
    metadata: Dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> Dict:
        return {
            "application_name": self.application_name,
            "start_url": self.start_url,
            "steps": [step.to_dict() for step in self.steps],
            "metadata": self.metadata,
        }