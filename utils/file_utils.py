from pathlib import Path
from typing import Iterable, List

def ensure_directory(path: str) -> Path:
    directory = Path(path)
    directory.mkdir(parents=True, exist_ok=True)
    return directory

def ensure_directories(paths: Iterable[str]) -> List[Path]:
    return [ensure_directory(path) for path in paths]

def file_exists(path: str) -> bool:
    return Path(path).exists()

def resolve_path(path: str) -> Path:
    return Path(path).expanduser().resolve()

def read_text_file(path: str) -> str:
    return Path(path).read_text(encoding="utf-8")