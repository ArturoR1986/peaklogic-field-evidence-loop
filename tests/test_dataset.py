import pytest
from peaklogic_field_evidence.dataset import DatasetRecord, read_manifest, write_manifest


def record(record_id="r1", label="critical_attachment"):
    return DatasetRecord(
        record_id=record_id,
        media_path=f"media/{record_id}.jpg",
        media_type="photo",
        label=label,
        split="train",
    )


def test_manifest_round_trip(tmp_path):
    path = tmp_path / "manifest.jsonl"
    write_manifest([record("r1"), record("r2", "finished_context")], path)
    loaded = read_manifest(path)
    assert [r.record_id for r in loaded] == ["r1", "r2"]
    assert loaded[1].label == "finished_context"


def test_manifest_rejects_unknown_label(tmp_path):
    with pytest.raises(ValueError):
        write_manifest([record("r1", "made_up")], tmp_path / "manifest.jsonl")


def test_manifest_rejects_duplicate_ids(tmp_path):
    with pytest.raises(ValueError):
        write_manifest([record("r1"), record("r1")], tmp_path / "manifest.jsonl")
