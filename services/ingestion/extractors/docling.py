from pathlib import Path
import subprocess


PROJECT_ROOT = Path(__file__).resolve().parents[3]
DOCLING_PYTHON = PROJECT_ROOT / "third_party" / "docling" / ".venv" / "bin" / "python"


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