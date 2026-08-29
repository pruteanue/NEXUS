from pathlib import Path


def ingest_text_file(file_path: str) -> str:
    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    if not path.is_file():
        raise ValueError(f"Not a file: {file_path}")

    return path.read_text(encoding="utf-8")


if __name__ == "__main__":
    text = ingest_text_file("data/test/test.txt")
    print("NEXUS Ingestion: OK")
    print(f"Characters read: {len(text)}")
    print(f"Content: {text.strip()}")