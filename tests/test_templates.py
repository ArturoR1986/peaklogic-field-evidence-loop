from peaklogic_field_evidence.templates import match_template


def test_matches_known_anchor_task():
    t = match_template("Install permanent roof fall protection anchor at Area A")
    assert t is not None
    assert t.quality_critical is True


def test_unknown_task_requires_human_mapping():
    assert match_template("Replace office door handle") is None
