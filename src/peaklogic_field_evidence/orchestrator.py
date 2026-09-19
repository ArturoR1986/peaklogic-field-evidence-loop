from __future__ import annotations

from pathlib import Path
import cv2
import numpy as np

from .evidence import STAGE_ORDER, apply_observation
from .media import analyze_quality, average_hash, hamming_distance
from .policy import next_action
from .report import build_evidence_packet
from .schemas import EvidenceState, MediaObservation, MediaType, NextAction, ProofTemplate
from .trace import TraceRecorder


class EvidenceLoop:
    """Smallest executable Agentic Vision orchestration loop.

    This class deliberately separates visual observations from professional approval.
    Learned proof-point classification is injected later; until then labels may be
    supplied only by tests/operator-controlled demo inputs and must not be described
    as model predictions.
    """

    def __init__(
        self,
        template: ProofTemplate,
        *,
        state: EvidenceState | None = None,
        recorder: TraceRecorder | None = None,
        duplicate_hamming: int = 14,
    ) -> None:
        self.template = template
        self.state = state or EvidenceState(template_id=template.id)
        self.recorder = recorder or TraceRecorder()
        self.duplicate_hamming = duplicate_hamming
        self._image_hashes: dict[str, np.ndarray] = {}

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
        scene_confidence: float | None = None,
        media_type: MediaType = MediaType.PHOTO,
        source_timestamp_seconds: float | None = None,
    ) -> tuple[MediaObservation, NextAction]:
        stage_before = self.state.current_stage
        quality = analyze_quality(image)
        duplicate_of = None
        if image is not None and image.size:
            bits = average_hash(image)
            duplicate_of = self._find_duplicate(bits)
            if duplicate_of is None and quality.usable:
                self._image_hashes[media_id] = bits

        observation = MediaObservation(
            media_id=media_id,
            media_type=media_type,
            quality=quality,
            source_timestamp_seconds=source_timestamp_seconds,
            duplicate_of=duplicate_of,
            proof_point_label=proof_point_label,
            proof_point_confidence=proof_point_confidence,
            scene_confidence=scene_confidence,
        )
        apply_observation(self.state, observation)
        action = next_action(self.state, self.template)
        self.recorder.record(
            event_type="media_observation",
            template_id=self.template.id,
            stage_before=stage_before,
            stage_after=self.state.current_stage,
            state=self.state,
            action=action,
            observation=observation,
        )
        return observation, action

    def process_image_path(self, path: str | Path, **kwargs) -> tuple[MediaObservation, NextAction]:
        image = cv2.imread(str(path))
        if image is None:
            raise ValueError(f"Could not read image: {path}")
        return self.process_image(image, **kwargs)

    def process_observation(self, observation: MediaObservation) -> NextAction:
        stage_before = self.state.current_stage
        apply_observation(self.state, observation)
        action = next_action(self.state, self.template)
        self.recorder.record(
            event_type="media_observation",
            template_id=self.template.id,
            stage_before=stage_before,
            stage_after=self.state.current_stage,
            state=self.state,
            action=action,
            observation=observation,
        )
        return action

    def advance_stage(self, stage: str) -> NextAction:
        if stage not in STAGE_ORDER:
            raise ValueError(f"Unknown workflow stage: {stage}")
        stage_before = self.state.current_stage
        self.state.current_stage = stage
        self.state.last_observation = None
        action = next_action(self.state, self.template)
        self.recorder.record(
            event_type="stage_transition",
            template_id=self.template.id,
            stage_before=stage_before,
            stage_after=stage,
            state=self.state,
            action=action,
            perception={"stage_requested": stage},
        )
        return action

    def review_packet(self) -> dict:
        # Let policy update missed-proof exceptions before materializing the packet
        # so the report and trace describe the same evidence state.
        action = next_action(self.state, self.template)
        packet = build_evidence_packet(self.state, self.template)
        self.recorder.record(
            event_type="review_packet",
            template_id=self.template.id,
            stage_before=self.state.current_stage,
            stage_after=self.state.current_stage,
            state=self.state,
            action=action,
            perception={"packet_complete": packet["evidence_package"]["complete"]},
        )
        return packet
