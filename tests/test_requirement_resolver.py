import pytest

from peaklogic_field_evidence.requirement_resolver import (
    EvidenceRequirement,
    RequirementEvidenceLink,
    RequirementEvidenceStatus,
    RequirementSet,
    RequirementSource,
    SourceKind,
    VisualCheckability,
    resolve_requirement,
)


def source(excerpt="Photo must show the required visible indicator."):
    return RequirementSource(
        source_id="wo-page-1",
        source_kind=SourceKind.WORK_ORDER,
        document_name="work-order.jpg",
        locator="page 1 highlighted instruction",
        excerpt=excerpt,
    )


def requirement(**kwargs):
    values = dict(
        requirement_id="req-1",
        name="Critical photo evidence",
        requirement_statement="Capture the required visible condition before concealment.",
        source=source(),
        evidence_question="Is the required visible condition recognizable in the evidence?",
        visual_checkability=VisualCheckability.VISUAL,
        capture_before_stage="covering_started",
        expected_capture="close and contextual views",
        visual_limits=("hidden embedment cannot be proven from pixels",),
    )
    values.update(kwargs)
    return EvidenceRequirement(**values)


def test_requirement_rejects_missing_source_excerpt():
    bad = requirement(source=source(excerpt=""))
    with pytest.raises(ValueError, match="source excerpt"):
        bad.validate()


def test_unbound_media_cannot_satisfy_requirement():
    rs = RequirementSet(job_id="job-1")
    rs.add_requirement(requirement())
    with pytest.raises(ValueError, match="not bound"):
        rs.link_evidence(
            RequirementEvidenceLink(
                requirement_id="req-1",
                media_id="photo-1",
                status=RequirementEvidenceStatus.SUPPORTED,
            ),
            bound_media_ids=[],
        )


def test_supported_requirement_continues():
    req = requirement()
    link = RequirementEvidenceLink(
        requirement_id="req-1",
        media_id="photo-1",
        status=RequirementEvidenceStatus.SUPPORTED,
        confidence=0.9,
        observation="Required visible indicator is readable.",
    )
    result = resolve_requirement(req, [link], current_stage="before_cover")
    assert result.status == "supported"
    assert result.next_action.action.value == "continue"


def test_uncertain_requirement_requests_targeted_proof():
    req = requirement()
    link = RequirementEvidenceLink(
        requirement_id="req-1",
        media_id="photo-1",
        status=RequirementEvidenceStatus.UNCERTAIN,
        confidence=0.4,
        observation="Angle is too oblique to judge spacing.",
    )
    result = resolve_requirement(req, [link], current_stage="installation")
    assert result.status == "uncertain"
    assert result.next_action.action.value == "request_targeted_proof"


def test_missing_before_deadline_requests_proof():
    result = resolve_requirement(requirement(), [], current_stage="installation")
    assert result.status == "missing"
    assert result.next_action.action.value == "request_targeted_proof"


def test_missing_after_deadline_escalates_as_missed_opportunity():
    result = resolve_requirement(requirement(), [], current_stage="covering_started")
    assert result.status == "missed_opportunity"
    assert result.next_action.action.value == "escalate_human"


def test_nonvisual_requirement_requires_human_confirmation():
    req = requirement(
        visual_checkability=VisualCheckability.NONVISUAL,
        capture_before_stage=None,
        visual_limits=("actual torque is not visually observable",),
    )
    result = resolve_requirement(req, [], current_stage="installation")
    assert result.status == "human_confirmation_required"
    assert result.next_action.action.value == "escalate_human"
