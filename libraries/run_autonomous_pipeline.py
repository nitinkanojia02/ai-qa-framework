from pathlib import Path
from typing import Dict, Optional

from libraries.ai_summary_service import AISummaryService
from libraries.authenticator import Authenticator
from libraries.browser_manager import BrowserManager
from libraries.config_loader import ConfigLoader
from libraries.exploration_analytics import ExplorationAnalytics
from libraries.gains_ai_client import GainsAIClient, GainsAIClientError
from libraries.intelligent_explorer import IntelligentExplorer
from libraries.knowledge_store import KnowledgeStore
from libraries.locator_ranker import LocatorRanker
from libraries.loop_detector import LoopDetector
from libraries.healing_applier import HealingApplier
from libraries.healing_suggester import HealingSuggester
from libraries.manual_test_case_generator import ManualTestCaseGenerator
from libraries.navigation_predictor import NavigationPredictor
from libraries.page_analyzer import PageAnalyzer
from libraries.robot_executor import RobotExecutor
from libraries.robot_test_generator import RobotTestGenerator
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
        self.knowledge_store: Optional[KnowledgeStore] = None
        self.manual_test_case_generator: Optional[ManualTestCaseGenerator] = None
        self.robot_test_generator: Optional[RobotTestGenerator] = None
        self.robot_executor: Optional[RobotExecutor] = None
        self.healing_suggester: Optional[HealingSuggester] = None
        self.healing_applier: Optional[HealingApplier] = None
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
        self.knowledge_store = KnowledgeStore(self.artifact_manager, app_name, start_url)
        self.robot_test_generator = RobotTestGenerator(self.artifact_manager, framework_config)
        self.robot_executor = RobotExecutor(self.artifact_manager)
        self.healing_suggester = HealingSuggester()
        self.healing_applier = HealingApplier()
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
        self.manual_test_case_generator = ManualTestCaseGenerator(self.artifact_manager, ai_client=self.ai_client)

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
                self.knowledge_store.add_page_snapshot(page_snapshot)
                result.executed_steps.append(
                    {
                        "step": "page_analysis",
                        "status": "passed",
                        "page_name": page_snapshot.page_analysis.page_name,
                        "title": page_snapshot.page_analysis.title,
                        "url": page_snapshot.page_analysis.url,
                        "semantic_page_type": page_snapshot.page_analysis.metadata.get("semantic_page_type", ""),
                        "module_name": page_snapshot.page_analysis.metadata.get("module_name", ""),
                        "primary_entity": page_snapshot.page_analysis.metadata.get("primary_entity", ""),
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
                self.knowledge_store.add_locator_records(
                    page_snapshot.page_analysis.page_name,
                    locator_records,
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
                self.knowledge_store.add_workflow_transitions(
                    [step.to_dict() for step in self.workflow_memory.graph.steps]
                )
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

            manual_test_case_artifacts = self.manual_test_case_generator.generate_from_knowledge(
                self.knowledge_store.knowledge
            )
            result.executed_steps.append(
                {
                    "step": "manual_test_case_generation",
                    "status": "passed",
                    "generated_count": manual_test_case_artifacts["count"],
                    "artifact_path": manual_test_case_artifacts["json_path"],
                }
            )
            result.artifacts["manual_test_cases_json"] = manual_test_case_artifacts["json_path"]
            result.artifacts["manual_test_cases_markdown"] = manual_test_case_artifacts["markdown_path"]

            robot_generation_artifacts = {}
            robot_execution_artifacts = {}
            healing_result = {"suggestions": [], "count": 0, "artifact_path": ""}

            if framework_config.get("features", {}).get("enable_robot_generation", False):
                robot_generation_artifacts = self.robot_test_generator.generate_from_manual_test_cases(
                    manual_test_case_artifacts,
                    self.knowledge_store.knowledge,
                )
                result.executed_steps.append(
                    {
                        "step": "robot_test_generation",
                        "status": "passed",
                        "generated_count": robot_generation_artifacts["count"],
                        "suite_path": robot_generation_artifacts["suite_path"],
                        "resource_path": robot_generation_artifacts["resource_path"],
                    }
                )
                result.artifacts["generated_robot_suite"] = robot_generation_artifacts["suite_path"]
                result.artifacts["generated_robot_resource"] = robot_generation_artifacts["resource_path"]
                result.artifacts["generated_robot_variables"] = robot_generation_artifacts.get("variables_path", "")
                result.artifacts["generated_robot_page_resources"] = robot_generation_artifacts.get("page_resource_paths", [])
                result.artifacts["generated_robot_flow_resources"] = robot_generation_artifacts.get("flow_resource_paths", [])
                result.artifacts["generated_robot_modular_suites"] = robot_generation_artifacts.get("suite_paths", [])
            else:
                result.executed_steps.append(
                    {
                        "step": "robot_test_generation",
                        "status": "skipped",
                        "reason": "robot_generation_disabled",
                    }
                )

            if robot_generation_artifacts:
                robot_execution_artifacts = self.robot_executor.execute_generated_suite(
                    robot_generation_artifacts["suite_path"]
                )
                failure_analysis = robot_execution_artifacts.get("failure_analysis", {})
                result.executed_steps.append(
                    {
                        "step": "robot_test_execution",
                        "status": robot_execution_artifacts.get("status", "unknown"),
                        "reason": robot_execution_artifacts.get("reason", ""),
                        "return_code": robot_execution_artifacts.get("return_code", ""),
                        "run_directory": robot_execution_artifacts.get("run_directory", ""),
                        "failure_count": failure_analysis.get("failure_count", 0),
                    }
                )
                for artifact_key in [
                    "run_directory",
                    "output_xml",
                    "log_html",
                    "report_html",
                    "stdout",
                    "stderr",
                ]:
                    if robot_execution_artifacts.get(artifact_key):
                        result.artifacts[f"robot_execution_{artifact_key}"] = robot_execution_artifacts[artifact_key]
                if failure_analysis:
                    result.metadata["robot_failure_count"] = str(failure_analysis.get("failure_count", 0))
                    result.artifacts["robot_failure_analysis"] = failure_analysis
                    self.knowledge_store.add_failure_records(started_at, failure_analysis)
                    self.knowledge_store.update_locator_success_metrics(failure_analysis)
            else:
                result.executed_steps.append(
                    {
                        "step": "robot_test_execution",
                        "status": "skipped",
                        "reason": "robot_generation_not_available",
                    }
                )

            if framework_config.get("features", {}).get("enable_self_healing", True):
                healing_artifact_path = Path(self.artifact_manager.get_path("healing")) / "healing_suggestions.json"
                healing_result = self.healing_suggester.generate(
                    self.knowledge_store.knowledge,
                    started_at,
                    healing_artifact_path.as_posix(),
                )
                added_suggestions = self.knowledge_store.add_healing_suggestions(
                    healing_result["suggestions"]
                )
                result.executed_steps.append(
                    {
                        "step": "healing_suggestion_generation",
                        "status": "passed",
                        "generated_count": healing_result.get("count", 0),
                        "added_to_knowledge": added_suggestions,
                        "artifact_path": healing_result.get("artifact_path", ""),
                    }
                )
                result.artifacts["healing_suggestions"] = healing_result.get("artifact_path", "")
            else:
                result.executed_steps.append(
                    {
                        "step": "healing_suggestion_generation",
                        "status": "skipped",
                        "reason": "self_healing_disabled",
                    }
                )

            if robot_generation_artifacts and healing_result.get("suggestions"):
                healing_apply_result = self.healing_applier.apply_top_suggestion(
                    robot_generation_artifacts["resource_path"],
                    healing_result,
                )
                result.executed_steps.append(
                    {
                        "step": "healing_application",
                        "status": healing_apply_result.get("status", "unknown"),
                        "reason": healing_apply_result.get("reason", ""),
                        "suggestion_id": healing_apply_result.get("suggestion_id", ""),
                        "backup_path": healing_apply_result.get("backup_path", ""),
                    }
                )
                if healing_apply_result.get("suggestion_id"):
                    self.knowledge_store.update_healing_suggestion_status(
                        healing_apply_result["suggestion_id"],
                        "applied" if healing_apply_result.get("applied") else "skipped",
                        {
                            "healing_application_reason": healing_apply_result.get("reason", ""),
                            "backup_path": healing_apply_result.get("backup_path", ""),
                        },
                    )
                result.artifacts["healing_applied_resource"] = healing_apply_result.get("resource_path", "")
                result.artifacts["healing_backup_resource"] = healing_apply_result.get("backup_path", "")

                if healing_apply_result.get("applied"):
                    retry_execution_artifacts = self.robot_executor.execute_generated_suite(
                        robot_generation_artifacts["suite_path"]
                    )
                    retry_failure_analysis = retry_execution_artifacts.get("failure_analysis", {})
                    result.executed_steps.append(
                        {
                            "step": "robot_test_execution_retry",
                            "status": retry_execution_artifacts.get("status", "unknown"),
                            "reason": retry_execution_artifacts.get("reason", ""),
                            "return_code": retry_execution_artifacts.get("return_code", ""),
                            "run_directory": retry_execution_artifacts.get("run_directory", ""),
                            "failure_count": retry_failure_analysis.get("failure_count", 0),
                        }
                    )
                    for artifact_key in [
                        "run_directory",
                        "output_xml",
                        "log_html",
                        "report_html",
                        "stdout",
                        "stderr",
                    ]:
                        if retry_execution_artifacts.get(artifact_key):
                            result.artifacts[f"robot_retry_{artifact_key}"] = retry_execution_artifacts[artifact_key]
                    if retry_failure_analysis:
                        result.artifacts["robot_retry_failure_analysis"] = retry_failure_analysis
                        self.knowledge_store.add_failure_records(f"{started_at}_retry", retry_failure_analysis)
                        self.knowledge_store.update_locator_success_metrics(retry_failure_analysis)
            else:
                result.executed_steps.append(
                    {
                        "step": "healing_application",
                        "status": "skipped",
                        "reason": "no_robot_assets_or_no_healing_suggestions",
                    }
                )

            result.status = "completed"
            result.completed_at = utc_now_iso()
            self.knowledge_store.add_execution_record(result, run_id=started_at)
            knowledge_path = self.knowledge_store.persist()
            result.artifacts["application_knowledge"] = knowledge_path

            execution_output = str(
                Path(self.artifact_manager.get_path("execution")) / "autonomous_pipeline_execution_result.json"
            )
            write_json(execution_output, result.to_dict())
            logger.info("Autonomous pipeline completed successfully")
            return result

        except Exception as exc:
            logger.exception("Pipeline execution failed: %s", exc)
            result.status = "failed"
            result.completed_at = utc_now_iso()
            result.errors.append(str(exc))

            if self.knowledge_store:
                self.knowledge_store.add_execution_record(result, run_id=started_at)
                knowledge_path = self.knowledge_store.persist()
                result.artifacts["application_knowledge"] = knowledge_path

            failure_output = str(
                Path(self.artifact_manager.get_path("execution")) / "autonomous_pipeline_execution_result.json"
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
            try:
                page_summary = self.ai_summary_service.generate_page_summary(page_snapshot)
                result.executed_steps.append(
                    {
                        "step": "ai_page_summary",
                        "status": "passed",
                        "artifact_path": page_summary["artifact_path"],
                    }
                )
                result.artifacts["ai_page_summary"] = page_summary["artifact_path"]
            except GainsAIClientError as exc:
                result.executed_steps.append(
                    {
                        "step": "ai_page_summary",
                        "status": "failed",
                        "error": str(exc),
                    }
                )
                logger.warning("AI page summary failed: %s", exc)

        if workflow_path:
            workflow_graph_dict = read_json(workflow_path, default={}) or {}
            try:
                workflow_summary = self.ai_summary_service.generate_workflow_summary(workflow_graph_dict)
                result.executed_steps.append(
                    {
                        "step": "ai_workflow_summary",
                        "status": "passed",
                        "artifact_path": workflow_summary["artifact_path"],
                    }
                )
                result.artifacts["ai_workflow_summary"] = workflow_summary["artifact_path"]
            except GainsAIClientError as exc:
                result.executed_steps.append(
                    {
                        "step": "ai_workflow_summary",
                        "status": "failed",
                        "error": str(exc),
                    }
                )
                logger.warning("AI workflow summary failed: %s", exc)

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