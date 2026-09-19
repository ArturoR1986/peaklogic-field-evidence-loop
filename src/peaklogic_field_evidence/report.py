from __future__ import annotations

from .schemas import EvidenceState, ProofTemplate


def build_evidence_packet(state: EvidenceState, template: ProofTemplate) -> dict:
    proof_rows = []
    for proof in template.proof_points:
        matching = [o for o in state.observations if o.proof_point_label == proof.id and o.quality.usable]
        proof_rows.append(
            {
                "proof_point_id": proof.id,
                "name": proof.name,
                "required": proof.required,
                "critical_before_stage": proof.critical_before_stage,
                "status": "accepted" if proof.id in state.accepted_proof_points else (
                    "missed_exception" if proof.id in state.missed_proof_points else "missing"
                ),
                "evidence": [
                    {
                        "media_id": o.media_id,
                        "media_type": o.media_type.value,
                        "source_timestamp_seconds": o.source_timestamp_seconds,
                        "proof_point_confidence": o.proof_point_confidence,
                        "proof_point_source": o.proof_point_source,
                        "scene_confidence": o.scene_confidence,
                        "perception_error": o.perception_error,
                    }
                    for o in matching
                ],
            }
        )
    required = [p for p in proof_rows if p["required"]]
    accepted_count = sum(1 for p in required if p["status"] == "accepted")
    return {
        "template_id": template.id,
        "template_version": template.version,
        "current_stage": state.current_stage,
        "evidence_package": {
            "accepted_required": accepted_count,
            "required_total": len(required),
            "complete": accepted_count == len(required),
        },
        "critical_proof": {
            "missed": sorted(state.missed_proof_points),
            "complete": not state.missed_proof_points
            and all(
                (not p.critical_before_stage) or p.id in state.accepted_proof_points
                for p in template.proof_points
            ),
        },
        "visual_criteria_status": "not_yet_implemented",
        "professional_review": {
            "status": state.professional_review_status,
            "actor": state.professional_review_actor,
            "note": state.professional_review_note,
        },
        "professional_review_status": state.professional_review_status,
        "proof_points": proof_rows,
        "authority_note": "Evidence readiness is not workmanship, safety, or compliance approval.",
    }
