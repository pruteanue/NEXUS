from datetime import datetime, timezone
from pathlib import Path

from .models import FileRecord


def discover_files(directory: str) -> list[FileRecord]:
    path = Path(directory)

    if not path.exists():
        raise FileNotFoundError(f"Directory not found: {directory}")

    if not path.is_dir():
        raise ValueError(f"Not a directory: {directory}")

    records: list[FileRecord] = []

    for item in path.rglob("*"):
        try:
            if not item.is_file():
                continue

            stat = item.stat()

            records.append(
                FileRecord(
                    path=item,
                    name=item.name,
                    extension=item.suffix,
                    size=stat.st_size,
                    is_hidden=item.name.startswith("."),
                    modified_at=datetime.fromtimestamp(
                        stat.st_mtime,
                        tz=timezone.utc,
                    ),
                    is_symlink=item.is_symlink(),
                )
            )
        except OSError:
            continue

    return records