from pathlib import Path
from typing import Dict

from utils.json_utils import write_json
from utils.logger import get_logger
from utils.time_utils import timestamp_slug

logger = get_logger(__name__)

class ExplorationAnalytics:
    def __init__(self, artifact_manager) -> None:
        self.artifact_manager = artifact_manager

    def build_summary(
        self,
        candidate_count: int,
        attempted_count: int,
        successful_count: int,
        failed_count: int,
        skipped_count: int,
        workflow_transition_count: int,
    ) -> Dict:
        return {
            "candidate_count": candidate_count,
            "attempted_count": attempted_count,
            "successful_count": successful_count,
            "failed_count": failed_count,
            "skipped_count": skipped_count,
            "workflow_transition_count": workflow_transition_count,
        }

    def persist(self, summary: Dict) -> str:
        analytics_dir = Path(self.artifact_manager.get_path("analytics"))
        output_path = analytics_dir / f"exploration_summary_{timestamp_slug()}.json"
        write_json(output_path.as_posix(), summary)
        logger.info("Saved exploration analytics: %s", output_path)
        return output_path.as_posix()