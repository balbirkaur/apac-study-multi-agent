# tools/document_parser.py

from typing import Union


def extract_text_from_string(text: str) -> str:
    """
    Simple text cleaner (for direct input)
    """
    return text.strip()


def extract_text_from_pdf(file_bytes: bytes) -> str:
    """
    Basic PDF text extraction
    """
    try:
        import PyPDF2
        from io import BytesIO

        reader = PyPDF2.PdfReader(BytesIO(file_bytes))
        text = ""

        for page in reader.pages:
            text += page.extract_text() or ""

        return text.strip()

    except Exception as e:
        return f"Error reading PDF: {str(e)}"