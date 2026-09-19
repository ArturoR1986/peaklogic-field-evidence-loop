from peaklogic_field_evidence.dataset import DatasetRecord
from peaklogic_field_evidence.dataset_audit import audit_records


def rec(
    record_id: str,
    *,
    split: str,
    group_id: str | None = None,
    source_media_path: str | None = None,
    job_reference: str | None = None,
    rights_basis: str = "owned_by_peaklogic",
    provenance: str = "staged_for_competition",
    consent_status: str = "confirmed",
    media_path: str | None = None,
):
    return DatasetRecord(
        record_id=record_id,
        media_path=media_path or f"media/{record_id}.jpg",
        media_type="photo",
        label="critical_attachment",
        split=split,
        group_id=group_id,
        source_media_path=source_media_path,
        job_reference=job_reference,
        rights_basis=rights_basis,
        provenance=provenance,
        consent_status=consent_status,
    )


def test_audit_detects_group_crossing_train_and_test():
    report = audit_records([
        rec("r1", split="train", group_id="job-1"),
        rec("r2", split="test", group_id="job-1"),
    ])
    assert report.leakage_groups == {"group:job-1": ("test", "train")}
    assert report.strict_ok is False


def test_video_frames_share_source_group_when_group_id_missing():
    a = DatasetRecord(
        record_id="v1",
        media_path="frames/v1.jpg",
        media_type="video_frame",
        label="location_context",
        split="train",
        source_media_path="raw/walkthrough.mp4",
        rights_basis="owned_by_peaklogic",
        provenance="staged_for_competition",
        consent_status="confirmed",
    )
    b = DatasetRecord(
        record_id="v2",
        media_path="frames/v2.jpg",
        media_type="video_frame",
        label="finished_context",
        split="validation",
        source_media_path="raw/walkthrough.mp4",
        rights_basis="owned_by_peaklogic",
        provenance="staged_for_competition",
        consent_status="confirmed",
    )
    report = audit_records([a, b])
    assert "source:raw/walkthrough.mp4" in report.leakage_groups


def test_audit_flags_unverified_rights_and_unassigned_records():
    record = DatasetRecord(
        record_id="r1",
        media_path="media/r1.jpg",
        media_type="photo",
        label="unsupported",
    )
    report = audit_records([record])
    assert report.unresolved_rights_record_ids == ("r1",)
    assert report.unresolved_provenance_record_ids == ("r1",)
    assert report.unresolved_consent_record_ids == ("r1",)
    assert report.unassigned_record_ids == ("r1",)
    assert report.strict_ok is False


def test_audit_requires_group_context_for_final_split():
    report = audit_records([rec("r1", split="test")])
    assert report.missing_group_context_record_ids == ("r1",)


def test_clean_grouped_dataset_passes_strict_audit():
    report = audit_records([
        rec("train-1", split="train", group_id="job-a"),
        rec("val-1", split="validation", group_id="job-b"),
        rec("test-1", split="test", group_id="job-c"),
    ])
    assert report.strict_ok is True
    assert report.split_counts["train"] == 1
    assert report.split_counts["validation"] == 1
    assert report.split_counts["test"] == 1
