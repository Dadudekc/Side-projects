import re
from typing import Dict

import pdfplumber


def extract_fields_from_pdf(file_path: str) -> Dict[str, str]:
    """Simple PDF text extraction with naive field parsing."""
    with pdfplumber.open(file_path) as pdf:
        text = "\n".join(page.extract_text() or "" for page in pdf.pages)

    fields = {}
    invoice_match = re.search(r"Invoice\s*(?:Number|#)\s*[:\-]?\s*(\S+)", text, re.IGNORECASE)
    if invoice_match:
        fields["invoice_number"] = invoice_match.group(1)
    date_match = re.search(r"Date\s*[:\-]?\s*([\d/\-]+)", text, re.IGNORECASE)
    if date_match:
        fields["date"] = date_match.group(1)
    total_match = re.search(r"Total\s*[:\-]?\s*\$?([\d,.]+)", text, re.IGNORECASE)
    if total_match:
        fields["total"] = total_match.group(1)

    return {"raw_text": text, **fields}
