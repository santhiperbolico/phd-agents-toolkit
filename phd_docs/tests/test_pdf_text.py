"""Tests for PDF text extraction."""

from phd_docs.extractors.zotero.pdf_text import extract_pdf_text


def test_extract_pdf_text_returns_empty_for_missing_file(tmp_path):
    missing = tmp_path / "missing.pdf"
    assert extract_pdf_text(missing) == ""
