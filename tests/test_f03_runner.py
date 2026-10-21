"""F03 runner regression tests against the REAL existing PersistentJobLoop."""
import hashlib
import importlib.util
import json
from pathlib import Path
import sqlite3
import subprocess
import sys

import pytest
from peaklogic_field_evidence import f03_runner as runner
from peaklogic_field_evidence.job_progress import PersistentJobLoop

spec = importlib.util.spec_from_file_location("f03_smoke", Path(__file__).parents[1] / "scripts/f03_smoke.py")
smoke = importlib.util.module_from_spec(spec)
spec.loader.exec_module(smoke)
COMMIT = "5dc56b4896c3f2c33d4f64aee4005546d45e9d2b"


def args_for(root, **fixture):
    db, image = smoke.make_fixture(root, **fixture)
    state, _ = runner.read_snapshot(db, "F03-synthetic")
    return dict(db=db, job_id="F03-synthetic", media_id="a", requirement_id="required-photo",
                image=image, output=root / "result", source_commit=COMMIT,
                expected_state_sha256=runner.digest(state), input_basis="synthetic_control",
                development_only=not runner.runtime_info()["pinned_runtime"])


def test_positive_control_and_actual_child_reopen(tmp_path):
    args = args_for(tmp_path)
    result = runner.run_image(**args)
    assert result["measurement_mode"] == "fresh_opencv_execution"
    assert result["requirement_decision"]["status"] == "supported"
    assert result["professional_acceptance"]["status"] == "pending"
    assert result["cloud_execution_proven"] is False
    assert result["event_count"] == result["event_count_before"] + 1
    assert json.loads((args["output"] / "reopen.json").read_text())["status"] == "PASS"
    assert result["state_sha256"] in (args["output"] / "report.md").read_text()


@pytest.mark.parametrize("kind", ["blur", "corrupt"])
def test_closed_record_unsuitable_inputs(tmp_path, kind):
    result = runner.run_image(**args_for(tmp_path, kind=kind, closed=True))
    assert result["requirement_decision"]["status"] != "supported"
    assert result["requirement_decision"]["next_action"]["action"] == "escalate_human"
    assert result["image_action"] == "record_quality_exception"


@pytest.mark.parametrize("checkability", ["partial", "nonvisual"])
def test_visual_quality_does_not_close_other_modalities(tmp_path, checkability):
    result = runner.run_image(**args_for(tmp_path, checkability=checkability))
    assert result["requirement_decision"]["status"] != "supported"
    assert result["professional_acceptance"]["status"] == "pending"


def test_unknown_component_zone_stays_unresolved(tmp_path):
    result = runner.run_image(**args_for(tmp_path, zone="unresolved"))
    assert result["requirement_decision"]["status"] != "supported"


def test_retry_is_not_fresh_and_not_a_second_event(tmp_path):
    args = args_for(tmp_path)
    first = runner.run_image(**args)
    args.update(output=tmp_path / "retry", expected_state_sha256=first["state_sha256"])
    second = runner.run_image(**args)
    assert second["measurement_mode"] == "idempotent_reuse_NOT_fresh"
    assert first["state_sha256"] == second["state_sha256"]
    assert first["trace_sha256"] == second["trace_sha256"]
    assert first["event_count"] == second["event_count"]


def test_duplicate_bytes_do_not_add_proof(tmp_path):
    args = args_for(tmp_path)
    first = runner.run_image(**args)
    args.update(media_id="b", output=tmp_path / "duplicate", expected_state_sha256=first["state_sha256"])
    second = runner.run_image(**args)
    assert second["image_action"] == "reject_duplicate"
    assert len(second["requirement_decision"]["supporting_media_ids"]) == 1


@pytest.mark.parametrize("field,value", [
    ("job_id", "foreign"), ("media_id", "foreign"), ("requirement_id", "foreign"),
    ("source_commit", "main"), ("expected_state_sha256", "0" * 64),
    ("input_basis", "verified_workmanship"),
])
def test_rejected_preflight_never_mutates_db(tmp_path, field, value):
    args = args_for(tmp_path)
    before = runner.read_snapshot(args["db"], "F03-synthetic")
    args[field] = value
    with pytest.raises(ValueError):
        runner.run_image(**args)
    assert runner.read_snapshot(args["db"], "F03-synthetic") == before
    assert not args["output"].exists()


