"""Teste unitare pentru cele 11 contracte NEXUS (services/contracts/models.py).

Pentru fiecare contract: constructie valida (inclusiv valorile implicite,
unde exista) si confirmarea imutabilitatii (dataclass frozen=True - orice
incercare de modificare dupa creare trebuie sa ridice FrozenInstanceError).
Nu au nevoie de Docling/LlamaIndex/GPU - doar stdlib + pytest.
"""
import dataclasses
from datetime import datetime, timezone

import pytest

from services.contracts.models import (
    Agent,
    Artifact,
    Atom,
    Claim,
    Content,
    Event,
    Evidence,
    Object,
    Segment,
    Source,
    Task,
)


def _assert_frozen(instance, field_name, value):
    with pytest.raises(dataclasses.FrozenInstanceError):
        setattr(instance, field_name, value)


def test_object_construction_and_immutability():
    obj = Object(
        object_id="OBJECT-000001",
        object_type="file",
        created_at=datetime(2026, 9, 6, tzinfo=timezone.utc),
        status="discovered",
    )
    assert obj.object_id == "OBJECT-000001"
    assert obj.status == "discovered"
    _assert_frozen(obj, "status", "processed")


def test_source_construction_and_immutability():
    src = Source(source_id="SOURCE-000001", source_type="filesystem", location="/data/test/test.txt")
    assert src.location == "/data/test/test.txt"
    _assert_frozen(src, "location", "/alt/path")


def test_content_construction_and_immutability():
    content = Content(content_id="CONTENT-000001", object_id="OBJECT-000001", media_type="text/plain")
    assert content.media_type == "text/plain"
    _assert_frozen(content, "media_type", "application/pdf")


def test_segment_construction_defaults_and_immutability():
    minimal = Segment(segment_id="SEGMENT-000001", content_id="CONTENT-000001")
    assert minimal.start is None and minimal.end is None and minimal.page is None

    full = Segment(segment_id="SEGMENT-000002", content_id="CONTENT-000001", start=0.0, end=12.5, page=3)
    assert full.page == 3
    _assert_frozen(full, "page", 4)


def test_atom_construction_defaults_and_immutability():
    minimal = Atom(atom_id="ATOM-000001", atom_type="paragraph", content="text")
    assert minimal.source_segment_id is None

    full = Atom(atom_id="ATOM-000002", atom_type="paragraph", content="text", source_segment_id="SEGMENT-000001")
    assert full.source_segment_id == "SEGMENT-000001"
    _assert_frozen(full, "content", "alt text")


def test_claim_construction_defaults_and_immutability():
    minimal = Claim(claim_id="CLAIM-000001", text="afirmatie")
    assert minimal.source_atom_id is None and minimal.confidence is None

    full = Claim(claim_id="CLAIM-000002", text="afirmatie", source_atom_id="ATOM-000001", confidence=0.9)
    assert full.confidence == 0.9
    _assert_frozen(full, "confidence", 0.5)


def test_evidence_construction_defaults_and_immutability():
    minimal = Evidence(evidence_id="EVIDENCE-000001", claim_id="CLAIM-000001", source_object_id="OBJECT-000001")
    assert minimal.reference is None

    full = Evidence(
        evidence_id="EVIDENCE-000002",
        claim_id="CLAIM-000001",
        source_object_id="OBJECT-000001",
        reference="pagina 3",
    )
    assert full.reference == "pagina 3"
    _assert_frozen(full, "reference", "alta pagina")


def test_artifact_construction_defaults_and_immutability():
    minimal = Artifact(artifact_id="ARTIFACT-000001", artifact_type="report")
    assert minimal.source_ids == () and minimal.agent_id is None

    full = Artifact(
        artifact_id="ARTIFACT-000002",
        artifact_type="report",
        source_ids=("OBJECT-000001", "OBJECT-000002"),
        agent_id="AGENT-000001",
    )
    assert full.source_ids == ("OBJECT-000001", "OBJECT-000002")
    _assert_frozen(full, "agent_id", "AGENT-000002")


def test_event_construction_defaults_and_immutability():
    ts = datetime(2026, 9, 6, tzinfo=timezone.utc)
    minimal = Event(event_id="EVENT-000001", event_type="ingested", timestamp=ts)
    assert minimal.object_id is None and minimal.payload is None

    full = Event(
        event_id="EVENT-000002",
        event_type="ingested",
        timestamp=ts,
        object_id="OBJECT-000001",
        payload={"source": "scanner"},
    )
    assert full.payload == {"source": "scanner"}
    _assert_frozen(full, "event_type", "processed")


def test_task_construction_defaults_and_immutability():
    minimal = Task(task_id="TASK-000001", task_type="scan", status="pending")
    assert minimal.object_id is None

    full = Task(task_id="TASK-000002", task_type="scan", status="pending", object_id="OBJECT-000001")
    assert full.object_id == "OBJECT-000001"
    _assert_frozen(full, "status", "done")


def test_agent_construction_defaults_and_immutability():
    minimal = Agent(agent_id="AGENT-000001", version="1.0.0")
    assert minimal.capabilities == ()

    full = Agent(agent_id="AGENT-000002", version="1.0.0", capabilities=("ocr", "chunking"))
    assert full.capabilities == ("ocr", "chunking")
    _assert_frozen(full, "version", "2.0.0")
