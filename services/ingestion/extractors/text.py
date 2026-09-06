from pathlib import Path

from services.contracts.models import Content


def extract_text(file_path: str, object_id: str) -> tuple[Content, str]:
    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    if not path.is_file():
        raise ValueError(f"Not a file: {file_path}")

    text = path.read_text(encoding="utf-8")

    content = Content(
        content_id=f"CONTENT-{object_id}",
        object_id=object_id,
        media_type="text/plain",
    )

    return content, text