def test_hash_mismatch_never_mutates(tmp_path):
    args = args_for(tmp_path)
    before = runner.read_snapshot(args["db"], args["job_id"])
    args["image"].write_bytes(b"changed bytes")
    with pytest.raises(ValueError, match="hash"):
        runner.run_image(**args)
    assert runner.read_snapshot(args["db"], args["job_id"]) == before


def test_oversize_is_rejected(tmp_path, monkeypatch):
    args = args_for(tmp_path)
    monkeypatch.setattr(runner, "MAX_INPUT_BYTES", 10)
    with pytest.raises(ValueError, match="10 MiB"):
        runner.run_image(**args)


def test_production_rejects_unpinned_runtime_before_writes(tmp_path, monkeypatch):
    args = args_for(tmp_path)
    monkeypatch.setattr(runner, "runtime_info", lambda: {"pinned_runtime": False})
    args["development_only"] = False
    with pytest.raises(ValueError, match="pinned OpenCV"):
        runner.run_image(**args)
    assert not args["output"].exists()


def test_missing_db_is_not_created(tmp_path):
    path = tmp_path / "absent.sqlite"
    with pytest.raises(FileNotFoundError):
        runner.read_snapshot(path, "job")
    assert not path.exists()


def test_existing_output_cannot_be_overwritten(tmp_path):
    args = args_for(tmp_path)
    args["output"].mkdir()
    with pytest.raises(ValueError, match="new output"):
        runner.run_image(**args)


def test_save_failure_is_partial_not_false_rollback(tmp_path, monkeypatch):
    args = args_for(tmp_path)
    original = runner._write
    def fail_report(path, text):
        if path.name == "report.md":
            raise OSError("controlled export failure")
        return original(path, text)
    monkeypatch.setattr(runner, "_write", fail_report)
    with pytest.raises(OSError):
        runner.run_image(**args)
    failure = json.loads((args["output"] / "failure.json").read_text())
    assert failure["new_quality_event_committed"] is True
    assert not (args["output"] / "receipt.json").exists()
    assert "a" in runner.read_snapshot(args["db"], args["job_id"])[0]["quality"]


def test_database_failure_does_not_claim_commit(tmp_path, monkeypatch):
    args = args_for(tmp_path)
    before = runner.read_snapshot(args["db"], args["job_id"])
    def fail(*a, **k):
        raise sqlite3.OperationalError("controlled storage failure")
    monkeypatch.setattr(PersistentJobLoop, "measure_image", fail)
    with pytest.raises(sqlite3.OperationalError):
        runner.run_image(**args)
    assert runner.read_snapshot(args["db"], args["job_id"]) == before
    assert json.loads((args["output"] / "failure.json").read_text())["new_quality_event_committed"] is False


def test_tampered_report_fails_reopen_verifier(tmp_path):
    args = args_for(tmp_path)
    runner.run_image(**args)
    (args["output"] / "report.md").write_text("altered")
    with pytest.raises(ValueError, match="artifact hash"):
        runner.verify(args["db"], args["job_id"], args["output"] / "receipt.json")


def test_conflicting_old_runtime_event_is_not_recomputed(tmp_path):
    args = args_for(tmp_path)
    state, _ = runner.read_snapshot(args["db"], args["job_id"])
    store = PersistentJobLoop(args["db"])
    try:
        store.measure_image(args["job_id"], "a", args["image"])
    finally:
        store.close()
    # Simulate historical imported metadata in this isolated test database only.
    with sqlite3.connect(args["db"]) as db:
        p = json.loads(db.execute("SELECT payload FROM events WHERE kind='quality'").fetchone()[0])
        p["opencv_version"] = "0.0.historical"
        db.execute("UPDATE events SET payload=? WHERE kind='quality'", (json.dumps(p),))
    state, events = runner.read_snapshot(args["db"], args["job_id"])
    args["expected_state_sha256"] = runner.digest(state)
    with pytest.raises(ValueError, match="historical CV"):
        runner.run_image(**args)
    assert runner.read_snapshot(args["db"], args["job_id"])[1] == events


def test_cli_snapshot_is_read_only_and_runtime_scoped(tmp_path):
    args = args_for(tmp_path)
    before = hashlib.sha256(args["db"].read_bytes()).hexdigest()
    r = subprocess.run([sys.executable, "-m", "peaklogic_field_evidence.f03_runner", "snapshot",
                        "--db", str(args["db"]), "--job-id", args["job_id"]],
                       capture_output=True, text=True, check=True, timeout=60)
    assert json.loads(r.stdout)["state_sha256"] == args["expected_state_sha256"]
    assert hashlib.sha256(args["db"].read_bytes()).hexdigest() == before
