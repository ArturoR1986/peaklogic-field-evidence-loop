"""Reviewer-only integration checks using existing APIs; not a new vision model.

Runs fresh OpenCV quality measurements on synthetic images, then replays both
frozen real-field packets through the installed persistent CLI. The replay does
not download private media or recompute its historical OpenCV measurements.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys
from typing import Any

import cv2
import numpy as np

from peaklogic_field_evidence.job_packet import JobEvidenceRecord
from peaklogic_field_evidence.job_progress import PersistentJobLoop
from peaklogic_field_evidence.job_progress_cli import render_report
from peaklogic_field_evidence.runtime import require_opencv5


def write_json(path: Path, value: Any) -> None:
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def logical(value: Any) -> Any:
    """Fresh ingestion times differ; no other state fields are ignored."""
    if isinstance(value, dict):
        return {k: logical(v) for k, v in value.items() if k != "ingested_at"}
    if isinstance(value, list):
        return [logical(v) for v in value]
    return value


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def cli(args: list[str], log: Path) -> None:
    command = [sys.executable, "-m", "peaklogic_field_evidence.job_progress_cli", *args]
    result = subprocess.run(command, text=True, capture_output=True, check=False)
    log.write_text("$ " + " ".join(command) + "\n" + result.stdout + result.stderr,
                   encoding="utf-8")
    require(result.returncode == 0, f"CLI failed; see {log}")


def synthetic_check(out: Path) -> dict[str, Any]:
    """Source and semantic labels are controlled inputs, never field predictions."""
    job_id = "SYNTHETIC-REVIEW"
    source = out / "synthetic_work_order.json"
    statement = "Record an overview for manual review."
    write_json(source, {"fixture": "synthetic", "job_id": job_id, "instruction": statement})
    rng = np.random.default_rng(7)
    sharp = rng.integers(30, 220, (400, 400, 3), dtype=np.uint8)
    smooth = cv2.GaussianBlur(sharp, (51, 51), 10)
    images = {"sharp": sharp, "smoothed": smooth}
    manifest = [{"media_id": "source", "job_id": job_id, "day": 0,
                 "media_type": "document", "provenance": "synthetic_work_order.json",
                 "sha256": hashlib.sha256(source.read_bytes()).hexdigest()}]
    for media_id, image in images.items():
        path = out / (media_id + ".png")
        require(cv2.imwrite(str(path), image), f"Could not write fixture {path}")
        manifest.append({"media_id": media_id, "job_id": job_id, "day": 1,
                         "media_type": "photo", "provenance": "generated synthetic " + media_id,
                         "sha256": hashlib.sha256(path.read_bytes()).hexdigest()})
    record = JobEvidenceRecord(job_id, "SYNTHETIC-WO", "review-fixture", "1",
                               "installation", ["source"])
    store = PersistentJobLoop(out / "synthetic.sqlite")
    try:
        store.create(record, manifest)
        requirement = {"requirement_id": "overview", "name": "Overview",
                       "requirement_statement": statement,
                       "source": {"source_id": "source", "source_kind": "work_order",
                                  "document_name": source.name, "locator": "instruction",
                                  "excerpt": statement},
                       "evidence_question": "Has an overview been reviewed?",
                       "visual_checkability": "visual"}
        store.append(job_id, "req", "requirement", {"requirement": requirement,
                     "component": "roof", "zone": "synthetic-zone", "authority": "work_order"}, day=0)
        for media_id in images:
            store.measure_image(job_id, media_id, out / (media_id + ".png"))
        before = store.report(job_id)
        require(before["quality"]["sharp"]["next_action"] == "continue_review", "Sharp fixture action changed")
        require(before["quality"]["smoothed"]["next_action"] == "retake", "Smoothed fixture action changed")
        require(before["component_decisions"][0]["status"] != "supported", "Quality alone closed proof")
        events = store.events(job_id)
        try:
            store.measure_image(job_id, "foreign-media", out / "sharp.png")
        except ValueError:
            pass
        else:
            raise RuntimeError("Unbound media was accepted")
        require(store.events(job_id) == events, "Failed binding changed the store")
        store.append(job_id, "closed", "close_record", {"source_ids": ["source"]}, day=1)
        after = store.report(job_id)
        require(after["component_decisions"][0]["next_action"]["action"] == "escalate_human",
                "Closed unresolved record did not escalate")
        require(after["quality"]["smoothed"]["next_action"] == "record_quality_exception",
                "Closed record still requests retake")
        require(after["professional_acceptance"]["status"] == "pending", "Automatic acceptance")
        write_json(out / "synthetic_before_close.json", before)
        write_json(out / "synthetic_after_close.json", after)
        (out / "synthetic_report.md").write_text(render_report(after), encoding="utf-8")
        (out / "synthetic.trace.jsonl").write_text(
            "".join(json.dumps(e) + "\n" for e in store.events(job_id)), encoding="utf-8")
    finally:
        store.close()
    cli(["report", "--db", str(out / "synthetic.sqlite"), "--job-id", job_id,
         "--output", str(out / "synthetic_reloaded")], out / "synthetic_reload.log")
    reloaded = json.loads((out / "synthetic_reloaded.json").read_text())
    # Compare the JSON contract: in-memory tuple fields serialize as lists.
    require(reloaded == json.loads(json.dumps(after)), "Separate-process reload changed synthetic state")
    return {"basis": "fresh synthetic OpenCV measurements; controlled requirement and closure",
            "opencv_version": cv2.__version__, "quality_actions": {"sharp": "continue_review", "smoothed": "retake"},
            "closed_record_action": "escalate_human", "unbound_media_rejected": True,
            "separate_process_reload_equal": True, "professional_acceptance": "pending"}


def frozen_checks(out: Path) -> list[dict[str, Any]]:
    repo = Path(__file__).resolve().parents[1]
    inputs = repo / "docs/trials/persistent_replay_2026_10_02_v2"
    checks = []
    for number, job_id, count in [(1, "Trial-001-Kissling-6956", 312),
                                   (2, "Trial-002-BMW-Thoma-20266878", 93)]:
        stem = f"trial00{number}"
        packet = inputs / (stem + "_events.json")
        prefix = out / stem
        args = ["replay", "--db", str(out / "trials.sqlite"), "--job-id", job_id,
                "--input", str(packet), "--output", str(prefix)]
        cli(args, out / (stem + "_replay.log"))
        actual = json.loads(prefix.with_suffix(".json").read_text())
        expected = json.loads((inputs / (stem + "_state.json")).read_text())
        require(logical(actual) == logical(expected), f"{stem}: frozen logical state differs")
        trace = Path(str(prefix) + ".trace.jsonl").read_bytes()
        require(len(trace.splitlines()) == count, f"{stem}: event count differs")
        cli(args, out / (stem + "_idempotency.log"))
        require(Path(str(prefix) + ".trace.jsonl").read_bytes() == trace, f"{stem}: replay appended events")
        cli(["report", "--db", str(out / "trials.sqlite"), "--job-id", job_id,
             "--output", str(out / (stem + "_reloaded"))], out / (stem + "_reload.log"))
        require(json.loads((out / (stem + "_reloaded.json")).read_text()) == actual,
                f"{stem}: separate-process report changed")
        checks.append({"job_id": job_id, "event_count": count,
                       "packet_sha256": hashlib.sha256(packet.read_bytes()).hexdigest(),
                       "logical_state_equal_excluding_ingested_at": True,
                       "idempotent_trace_equal": True, "separate_process_reload_equal": True,
                       "historical_cv_recomputed": False,
                       "unreviewed_media_entries": len(actual["unreviewed_media_ids"]),
                       "exception_history_count": len(actual["exception_history"]),
                       "professional_acceptance": actual["professional_acceptance"]["status"]})
    cli(["report", "--db", str(out / "trials.sqlite"), "--job-id", "Trial-001-Kissling-6956",
         "--through-day", "6", "--from-day", "6", "--output", str(out / "trial001_day06")],
        out / "trial001_day06.log")
    return checks


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", required=True, type=Path, help="New directory; never overwritten")
    args = parser.parse_args()
    require_opencv5()
    args.output_dir.mkdir(parents=True, exist_ok=False)
    result: dict[str, Any] = {"status": "RUNNING", "opencv_version": cv2.__version__}
    try:
        result["synthetic"] = synthetic_check(args.output_dir)
        result["frozen_replays"] = frozen_checks(args.output_dir)
        result["status"] = "PASS"
    except Exception as exc:
        result.update(status="FAIL", error=f"{type(exc).__name__}: {exc}")
        raise
    finally:
        write_json(args.output_dir / "verification.json", result)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
