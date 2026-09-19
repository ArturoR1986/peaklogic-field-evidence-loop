from __future__ import annotations

from .evidence import STAGE_ORDER, required_visual_proofs, update_missed_proof
from .schemas import ActionType, EvidenceState, NextAction, ProofTemplate


def next_action(state: EvidenceState, template: ProofTemplate) -> NextAction:
    update_missed_proof(state, template)

    if state.missed_proof_points:
        proof_id = sorted(state.missed_proof_points)[0]
        return NextAction(
            ActionType.ESCALATE_HUMAN,
            "A concealment-sensitive proof opportunity has passed without accepted evidence; create an exception rather than inventing proof.",
            proof_id,
        )

    obs = state.last_observation
    if obs is not None:
        allowed = {p.id for p in template.proof_points}
        if not obs.quality.usable:
            return NextAction(
                ActionType.RETAKE,
                f"Latest capture is unusable: {', '.join(obs.quality.reasons)}",
            )
        if obs.duplicate_of:
            return NextAction(
                ActionType.REJECT_DUPLICATE,
                "Latest capture is redundant and does not count as new proof.",
            )
        if obs.perception_error:
            return NextAction(
                ActionType.ESCALATE_HUMAN,
                "Visual perception is unavailable; do not infer proof from this capture.",
            )
        if (
            obs.proof_point_label is None
            or obs.proof_point_label not in allowed
            or (obs.proof_point_confidence or 0.0) < 0.65
        ):
            return NextAction(
                ActionType.REQUEST_TARGETED_PROOF,
                "The evidence cannot be confidently assigned to a required proof point.",
            )
        if obs.scene_confidence is not None and obs.scene_confidence < 0.50:
            return NextAction(
                ActionType.REQUEST_TARGETED_PROOF,
                "Scene association is too weak; request wider context or a targeted recapture.",
            )

    current_order = STAGE_ORDER.get(state.current_stage, 0)
    for proof in template.proof_points:
        if proof.id in state.accepted_proof_points or not proof.critical_before_stage:
            continue
        deadline = STAGE_ORDER.get(proof.critical_before_stage, 999)
        if current_order == deadline - 1:
            return NextAction(
                ActionType.REMIND_CRITICAL_PROOF,
                "Critical proof is still missing before the configured concealment stage.",
                proof.id,
            )

    required = required_visual_proofs(template)
    if required.issubset(state.accepted_proof_points):
        return NextAction(
            ActionType.PREPARE_REVIEW_PACKET,
            "All required visual evidence is accepted; prepare the packet for qualified professional review.",
        )

    return NextAction(
        ActionType.CONTINUE,
        "Evidence workflow is still active; continue normal work and capture required proof at the configured stage.",
    )
