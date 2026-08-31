import numpy as np
import cv2
from peaklogic_field_evidence.document_scan import scan_document


def synthetic_page():
    canvas = np.full((700, 900, 3), 55, dtype=np.uint8)
    page = np.full((500, 650, 3), 255, dtype=np.uint8)
    cv2.rectangle(page, (20, 20), (630, 480), (0, 0, 0), 3)
    cv2.putText(page, "WORK ORDER # A-101", (55, 90), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0,0,0), 2)
    cv2.putText(page, "TASK: INSTALL SAFETY ANCHOR", (55, 160), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,0,0), 2)
    src = np.float32([[0,0],[649,0],[649,499],[0,499]])
    dst = np.float32([[110,100],[760,65],[800,620],[85,655]])
    m = cv2.getPerspectiveTransform(src, dst)
    warped = cv2.warpPerspective(page, m, (900,700), borderValue=(55,55,55))
    mask = cv2.warpPerspective(np.full((500,650),255,dtype=np.uint8),m,(900,700))
    canvas[mask>0] = warped[mask>0]
    return canvas


def test_detects_and_rectifies_page():
    result = scan_document(synthetic_page(), min_area_ratio=0.15)
    assert result.found_document
    assert result.rectified is not None
    assert result.cleaned is not None
    assert result.cleaned.shape[0] > 300
    assert result.cleaned.shape[1] > 400
