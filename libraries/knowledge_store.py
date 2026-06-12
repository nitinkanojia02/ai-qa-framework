from pathlib import Path
from typing import Dict, List, Optional

from models.knowledge_models import (
    ApplicationKnowledge,
    KnowledgeElement,
    KnowledgeExecutionRecord,
    KnowledgeFailureRecord,
    KnowledgeHealingSuggestion,
    KnowledgeLocator,
    KnowledgePage,
    KnowledgeWorkflowTransition,
)
from libraries.semantic_enricher import SemanticEnricher
from utils.json_utils import read_json, write_json
from utils.logger import get_logger
from utils.time_utils import timestamp_slug

logger = get_logger(__name__)


class KnowledgeStore:
    def __init__(self, artifact_manager, application_name: str, start_url: str) -> None:
        self.artifact_manager = artifact_manager
        self.knowledge_dir = Path(self.artifact_manager.get_path("knowledge_graph"))
        self.file_path = self.knowledge_dir / "application_knowledge.json"
        self.application_name = application_name
        self.start_url = start_url
        self.semantic_enricher = SemanticEnricher()
        self.knowledge = self._load_or_initialize()

    def _load_or_initialize(self) -> ApplicationKnowledge:
        existing = read_json(self.file_path.as_posix(), default=None)
        if existing:
            logger.info("Loaded existing application knowledge store: %s", self.file_path)
            return ApplicationKnowledge(
                application_name=existing.get("application_name", self.application_name),
                start_url=existing.get("start_url", self.start_url),
                pages=[KnowledgePage(**item) for item in existing.get("pages", [])],
                elements=[KnowledgeElement(**item) for item in existing.get("elements", [])],
                locators=[KnowledgeLocator(**item) for item in existing.get("locators", [])],
                workflow_transitions=[KnowledgeWorkflowTransition(**item) for item in existing.get("workflow_transitions", [])],
                executions=[KnowledgeExecutionRecord(**item) for item in existing.get("executions", [])],
                failures=[KnowledgeFailureRecord(**item) for item in existing.get("failures", [])],
                healing_suggestions=[KnowledgeHealingSuggestion(**item) for item in existing.get("healing_suggestions", [])],
                metadata=existing.get("metadata", {}),
            )

        logger.info("Creating new application knowledge store: %s", self.file_path)
        return ApplicationKnowledge(application_name=self.application_name, start_url=self.start_url)

    def add_page_snapshot(self, page_snapshot) -> None:
        page_analysis = page_snapshot.page_analysis
        page_name = page_analysis.page_name
        semantic_metadata = self.semantic_enricher.enrich_page_analysis(page_analysis)
        page_analysis.metadata.update(semantic_metadata)

        page = self._find_page(page_name, page_analysis.url)
        if page:
            page.title = page_analysis.title
            page.page_type = semantic_metadata.get("semantic_page_type", page.page_type)
            page.business_purpose = semantic_metadata.get("business_purpose", page.business_purpose)
            page.module_name = semantic_metadata.get("module_name", page.module_name)
            page.primary_entity = semantic_metadata.get("primary_entity", page.primary_entity)
            page.metadata.update(page_analysis.metadata)
            page.discovered_at = page.discovered_at or page_snapshot.captured_at
        else:
            page = KnowledgePage(
                page_name=page_name,
                url=page_analysis.url,
                title=page_analysis.title,
                page_type=semantic_metadata.get("semantic_page_type", self._infer_page_type(page_analysis)),
                business_purpose=semantic_metadata.get("business_purpose", ""),
                module_name=semantic_metadata.get("module_name", ""),
                primary_entity=semantic_metadata.get("primary_entity", ""),
                metadata=page_analysis.metadata,
                discovered_at=page_snapshot.captured_at,
            )
            self.knowledge.pages.append(page)

        all_elements = page_analysis.buttons + page_analysis.inputs + page_analysis.links
        for index, element in enumerate(all_elements, start=1):
            element_name = self._derive_element_name(element, index)
            knowledge_element = KnowledgeElement(
                element_name=element_name,
                tag=element.tag,
                page_name=page_name,
                text=element.text,
                semantic_role=element.role,
                intent=self.semantic_enricher.infer_element_intent(element),
                risk_class=self.semantic_enricher.classify_action_risk(element),
                attributes=element.attributes,
                discovered_at=page_snapshot.captured_at,
            )
            self._upsert_element(knowledge_element)

    def add_locator_records(self, page_name: str, locator_records: List) -> None:
        for record in locator_records:
            locator = KnowledgeLocator(
                element_name=record.element_name,
                page_name=page_name,
                best_locator=record.best_locator.to_dict(),
                fallback_locators=[item.to_dict() for item in record.fallback_locators],
                stability_score=record.best_locator.score,
                success_rate=0.0,
            )
            self.knowledge.locators = [
                existing
                for existing in self.knowledge.locators
                if not (existing.element_name == locator.element_name and existing.page_name == locator.page_name)
            ]
            self.knowledge.locators.append(locator)

    def add_workflow_transitions(self, transitions: List[Dict]) -> None:
        for transition in transitions:
            semantic_fields = self.semantic_enricher.infer_transition_semantics(transition)
            combined = {**transition, **semantic_fields}
            workflow_transition = KnowledgeWorkflowTransition(**combined)
            if not self._transition_exists(workflow_transition):
                self.knowledge.workflow_transitions.append(workflow_transition)

    def add_execution_record(self, execution_result, run_id: str) -> None:
        self.knowledge.executions.append(
            KnowledgeExecutionRecord(
                run_id=run_id,
                status=execution_result.status,
                started_at=execution_result.started_at,
                completed_at=execution_result.completed_at,
                executed_steps=execution_result.executed_steps,
                errors=execution_result.errors,
                artifacts=execution_result.artifacts,
                metadata=execution_result.metadata,
            )
        )

    def add_failure_records(self, run_id: str, failure_analysis: Dict) -> None:
        for failure in failure_analysis.get("failed_tests", []):
            record = KnowledgeFailureRecord(
                run_id=run_id,
                test_name=failure.get("test_name", ""),
                classification=failure.get("classification", "execution_failure"),
                message=failure.get("message", ""),
                suspected_locator_issue=failure.get("suspected_locator_issue", False),
                created_at=failure_analysis.get("generated_at", ""),
                metadata={
                    "start_time": failure.get("start_time", ""),
                    "end_time": failure.get("end_time", ""),
                },
            )
            if not self._failure_exists(record):
                self.knowledge.failures.append(record)

    def update_locator_success_metrics(self, failure_analysis: Dict) -> None:
        failure_count = failure_analysis.get("failure_count", 0)
        if not self.knowledge.locators:
            return
        if failure_count == 0:
            for locator in self.knowledge.locators:
                locator.success_rate = min(1.0, locator.success_rate + 0.1)
            return
        for locator in self.knowledge.locators:
            locator.success_rate = max(0.0, locator.success_rate - 0.05)

    def add_healing_suggestions(self, suggestions: List[KnowledgeHealingSuggestion]) -> int:
        added = 0
        for suggestion in suggestions:
            if not self._healing_suggestion_exists(suggestion):
                self.knowledge.healing_suggestions.append(suggestion)
                added += 1
        return added

    def update_healing_suggestion_status(self, suggestion_id: str, status: str, metadata: Optional[Dict[str, str]] = None) -> bool:
        for suggestion in self.knowledge.healing_suggestions:
            if suggestion.suggestion_id == suggestion_id:
                suggestion.status = status
                if status == "applied":
                    suggestion.applied_at = timestamp_slug()
                if metadata:
                    suggestion.metadata.update(metadata)
                return True
        return False

    def persist(self) -> str:
        write_json(self.file_path.as_posix(), self.knowledge.to_dict())

        snapshot_path = self.knowledge_dir / f"application_knowledge_{timestamp_slug()}.json"
        write_json(snapshot_path.as_posix(), self.knowledge.to_dict())
        logger.info("Saved application knowledge store: %s", self.file_path)
        logger.info("Saved application knowledge snapshot: %s", snapshot_path)
        return self.file_path.as_posix()

    def _infer_page_type(self, page_analysis) -> str:
        if page_analysis.forms:
            return "form"
        if page_analysis.inputs and not page_analysis.links:
            return "data_entry"
        if page_analysis.links and not page_analysis.inputs:
            return "navigation"
        return "general"

    def _find_page(self, page_name: str, url: str) -> Optional[KnowledgePage]:
        for page in self.knowledge.pages:
            if page.page_name == page_name and page.url == url:
                return page
        return None

    def _upsert_element(self, knowledge_element: KnowledgeElement) -> None:
        for existing in self.knowledge.elements:
            if existing.element_name == knowledge_element.element_name and existing.page_name == knowledge_element.page_name:
                existing.tag = knowledge_element.tag
                existing.text = knowledge_element.text
                existing.semantic_role = knowledge_element.semantic_role
                existing.intent = knowledge_element.intent
                existing.risk_class = knowledge_element.risk_class
                existing.attributes = knowledge_element.attributes
                existing.discovered_at = existing.discovered_at or knowledge_element.discovered_at
                return
        self.knowledge.elements.append(knowledge_element)

    def _transition_exists(self, transition: KnowledgeWorkflowTransition) -> bool:
        return any(
            existing.action == transition.action
            and existing.target == transition.target
            and existing.source_page == transition.source_page
            and existing.destination_page == transition.destination_page
            and existing.status == transition.status
            for existing in self.knowledge.workflow_transitions
        )

    def _derive_element_name(self, element, index: int) -> str:
        raw_name = (
            element.attributes.get("aria-label")
            or element.name
            or element.element_id
            or element.placeholder
            or element.text
            or f"{element.tag}_{index}"
        )
        normalized = raw_name.strip().lower().replace(" ", "_")
        normalized = "".join(ch if ch.isalnum() or ch in ("_", "-") else "_" for ch in normalized)
        while "__" in normalized:
            normalized = normalized.replace("__", "_")
        return normalized.strip("_") or f"{element.tag}_{index}"

    def _failure_exists(self, record: KnowledgeFailureRecord) -> bool:
        return any(
            existing.run_id == record.run_id
            and existing.test_name == record.test_name
            and existing.classification == record.classification
            and existing.message == record.message
            for existing in self.knowledge.failures
        )

    def _healing_suggestion_exists(self, suggestion: KnowledgeHealingSuggestion) -> bool:
        return any(
            existing.run_id == suggestion.run_id
            and existing.related_test_name == suggestion.related_test_name
            and existing.target_page == suggestion.target_page
            and existing.target_element == suggestion.target_element
            and existing.suggested_locator == suggestion.suggested_locator
            for existing in self.knowledge.healing_suggestions
        )
