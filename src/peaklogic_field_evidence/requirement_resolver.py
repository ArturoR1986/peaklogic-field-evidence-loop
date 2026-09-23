from __future__ import annotations

from dataclasses import asdict, dataclass, field
from enum import Enum
from typing import Any, Iterable

from .evidence import STAGE_ORDER
from .schemas import ActionType, NextAction


class SourceKind(str, Enum):
    WORK_ORDER = "work_order"
    APPROVED_DRAWING = "approved_drawing"
    MANUFACTURER_GUIDE = "manufacturer_guide"
    SPECIFICATION = "specification"
    HUMAN_CONFIRMATION = "human_confirmation"


class VisualCheckability(str, Enum):
    VISUAL = "visual"
    PARTIAL = "partial"
    NONVISUAL = "nonvisual"


class RequirementEvidenceStatus(str, Enum):
    SUPPORTED = "supported"
    UNCERTAIN = "uncertain"
    REJECTED = "rejected"


@dataclass(frozen=True)
class RequirementSource:
    source_id: str
    source_kind: SourceKind
    document_name: str
    locator: str
    excerpt: str

    def validate(self) -> None:
        if not self.source_id.strip():
            raise ValueError("source_id is required")
        if not self.document_name.strip():
            raise ValueError("document_name is required")
        if not self.locator.strip():
            raise ValueError("source locator is required")
        if not self.excerpt.strip():
            raise ValueError("source excerpt is required; do not invent unsourced requirements")


@dataclass(frozen=True)
class EvidenceRequirement:
    requirement_id: str
    name: str
    requirement_statement: str
    source: RequirementSource
    evidence_question: str
    visual_checkability: VisualCheckability
    required: bool = True
    capture_before_stage: str | None = None
    expected_capture: str | None = None
    visual_limits: tuple[str, ...] = ()

    def validate(self) -> None:
        self.source.validate()
        if not self.requirement_id.strip():
            raise ValueError("requirement_id is required")
        if not self.name.strip():
            raise ValueError("requirement name is required")
        if not self.requirement_statement.strip():
            raise ValueError("requirement_statement is required")
        if not self.evidence_question.strip():
            raise ValueError("evidence_question is required")
        if self.capture_before_stage and self.capture_before_stage not in STAGE_ORDER:
            raise ValueError(f"unknown capture stage: {self.capture_before_stage}")

    def to_dict(self) -> dict[str, Any]:
        self.validate()
        data = asdict(self)
        data["source"]["source_kind"] = self.source.source_kind.value
        data["visual_checkability"] = self.visual_checkability.value
        return data


@dataclass(frozen=True)
class RequirementEvidenceLink:
    requirement_id: str
    media_id: str
    status: RequirementEvidenceStatus
    confidence: float | None = None
    observation: str = ""
    evidence_source: str = "human_reviewed"

    def validate(self) -> None:
        if not self.requirement_id.strip():
            raise ValueError("requirement_id is required")
        if not self.media_id.strip():
            raise ValueError("media_id is required")
        if self.confidence is not None and not 0.0 <= self.confidence <= 1.0:
            raise ValueError("confidence must be between 0 and 1")


@dataclass
class RequirementSet:
    job_id: str
    requirements: dict[str, EvidenceRequirement] = field(default_factory=dict)
    evidence_links: list[RequirementEvidenceLink] = field(default_factory=list)

    def add_requirement(self, requirement: EvidenceRequirement) -> None:
        requirement.validate()
        if requirement.requirement_id in self.requirements:
            raise ValueError(f"duplicate requirement_id: {requirement.requirement_id}")
        self.requirements[requirement.requirement_id] = requirement

    def link_evidence(
        self,
        link: RequirementEvidenceLink,
        *,
        bound_media_ids: Iterable[str],
    ) -> None:
        link.validate()
        if link.requirement_id not in self.requirements:
            raise ValueError(f"unknown requirement_id: {link.requirement_id}")
        bound = set(bound_media_ids)
        if link.media_id not in bound:
            raise ValueError(
                "media is not bound to this job; evidence cannot satisfy a requirement"
            )
        self.evidence_links.append(link)

    def to_dict(self) -> dict[str, Any]:
        return {
            "job_id": self.job_id,
            "requirements": [
                self.requirements[key].to_dict() for key in sorted(self.requirements)
            ],
            "evidence_links": [
                {
                    **asdict(link),
                    "status": link.status.value,
                }
                for link in self.evidence_links
            ],
        }


