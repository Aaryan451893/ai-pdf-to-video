# app/modules/pdf_utils.py
from typing import Optional
import re

def _clean_text(s: str) -> str:
    s = s.replace("\x00", " ")
    s = re.sub(r"[ \t]+", " ", s)
    s = re.sub(r"\n\s*\n", "\n\n", s)
    return s.strip()

def extract_text(pdf_path: str) -> str:
    """
    Light-weight text extraction using PyPDF2 (simple and fast).
    If PyPDF2 fails on a specific PDF, switch to pdfminer.six.
    """
    try:
        from PyPDF2 import PdfReader
        reader = PdfReader(pdf_path)
        parts = []
        for page in reader.pages:
            parts.append(page.extract_text() or "")
        text = "\n".join(parts)
        return _clean_text(text)
    except Exception as e:
        # Fallback: pdfminer.six
        try:
            from pdfminer.high_level import extract_text as pdfminer_extract
            text = pdfminer_extract(pdf_path)
            return _clean_text(text)
        except Exception as e2:
            raise RuntimeError(f"Failed to extract text. PyPDF2 error: {e}. pdfminer error: {e2}")
