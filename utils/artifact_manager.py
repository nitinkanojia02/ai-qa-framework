from pathlib import Path
from typing import Dict

from utils.file_utils import ensure_directory

class ArtifactManager:
    def __init__(self, base_dir: str = "artifacts") -> None:
        self.base_dir = Path(base_dir)
        self._artifact_dirs: Dict[str, Path] = {
            "page_data": self.base_dir / "page_data",
            "workflow_data": self.base_dir / "workflow_data",
            "ai_testcases": self.base_dir / "ai_testcases",
            "generated_robot_tests": self.base_dir / "generated_robot_tests",
            "locator_intelligence": self.base_dir / "locator_intelligence",
            "assertions": self.base_dir / "assertions",
            "screenshots": self.base_dir / "screenshots",
            "analytics": self.base_dir / "analytics",
            "execution": self.base_dir / "execution",
            "knowledge_graph": self.base_dir / "knowledge_graph",
        }

    def initialize(self) -> Dict[str, str]:
        for path in self._artifact_dirs.values():
            ensure_directory(str(path))
        return {key: str(value) for key, value in self._artifact_dirs.items()}

    def get_path(self, artifact_type: str) -> str:
        if artifact_type not in self._artifact_dirs:
            raise KeyError(f"Unknown artifact type: {artifact_type}")
        ensure_directory(str(self._artifact_dirs[artifact_type]))
        return str(self._artifact_dirs[artifact_type])