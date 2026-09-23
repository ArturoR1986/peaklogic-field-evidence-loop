import numpy as np
import pytest

from peaklogic_field_evidence.job_packet import JobAttachment, JobEvidenceSession
from peaklogic_field_evidence.schemas import ActionType, MediaType
from peaklogic_field_evidence.templates import registry


def usable_image():
    image = np.zeros((600, 800, 3), dtype=np.uint8)
    image[::2, ::2] = 255
    return image


def test_unbound_media_cannot_change_job_evidence_state():
    t = registry()[0]
    session = JobEvidenceSession.create(
        job_id="job-1",
        work_order_id="wo-1",
        template=t,
        work_order_artifacts=["work-order-page-1.jpg"],
    )
    with pytest.raises(ValueError, match="not bound"):
        session.process_bound_image(
            usable_image(),
            media_id="photo-1",
            proof_point_label="location_context",
            proof_point_confidence=0.99,
        )
    assert not session.loop.state.observations


def test_bound_media_is_traceable_to_job_and_attachment():
    t = registry()[0]
    session = JobEvidenceSession.create(
        job_id="job-1",
        work_order_id="wo-1",
        template=t,
        work_order_artifacts=["work-order-page-1.jpg"],
        extracted_context={"task": "INSTALL SAFETY ANCHOR"},
    )
    session.bind_attachment(JobAttachment(
        media_id="photo-1",
        source_name="arrival.jpg",
        media_type=MediaType.PHOTO,
        stage="arrival",
        role="location_context",
        rights_status="owned_or_authorized",
    ))
    observation, action = session.process_bound_image(
        usable_image(),
        media_id="photo-1",
        proof_point_label="location_context",
        proof_point_confidence=0.99,
        scene_confidence=0.9,
    )
    packet = session.review_packet()
    assert observation.media_id == "photo-1"
    assert packet["job"]["job_id"] == "job-1"
    assert packet["job"]["work_order_id"] == "wo-1"
    assert packet["job"]["attachments"][0]["media_id"] == "photo-1"
    assert packet["job"]["work_order_artifacts"] == ["work-order-page-1.jpg"]
    assert action.action in {ActionType.CONTINUE, ActionType.REMIND_CRITICAL_PROOF}


def test_job_packet_stays_pending_when_only_arrival_context_exists():
    t = registry()[0]
    session = JobEvidenceSession.create(
        job_id="job-day1",
        work_order_id="wo-day1",
        template=t,
    )
    session.bind_attachment(JobAttachment(
        media_id="arrival-1",
        source_name="arrival-1.jpg",
        media_type=MediaType.PHOTO,
        stage="arrival",
        role="location_context",
        rights_status="owned_or_authorized",
    ))
    session.process_bound_image(
        usable_image(),
        media_id="arrival-1",
        proof_point_label="location_context",
        proof_point_confidence=0.99,
        scene_confidence=0.95,
    )
    packet = session.review_packet()
    assert packet["evidence"]["evidence_package"]["complete"] is False
    assert packet["evidence"]["professional_review_status"] == "pending"
    assert packet["evidence"]["critical_proof"]["complete"] is False


def test_job_packet_includes_requirement_resolution_and_rejects_unbound_requirement_evidence():
    from peaklogic_field_evidence.requirement_resolver import (
        EvidenceRequirement,
        RequirementEvidenceLink,
        RequirementEvidenceStatus,
        RequirementSet,
        RequirementSource,
        SourceKind,
        VisualCheckability,
    )

    t = registry()[0]
    requirements = RequirementSet(job_id="job-r1")
    requirements.add_requirement(EvidenceRequirement(
        requirement_id="photo-before-cover",
        name="Source-grounded photo requirement",
        requirement_statement="Capture visible evidence before concealment.",
        source=RequirementSource(
            source_id="wo-1",
            source_kind=SourceKind.WORK_ORDER,
            document_name="work-order.jpg",
            locator="page 1",
            excerpt="Photo evidence is required before departure.",
        ),
        evidence_question="Is the required condition visibly documented before concealment?",
        visual_checkability=VisualCheckability.VISUAL,
        capture_before_stage="covering_started",
    ))
    session = JobEvidenceSession.create(
        job_id="job-r1",
        work_order_id="wo-r1",
        template=t,
        requirement_set=requirements,
    )

    with pytest.raises(ValueError, match="not bound"):
        session.link_requirement_evidence(RequirementEvidenceLink(
            requirement_id="photo-before-cover",
            media_id="unbound.jpg",
            status=RequirementEvidenceStatus.SUPPORTED,
        ))

    session.bind_attachment(JobAttachment(
        media_id="bound.jpg",
        source_name="bound.jpg",
        media_type=MediaType.PHOTO,
        stage="installation",
        role="process_before_cover",
        rights_status="owned_or_authorized",
    ))
    session.link_requirement_evidence(RequirementEvidenceLink(
        requirement_id="photo-before-cover",
        media_id="bound.jpg",
        status=RequirementEvidenceStatus.SUPPORTED,
        evidence_source="human_reviewed",
        observation="Visible condition documented before concealment.",
    ))
    packet = session.review_packet()
    assert packet["requirement_resolutions"][0]["status"] == "supported"
    assert packet["requirement_resolutions"][0]["supporting_media_ids"] == ("bound.jpg",)
