import os
from pathlib import Path
import json
import subprocess


PROJECT_ROOT = Path(__file__).resolve().parents[3]
# Implicit: venv-ul Docling langa cod (comportament neschimbat).
# Supapa: NEXUS_DOCLING_PYTHON, pentru cazuri unde venv-ul nu poate fi creat
# langa cod (ex: WSL2 nu poate crea symlink-uri pe un disc Windows montat sub
# /mnt/...) - venv-ul e atunci pus pe filesystem nativ Linux, in alta parte.
DOCLING_PYTHON = Path(
    os.environ.get("NEXUS_DOCLING_PYTHON")
    or (PROJECT_ROOT / "third_party" / "docling" / ".venv" / "bin" / "python")
)


def extract_pdf(file_path: str) -> str:
    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    if not path.is_file():
        raise ValueError(f"Not a file: {file_path}")

    if not DOCLING_PYTHON.exists():
        raise RuntimeError(f"Docling runtime not found: {DOCLING_PYTHON}")

    script = """
from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import PdfPipelineOptions, RapidOcrOptions
from docling.document_converter import DocumentConverter, PdfFormatOption
import sys

pipeline_options = PdfPipelineOptions()
pipeline_options.do_ocr = True
pipeline_options.ocr_options = RapidOcrOptions()

converter = DocumentConverter(
    format_options={
        InputFormat.PDF: PdfFormatOption(
            pipeline_options=pipeline_options
        )
    }
)

result = converter.convert(sys.argv[1])
print(result.document.export_to_markdown())
"""

    result = subprocess.run(
        [str(DOCLING_PYTHON), "-c", script, str(path)],
        capture_output=True,
        text=True,
        check=True,
    )

    return result.stdout


def extract_pdf_document(file_path: str) -> dict:
    """Ca extract_pdf(), dar returneaza structura DoclingDocument completa (dict),
    nu markdown-ul rezultat din ea.

    Foloseste export_to_dict() daca exista pe obiectul rezultat de Docling, cu
    fallback la model_dump() (DoclingDocument e un model Pydantic) - astfel
    functioneaza indiferent de varianta exacta de API expusa de versiunea
    Docling instalata in third_party/docling/.venv.

    Rezultatul e consumat de services/content/adapters/docling.py
    (docling_document_to_content) pentru Modulul 5 - Universal Content Model.
    """
    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    if not path.is_file():
        raise ValueError(f"Not a file: {file_path}")

    if not DOCLING_PYTHON.exists():
        raise RuntimeError(f"Docling runtime not found: {DOCLING_PYTHON}")

    script = """
from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import PdfPipelineOptions, RapidOcrOptions
from docling.document_converter import DocumentConverter, PdfFormatOption
import json
import sys

pipeline_options = PdfPipelineOptions()
pipeline_options.do_ocr = True
pipeline_options.ocr_options = RapidOcrOptions()

converter = DocumentConverter(
    format_options={
        InputFormat.PDF: PdfFormatOption(
            pipeline_options=pipeline_options
        )
    }
)

result = converter.convert(sys.argv[1])
doc = result.document

if hasattr(doc, "export_to_dict"):
    data = doc.export_to_dict()
elif hasattr(doc, "model_dump"):
    data = doc.model_dump(mode="json")
else:
    raise RuntimeError("DoclingDocument nu expune export_to_dict() sau model_dump()")

print(json.dumps(data))
"""

    result = subprocess.run(
        [str(DOCLING_PYTHON), "-c", script, str(path)],
        capture_output=True,
        text=True,
        check=True,
    )

    return json.loads(result.stdout)
