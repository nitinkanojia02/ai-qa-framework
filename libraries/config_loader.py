import os
import re
from pathlib import Path
from typing import Any, Dict

from utils.logger import get_logger

logger = get_logger(__name__)

ENV_VAR_PATTERN = re.compile(r"^\$\{([A-Z0-9_]+)\}$")


class ConfigLoaderError(Exception):
    """Raised when configuration loading fails."""


class ConfigLoader:
    def __init__(self, config_dir: str = "config") -> None:
        self.config_dir = Path(config_dir)

    def _resolve_env_placeholders(self, value: Any) -> Any:
        if isinstance(value, dict):
            return {key: self._resolve_env_placeholders(val) for key, val in value.items()}
        if isinstance(value, list):
            return [self._resolve_env_placeholders(item) for item in value]
        if isinstance(value, str):
            match = ENV_VAR_PATTERN.match(value.strip())
            if match:
                env_var = match.group(1)
                resolved = os.getenv(env_var)
                if resolved is None:
                    logger.warning("Environment variable %s is not set; keeping placeholder value", env_var)
                    return value
                logger.info("Resolved config value from environment variable: %s", env_var)
                return resolved
        return value

    def _apply_framework_env_overrides(self, data: Dict[str, Any]) -> Dict[str, Any]:
        env_override_map = {
            ("application", "base_url"): "APP_BASE_URL",
            ("application", "environment"): "APP_ENVIRONMENT",
            ("authentication", "login_url"): "APP_LOGIN_URL",
            ("authentication", "username"): "APP_USERNAME",
            ("authentication", "password"): "APP_PASSWORD",
        }

        for path, env_var in env_override_map.items():
            override_value = os.getenv(env_var)
            if not override_value:
                continue

            section = data
            for key in path[:-1]:
                if key not in section or not isinstance(section[key], dict):
                    section[key] = {}
                section = section[key]

            section[path[-1]] = override_value
            logger.info("Applied environment override for %s from %s", ".".join(path), env_var)

        return data

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

        data = self._resolve_env_placeholders(data)
        if file_name == "framework_config.yaml":
            data = self._apply_framework_env_overrides(data)

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
