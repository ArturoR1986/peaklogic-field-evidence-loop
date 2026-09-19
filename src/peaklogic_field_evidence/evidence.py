from __future__ import annotations

from .schemas import EvidenceState, MediaObservation, ProofTemplate

STAGE_ORDER = {
    "arrival": 0,
    "installation": 1,
    "before_cover": 2,
    "covering_started": 3,
    "completion": 4,
}


def apply_observation(
    state: EvidenceState,
    observation: MediaObservation,
    min_proof_confidence: float = 0.65,
    allowed_proof_points: set[str] | None = None,
) -> EvidenceState:
    state.last_observation = observation
    state.observations.append(observation)
    label_allowed = (
        observation.proof_point_label is not None
        and (allowed_proof_points is None or observation.proof_point_label in allowed_proof_points)
    )
    if (
        observation.quality.usable
        and observation.duplicate_of is None
        and label_allowed
        and (observation.proof_point_confidence or 0.0) >= min_proof_confidence
    ):
        state.accepted_proof_points.add(observation.proof_point_label)
    return state


def update_missed_proof(state: EvidenceState, template: ProofTemplate) -> EvidenceState:
    current_order = STAGE_ORDER.get(state.current_stage, 0)
    for proof in template.proof_points:
        if not proof.critical_before_stage:
            continue
        deadline = STAGE_ORDER.get(proof.critical_before_stage)
        if deadline is None:
            continue
        if current_order >= deadline and proof.id not in state.accepted_proof_points:
            state.missed_proof_points.add(proof.id)
    return state


def required_visual_proofs(template: ProofTemplate) -> set[str]:
    return {p.id for p in template.proof_points if p.required and not p.human_only}
