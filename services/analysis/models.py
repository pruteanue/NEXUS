from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class AnalysisResult:
    analysis_type: str
    path: Path
    size: int | None = None

@dataclass(frozen=True)
class DuplicateGroup:
    files: list[Path]
    size: int