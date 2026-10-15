import json

import numpy as np
import pytest
import cv2

from peaklogic_field_evidence.job_packet import JobEvidenceRecord
from peaklogic_field_evidence.job_progress import PersistentJobLoop


def setup_job(tmp_path, classification="installation", checkability="visual"):
    store = PersistentJobLoop(tmp_path / "job.db")
    record = JobEvidenceRecord("job", "wo", "persistent", "0.2", classification)
    manifest = [dict(media_id=m, job_id="job", provenance="preserved source", day=1)
                for m in ("a", "b", "source")]
    store.create(record, manifest)
    req = dict(requirement_id="anchor", name="Anchor proof", requirement_statement="Record arrow",
        source=dict(source_id="source", source_kind="work_order", document_name="WO", locator="anchor line", excerpt="Record arrow"),
        evidence_question="Is the arrow visible?", visual_checkability=checkability,
        capture_before_stage="covering_started")
    store.append("job", "req", "requirement", dict(requirement=req, component="anchor", zone="roof", authority="work_order"), day=0)
    return store


def observation(store, oid="obs", mid="a", day=1, zone="roof"):
    store.append("job", oid, "observation", dict(media_id=mid, actor="reviewer", method="manual_annotation",
        statement="Visible anchor", component="anchor", zone=zone), day=day)


def link(store, oid="obs", eid="link", modality="visual", **kwargs):
    return store.append("job", eid, "link", dict(requirement_id="anchor", observation_id=oid,
        status="supported", modality=modality, human_confirmed=True,
        capture_provenance_verified=True, **kwargs), day=1)


def quality(store, tmp_path, mid="a"):
    path = tmp_path / (mid + ".png")
    rng = np.random.default_rng(7)
    cv2.imwrite(str(path), rng.integers(30, 220, (400, 400, 3), dtype=np.uint8))
    store.measure_image("job", mid, path)


@pytest.mark.parametrize("classification", ["installation", "service_inspection"])
def test_reload_and_idempotent_replay(tmp_path, classification):
    store = setup_job(tmp_path, classification)
    quality(store, tmp_path)
    observation(store)
    expected = link(store)
    assert expected["component_decisions"][0]["status"] == "supported"
    events = store.events("job")
    store.close()
    store = PersistentJobLoop(tmp_path / "job.db")
    assert store.report("job") == expected
    for e in events:
        store.append("job", e["event_id"], e["kind"], e["payload"], day=e["day"], captured_at=e["captured_at"])
    assert store.report("job") == expected
    assert len(store.events("job")) == len(events)


def test_failed_mutation_rolls_back_and_conflicts_rejected(tmp_path):
    store = setup_job(tmp_path)
    before = store.events("job")
    with pytest.raises(ValueError):
        store.append("job", "bad", "quality", {"media_id": "foreign"})
    assert store.events("job") == before
    with pytest.raises(ValueError, match="conflicting"):
        store.append("job", "req", "different", {})
    assert store.events("job") == before


def test_late_precover_proof_resolves_without_erasing_gap(tmp_path):
    store = setup_job(tmp_path)
    store.append("job", "conceal", "concealment", dict(component="anchor", actor="reviewer", source_ids=["source"]), day=3)
    assert store.report("job")["component_decisions"][0]["status"] == "missed_opportunity"
    quality(store, tmp_path)
    observation(store, day=1)
    report = link(store)
    assert report["component_decisions"][0]["status"] == "supported"
    assert len(report["exception_history"]) == 1
    store.append("job", "correction", "correction", dict(target_event_id="link", reason="Wrong anchor", actor="reviewer"), day=4)
    assert store.report("job")["component_decisions"][0]["status"] == "missed_opportunity"
    assert len(store.report("job")["exception_history"]) == 1


@pytest.mark.parametrize("capture_day", [None, 3, 4])
def test_later_or_unknown_capture_cannot_recreate_precover_proof(tmp_path, capture_day):
    store = setup_job(tmp_path)
    quality(store, tmp_path)
    store.append("job", "conceal", "concealment", dict(component="anchor", actor="reviewer", source_ids=["source"]), day=3)
    observation(store, day=capture_day)
    assert link(store)["component_decisions"][0]["status"] == "missed_opportunity"


def test_duplicate_bytes_do_not_double_count(tmp_path):
    store = setup_job(tmp_path)
    for mid in ["b", "a"]:
        quality(store, tmp_path, mid)
        observation(store, "obs" + mid, mid)
        link(store, "obs" + mid, "link" + mid)
    report = store.report("job")
    assert report["quality"]["b"]["duplicate_of"] == "a"
    assert len(report["component_decisions"][0]["supporting_media_ids"]) == 1


def test_unresolved_binding_and_nonvisual_guard(tmp_path):
    store = setup_job(tmp_path, checkability="nonvisual")
    quality(store, tmp_path)
    observation(store, zone="unresolved")
    assert link(store)["component_decisions"][0]["status"] == "human_confirmation_required"
    observation(store, "bound")
    assert link(store, "bound", "boundlink")["component_decisions"][0]["status"] == "human_confirmation_required"
    assert link(store, "bound", "confirmed", modality="nonvisual", nonvisual_confirmation="Signed test result")["component_decisions"][0]["status"] == "supported"


def test_closed_record_actions_and_temporal_report(tmp_path):
    store = setup_job(tmp_path)
    observation(store, day=1)
    store.append("job", "progress", "progress", dict(component="anchor", status="installed_observed",
        actor="reviewer", method="manual_annotation", source_ids=["a"]), day=4)
    store.append("job", "closed", "close_record", dict(source_ids=["source"]), day=6)
    report = store.report("job")
    assert report["component_decisions"][0]["next_action"]["action"] == "escalate_human"
    assert report["professional_acceptance"]["status"] == "pending"
    assert report["physical_progress"]["anchor"]["status"] == "installed_observed"
    daily = store.report("job", through_day=1, from_day=1)
    assert not daily["field_record_closed"]
    assert not daily["physical_progress"]
    assert len(daily["period_observations"]) == 1


def test_blurred_real_failure_does_not_satisfy_proof(tmp_path):
    store = setup_job(tmp_path)
    path = tmp_path / "blur.png"
    cv2.imwrite(str(path), np.full((400, 400, 3), 120, dtype=np.uint8))
    store.measure_image("job", "a", path)
    observation(store)
    report = link(store)
    assert report["quality"]["a"]["metrics"]["reasons"] == ["blurred"]
    assert report["component_decisions"][0]["status"] == "missing"
