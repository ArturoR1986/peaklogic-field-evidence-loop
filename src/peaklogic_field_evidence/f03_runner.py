"""Bounded fresh-image runner for F02/F03; reuses the existing SQLite job loop.

No HTTP server, credentials, infrastructure creation, new job schema, inferred
annotations, or professional approval. Run on a single-writer sandbox job DB.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.metadata
import json
import os
from pathlib import Path
import re
import sqlite3
import subprocess
import sys
import tempfile
from datetime import datetime, timezone

# Must be set before OpenCV is imported in this command-line process.
os.environ.setdefault("OPENCV_IO_MAX_IMAGE_PIXELS", "25000000")
import cv2
import numpy as np

from .job_progress import PersistentJobLoop, canonical
from .job_progress_cli import render_report

MAX_INPUT_BYTES = 10 * 1024 * 1024


def digest(value) -> str:
    return hashlib.sha256(canonical(value).encode("utf-8")).hexdigest()


def runtime_info() -> dict:
    try:
        wheel = importlib.metadata.version("opencv-contrib-python-headless")
    except importlib.metadata.PackageNotFoundError:
        wheel = None
    return {"python": sys.version.split()[0], "opencv": cv2.__version__,
            "opencv_wheel": wheel, "numpy": np.__version__,
            "pinned_runtime": cv2.__version__ == "5.0.0" and
                wheel == "5.0.0.93" and np.__version__ == "2.3.2"}


def read_snapshot(db: Path, job_id: str) -> tuple[dict, list[dict]]:
    """Read without creating a DB, executing schema DDL, or allowing writes."""
    db = Path(db).resolve(strict=True)
    reader = PersistentJobLoop.__new__(PersistentJobLoop)
    reader.db = sqlite3.connect(db.as_uri() + "?mode=ro", uri=True)
    reader.db.execute("PRAGMA query_only=ON")
    try:
        reader.db.execute("BEGIN")
        state = reader.report(job_id)
        events = reader.events(job_id)
        return state, events
    finally:
        reader.close()


def _write(path: Path, content: str) -> None:
    with path.open("x", encoding="utf-8") as stream:
        stream.write(content)
        stream.flush()
        os.fsync(stream.fileno())


def verify(db: Path, job_id: str, receipt_path: Path) -> dict:
    receipt_path = Path(receipt_path).resolve(strict=True)
    receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    if receipt["job_id"] != job_id:
        raise ValueError("receipt belongs to another job")
    state, events = read_snapshot(db, job_id)
    if digest(state) != receipt["state_sha256"] or digest(events) != receipt["trace_sha256"]:
        raise ValueError("reopened state/trace differs from the demonstrated revision")
    for name, expected in receipt["artifact_sha256"].items():
        if Path(name).name != name:
            raise ValueError("receipt artifact path must be a basename")
        if hashlib.sha256((receipt_path.parent / name).read_bytes()).hexdigest() != expected:
            raise ValueError("report/trace artifact hash mismatch")
    return {"status": "PASS", "job_id": job_id, "state_sha256": digest(state),
            "trace_sha256": digest(events), "event_count": len(events)}


def run_image(*, db: Path, job_id: str, media_id: str, requirement_id: str,
              image: Path, output: Path, source_commit: str,
              expected_state_sha256: str, input_basis: str,
              development_only: bool = False) -> dict:
    """Save actual quality results; return evidence/actions from the same revision.

    source_commit and input_basis are operator declarations, not remote attestation.
    This runner refuses a conflicting/recomputed historical quality event. Use an
    explicitly reviewed sandbox packet for a fresh experiment; do not delete events.
    """
    info = runtime_info()
    if not info["pinned_runtime"] and not development_only:
        raise ValueError("pinned OpenCV 5.0.0 / wheel 5.0.0.93 / NumPy 2.3.2 required")
    if not re.fullmatch(r"[0-9a-f]{40}", source_commit):
        raise ValueError("full lowercase source commit SHA required")
    if not re.fullmatch(r"[0-9a-f]{64}", expected_state_sha256):
        raise ValueError("expected state SHA-256 required")
    if input_basis not in {"synthetic_control", "preserved_field_input"}:
        raise ValueError("explicit input basis required")
    db, image = Path(db).resolve(strict=True), Path(image).resolve(strict=True)
    output = Path(output).resolve()
    if output.exists():
        raise ValueError("use a new output directory; prior run evidence is immutable")
    if db.is_relative_to(output) or image.is_relative_to(output):
        raise ValueError("output must not contain the database or input")
    with image.open("rb") as stream:
        raw = stream.read(MAX_INPUT_BYTES + 1)
    if not raw or len(raw) > MAX_INPUT_BYTES:
        raise ValueError("input must be nonempty and at most 10 MiB")
    raw_sha = hashlib.sha256(raw).hexdigest()

    # This lock coordinates this runner's processes. Other clients must not write
    # the sandbox DB concurrently; the canonical loop still owns transactions.
    import fcntl
    lock_path = db.with_name(db.name + ".f03.lock")
    with lock_path.open("a") as lock:
        fcntl.flock(lock.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        before, before_events = read_snapshot(db, job_id)
        if digest(before) != expected_state_sha256:
            raise ValueError("stale expected state revision; obtain Main's current snapshot")
        if requirement_id not in before["expected_work_map"]:
            raise ValueError("requirement not present in this job")
        bound = {item["media_id"]: item for item in before["manifest"]}
        entry = bound.get(media_id)
        if not entry or entry.get("media_type") not in {"photo", "video_frame"}:
            raise ValueError("image must be explicitly bound as photo/video_frame")
        if not entry.get("sha256") or entry["sha256"] != raw_sha:
            raise ValueError("input hash does not match the frozen manifest")
        previous = before["quality"].get(media_id)
        if previous and (previous["sha256"] != raw_sha or
                         previous["opencv_version"] != cv2.__version__):
            raise ValueError("existing quality event conflicts; do not overwrite historical CV")

        output.mkdir(parents=True, mode=0o700)
        persisted = False
        try:
            if previous:
                state = before
                measurement_mode = "idempotent_reuse_NOT_fresh"
            else:
                with tempfile.TemporaryDirectory(prefix="f03-input-") as tmp:
                    staged = Path(tmp) / ("input" + image.suffix)
                    staged.write_bytes(raw)
                    store = PersistentJobLoop(db)
                    try:
                        state = store.measure_image(job_id, media_id, staged)
                    finally:
                        store.close()
                persisted = True
                measurement_mode = "fresh_opencv_execution"
            reopened, events = read_snapshot(db, job_id)
            if reopened != state:
                raise ValueError("state changed during run; no stable snapshot can be claimed")
            if len(events) != len(before_events) + (0 if previous else 1):
                raise ValueError("unexpected concurrent event count")
            q = state["quality"][media_id]
            selected = next(d for d in state["component_decisions"]
                            if d["requirement_id"] == requirement_id)
            # Assertions protect the runner itself from ever introducing acceptance.
            if state["professional_acceptance"] != before["professional_acceptance"]:
                raise ValueError("quality processing must not alter professional acceptance")
            artifacts = {
                "state.json": json.dumps(state, indent=2, ensure_ascii=False) + "\n",
                "trace.jsonl": "".join(json.dumps(e, ensure_ascii=False) + "\n" for e in events),
                "report.md": ("<!-- F03 saved state SHA-256: " + digest(state) + " -->\n"
                              + render_report(state)),
            }
            hashes = {}
            for name, text in artifacts.items():
                _write(output / name, text)
                hashes[name] = hashlib.sha256(text.encode("utf-8")).hexdigest()
            receipt = {
                "receipt_schema": 1, "task_id": "F03", "job_id": job_id,
                "requirement_id": requirement_id, "media_id": media_id,
                "created_at": datetime.now(timezone.utc).isoformat(),
                "source_commit_declared": source_commit, "input_basis_declared": input_basis,
                "execution_environment": "not_cloud_attested", "runtime": info,
                "development_only": development_only, "measurement_mode": measurement_mode,
                "input_sha256": raw_sha, "before_state_sha256": digest(before),
                "state_sha256": digest(state), "trace_sha256": digest(events),
                "event_count_before": len(before_events), "event_count": len(events),
                "quality_event_id": q["event_id"], "image_action": q["next_action"],
                "requirement_decision": selected,
                "before_requirement_decision": next(d for d in before["component_decisions"]
                                                    if d["requirement_id"] == requirement_id),
                "requirement_decision_changed": selected != next(d for d in before["component_decisions"]
                                                                if d["requirement_id"] == requirement_id),
                "professional_acceptance": state["professional_acceptance"],
                "artifact_sha256": hashes,
                "verification_scope": "local_process_readback; see separate reopen result",
                "cloud_execution_proven": False,
            }
            _write(output / "receipt.json", json.dumps(receipt, indent=2, ensure_ascii=False) + "\n")
            # A genuinely separate process reopens the existing SQLite DB read-only.
            result = subprocess.run([
                sys.executable, "-m", "peaklogic_field_evidence.f03_runner", "verify",
                "--db", str(db), "--job-id", job_id,
                "--receipt", str(output / "receipt.json")],
                text=True, capture_output=True, timeout=60, check=True)
            child = json.loads(result.stdout)
            if child["status"] != "PASS":
                raise ValueError("child-process reopen verification failed")
            _write(output / "reopen.json", json.dumps(child, indent=2) + "\n")
            return receipt
        except Exception as exc:
            failure = {"status": "INCOMPLETE", "job_id": job_id,
                       "new_quality_event_committed": persisted,
                       "error_type": type(exc).__name__, "detail": str(exc),
                       "next_action": "Inspect the saved DB before retry; never infer a rollback or completed export."}
            try:
                _write(output / "failure.json", json.dumps(failure, indent=2) + "\n")
            except OSError:
                pass
            raise


def main() -> int:
    os.umask(0o077)
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    snapshot = sub.add_parser("snapshot")
    verify_p = sub.add_parser("verify")
    run = sub.add_parser("run")
    for command in (snapshot, verify_p, run):
        command.add_argument("--db", type=Path, required=True)
        command.add_argument("--job-id", required=True)
    verify_p.add_argument("--receipt", type=Path, required=True)
    for name in ("media-id", "requirement-id", "source-commit", "expected-state-sha256"):
        run.add_argument("--" + name, required=True)
    run.add_argument("--image", type=Path, required=True)
    run.add_argument("--output", type=Path, required=True)
    run.add_argument("--input-basis", choices=["synthetic_control", "preserved_field_input"], required=True)
    run.add_argument("--development-only", action="store_true",
                     help="Permit noncompetition runtime; permanently label the receipt")
    args = vars(parser.parse_args())
    command = args.pop("command")
    try:
        if command == "snapshot":
            state, events = read_snapshot(**args)
            result = {"job_id": args["job_id"], "state_sha256": digest(state),
                      "trace_sha256": digest(events), "event_count": len(events)}
        elif command == "verify":
            args["receipt_path"] = args.pop("receipt")
            result = verify(**args)
        else:
            result = run_image(**args)
        print(json.dumps(result, ensure_ascii=False))
        return 0
    except (ValueError, OSError, sqlite3.Error, cv2.error,
            subprocess.SubprocessError) as exc:
        print(json.dumps({"status": "BLOCKED_OR_INCOMPLETE", "error": str(exc)}), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
