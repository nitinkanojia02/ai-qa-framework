from pathlib import Path
from typing import Dict, List

from models.workflow_models import WorkflowGraph, WorkflowStep
from utils.json_utils import write_json
from utils.logger import get_logger
from utils.time_utils import timestamp_slug

logger = get_logger(__name__)

class WorkflowMemory:
    def __init__(self, artifact_manager, application_name: str, start_url: str) -> None:
        self.artifact_manager = artifact_manager
        self.graph = WorkflowGraph(application_name=application_name, start_url=start_url)
        self.visited_states = set()

    def add_transition(
        self,
        action: str,
        target: str,
        source_page: str,
        destination_page: str,
        locator: Dict[str, str],
        status: str = "passed",
        metadata: Dict = None,
    ) -> None:
        step = WorkflowStep(
            action=action,
            target=target,
            source_page=source_page,
            destination_page=destination_page,
            locator=locator,
            status=status,
            metadata=metadata or {},
        )
        self.graph.steps.append(step)
        logger.info(
            "Recorded workflow transition | action=%s | target=%s | source=%s | destination=%s | status=%s",
            action,
            target,
            source_page,
            destination_page,
            status,
        )

    def mark_state_visited(self, state_key: str) -> None:
        self.visited_states.add(state_key)

    def has_state_been_visited(self, state_key: str) -> bool:
        return state_key in self.visited_states

    def persist(self) -> str:
        workflow_dir = Path(self.artifact_manager.get_path("workflow_data"))
        output_path = workflow_dir / f"workflow_graph_{timestamp_slug()}.json"
        write_json(output_path.as_posix(), self.graph.to_dict())
        logger.info("Saved workflow graph: %s", output_path)
        return output_path.as_posix()

    def get_transition_count(self) -> int:
        return len(self.graph.steps)

    def get_failed_transitions(self) -> List[Dict]:
        return [step.to_dict() for step in self.graph.steps if step.status != "passed"]