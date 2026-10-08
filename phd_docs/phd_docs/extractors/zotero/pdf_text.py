"""Extract plain text from PDF files for indexing."""

from pathlib import Path

MAX_PDF_PAGES = 80


def extract_pdf_text(pdf_path: Path, *, max_pages: int = MAX_PDF_PAGES) -> str:
    """
    Extract text from a PDF file using PyMuPDF when available.

    Parameters
    ----------
    pdf_path : Path
        Absolute path to the PDF file.
    max_pages : int, optional
        Maximum number of pages to read from the start of the document.

    Returns
    -------
    str
        Extracted text, or an empty string when extraction is unavailable.
    """
    try:
        import pymupdf
    except ImportError:
        return ""

    if not pdf_path.is_file():
        return ""

    parts: list[str] = []
    with pymupdf.open(pdf_path) as document:
        page_limit = min(len(document), max_pages)
        for page_index in range(page_limit):
            page = document.load_page(page_index)
            text = page.get_text("text").strip()
            if text:
                parts.append(text)
    return "\n\n".join(parts)
