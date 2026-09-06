from dataclasses import dataclass
from datetime import datetime
from typing import Any


@dataclass(frozen=True)
class ContentMetadata:
    title: str | None = None
    language: str | None = None
    author: str | None = None
    page_count: int | None = None
    extra: dict[str, Any] | None = None


@dataclass(frozen=True)
class ContentBlock:
    block_id: str
    content_id: str
    block_type: str
    text: str
    sequence: int
    page: int | None = None
    metadata: dict[str, Any] | None = None


@dataclass(frozen=True)
class UniversalContent:
    content_id: str
    object_id: str
    media_type: str
    extracted_at: datetime
    text: str
    metadata: ContentMetadata
    blocks: tuple[ContentBlock, ...] = ()
