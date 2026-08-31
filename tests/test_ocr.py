from peaklogic_field_evidence.ocr import extract_key_fields


def test_normalizes_ocr_dash_artifact():
    fields = extract_key_fields("WORK ORDER # A-—101\nTASK: INSTALL SAFETY ANCHOR")
    assert fields["job_id"] == "A-101"
    assert fields["task"] == "INSTALL SAFETY ANCHOR"
