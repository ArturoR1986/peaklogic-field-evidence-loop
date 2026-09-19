from peaklogic_field_evidence.schemas import EvidenceState, QualityMetrics, MediaObservation, MediaType
from peaklogic_field_evidence.templates import registry
from peaklogic_field_evidence.evidence import apply_observation
from peaklogic_field_evidence.report import build_evidence_packet


def test_packet_is_traceable_and_human_owned():
    t = registry()[0]
    state = EvidenceState(template_id=t.id, current_stage="installation")
    obs = MediaObservation(
        media_id="photo-1",
        media_type=MediaType.PHOTO,
        quality=QualityMetrics(90, 120, 800, 600, True),
        proof_point_label="location_context",
        proof_point_confidence=0.91,
        proof_point_source="controlled_input",
        scene_confidence=0.88,
    )
    apply_observation(state, obs)
    packet = build_evidence_packet(state, t)
    row = next(r for r in packet["proof_points"] if r["proof_point_id"] == "location_context")
    assert row["status"] == "accepted"
    assert row["evidence"][0]["media_id"] == "photo-1"
    assert row["evidence"][0]["proof_point_source"] == "controlled_input"
    assert packet["professional_review_status"] == "pending"
    assert packet["professional_review"]["actor"] is None
    assert "not workmanship" in packet["authority_note"]


def test_packet_carries_explicit_human_review_metadata():
    t = registry()[0]
    state = EvidenceState(
        template_id=t.id,
        professional_review_status="needs_follow_up",
        professional_review_actor="reviewer-1",
        professional_review_note="Need torque record.",
    )
    packet = build_evidence_packet(state, t)
    assert packet["professional_review"] == {
        "status": "needs_follow_up",
        "actor": "reviewer-1",
        "note": "Need torque record.",
    }
