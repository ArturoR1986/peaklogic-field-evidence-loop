from __future__ import annotations

import re
import unicodedata
import numpy as np
import pytesseract


def extract_text(cleaned_document: np.ndarray, lang: str = "eng") -> str:
    return pytesseract.image_to_string(cleaned_document, lang=lang, config="--psm 6").strip()


def _normalize_field(value: str) -> str:
    value = unicodedata.normalize("NFKC", value).strip()
    value = value.translate(str.maketrans({"—": "-", "–": "-", "−": "-"}))
    value = re.sub(r"-{2,}", "-", value)
    value = re.sub(r"\s+", " ", value)
    return value.strip()


def extract_key_fields(text: str) -> dict[str, str]:
    fields: dict[str, str] = {}
    patterns = {
        "job_id": r"(?im)^\s*(?:job|work\s*order)(?:\s*(?:id|no\.?|#))?\s*[:#-]\s*(.+)$",
        "site": r"(?im)^\s*site\s*[:#-]\s*(.+)$",
        "area": r"(?im)^\s*area\s*[:#-]\s*(.+)$",
        "task": r"(?im)^\s*task\s*[:#-]\s*(.+)$",
    }
    for key, pattern in patterns.items():
        match = re.search(pattern, text)
        if match:
            fields[key] = _normalize_field(match.group(1))
    return fields
