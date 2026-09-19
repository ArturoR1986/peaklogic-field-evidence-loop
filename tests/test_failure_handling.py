import numpy as np
import pytest

from peaklogic_field_evidence.classifier import ProofPointClassifier
from peaklogic_field_evidence.failure_matrix import run_failure_matrix
from peaklogic_field_evidence.orchestrator import EvidenceLoop
from peaklogic_field_evidence.schemas import ActionType, MediaObservation, MediaType, QualityMetrics
from peaklogic_field_evidence.templates import registry
from peaklogic_field_evidence.trace import TracePersistenceError, TraceRecorder


class FailingClassifier(ProofPointClassifier):
    def predict(self, image):
        raise RuntimeError("offline")


class FailingRecorder(TraceRecorder):
    def record(self, **kwargs):
        raise TracePersistenceError("offline")


def q():
    return QualityMetrics(100, 120, 800, 600, True)


def checkerboard():
    image = np.zeros((600, 800, 3), dtype=np.uint8)
    image[::2, ::2] = 255
    return image


def test_weak_scene_does_not_enter_accepted_proofs():
    t = registry()[0]
    loop = EvidenceLoop(t)
    action = loop.process_observation(MediaObservation(
        media_id="wrong-scene", media_type=MediaType.PHOTO, quality=q(),
        proof_point_label="critical_attachment", proof_point_confidence=0.99,
        proof_point_source="controlled_input", scene_confidence=0.10,
    ))
    assert action.action == ActionType.REQUEST_TARGETED_PROOF
    assert "critical_attachment" not in loop.state.accepted_proof_points


def test_classifier_failure_escalates_and_is_traced():
    t = registry()[0]
    loop = EvidenceLoop(t, classifier=FailingClassifier())
    obs, action = loop.process_image(checkerboard(), media_id="classifier-down")
    assert action.action == ActionType.ESCALATE_HUMAN
    assert obs.perception_error == "classifier_failure:RuntimeError"
    assert loop.recorder.events[-1].perception["perception_error"] == "classifier_failure:RuntimeError"
    assert not loop.state.accepted_proof_points


def test_trace_failure_rolls_back_observation_state():
    t = registry()[0]
    loop = EvidenceLoop(t, recorder=FailingRecorder())
    before = loop.state.to_dict()
    with pytest.raises(TracePersistenceError):
        loop.process_observation(MediaObservation(
            media_id="proof", media_type=MediaType.PHOTO, quality=q(),
            proof_point_label="location_context", proof_point_confidence=0.99,
            proof_point_source="controlled_input", scene_confidence=0.90,
        ))
    assert loop.state.to_dict() == before


def test_trace_failure_rolls_back_stage_transition():
    t = registry()[0]
    loop = EvidenceLoop(t, recorder=FailingRecorder())
    with pytest.raises(TracePersistenceError):
        loop.advance_stage("before_cover")
    assert loop.state.current_stage == "arrival"
    assert not loop.state.missed_proof_points


def test_human_review_is_explicit_and_audited():
    t = registry()[0]
    loop = EvidenceLoop(t)
    action = loop.record_human_review(
        "needs_follow_up",
        actor="qualified-reviewer",
        note="Needs additional non-visual confirmation.",
    )
    assert action.action == ActionType.HUMAN_REVIEW_RECORDED
    assert loop.state.professional_review_status == "needs_follow_up"
    assert loop.state.professional_review_actor == "qualified-reviewer"
    assert loop.recorder.events[-1].event_type == "human_review"


def test_incomplete_approval_requires_explicit_note():
    t = registry()[0]
    loop = EvidenceLoop(t)
    with pytest.raises(ValueError):
        loop.record_human_review("approved", actor="qualified-reviewer")


def test_failure_matrix_all_cases_pass():
    results = run_failure_matrix()
    assert results
    assert all(r.passed for r in results)
