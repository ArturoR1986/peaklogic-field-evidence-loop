from __future__ import annotations

from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import Optional


class MediaType(str, Enum):
    PHOTO = "photo"
    VIDEO_FRAME = "video_frame"
    DOCUMENT_SCAN = "document_scan"


class ActionType(str, Enum):
    ACCEPT = "accept"
    REQUEST_RESCAN = "request_rescan"
    RETAKE = "retake"
    REJECT_DUPLICATE = "reject_duplicate"
    REQUEST_TARGETED_PROOF = "request_targeted_proof"
    REMIND_CRITICAL_PROOF = "remind_critical_proof"
    ESCALATE_HUMAN = "escalate_human"
    PREPARE_REVIEW_PACKET = "prepare_review_packet"
    HUMAN_REVIEW_RECORDED = "human_review_recorded"
    CONTINUE = "continue"


@dataclass(frozen=True)
class QualityMetrics:
    sharpness: float
    mean_luminance: float
    width: int
    height: int
    usable: bool
    reasons: tuple[str, ...] = ()


@dataclass(frozen=True)
class MediaObservation:
    media_id: str
    media_type: MediaType
    quality: QualityMetrics
    source_timestamp_seconds: Optional[float] = None
    duplicate_of: Optional[str] = None
    proof_point_label: Optional[str] = None
    proof_point_confidence: Optional[float] = None
    proof_point_source: Optional[str] = None
    scene_confidence: Optional[float] = None
    perception_error: Optional[str] = None


@dataclass(frozen=True)
class ProofPoint:
    id: str
    name: str
    required: bool = True
    critical_before_stage: Optional[str] = None
    human_only: bool = False


@dataclass(frozen=True)
class ProofTemplate:
    id: str
    version: str
    task_type: str
    quality_critical: bool
    keywords: tuple[str, ...]
    proof_points: tuple[ProofPoint, ...]


@dataclass
class EvidenceState:
    template_id: str
    current_stage: str = "arrival"
    accepted_proof_points: set[str] = field(default_factory=set)
    missed_proof_points: set[str] = field(default_factory=set)
    last_observation: Optional[MediaObservation] = None
    observations: list[MediaObservation] = field(default_factory=list)
    professional_review_status: str = "pending"
    professional_review_actor: Optional[str] = None
    professional_review_note: Optional[str] = None

    def to_dict(self) -> dict:
        data = asdict(self)
        data["accepted_proof_points"] = sorted(self.accepted_proof_points)
        data["missed_proof_points"] = sorted(self.missed_proof_points)
        return data


@dataclass(frozen=True)
class NextAction:
    action: ActionType
    reason: str
    proof_point_id: Optional[str] = None
