from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any

import numpy as np

from .orchestrator import EvidenceLoop
from .requirement_resolver import (
    RequirementEvidenceLink,
    RequirementResolution,
    RequirementSet,
    resolve_requirement_set,
)
from .schemas import MediaType, NextAction, ProofTemplate


@dataclass(frozen=True)
class JobAttachment:
    media_id: str
    source_name: str
    media_type: MediaType
    stage: str
    role: str
    rights_status: str = "unverified"
    source_timestamp_seconds: float | None = None

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["media_type"] = self.media_type.value
        return data


@dataclass
class JobEvidenceRecord:
    job_id: str
    work_order_id: str
    template_id: str
    template_version: str
    task_type: str
    work_order_artifacts: list[str] = field(default_factory=list)
    extracted_context: dict[str, Any] = field(default_factory=dict)
    attachments: dict[str, JobAttachment] = field(default_factory=dict)

    def bind_attachment(self, attachment: JobAttachment) -> None:
        if attachment.media_id in self.attachments:
            raise ValueError(f"attachment already bound: {attachment.media_id}")
        self.attachments[attachment.media_id] = attachment

    def to_dict(self) -> dict[str, Any]:
        return {
            "job_id": self.job_id,
            "work_order_id": self.work_order_id,
            "template_id": self.template_id,
            "template_version": self.template_version,
            "task_type": self.task_type,
            "work_order_artifacts": list(self.work_order_artifacts),
            "extracted_context": dict(self.extracted_context),
            "attachments": [
                self.attachments[key].to_dict() for key in sorted(self.attachments)
            ],
        }


class JobEvidenceSession:
    """Bind work-order context, requirements, and attachments to one Evidence Loop."""

    def __init__(
        self,
        record: JobEvidenceRecord,
        template: ProofTemplate,
        *,
        loop: EvidenceLoop | None = None,
        requirement_set: RequirementSet | None = None,
    ) -> None:
        if record.template_id != template.id or record.template_version != template.version:
            raise ValueError("job record template does not match Evidence Loop template")
        if requirement_set is not None and requirement_set.job_id != record.job_id:
            raise ValueError("requirement set belongs to a different job")
        self.record = record
        self.loop = loop or EvidenceLoop(template)
        self.requirement_set = requirement_set or RequirementSet(job_id=record.job_id)

    @classmethod
    def create(
        cls,
        *,
        job_id: str,
        work_order_id: str,
        template: ProofTemplate,
        work_order_artifacts: list[str] | None = None,
        extracted_context: dict[str, Any] | None = None,
        loop: EvidenceLoop | None = None,
        requirement_set: RequirementSet | None = None,
    ) -> "JobEvidenceSession":
        record = JobEvidenceRecord(
            job_id=job_id,
            work_order_id=work_order_id,
            template_id=template.id,
            template_version=template.version,
            task_type=template.task_type,
            work_order_artifacts=list(work_order_artifacts or []),
            extracted_context=dict(extracted_context or {}),
        )
        return cls(
            record,
            template,
            loop=loop,
            requirement_set=requirement_set,
        )

    def bind_attachment(self, attachment: JobAttachment) -> None:
        self.record.bind_attachment(attachment)

    def link_requirement_evidence(self, link: RequirementEvidenceLink) -> None:
        self.requirement_set.link_evidence(
            link,
            bound_media_ids=self.record.attachments.keys(),
        )

    def process_bound_image(
        self,
        image: np.ndarray,
        *,
        media_id: str,
        proof_point_label: str | None = None,
        proof_point_confidence: float | None = None,
        proof_point_source: str | None = None,
        scene_confidence: float | None = None,
    ) -> tuple[Any, NextAction]:
        attachment = self.record.attachments.get(media_id)
        if attachment is None:
            raise ValueError(
                "media is not bound to this job; bind the attachment before it can affect evidence state"
            )
        if attachment.media_type not in {MediaType.PHOTO, MediaType.VIDEO_FRAME}:
            raise ValueError("bound attachment is not image evidence")
        return self.loop.process_image(
            image,
            media_id=media_id,
            proof_point_label=proof_point_label,
            proof_point_confidence=proof_point_confidence,
            proof_point_source=proof_point_source,
            scene_confidence=scene_confidence,
            media_type=attachment.media_type,
            source_timestamp_seconds=attachment.source_timestamp_seconds,
        )

    def advance_stage(self, stage: str) -> NextAction:
        return self.loop.advance_stage(stage)

    def resolve_requirements(self) -> list[RequirementResolution]:
        return resolve_requirement_set(
            self.requirement_set,
            current_stage=self.loop.state.current_stage,
        )

    def review_packet(self) -> dict[str, Any]:
        packet = self.loop.review_packet()
        resolutions = self.resolve_requirements()
        return {
            "job": self.record.to_dict(),
            "requirements": self.requirement_set.to_dict(),
            "requirement_resolutions": [r.to_dict() for r in resolutions],
            "evidence": packet,
            "comparison_question": (
                "Given what this work order and approved sources say should be done, "
                "what evidence is present, what evidence is missing or uncertain, "
                "and what should happen next?"
            ),
        }
