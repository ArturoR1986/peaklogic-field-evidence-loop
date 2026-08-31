from peaklogic_field_evidence.schemas import EvidenceState, QualityMetrics, MediaObservation, MediaType, ActionType
from peaklogic_field_evidence.templates import registry
from peaklogic_field_evidence.evidence import apply_observation
from peaklogic_field_evidence.policy import next_action


def template():
    return registry()[0]


def good_obs(label, conf=0.9, scene=0.9):
    return MediaObservation(
        media_id=f"m-{label}", media_type=MediaType.PHOTO,
        quality=QualityMetrics(100, 120, 800, 600, True),
        proof_point_label=label, proof_point_confidence=conf, scene_confidence=scene,
    )


def test_reminds_before_critical_proof_deadline():
    t = template()
    state = EvidenceState(template_id=t.id, current_stage="before_cover")
    action = next_action(state, t)
    assert action.action == ActionType.REMIND_CRITICAL_PROOF
    assert action.proof_point_id in {"critical_attachment", "process_before_cover"}


def test_missed_critical_proof_escalates_after_covering_started():
    t = template()
    state = EvidenceState(template_id=t.id, current_stage="covering_started")
    action = next_action(state, t)
    assert action.action == ActionType.ESCALATE_HUMAN


def test_unusable_capture_triggers_retake():
    t = template()
    state = EvidenceState(template_id=t.id, current_stage="installation")
    state.last_observation = MediaObservation(
        media_id="bad", media_type=MediaType.PHOTO,
        quality=QualityMetrics(2, 120, 800, 600, False, ("blurred",))
    )
    assert next_action(state, t).action == ActionType.RETAKE


def test_all_required_visual_proofs_prepare_review_packet():
    t = template()
    state = EvidenceState(template_id=t.id, current_stage="completion")
    for proof in t.proof_points:
        apply_observation(state, good_obs(proof.id))
    state.missed_proof_points.clear()
    action = next_action(state, t)
    assert action.action == ActionType.PREPARE_REVIEW_PACKET
