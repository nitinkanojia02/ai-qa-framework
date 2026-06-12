import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Dict, List

from utils.logger import get_logger
from utils.time_utils import utc_now_iso

logger = get_logger(__name__)


class RobotFailureAnalyzer:
    def analyze(self, output_xml_path: str) -> Dict:
        path = Path(output_xml_path)
        if not path.exists():
            return {
                "status": "skipped",
                "reason": "output_xml_not_found",
                "generated_at": utc_now_iso(),
                "failed_tests": [],
                "failure_count": 0,
            }

        try:
            root = ET.parse(path).getroot()
        except Exception as exc:
            logger.warning("Unable to parse Robot output XML %s: %s", output_xml_path, exc)
            return {
                "status": "failed",
                "reason": "output_xml_parse_error",
                "error": str(exc),
                "generated_at": utc_now_iso(),
                "failed_tests": [],
                "failure_count": 0,
            }

        failed_tests: List[Dict] = []
        for test in root.iter("test"):
            test_name = test.attrib.get("name", "Unnamed Test")
            status_node = test.find("status")
            if status_node is None:
                continue
            if status_node.attrib.get("status") != "FAIL":
                continue

            failed_tests.append(
                {
                    "test_name": test_name,
                    "message": (status_node.text or "").strip(),
                    "start_time": status_node.attrib.get("starttime", ""),
                    "end_time": status_node.attrib.get("endtime", ""),
                    "classification": self._classify_failure(test_name, status_node.text or ""),
                    "suspected_locator_issue": self._is_locator_issue(status_node.text or ""),
                }
            )

        return {
            "status": "passed",
            "generated_at": utc_now_iso(),
            "failed_tests": failed_tests,
            "failure_count": len(failed_tests),
        }

    def _classify_failure(self, test_name: str, message: str) -> str:
        combined = f"{test_name} {message}".lower()
        if any(token in combined for token in ["locator", "element", "not found", "waiting for element", "no such element"]):
            return "locator_failure"
        if any(token in combined for token in ["timeout", "timed out"]):
            return "timeout_failure"
        if any(token in combined for token in ["assert", "should be", "expected", "mismatch"]):
            return "assertion_failure"
        return "execution_failure"

    def _is_locator_issue(self, message: str) -> bool:
        lowered = message.lower()
        return any(token in lowered for token in ["locator", "element", "not found", "no such element", "waiting for element"])
