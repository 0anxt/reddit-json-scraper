import json
import os
from pathlib import Path
from typing import Optional

def file_matches_size(path: str, expected_size: Optional[int]) -> bool:
    if expected_size is None:
        return os.path.exists(path)
    try:
        return os.path.getsize(path) == expected_size
    except OSError:
        return False

def should_skip(path: str, expected_size: Optional[int] = None) -> bool:
    return file_matches_size(path, expected_size)

def append_manifest(output_dir: str, record: dict) -> None:
    p = Path(output_dir) / "manifest.json"
    data = []
    if p.exists():
        try:
            data = json.loads(p.read_text())
        except Exception:
            data = []
    data.append(record)
    p.write_text(json.dumps(data, indent=2))
