from services.ingestion.extractors.text import extract_text


def ingest_text_file(file_path: str, object_id: str = "OBJECT-000001") -> str:
    """Wrapper subtire peste extract_text(), pentru cazuri cand ai nevoie doar
    de textul extras, nu si de obiectul Content asociat. Folosit de
    tests/test_ingestion.py.
    """
    _, text = extract_text(file_path, object_id)
    return text


if __name__ == "__main__":
    content, text = extract_text(
        "data/test/test.txt",
        "OBJECT-000001",
    )

    print("NEXUS Content Extraction: OK")
    print(content)
    print(f"Characters read: {len(text)}")
