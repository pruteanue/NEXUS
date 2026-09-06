"""Adaptor Modulul 5: DoclingDocument (ca dict, din export_to_dict) -> UniversalContent.

ATENTIE - de verificat la primul test real: schema exacta a lui
export_to_dict() nu a fost inca confirmata prin rulare (scris fara acces la
Docling instalat). Cheile folosite mai jos (texts/label/text/prov/page_no,
tables/...) reflecta structura documentata a DoclingDocument si notele reale
din Modulul 4 (ex: document.pages e dict cheie=nr. pagina, nu lista) - dar
raman de confirmat exact la primul checkpoint de test cu un PDF din
data/test/. Codul e scris defensiv (.get() cu fallback), ca o eventuala
diferenta de schema sa produca un bloc mai sarac, nu o eroare.
"""
from datetime import datetime, timezone
from typing import Any

from services.content.models import ContentBlock, ContentMetadata, UniversalContent

_LABEL_TO_BLOCK_TYPE = {
    "title": "heading",
    "section_header": "heading",
    "text": "text",
    "paragraph": "text",
    "list_item": "list_item",
    "table": "table",
    "picture": "image",
    "caption": "caption",
    "footnote": "footnote",
    "page_header": "page_header",
    "page_footer": "page_footer",
    "formula": "formula",
    "code": "code",
}


def _page_of(item: dict[str, Any]) -> int | None:
    prov = item.get("prov") or []
    first = prov[0] if isinstance(prov, list) and prov else (prov if isinstance(prov, dict) else None)
    if isinstance(first, dict):
        return first.get("page_no")
    return None


def docling_document_to_content(
    *,
    content_id: str,
    object_id: str,
    media_type: str,
    docling_doc: dict[str, Any],
) -> UniversalContent:
    blocks: list[ContentBlock] = []
    sequence = 0

    for item in docling_doc.get("texts", []) or []:
        text = (item.get("text") or "").strip()
        if not text:
            continue

        label = item.get("label", "text")
        blocks.append(
            ContentBlock(
                block_id=f"{content_id}:block:{sequence:06d}",
                content_id=content_id,
                block_type=_LABEL_TO_BLOCK_TYPE.get(label, "text"),
                text=text,
                sequence=sequence,
                page=_page_of(item),
                metadata={"docling_label": label} if label else None,
            )
        )
        sequence += 1

    for item in docling_doc.get("tables", []) or []:
        # Nu presupunem inca formatul exact al datelor de tabel (grid/cells) -
        # pastram ce gasim ca text/caption, de rafinat dupa primul test real.
        table_text = item.get("text") or item.get("caption") or "[TABLE]"
        blocks.append(
            ContentBlock(
                block_id=f"{content_id}:block:{sequence:06d}",
                content_id=content_id,
                block_type="table",
                text=str(table_text),
                sequence=sequence,
                page=_page_of(item),
                metadata={"raw_table": item.get("data")} if item.get("data") else None,
            )
        )
        sequence += 1

    origin = docling_doc.get("origin") or {}
    pages = docling_doc.get("pages") or {}

    return UniversalContent(
        content_id=content_id,
        object_id=object_id,
        media_type=media_type,
        extracted_at=datetime.now(timezone.utc),
        text="\n\n".join(b.text for b in blocks),
        metadata=ContentMetadata(
            title=origin.get("filename"),
            page_count=(len(pages) or None),
        ),
        blocks=tuple(blocks),
    )
