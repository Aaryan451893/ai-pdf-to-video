# app/modules/pdf_utils.py
from typing import Optional
import re

def _clean_text(s: str) -> str:
    s = s.replace("\x00", " ")
    s = re.sub(r"[ \t]+", " ", s)
    s = re.sub(r"\n\s*\n", "\n\n", s)
    return s.strip()

from PyPDF2 import PdfReader

def extract_text_from_pdf(pdf_path: str) -> str:
    """Extracts text from a PDF file and returns as string."""
    reader = PdfReader(pdf_path)
    text = []
    for page in reader.pages:
        text.append(page.extract_text())
    return "\n".join(filter(None, text))
