import re
from datetime import datetime, timezone

from services.content.models import (
    ContentBlock,
    ContentMetadata,
    UniversalContent,
)


def markdown_to_content(
    *,
    content_id: str,
    object_id: str,
    media_type: str,
    markdown: str,
) -> UniversalContent:
    blocks: list[ContentBlock] = []

    lines = markdown.splitlines()
    sequence = 0
    current: list[str] = []

    def flush() -> None:
        nonlocal sequence

        text = "\n".join(current).strip()
        if not text:
            return

        block_id = f"{content_id}:block:{sequence:06d}"

        blocks.append(
            ContentBlock(
                block_id=block_id,
                content_id=content_id,
                block_type="text",
                text=text,
                sequence=sequence,
            )
        )

        sequence += 1
        current.clear()

    for line in lines:
        if re.match(r"^\s*#{1,6}\s+", line):
            flush()

            blocks.append(
                ContentBlock(
                    block_id=f"{content_id}:block:{sequence:06d}",
                    content_id=content_id,
                    block_type="heading",
                    text=re.sub(r"^\s*#{1,6}\s+", "", line).strip(),
                    sequence=sequence,
                )
            )
            sequence += 1
            continue

        if not line.strip():
            flush()
            continue

        current.append(line)

    flush()

    return UniversalContent(
        content_id=content_id,
        object_id=object_id,
        media_type=media_type,
        extracted_at=datetime.now(timezone.utc),
        text=markdown,
        metadata=ContentMetadata(),
        blocks=tuple(blocks),
    )
