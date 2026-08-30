from services.ingestion.extractors.text import extract_text


if __name__ == "__main__":
    content, text = extract_text(
        "data/test/test.txt",
        "OBJECT-000001",
    )

    print("NEXUS Content Extraction: OK")
    print(content)
    print(f"Characters read: {len(text)}")
