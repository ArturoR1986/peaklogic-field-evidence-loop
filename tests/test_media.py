import numpy as np
import cv2
from peaklogic_field_evidence.media import analyze_quality, is_near_duplicate


def checkerboard(w=640, h=480, cell=24):
    y, x = np.indices((h, w))
    img = (((x // cell + y // cell) % 2) * 255).astype(np.uint8)
    return cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)


def test_quality_accepts_sharp_checkerboard():
    q = analyze_quality(checkerboard())
    assert q.usable
    assert q.sharpness > 45


def test_quality_rejects_blurred_image():
    img = checkerboard()
    blurred = cv2.GaussianBlur(img, (81, 81), 0)
    q = analyze_quality(blurred)
    assert not q.usable
    assert "blurred" in q.reasons


def test_near_duplicate_detection():
    a = checkerboard()
    b = a.copy()
    assert is_near_duplicate(a, b)
