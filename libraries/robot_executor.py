import shutil
import subprocess
from pathlib import Path
from typing import Dict

from libraries.robot_failure_analyzer import RobotFailureAnalyzer
from utils.logger import get_logger
from utils.time_utils import timestamp_slug, utc_now_iso

logger = get_logger(__name__)


class RobotExecutor:
    def __init__(self, artifact_manager) -> None:
        self.artifact_manager = artifact_manager
        self.output_root = Path(self.artifact_manager.get_path("execution")) / "robot_runs"
        self.output_root.mkdir(parents=True, exist_ok=True)
        self.failure_analyzer = RobotFailureAnalyzer()

    def execute_generated_suite(self, suite_path: str) -> Dict[str, str]:
        run_timestamp = timestamp_slug()
        run_dir = self.output_root / f"run_{run_timestamp}"
        run_dir.mkdir(parents=True, exist_ok=True)

        robot_cmd = shutil.which("robot")
        if not robot_cmd:
            logger.warning("Robot Framework CLI not found in PATH; skipping generated suite execution")
            return {
                "status": "skipped",
                "reason": "robot_cli_not_found",
                "run_directory": run_dir.as_posix(),
                "generated_at": utc_now_iso(),
            }

        command = [
            robot_cmd,
            "-d",
            run_dir.as_posix(),
            suite_path,
        ]

        logger.info("Executing generated Robot suite: %s", " ".join(command))
        completed = subprocess.run(command, capture_output=True, text=True)

        output_xml = run_dir / "output.xml"
        log_html = run_dir / "log.html"
        report_html = run_dir / "report.html"
        stdout_path = run_dir / "stdout.txt"
        stderr_path = run_dir / "stderr.txt"
        stdout_path.write_text(completed.stdout or "", encoding="utf-8")
        stderr_path.write_text(completed.stderr or "", encoding="utf-8")

        status = "passed" if completed.returncode == 0 else "failed"
        failure_analysis = self.failure_analyzer.analyze(output_xml.as_posix())
        return {
            "status": status,
            "return_code": str(completed.returncode),
            "suite_path": suite_path,
            "run_directory": run_dir.as_posix(),
            "output_xml": output_xml.as_posix(),
            "log_html": log_html.as_posix(),
            "report_html": report_html.as_posix(),
            "stdout": stdout_path.as_posix(),
            "stderr": stderr_path.as_posix(),
            "failure_analysis": failure_analysis,
            "generated_at": utc_now_iso(),
        }
