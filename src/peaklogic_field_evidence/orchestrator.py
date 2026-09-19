from __future__ import annotations

from copy import deepcopy
from pathlib import Path
import cv2
import numpy as np

from .classifier import ProofPointClassifier
from .evidence import STAGE_ORDER, apply_observation
from .media import analyze_quality, average_hash, hamming_distance
from .policy import next_action
from .report import build_evidence_packet
from .schemas import ActionType, EvidenceState, MediaObservation, MediaType, NextAction, ProofTemplate
from .trace import TracePersistenceError, TraceRecorder

HUMAN_REVIEW_STATUSES = {"approved", "rejected", "needs_follow_up"}


class EvidenceLoop:
    """Smallest executable Agentic Vision orchestration loop."""

    def __init__(
        self,
        template: ProofTemplate,
        *,
        state: EvidenceState | None = None,
        recorder: TraceRecorder | None = None,
        classifier: ProofPointClassifier | None = None,
        duplicate_hamming: int = 14,
    ) -> None:
        self.template = template
        self.state = state or EvidenceState(template_id=template.id)
        self.recorder = recorder or TraceRecorder()
        self.classifier = classifier
        self.duplicate_hamming = duplicate_hamming
        self._image_hashes: dict[str, np.ndarray] = {}
        self._allowed_proof_points = {p.id for p in template.proof_points}

    def _snapshot_state(self) -> EvidenceState:
        return deepcopy(self.state)

    def _restore_state(self, snapshot: EvidenceState) -> None:
        self.state.__dict__.clear()
        self.state.__dict__.update(deepcopy(snapshot.__dict__))

    def _find_duplicate(self, bits: np.ndarray) -> str | None:
        for media_id, prior_bits in self._image_hashes.items():
            if hamming_distance(bits, prior_bits) <= self.duplicate_hamming:
                return media_id
        return None

    def process_image(
        self,
        image: np.ndarray,
        *,
        media_id: str,
        proof_point_label: str | None = None,
        proof_point_confidence: float | None = None,
        proof_point_source: str | None = None,
        scene_confidence: float | None = None,
        media_type: MediaType = MediaType.PHOTO,
        source_timestamp_seconds: float | None = None,
    ) -> tuple[MediaObservation, NextAction]:
        snapshot = self._snapshot_state()
        stage_before = self.state.current_stage
        quality = analyze_quality(image)
        duplicate_of = None
        bits = None
        if image is not None and image.size:
            bits = average_hash(image)
            duplicate_of = self._find_duplicate(bits)

        if proof_point_label is not None and proof_point_source is None:
            proof_point_source = "controlled_input"

        perception_error = None
        if (
            quality.usable
            and duplicate_of is None
            and proof_point_label is None
            and self.classifier is not None
        ):
            try:
                classification = self.classifier.predict(image)
                proof_point_label = classification.label
                proof_point_confidence = classification.confidence
                proof_point_source = classification.source
            except Exception as exc:  # model/tool failure becomes an auditable safe escalation
                proof_point_label = None
                proof_point_confidence = None
                proof_point_source = "opencv_dnn"
                perception_error = f"classifier_failure:{type(exc).__name__}"

        observation = MediaObservation(
            media_id=media_id,
            media_type=media_type,
            quality=quality,
            source_timestamp_seconds=source_timestamp_seconds,
            duplicate_of=duplicate_of,
            proof_point_label=proof_point_label,
            proof_point_confidence=proof_point_confidence,
            proof_point_source=proof_point_source,
            scene_confidence=scene_confidence,
            perception_error=perception_error,
        )
        apply_observation(
            self.state,
            observation,
            allowed_proof_points=self._allowed_proof_points,
        )
        action = next_action(self.state, self.template)
        try:
            self.recorder.record(
                event_type="media_observation",
                template_id=self.template.id,
                stage_before=stage_before,
                stage_after=self.state.current_stage,
                state=self.state,
                action=action,
                observation=observation,
            )
        except TracePersistenceError:
            self._restore_state(snapshot)
            raise

        if bits is not None and duplicate_of is None and quality.usable:
            self._image_hashes[media_id] = bits
        return observation, action

    def process_image_path(self, path: str | Path, **kwargs) -> tuple[MediaObservation, NextAction]:
        image = cv2.imread(str(path))
        if image is None:
            raise ValueError(f"Could not read image: {path}")
        return self.process_image(image, **kwargs)

    def process_observation(self, observation: MediaObservation) -> NextAction:
        snapshot = self._snapshot_state()
        stage_before = self.state.current_stage
        apply_observation(
            self.state,
            observation,
            allowed_proof_points=self._allowed_proof_points,
        )
        action = next_action(self.state, self.template)
        try:
            self.recorder.record(
                event_type="media_observation",
                template_id=self.template.id,
                stage_before=stage_before,
                stage_after=self.state.current_stage,
                state=self.state,
                action=action,
                observation=observation,
            )
        except TracePersistenceError:
            self._restore_state(snapshot)
            raise
        return action

    def advance_stage(self, stage: str) -> NextAction:
        if stage not in STAGE_ORDER:
            raise ValueError(f"Unknown workflow stage: {stage}")
        snapshot = self._snapshot_state()
        stage_before = self.state.current_stage
        self.state.current_stage = stage
        self.state.last_observation = None
        action = next_action(self.state, self.template)
        try:
            self.recorder.record(
                event_type="stage_transition",
                template_id=self.template.id,
                stage_before=stage_before,
                stage_after=stage,
                state=self.state,
                action=action,
                perception={"stage_requested": stage},
            )
        except TracePersistenceError:
            self._restore_state(snapshot)
            raise
        return action

    def review_packet(self) -> dict:
        snapshot = self._snapshot_state()
        action = next_action(self.state, self.template)
        packet = build_evidence_packet(self.state, self.template)
        try:
            self.recorder.record(
                event_type="review_packet",
                template_id=self.template.id,
                stage_before=self.state.current_stage,
                stage_after=self.state.current_stage,
                state=self.state,
                action=action,
                perception={"packet_complete": packet["evidence_package"]["complete"]},
            )
        except TracePersistenceError:
            self._restore_state(snapshot)
            raise
        return packet

    def record_human_review(
        self,
        status: str,
        *,
        actor: str,
        note: str | None = None,
    ) -> NextAction:
        if status not in HUMAN_REVIEW_STATUSES:
            raise ValueError(f"Unsupported human review status: {status}")
        if not actor.strip():
            raise ValueError("human review actor is required")

        snapshot = self._snapshot_state()
        next_action(self.state, self.template)
        packet = build_evidence_packet(self.state, self.template)
        incomplete_override = not (
            packet["evidence_package"]["complete"] and packet["critical_proof"]["complete"]
        )
        if status == "approved" and incomplete_override and not (note or "").strip():
            self._restore_state(snapshot)
            raise ValueError("approving incomplete evidence requires an explicit human review note")

        self.state.professional_review_status = status
        self.state.professional_review_actor = actor
        self.state.professional_review_note = note
        action = NextAction(
            ActionType.HUMAN_REVIEW_RECORDED,
            f"Qualified human review status recorded: {status}.",
        )
        try:
            self.recorder.record(
                event_type="human_review",
                template_id=self.template.id,
                stage_before=self.state.current_stage,
                stage_after=self.state.current_stage,
                state=self.state,
                action=action,
                perception={
                    "review_status": status,
                    "review_actor": actor,
                    "incomplete_evidence_override": incomplete_override,
                    "note_present": bool((note or "").strip()),
                },
            )
        except TracePersistenceError:
            self._restore_state(snapshot)
            raise
        return action
