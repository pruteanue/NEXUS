"""Teste pentru adaptorul Modulul 5: DoclingDocument (dict) -> UniversalContent.

Aceste teste NU au nevoie de Docling instalat si NU apeleaza subprocess-ul
din services/ingestion/extractors/docling.py (extract_pdf_document). Folosesc
un fixture sintetic care imita forma documentata a unui export_to_dict() -
astfel putem rula si valida logica de mapare a adaptorului imediat, fara
`uv sync` in third_party/docling.

Verificarea REALA a schemei exacte intoarse de export_to_dict() ramane de
facut la primul checkpoint cu un PDF real (vezi NEXUS_STATUS.md).
"""
from services.content.adapters.docling import docling_document_to_content


def _sample_docling_doc() -> dict:
    return {
        "origin": {"filename": "curs_criptografie.pdf"},
        "pages": {"1": {}, "2": {}, "3": {}},
        "texts": [
            {"label": "title", "text": "Curs de Criptografie", "prov": [{"page_no": 1}]},
            {"label": "section_header", "text": "1. Introducere", "prov": [{"page_no": 1}]},
            {"label": "text", "text": "Criptografia este stiinta protejarii informatiei.", "prov": [{"page_no": 1}]},
            {"label": "text", "text": "   ", "prov": [{"page_no": 2}]},
            {"label": "list_item", "text": "Confidentialitate", "prov": [{"page_no": 2}]},
            {"label": "footnote", "text": "Sursa: RFC 1234", "prov": [{"page_no": 3}]},
        ],
        "tables": [
            {
                "caption": "Tabel 1 - Algoritmi",
                "prov": [{"page_no": 2}],
                "data": {"grid": [["AES", "simetric"]]},
            },
        ],
    }


def test_docling_document_to_content_maps_blocks_and_pages():
    content = docling_document_to_content(
        content_id="CONTENT-000001",
        object_id="OBJECT-000001",
        media_type="application/pdf",
        docling_doc=_sample_docling_doc(),
    )

    assert content.content_id == "CONTENT-000001"
    assert content.object_id == "OBJECT-000001"
    assert content.metadata.title == "curs_criptografie.pdf"
    assert content.metadata.page_count == 3

    # blocul gol ("   ") trebuie ignorat: 5 din 6 items text + 1 tabel = 6 blocuri
    assert len(content.blocks) == 6

    assert content.blocks[0].block_type == "heading"
    assert content.blocks[0].text == "Curs de Criptografie"
    assert content.blocks[0].page == 1

    assert content.blocks[1].block_type == "heading"
    assert content.blocks[2].block_type == "text"
    assert "Criptografia" in content.blocks[2].text

    list_block = next(b for b in content.blocks if b.block_type == "list_item")
    assert list_block.text == "Confidentialitate"
    assert list_block.page == 2

    footnote_block = next(b for b in content.blocks if b.block_type == "footnote")
    assert footnote_block.page == 3

    table_block = next(b for b in content.blocks if b.block_type == "table")
    assert table_block.text == "Tabel 1 - Algoritmi"
    assert table_block.page == 2
    assert table_block.metadata == {"raw_table": {"grid": [["AES", "simetric"]]}}

    assert "Criptografia" in content.text


def test_docling_document_to_content_handles_missing_fields_gracefully():
    content = docling_document_to_content(
        content_id="CONTENT-000002",
        object_id="OBJECT-000002",
        media_type="application/pdf",
        docling_doc={},
    )

    assert content.blocks == ()
    assert content.text == ""
    assert content.metadata.title is None
    assert content.metadata.page_count is None
