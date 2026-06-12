import json
from pathlib import Path
from typing import Any

class JsonUtilsError(Exception):
    """Raised when JSON read/write operations fail."""

def read_json(path: str, default: Any = None) -> Any:
    file_path = Path(path)
    if not file_path.exists():
        return default

    try:
        with file_path.open("r", encoding="utf-8") as handle:
            return json.load(handle)
    except json.JSONDecodeError as exc:
        raise JsonUtilsError(f"Invalid JSON in file: {path}") from exc

def write_json(path: str, data: Any, indent: int = 2) -> None:
    file_path = Path(path)
    file_path.parent.mkdir(parents=True, exist_ok=True)
    with file_path.open("w", encoding="utf-8") as handle:
        json.dump(data, handle, indent=indent, ensure_ascii=False)