"""Synthetic F03 controls only. NOT a real-field or AWS attestation."""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path

import cv2
import numpy as np
from peaklogic_field_evidence.f03_runner import digest, read_snapshot, run_image, verify
from peaklogic_field_evidence.job_packet import JobEvidenceRecord
from peaklogic_field_evidence.job_progress import PersistentJobLoop


def make_fixture(root: Path, kind="sharp", checkability="visual", zone="roof", closed=False):
    root.mkdir(parents=True, exist_ok=True)
    image = root / "input.png"
    if kind == "corrupt":
        image.write_bytes(b"synthetic undecodable image")
    else:
        pixels = (np.random.default_rng(7).integers(30, 220, (400, 400, 3), dtype=np.uint8)
                  if kind == "sharp" else np.full((400, 400, 3), 120, dtype=np.uint8))
        assert cv2.imwrite(str(image), pixels)
    sha = hashlib.sha256(image.read_bytes()).hexdigest()
    db = root / "job.sqlite3"
    store = PersistentJobLoop(db)
    try:
        record = JobEvidenceRecord("F03-synthetic", "SYNTHETIC-WO", "persistent", "0.2", "installation",
                                   work_order_artifacts=["source"])
        manifest = [dict(media_id="source", job_id=record.job_id, provenance="synthetic fixture", day=0, media_type="document_scan")]
        manifest += [dict(media_id=mid, job_id=record.job_id, provenance="synthetic fixture; NOT field evidence",
                         day=1, media_type="photo", sha256=sha) for mid in ("a", "b")]
        store.create(record, manifest)
        req = dict(requirement_id="required-photo", name="Synthetic photo control",
            requirement_statement="SYNTHETIC: record the required detail",
            source=dict(source_id="source", source_kind="work_order", document_name="SYNTHETIC-WO",
                        locator="test only", excerpt="SYNTHETIC: record the required detail"),
            evidence_question="Does the declared synthetic evidence qualify?",
            visual_checkability=checkability, capture_before_stage="covering_started")
        store.append(record.job_id, "req", "requirement",
                     dict(requirement=req, component="detail", zone="roof", authority="synthetic_work_order"), day=0)
        for mid in ("a", "b"):
            store.append(record.job_id, "obs-" + mid, "observation",
                dict(media_id=mid, actor="synthetic-reviewer", method="synthetic_manual_annotation",
                     statement="Controlled annotation; no semantic model prediction", component="detail", zone=zone), day=1)
            store.append(record.job_id, "link-" + mid, "link",
                dict(requirement_id="required-photo", observation_id="obs-" + mid,
                     status="supported", modality="visual", human_confirmed=True,
                     capture_provenance_verified=True), day=1)
        if closed:
            store.append(record.job_id, "closed", "close_record", dict(source_ids=["source"]), day=6)
    finally:
        store.close()
    return db, image


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=["run", "verify"])
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--source-commit")
    parser.add_argument("--development-only", action="store_true")
    args = parser.parse_args()
    if args.command == "verify":
        index = json.loads((args.output_dir / "index.json").read_text())
        results = [verify(args.output_dir / case / "job.sqlite3", "F03-synthetic",
                          args.output_dir / case / "run" / "receipt.json") for case in index["cases"]]
        print(json.dumps({"status": "PASS", "basis": "synthetic_controls", "reopened": results}))
        return
    if not args.source_commit:
        parser.error("run requires --source-commit")
    if args.output_dir.exists():
        parser.error("use a new output directory")
    results = []
    for kind in ("sharp", "blur", "corrupt"):
        db, image = make_fixture(args.output_dir / kind, kind=kind, closed=kind != "sharp")
        before, _ = read_snapshot(db, "F03-synthetic")
        r = run_image(db=db, job_id="F03-synthetic", media_id="a", requirement_id="required-photo",
            image=image, output=args.output_dir / kind / "run", source_commit=args.source_commit,
            expected_state_sha256=digest(before), input_basis="synthetic_control", development_only=args.development_only)
        assert r["measurement_mode"] == "fresh_opencv_execution"
        assert r["professional_acceptance"]["status"] == "pending"
        if kind == "sharp":
            assert r["requirement_decision"]["status"] == "supported"
            assert r["image_action"] == "continue_review"
        else:
            assert r["requirement_decision"]["status"] != "supported"
            assert r["requirement_decision"]["next_action"]["action"] == "escalate_human"
            assert r["image_action"] == "record_quality_exception"
        results.append({"case": kind, "state_sha256": r["state_sha256"],
                        "action": r["requirement_decision"]["next_action"]["action"]})
    (args.output_dir / "index.json").write_text(json.dumps({"cases": ["sharp", "blur", "corrupt"]}) + "\n")
    print(json.dumps({"status": "PASS", "basis": "synthetic_controls_NOT_field_evidence",
                      "aws_execution_attested": False, "results": results}))


if __name__ == "__main__":
    main()
