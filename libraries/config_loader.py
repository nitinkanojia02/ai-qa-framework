from pathlib import Path
from typing import Any, Dict

from utils.logger import get_logger

logger = get_logger(__name__)

class ConfigLoaderError(Exception):
    """Raised when configuration loading fails."""

class ConfigLoader:
    def __init__(self, config_dir: str = "config") -> None:
        self.config_dir = Path(config_dir)

    def load_yaml(self, file_name: str) -> Dict[str, Any]:
        path = self.config_dir / file_name
        if not path.exists():
            raise ConfigLoaderError(f"Config file not found: {path}")

        try:
            import yaml
        except ImportError as exc:
            raise ConfigLoaderError("PyYAML is required. Install it with: pip install pyyaml") from exc

        with path.open("r", encoding="utf-8") as handle:
            data = yaml.safe_load(handle) or {}
            logger.info("Loaded config file: %s", path)
            return data

    def load_all(self) -> Dict[str, Dict[str, Any]]:
        return {
            "framework": self.load_yaml("framework_config.yaml"),
            "browser": self.load_yaml("browser_config.yaml"),
            "ai": self.load_yaml("ai_config.yaml"),
            "locator": self.load_yaml("locator_config.yaml"),
            "assertion": self.load_yaml("assertion_config.yaml"),
        }