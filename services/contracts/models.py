from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class Object:
    object_id: str
    object_type: str
    created_at: datetime
    status: str


@dataclass(frozen=True)
class Source:
    source_id: str
    source_type: str
    location: str


@dataclass(frozen=True)
class Content:
    content_id: str
    object_id: str
    media_type: str


@dataclass(frozen=True)
class Segment:
    segment_id: str
    content_id: str
    start: float | None = None
    end: float | None = None
    page: int | None = None


@dataclass(frozen=True)
class Atom:
    atom_id: str
    atom_type: str
    content: str
    source_segment_id: str | None = None


@dataclass(frozen=True)
class Claim:
    claim_id: str
    text: str
    source_atom_id: str | None = None
    confidence: float | None = None


@dataclass(frozen=True)
class Evidence:
    evidence_id: str
    claim_id: str
    source_object_id: str
    reference: str | None = None


@dataclass(frozen=True)
class Artifact:
    artifact_id: str
    artifact_type: str
    source_ids: tuple[str, ...] = ()
    agent_id: str | None = None


@dataclass(frozen=True)
class Event:
    event_id: str
    event_type: str
    timestamp: datetime
    object_id: str | None = None
    payload: dict[str, Any] | None = None


@dataclass(frozen=True)
class Task:
    task_id: str
    task_type: str
    status: str
    object_id: str | None = None


@dataclass(frozen=True)
class Agent:
    agent_id: str
    version: str
    capabilities: tuple[str, ...] = ()
