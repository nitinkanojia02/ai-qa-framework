from dataclasses import asdict, dataclass, field
from typing import Dict, List


@dataclass
class KnowledgeHealingSuggestion:
    suggestion_id: str
    run_id: str
    related_test_name: str
    target_page: str = ""
    target_element: str = ""
    current_locator: str = ""
    suggested_locator: str = ""
    suggestion_type: str = "locator_replacement"
    confidence: float = 0.0
    reason: str = ""
    status: str = "proposed"
    applied_at: str = ""
    created_at: str = ""
    metadata: Dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class KnowledgePage:
    page_name: str
    url: str
    title: str = ""
    page_type: str = "unknown"
    business_purpose: str = ""
    module_name: str = ""
    primary_entity: str = ""
    metadata: Dict[str, str] = field(default_factory=dict)
    discovered_at: str = ""

    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class KnowledgeElement:
    element_name: str
    tag: str
    page_name: str
    text: str = ""
    semantic_role: str = ""
    intent: str = "generic"
    risk_class: str = "unknown"
    attributes: Dict[str, str] = field(default_factory=dict)
    discovered_at: str = ""

    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class KnowledgeLocator:
    element_name: str
    page_name: str
    best_locator: Dict = field(default_factory=dict)
    fallback_locators: List[Dict] = field(default_factory=list)
    stability_score: float = 0.0
    success_rate: float = 0.0
    discovered_at: str = ""

    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class KnowledgeWorkflowTransition:
    action: str
    target: str
    source_page: str = ""
    destination_page: str = ""
    workflow_type: str = "navigation"
    transition_intent: str = "navigation"
    business_context: str = ""
    status: str = "pending"
    locator: Dict[str, str] = field(default_factory=dict)
    metadata: Dict = field(default_factory=dict)

    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class KnowledgeExecutionRecord:
    run_id: str
    status: str
    started_at: str
    completed_at: str = ""
    executed_steps: List[Dict] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    artifacts: Dict[str, str] = field(default_factory=dict)
    metadata: Dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class KnowledgeFailureRecord:
    run_id: str
    test_name: str
    classification: str
    message: str = ""
    suspected_locator_issue: bool = False
    source: str = "robot_execution"
    created_at: str = ""
    metadata: Dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class ApplicationKnowledge:
    application_name: str
    start_url: str
    pages: List[KnowledgePage] = field(default_factory=list)
    elements: List[KnowledgeElement] = field(default_factory=list)
    locators: List[KnowledgeLocator] = field(default_factory=list)
    workflow_transitions: List[KnowledgeWorkflowTransition] = field(default_factory=list)
    executions: List[KnowledgeExecutionRecord] = field(default_factory=list)
    failures: List[KnowledgeFailureRecord] = field(default_factory=list)
    healing_suggestions: List[KnowledgeHealingSuggestion] = field(default_factory=list)
    metadata: Dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> Dict:
        return {
            "application_name": self.application_name,
            "start_url": self.start_url,
            "pages": [item.to_dict() for item in self.pages],
            "elements": [item.to_dict() for item in self.elements],
            "locators": [item.to_dict() for item in self.locators],
            "workflow_transitions": [item.to_dict() for item in self.workflow_transitions],
            "executions": [item.to_dict() for item in self.executions],
            "failures": [item.to_dict() for item in self.failures],
            "healing_suggestions": [item.to_dict() for item in self.healing_suggestions],
            "metadata": self.metadata,
        }
