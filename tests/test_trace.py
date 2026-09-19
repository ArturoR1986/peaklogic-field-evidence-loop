from datetime import datetime, timezone
import json
import numpy as np

from peaklogic_field_evidence.orchestrator import EvidenceLoop
from peaklogic_field_evidence.schemas import ActionType, MediaObservation, MediaType, QualityMetrics
from peaklogic_field_evidence.templates import registry
from peaklogic_field_evidence.trace import TraceRecorder


def fixed_clock():
    return datetime(2026, 9, 19, 12, 0, tzinfo=timezone.utc)


def test_opencv_quality_changes_next_action_and_is_traced(tmp_path):
    t = registry()[0]
    recorder = TraceRecorder(tmp_path / "trace.jsonl", clock=fixed_clock)
    loop = EvidenceLoop(t, recorder=recorder)
    blurred = np.full((600, 800, 3), 120, dtype=np.uint8)

    _, action = loop.process_image(blurred, media_id="blurred-1")

    assert action.action == ActionType.RETAKE
    assert recorder.events[-1].decision["action"] == "retake"
    assert recorder.events[-1].perception["quality"]["usable"] is False
    line = json.loads((tmp_path / "trace.jsonl").read_text().splitlines()[0])
    assert line["decision"]["action"] == "retake"


def test_stage_transition_creates_critical_reminder_trace():
    t = registry()[0]
    recorder = TraceRecorder(clock=fixed_clock)
    loop = EvidenceLoop(t, recorder=recorder)
    action = loop.advance_stage("before_cover")
    assert action.action == ActionType.REMIND_CRITICAL_PROOF
    assert recorder.events[-1].event_type == "stage_transition"


def test_missed_proof_escalates_and_trace_preserves_human_boundary():
    t = registry()[0]
    recorder = TraceRecorder(clock=fixed_clock)
    loop = EvidenceLoop(t, recorder=recorder)
    action = loop.advance_stage("covering_started")
    assert action.action == ActionType.ESCALATE_HUMAN
    assert loop.state.professional_review_status == "pending"


def test_complete_packet_is_review_ready_not_professionally_approved():
    t = registry()[0]
    recorder = TraceRecorder(clock=fixed_clock)
    loop = EvidenceLoop(t, recorder=recorder)
    q = QualityMetrics(100, 120, 800, 600, True)
    for proof in t.proof_points:
        loop.process_observation(MediaObservation(
            media_id=f"m-{proof.id}", media_type=MediaType.PHOTO, quality=q,
            proof_point_label=proof.id, proof_point_confidence=0.99, scene_confidence=0.9,
        ))
    loop.advance_stage("completion")
    packet = loop.review_packet()
    assert packet["evidence_package"]["complete"] is True
    assert packet["professional_review_status"] == "pending"
    assert recorder.events[-1].event_type == "review_packet"


def test_low_confidence_proof_requests_targeted_recapture():
    t = registry()[0]
    recorder = TraceRecorder(clock=fixed_clock)
    loop = EvidenceLoop(t, recorder=recorder)
    q = QualityMetrics(100, 120, 800, 600, True)
    action = loop.process_observation(MediaObservation(
        media_id="uncertain", media_type=MediaType.PHOTO, quality=q,
        proof_point_label="critical_attachment", proof_point_confidence=0.30,
        scene_confidence=0.90,
    ))
    assert action.action == ActionType.REQUEST_TARGETED_PROOF
    assert "critical_attachment" not in loop.state.accepted_proof_points


def test_duplicate_image_does_not_count_as_new_evidence():
    t = registry()[0]
    recorder = TraceRecorder(clock=fixed_clock)
    loop = EvidenceLoop(t, recorder=recorder)
    image = np.zeros((600, 800, 3), dtype=np.uint8)
    image[::2, ::2] = 255
    loop.process_image(
        image, media_id="first", proof_point_label="location_context",
        proof_point_confidence=0.99, scene_confidence=0.9,
    )
    obs2, second = loop.process_image(
        image.copy(), media_id="second", proof_point_label="finished_context",
        proof_point_confidence=0.99, scene_confidence=0.9,
    )
    assert obs2.duplicate_of == "first"
    assert second.action == ActionType.REJECT_DUPLICATE
    assert "finished_context" not in loop.state.accepted_proof_points


def test_stage_transition_ignores_stale_bad_capture_and_evaluates_stage_policy():
    t = registry()[0]
    recorder = TraceRecorder(clock=fixed_clock)
    loop = EvidenceLoop(t, recorder=recorder)
    bad = np.full((600, 800, 3), 120, dtype=np.uint8)
    _, action1 = loop.process_image(bad, media_id="bad")
    assert action1.action == ActionType.RETAKE
    action2 = loop.advance_stage("before_cover")
    assert action2.action == ActionType.REMIND_CRITICAL_PROOF


def test_review_packet_materializes_missed_proof_exception_consistently():
    t = registry()[0]
    recorder = TraceRecorder(clock=fixed_clock)
    loop = EvidenceLoop(t, recorder=recorder)
    loop.state.current_stage = "completion"
    packet = loop.review_packet()
    critical = next(r for r in packet["proof_points"] if r["proof_point_id"] == "critical_attachment")
    assert critical["status"] == "missed_exception"
    assert packet["critical_proof"]["complete"] is False
    assert recorder.events[-1].state["missed_proof_points"]
