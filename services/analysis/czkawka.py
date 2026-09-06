import subprocess
from pathlib import Path

from .models import AnalysisResult, DuplicateGroup


CZKAWKA_CLI = (
    Path(__file__).resolve().parents[2]
    / "third_party"
    / "czkawka"
    / "target"
    / "release"
    / "czkawka_cli"
)

FOUND_RESULTS_EXIT_CODE = 11


def run_czkawka(*args: str) -> str:
    if not CZKAWKA_CLI.is_file():
        raise FileNotFoundError(f"Czkawka CLI not found: {CZKAWKA_CLI}")

    result = subprocess.run(
        [str(CZKAWKA_CLI), *args],
        capture_output=True,
        text=True,
        check=False,
    )

    if result.returncode not in (0, FOUND_RESULTS_EXIT_CODE):
        stderr = result.stderr.strip()
        stdout = result.stdout.strip()
        details = stderr or stdout or "No diagnostic output"

        raise RuntimeError(
            f"Czkawka failed with exit code {result.returncode}: {details}"
        )

    return result.stdout


def _validate_directory(directory: str) -> Path:
    path = Path(directory)

    if not path.exists():
        raise FileNotFoundError(f"Directory not found: {directory}")

    if not path.is_dir():
        raise ValueError(f"Not a directory: {directory}")

    return path


def _parse_file_paths(output: str) -> list[Path]:
    paths: list[Path] = []

    for line in output.splitlines():
        line = line.strip()

        if not line:
            continue

        if line.startswith('"') and line.endswith('"'):
            line = line[1:-1]
        elif not line.startswith("/"):
            continue

        path = Path(line)

        if path.exists():
            paths.append(path)

    return paths


def find_big_files(
    directory: str,
    minimum_count: int = 10,
) -> list[AnalysisResult]:
    path = _validate_directory(directory)

    output = run_czkawka(
        "big",
        "-d",
        str(path),
        "-n",
        str(minimum_count),
    )

    records: list[AnalysisResult] = []

    for line in output.splitlines():
        line = line.strip()

        if " - " not in line:
            continue

        _, file_path = line.split(" - ", 1)
        file_path = file_path.strip()

        if (
            len(file_path) >= 2
            and file_path.startswith('"')
            and file_path.endswith('"')
        ):
            file_path = file_path[1:-1]

        candidate = Path(file_path)

        try:
            size = candidate.stat().st_size
        except OSError:
            continue

        records.append(
            AnalysisResult(
                analysis_type="big",
                path=candidate,
                size=size,
            )
        )

    return records


def find_duplicates(
    directory: str,
    minimum_file_size: int = 1,
) -> list[DuplicateGroup]:
    path = _validate_directory(directory)

    if minimum_file_size < 1:
        raise ValueError("minimum_file_size must be at least 1 byte")

    output = run_czkawka(
        "dup",
        "-d",
        str(path),
        "-m",
        str(minimum_file_size),
    )

    groups: list[DuplicateGroup] = []
    current_files: list[Path] = []
    current_size: int | None = None

    for line in output.splitlines():
        line = line.strip()

        if line.startswith("---- Size ") and " - " in line:
            if current_files:
                groups.append(
                    DuplicateGroup(
                        files=current_files,
                        size=current_size or 0,
                    )
                )

            current_files = []
            current_size = None

            size_part = line[len("---- Size ") :].split(" - ", 1)[0]
            size_text = size_part.rsplit("(", 1)[-1].rstrip(")")

            try:
                current_size = int(size_text)
            except ValueError:
                current_size = 0

            continue

        if line.startswith('"') and line.endswith('"'):
            current_files.append(Path(line[1:-1]))

    if current_files:
        groups.append(
            DuplicateGroup(
                files=current_files,
                size=current_size or 0,
            )
        )

    return groups


def find_empty_files(directory: str) -> list[AnalysisResult]:
    path = _validate_directory(directory)

    output = run_czkawka(
        "empty-files",
        "-d",
        str(path),
    )

    return [
        AnalysisResult(
            analysis_type="empty-file",
            path=file_path,
            size=0,
        )
        for file_path in _parse_file_paths(output)
    ]


def find_empty_folders(directory: str) -> list[AnalysisResult]:
    path = _validate_directory(directory)

    output = run_czkawka(
        "empty-folders",
        "-d",
        str(path),
    )

    return [
        AnalysisResult(
            analysis_type="empty-folder",
            path=folder_path,
        )
        for folder_path in _parse_file_paths(output)
    ]