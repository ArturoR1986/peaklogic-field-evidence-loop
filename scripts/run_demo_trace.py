from __future__ import annotations

import json
from peaklogic_field_evidence.schemas import (
    EvidenceState, MediaObservation, MediaType, QualityMetrics
)
from peaklogic_field_evidence.templates import registry
from peaklogic_field_evidence.evidence import apply_observation
from peaklogic_field_evidence.policy import next_action
from peaklogic_field_evidence.report import build_evidence_packet


def obs(media_id: str, label: str | None, usable=True, conf=0.90, scene=0.90, reasons=()):
    return MediaObservation(
        media_id=media_id,
        media_type=MediaType.PHOTO,
        quality=QualityMetrics(100 if usable else 3, 120, 800, 600, usable, tuple(reasons)),
        proof_point_label=label,
        proof_point_confidence=conf if label else None,
        scene_confidence=scene if label else None,
    )


def main():
    template = registry()[0]
    state = EvidenceState(template_id=template.id, current_stage="installation")
    trace = []

    state.last_observation = obs("blur-1", None, usable=False, reasons=("blurred",))
    trace.append({"step": "bad capture", "next_action": next_action(state, template).__dict__})

    state.last_observation = None
    state.current_stage = "before_cover"
    trace.append({"step": "critical proof check", "next_action": next_action(state, template).__dict__})

    for proof in template.proof_points:
        apply_observation(state, obs(f"media-{proof.id}", proof.id))

    state.current_stage = "completion"
    action = next_action(state, template)
    trace.append({"step": "completion", "next_action": action.__dict__})

    packet = build_evidence_packet(state, template)
    print(json.dumps({"trace": trace, "packet": packet}, indent=2, default=str))


if __name__ == "__main__":
    main()
