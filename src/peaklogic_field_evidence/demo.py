from __future__ import annotations

from pathlib import Path
import numpy as np

from .orchestrator import EvidenceLoop
from .schemas import MediaObservation, MediaType, QualityMetrics
from .templates import registry
from .trace import TraceRecorder


def run_trace_demo(trace_path: str | Path) -> dict:
    """Run the bounded midpoint demo with explicit synthetic/operator-controlled labels."""
    trace_path = Path(trace_path)
    if trace_path.exists():
        trace_path.unlink()

    template = registry()[0]
    recorder = TraceRecorder(trace_path)
    loop = EvidenceLoop(template, recorder=recorder)

    blurred = np.full((600, 800, 3), 120, dtype=np.uint8)
    _, bad_action = loop.process_image(blurred, media_id="blurred-arrival")

    corrected = np.zeros((600, 800, 3), dtype=np.uint8)
    corrected[::2, ::2] = 255
    loop.process_image(
        corrected,
        media_id="arrival-retake",
        proof_point_label="location_context",
        proof_point_confidence=0.99,
        scene_confidence=0.95,
    )

    reminder_action = loop.advance_stage("before_cover")

    good_quality = QualityMetrics(120.0, 120.0, 800, 600, True)
    for proof in template.proof_points:
        if proof.id == "location_context":
            continue
        loop.process_observation(
            MediaObservation(
                media_id=f"demo-{proof.id}",
                media_type=MediaType.PHOTO,
                quality=good_quality,
                proof_point_label=proof.id,
                proof_point_confidence=0.99,
                scene_confidence=0.95,
            )
        )

    completion_action = loop.advance_stage("completion")
    packet = loop.review_packet()

    return {
        "first_action": bad_action.action.value,
        "critical_reminder_action": reminder_action.action.value,
        "completion_action": completion_action.action.value,
        "trace_path": str(trace_path),
        "trace_events": len(recorder.events),
        "packet": packet,
        "demo_note": (
            "Proof-point labels are controlled demo inputs until the Gate 2 classifier "
            "is trained and evaluated."
        ),
    }
