from pathlib import Path
from typing import Dict, Optional

from libraries.ai_summary_service import AISummaryService
from libraries.authenticator import Authenticator
from libraries.browser_manager import BrowserManager
from libraries.config_loader import ConfigLoader
from libraries.exploration_analytics import ExplorationAnalytics
from libraries.gains_ai_client import GainsAIClient
from libraries.intelligent_explorer import IntelligentExplorer
from libraries.locator_ranker import LocatorRanker
from libraries.loop_detector import LoopDetector
from libraries.navigation_predictor import NavigationPredictor
from libraries.page_analyzer import PageAnalyzer
from libraries.self_healing_locator import SelfHealingLocator
from libraries.workflow_agent import WorkflowAgent
from libraries.workflow_memory import WorkflowMemory
from models.execution_models import ExecutionResult
from utils.artifact_manager import ArtifactManager
from utils.json_utils import read_json, write_json
from utils.logger import get_logger
from utils.time_utils import utc_now_iso

logger = get_logger(__name__)

class AutonomousPipeline:
    def __init__(self) -> None:
        self.config_loader = ConfigLoader()
        self.artifact_manager = ArtifactManager()
        self.configs: Dict = {}
        self.browser_manager: Optional[BrowserManager] = None
        self.authenticator: Optional[Authenticator] = None
        self.page_analyzer: Optional[PageAnalyzer] = None
        self.locator_ranker: Optional[LocatorRanker] = None
        self.self_healing_locator: Optional[SelfHealingLocator] = None
        self.workflow_memory: Optional[WorkflowMemory] = None
        self.workflow_agent: Optional[WorkflowAgent] = None
        self.navigation_predictor: Optional[NavigationPredictor] = None
        self.loop_detector: Optional[LoopDetector] = None
        self.explorer: Optional[IntelligentExplorer] = None
        self.exploration_analytics: Optional[ExplorationAnalytics] = None
        self.ai_client: Optional[GainsAIClient] = None
        self.ai_summary_service: Optional[AISummaryService] = None

    def initialize(self) -> None:
        logger.info("Initializing autonomous pipeline")
        self.configs = self.config_loader.load_all()
        artifact_dirs = self.artifact_manager.initialize()
        logger.info("Artifact directories ready: %s", artifact_dirs)

        framework_config = self.configs["framework"]
        app_name = framework_config["application"]["name"]
        start_url = framework_config["application"]["base_url"]
        auth_config = framework_config.get("authentication", {})
        max_actions = framework_config.get("execution", {}).get("max_exploration_actions", 5)

        self.browser_manager = BrowserManager(self.configs["browser"])
        self.authenticator = Authenticator(auth_config)
        self.page_analyzer = PageAnalyzer(self.artifact_manager)
        self.locator_ranker = LocatorRanker(self.artifact_manager, self.configs["locator"])
        self.self_healing_locator = SelfHealingLocator()
        self.workflow_memory = WorkflowMemory(self.artifact_manager, app_name, start_url)
        self.workflow_agent = WorkflowAgent()
        self.navigation_predictor = NavigationPredictor()
        self.loop_detector = LoopDetector()
        self.exploration_analytics = ExplorationAnalytics(self.artifact_manager)

        self.explorer = IntelligentExplorer(
            self_healing_locator=self.self_healing_locator,
            workflow_agent=self.workflow_agent,
            navigation_predictor=self.navigation_predictor,
            workflow_memory=self.workflow_memory,
            loop_detector=self.loop_detector,
            max_actions=max_actions,
        )

        self.ai_client = GainsAIClient(self.configs["ai"])
        self.ai_summary_service = AISummaryService(self.ai_client, self.artifact_manager)

    def run(self) -> ExecutionResult:
        started_at = utc_now_iso()
        result = ExecutionResult(status="initialized", started_at=started_at)

        try:
            self.initialize()
            framework_config = self.configs["framework"]
            target_url = framework_config["application"]["base_url"]

            page = self.browser_manager.start()
            self.browser_manager.navigate(target_url)

            initial_screenshot = self._capture_named_screenshot("initial_landing_page.png")
            result.executed_steps.append(
                {
                    "step": "browser_launch_and_navigation",
                    "status": "passed",
                    "url": target_url,
                }
            )
            result.artifacts["initial_screenshot"] = initial_screenshot

            auth_result = self.authenticator.login(page)
            result.executed_steps.append(
                {
                    "step": "authentication",
                    "status": auth_result.get("status", "unknown"),
                    "current_url": auth_result.get("current_url", ""),
                    "title": auth_result.get("title", ""),
                }
            )

            authenticated_screenshot = self._capture_named_screenshot("post_login_page.png")
            result.artifacts["post_login_screenshot"] = authenticated_screenshot
            result.metadata["authenticated_url"] = page.url

            page_snapshot = None
            locator_records = []
            workflow_path = ""
            analytics_path = ""

            if framework_config.get("features", {}).get("enable_page_analysis", True) or \
               framework_config.get("execution", {}).get("analyze_landing_page", True):
                page_snapshot = self.page_analyzer.analyze_page(page)
                result.executed_steps.append(
                    {
                        "step": "page_analysis",
                        "status": "passed",
                        "page_name": page_snapshot.page_analysis.page_name,
                        "title": page_snapshot.page_analysis.title,
                        "url": page_snapshot.page_analysis.url,
                    }
                )
                result.artifacts["page_analysis_dom"] = page_snapshot.dom_path or ""
                result.artifacts["page_analysis_screenshot"] = page_snapshot.screenshot_path or ""

            if page_snapshot:
                locator_records = self.locator_ranker.generate_locator_repository(page_snapshot)
                result.executed_steps.append(
                    {
                        "step": "locator_repository_generation",
                        "status": "passed",
                        "locator_count": len(locator_records),
                    }
                )

            healing_test_result = self._run_self_healing_smoke_check(page, locator_records)
            if healing_test_result:
                result.executed_steps.append(healing_test_result)

            if framework_config.get("features", {}).get("enable_autonomous_exploration", False):
                exploration_result = self.explorer.explore(page, locator_records)

                result.executed_steps.append(
                    {
                        "step": "intelligent_exploration",
                        "status": "passed",
                        "candidate_count": exploration_result["candidate_count"],
                        "attempted_count": exploration_result["attempted_count"],
                        "successful_count": exploration_result["successful_count"],
                        "failed_count": exploration_result["failed_count"],
                        "skipped_count": exploration_result["skipped_count"],
                    }
                )

                workflow_path = self.workflow_memory.persist()
                result.artifacts["workflow_graph"] = workflow_path

                analytics_summary = self.exploration_analytics.build_summary(
                    candidate_count=exploration_result["candidate_count"],
                    attempted_count=exploration_result["attempted_count"],
                    successful_count=exploration_result["successful_count"],
                    failed_count=exploration_result["failed_count"],
                    skipped_count=exploration_result["skipped_count"],
                    workflow_transition_count=self.workflow_memory.get_transition_count(),
                )
                analytics_path = self.exploration_analytics.persist(analytics_summary)
                result.artifacts["exploration_analytics"] = analytics_path

            self._run_ai_summaries(result, page_snapshot, workflow_path)

            result.status = "phase_5_completed"
            result.completed_at = utc_now_iso()

            execution_output = str(
                Path(self.artifact_manager.get_path("execution")) / "phase_5_execution_result.json"
            )
            write_json(execution_output, result.to_dict())
            logger.info("Phase 5 pipeline completed successfully")
            return result

        except Exception as exc:
            logger.exception("Pipeline execution failed: %s", exc)
            result.status = "failed"
            result.completed_at = utc_now_iso()
            result.errors.append(str(exc))

            failure_output = str(
                Path(self.artifact_manager.get_path("execution")) / "phase_5_execution_result.json"
            )
            write_json(failure_output, result.to_dict())
            return result

        finally:
            if self.browser_manager:
                self.browser_manager.close()

    def _run_ai_summaries(self, result: ExecutionResult, page_snapshot, workflow_path: str) -> None:
        if not self.ai_client or not self.ai_client.is_enabled():
            result.executed_steps.append(
                {
                    "step": "ai_summary_generation",
                    "status": "skipped",
                    "reason": "ai_disabled",
                }
            )
            return

        if page_snapshot:
            page_summary = self.ai_summary_service.generate_page_summary(page_snapshot)
            result.executed_steps.append(
                {
                    "step": "ai_page_summary",
                    "status": "passed",
                    "artifact_path": page_summary["artifact_path"],
                }
            )
            result.artifacts["ai_page_summary"] = page_summary["artifact_path"]

        if workflow_path:
            workflow_graph_dict = read_json(workflow_path, default={}) or {}
            workflow_summary = self.ai_summary_service.generate_workflow_summary(workflow_graph_dict)
            result.executed_steps.append(
                {
                    "step": "ai_workflow_summary",
                    "status": "passed",
                    "artifact_path": workflow_summary["artifact_path"],
                }
            )
            result.artifacts["ai_workflow_summary"] = workflow_summary["artifact_path"]

    def _capture_named_screenshot(self, file_name: str) -> str:
        screenshot_dir = self.artifact_manager.get_path("screenshots")
        screenshot_path = str(Path(screenshot_dir) / file_name)
        self.browser_manager.capture_screenshot(screenshot_path)
        return screenshot_path

    def _run_self_healing_smoke_check(self, page, locator_records):
        if not locator_records:
            return {
                "step": "self_healing_smoke_check",
                "status": "skipped",
                "reason": "no_locator_records_available",
            }

        first_record = locator_records[0]

        try:
            element = self.self_healing_locator.find_element(page, first_record)
            if element:
                return {
                    "step": "self_healing_smoke_check",
                    "status": "passed",
                    "element_name": first_record.element_name,
                    "best_locator": first_record.best_locator.to_dict(),
                }
        except Exception as exc:
            logger.warning("Self-healing smoke check failed: %s", exc)
            return {
                "step": "self_healing_smoke_check",
                "status": "failed",
                "element_name": first_record.element_name,
                "error": str(exc),
            }

        return {
            "step": "self_healing_smoke_check",
            "status": "skipped",
            "reason": "unknown_condition",
        }

if __name__ == "__main__":
    pipeline = AutonomousPipeline()
    execution_result = pipeline.run()
    print(execution_result.to_dict())