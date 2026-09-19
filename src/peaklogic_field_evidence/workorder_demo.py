from __future__ import annotations

from pathlib import Path

import cv2
import numpy as np

from .document_scan import scan_document
from .ocr import extract_key_fields, extract_text
from .templates import match_template

EXPECTED_TEMPLATE_ID = "fall_protection_anchor_demo_v1"


def generate_demo_work_order() -> np.ndarray:
    """Create a synthetic photographed work order for deterministic mechanics testing."""
    page = np.full((900, 650, 3), 255, dtype=np.uint8)
    lines = [
        ("WORK ORDER # A-101", 90),
        ("SITE: DEMO ROOF", 165),
        ("AREA: ROOF ZONE A", 240),
        ("TASK: INSTALL SAFETY ANCHOR", 315),
    ]
    for text, y in lines:
        cv2.putText(
            page, text, (45, y), cv2.FONT_HERSHEY_SIMPLEX,
            0.85, (0, 0, 0), 2, cv2.LINE_AA,
        )
    cv2.rectangle(page, (20, 20), (630, 880), (0, 0, 0), 3)

    src = np.float32([[0, 0], [649, 0], [649, 899], [0, 899]])
    dst = np.float32([[110, 80], [770, 115], [805, 1040], [70, 980]])
    matrix = cv2.getPerspectiveTransform(src, dst)
    canvas = np.full((1120, 900, 3), 50, dtype=np.uint8)
    warped = cv2.warpPerspective(page, matrix, (900, 1120), borderValue=(50, 50, 50))
    mask = cv2.warpPerspective(np.full((900, 650), 255, dtype=np.uint8), matrix, (900, 1120))
    canvas[mask > 0] = warped[mask > 0]
    return canvas


def run_workorder_demo(output_dir: str | Path, *, lang: str = "eng") -> dict:
    """Run synthetic photo -> OpenCV scan -> OCR -> approved-template matching."""
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    photographed = generate_demo_work_order()
    source_path = output_dir / "work_order_skewed.png"
    cv2.imwrite(str(source_path), photographed)

    scan = scan_document(photographed, min_area_ratio=0.15)
    if not scan.found_document or scan.cleaned is None:
        return {
            "ok": False,
            "stage": "document_scan",
            "reason": "document_not_found",
            "source_path": str(source_path),
            "demo_evidence_type": "synthetic_mechanics_fixture",
        }

    cleaned_path = output_dir / "work_order_cleaned.png"
    cv2.imwrite(str(cleaned_path), scan.cleaned)

    text = extract_text(scan.cleaned, lang=lang)
    fields = extract_key_fields(text)
    template = match_template(fields.get("task", text))
    template_id = template.id if template else None

    return {
        "ok": template_id == EXPECTED_TEMPLATE_ID,
        "found_document": True,
        "ocr_text": text,
        "fields": fields,
        "template_id": template_id,
        "quality_critical": template.quality_critical if template else None,
        "next_action": "load_template" if template else "human_confirm_task_type",
        "source_path": str(source_path),
        "cleaned_path": str(cleaned_path),
        "demo_evidence_type": "synthetic_mechanics_fixture",
        "representative_ocr_accuracy_claimed": False,
    }
