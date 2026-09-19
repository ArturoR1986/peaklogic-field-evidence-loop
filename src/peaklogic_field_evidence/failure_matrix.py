from __future__ import annotations

from dataclasses import asdict, dataclass
import numpy as np

from .classifier import Classification, ProofPointClassifier
from .orchestrator import EvidenceLoop
from .schemas import ActionType, MediaObservation, MediaType, QualityMetrics
from .templates import registry
from .trace import TracePersistenceError, TraceRecorder


@dataclass(frozen=True)
class FailureCaseResult:
    name: str
    expected: str
    actual: str
    passed: bool
    detail: str = ""

    def to_dict(self) -> dict:
        return asdict(self)


class _FailingClassifier(ProofPointClassifier):
    def predict(self, image):
        raise RuntimeError("simulated classifier outage")


class _FailingRecorder(TraceRecorder):
    def record(self, **kwargs):
        raise TracePersistenceError("simulated trace outage")


def _good_quality() -> QualityMetrics:
    return QualityMetrics(100.0, 120.0, 800, 600, True)


def _checkerboard() -> np.ndarray:
    image = np.zeros((600, 800, 3), dtype=np.uint8)
    image[::2, ::2] = 255
    return image


def _result(name: str, expected: str, actual: str, detail: str = "") -> FailureCaseResult:
    return FailureCaseResult(name, expected, actual, expected == actual, detail)


def run_failure_matrix() -> list[FailureCaseResult]:
    template = registry()[0]
    results: list[FailureCaseResult] = []

    # 1. Blurred capture
    loop = EvidenceLoop(template)
    flat = np.full((600, 800, 3), 120, dtype=np.uint8)
    _, action = loop.process_image(flat, media_id="blurred")
    results.append(_result("blurred_media", ActionType.RETAKE.value, action.action.value))

    # 2. Duplicate evidence
    loop = EvidenceLoop(template)
    image = _checkerboard()
    loop.process_image(
        image,
        media_id="first",
        proof_point_label="location_context",
        proof_point_confidence=0.99,
        scene_confidence=0.90,
    )
    _, action = loop.process_image(
        image.copy(),
        media_id="duplicate",
        proof_point_label="finished_context",
        proof_point_confidence=0.99,
        scene_confidence=0.90,
    )
    results.append(_result("duplicate_evidence", ActionType.REJECT_DUPLICATE.value, action.action.value))

    # 3. Unsupported evidence
    loop = EvidenceLoop(template)
    action = loop.process_observation(MediaObservation(
        media_id="unsupported",
        media_type=MediaType.PHOTO,
        quality=_good_quality(),
        proof_point_label="unsupported",
        proof_point_confidence=0.99,
        proof_point_source="controlled_input",
        scene_confidence=0.90,
    ))
    results.append(_result("unsupported_evidence", ActionType.REQUEST_TARGETED_PROOF.value, action.action.value))

    # 4. Low-confidence classification
    loop = EvidenceLoop(template)
    action = loop.process_observation(MediaObservation(
        media_id="low-confidence",
        media_type=MediaType.PHOTO,
        quality=_good_quality(),
        proof_point_label="critical_attachment",
        proof_point_confidence=0.30,
        proof_point_source="controlled_input",
        scene_confidence=0.90,
    ))
    results.append(_result("low_confidence", ActionType.REQUEST_TARGETED_PROOF.value, action.action.value))

    # 5. Wrong/weak scene association
    loop = EvidenceLoop(template)
    action = loop.process_observation(MediaObservation(
        media_id="wrong-scene",
        media_type=MediaType.PHOTO,
        quality=_good_quality(),
        proof_point_label="critical_attachment",
        proof_point_confidence=0.99,
        proof_point_source="controlled_input",
        scene_confidence=0.10,
    ))
    actual = action.action.value
    if "critical_attachment" in loop.state.accepted_proof_points:
        actual = "unsafe_accepted"
    results.append(_result("weak_scene_association", ActionType.REQUEST_TARGETED_PROOF.value, actual))

    # 6. Missed proof after concealment
    loop = EvidenceLoop(template)
    action = loop.advance_stage("covering_started")
    results.append(_result("missed_proof_after_concealment", ActionType.ESCALATE_HUMAN.value, action.action.value))

    # 7. Classifier unavailable
    loop = EvidenceLoop(template, classifier=_FailingClassifier())
    observation, action = loop.process_image(_checkerboard(), media_id="classifier-down")
    actual = action.action.value
    if not observation.perception_error:
        actual = "missing_error_trace"
    results.append(_result("classifier_unavailable", ActionType.ESCALATE_HUMAN.value, actual))

    # 8. Audit persistence failure must roll back state
    loop = EvidenceLoop(template, recorder=_FailingRecorder())
    before = loop.state.to_dict()
    try:
        loop.process_observation(MediaObservation(
            media_id="trace-fail",
            media_type=MediaType.PHOTO,
            quality=_good_quality(),
            proof_point_label="location_context",
            proof_point_confidence=0.99,
            proof_point_source="controlled_input",
            scene_confidence=0.90,
        ))
        actual = "silent_commit"
    except TracePersistenceError:
        actual = "rolled_back" if loop.state.to_dict() == before else "state_mutated"
    results.append(_result("trace_persistence_failure", "rolled_back", actual))

    # 9. Human authority remains explicit
    loop = EvidenceLoop(template)
    action = loop.record_human_review(
        "needs_follow_up",
        actor="reviewer-demo",
        note="Representative human review event for failure-matrix mechanics.",
    )
    actual = action.action.value
    if loop.state.professional_review_status != "needs_follow_up":
        actual = "review_state_not_recorded"
    results.append(_result("explicit_human_review", ActionType.HUMAN_REVIEW_RECORDED.value, actual))

    return results
