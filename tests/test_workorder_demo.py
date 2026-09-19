from peaklogic_field_evidence.document_scan import scan_document
from peaklogic_field_evidence.workorder_demo import generate_demo_work_order


def test_generated_work_order_is_detected_and_rectified():
    image = generate_demo_work_order()
    result = scan_document(image, min_area_ratio=0.15)
    assert result.found_document is True
    assert result.cleaned is not None
    assert result.rectified is not None
    assert result.cleaned.shape[0] > 500
    assert result.cleaned.shape[1] > 400
