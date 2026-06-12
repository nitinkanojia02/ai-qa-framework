from dataclasses import asdict, dataclass, field
from typing import Dict, List

@dataclass
class ExecutionResult:
    status: str
    started_at: str
    completed_at: str = ""
    executed_steps: List[Dict] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    artifacts: Dict[str, str] = field(default_factory=dict)
    metadata: Dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> Dict:
        return asdict(self)