from services.ingestion.main import ingest_text_file


def test_ingest_text_file():
    text = ingest_text_file("data/test/test.txt")

    assert text.strip() == "NEXUS este un sistem de cunoaștere multimodală."