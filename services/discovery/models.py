from dataclasses import dataclass
from datetime import datetime
from pathlib import Path


@dataclass(frozen=True)
class FileRecord:
    path: Path
    name: str
    extension: str
    size: int
    is_hidden: bool
    modified_at: datetime
    is_symlink: bool