@dataclass(frozen=True)
class RequirementResolution:
    requirement_id: str
    status: str
    supporting_media_ids: tuple[str, ...]
    uncertain_media_ids: tuple[str, ...]
    rejected_media_ids: tuple[str, ...]
    next_action: NextAction

    def to_dict(self) -> dict[str, Any]:
        return {
            "requirement_id": self.requirement_id,
            "status": self.status,
            "supporting_media_ids": self.supporting_media_ids,
            "uncertain_media_ids": self.uncertain_media_ids,
            "rejected_media_ids": self.rejected_media_ids,
            "next_action": {
                "action": self.next_action.action.value,
                "reason": self.next_action.reason,
                "proof_point_id": self.next_action.proof_point_id,
            },
        }


def resolve_requirement(
    requirement: EvidenceRequirement,
    links: Iterable[RequirementEvidenceLink],
    *,
    current_stage: str,
) -> RequirementResolution:
    requirement.validate()
    related = [link for link in links if link.requirement_id == requirement.requirement_id]

    supported = tuple(
        link.media_id for link in related if link.status == RequirementEvidenceStatus.SUPPORTED
    )
    uncertain = tuple(
        link.media_id for link in related if link.status == RequirementEvidenceStatus.UNCERTAIN
    )
    rejected = tuple(
        link.media_id for link in related if link.status == RequirementEvidenceStatus.REJECTED
    )

    if supported:
        return RequirementResolution(
            requirement.requirement_id,
            "supported",
            supported,
            uncertain,
            rejected,
            NextAction(
                ActionType.CONTINUE,
                "Required evidence is present for this requirement; continue the job workflow.",
                requirement.requirement_id,
            ),
        )

    current_order = STAGE_ORDER.get(current_stage, 0)
    if requirement.capture_before_stage:
        deadline_order = STAGE_ORDER[requirement.capture_before_stage]
        if current_order >= deadline_order:
            return RequirementResolution(
                requirement.requirement_id,
                "missed_opportunity",
                supported,
                uncertain,
                rejected,
                NextAction(
                    ActionType.ESCALATE_HUMAN,
                    "The required capture opportunity has passed without supported evidence; record an exception rather than inventing proof.",
                    requirement.requirement_id,
                ),
            )

    if uncertain:
        return RequirementResolution(
            requirement.requirement_id,
            "uncertain",
            supported,
            uncertain,
            rejected,
            NextAction(
                ActionType.REQUEST_TARGETED_PROOF,
                "Available evidence is uncertain; request a clearer targeted capture or human confirmation.",
                requirement.requirement_id,
            ),
        )

    if requirement.visual_checkability == VisualCheckability.NONVISUAL:
        return RequirementResolution(
            requirement.requirement_id,
            "human_confirmation_required",
            supported,
            uncertain,
            rejected,
            NextAction(
                ActionType.ESCALATE_HUMAN,
                "This requirement cannot be established visually and requires human/nonvisual confirmation.",
                requirement.requirement_id,
            ),
        )

    return RequirementResolution(
        requirement.requirement_id,
        "missing",
        supported,
        uncertain,
        rejected,
        NextAction(
            ActionType.REQUEST_TARGETED_PROOF,
            "Required evidence is missing; request a capture targeted to the source-grounded requirement.",
            requirement.requirement_id,
        ),
    )


def resolve_requirement_set(
    requirement_set: RequirementSet,
    *,
    current_stage: str,
) -> list[RequirementResolution]:
    return [
        resolve_requirement(
            requirement,
            requirement_set.evidence_links,
            current_stage=current_stage,
        )
        for requirement in requirement_set.requirements.values()
    ]
