# PeakLogic Field Evidence Loop

Competition build for **Process-Evidence Intelligence for Field Quality Workflows**.

> PeakLogic makes sure the office gets the proof it needs before the work hides it.

## Current build status

### 2 October 2026 — approved persistent Job Loop priority

The current build follows Aurelian's reviewed v0.2 handoff: persistent Trial 001
Days 1–6 replay first, then Trial 002 through the same job contract. Standalone
CV measurement and live AWS remain downstream. Historical gates below retain
their original scope.

The new SQLite adapter stores immutable job events and derives component/zone
progress, evidence decisions and daily/weekly/closed-record reports. OpenCV 5
supplies image quality, video sampling and scene-continuity measurements;
semantic bindings are explicitly manual. Missing proof and professional
acceptance stay separate from visible progress.

See [implementation and replay report](docs/trials/PERSISTENT_JOB_LOOP_BUILD_REPORT_2026_10_02.md)
and [replay instructions](docs/PERSISTENT_JOB_LOOP.md). The frozen replay includes
all retrieved photos, but component-level semantic review remains partial and
the original Day 1 walkthrough raw file was not located.

### Core mechanics
- **Build Gate 0 — OpenCV 5 runtime: PASS**
- **M1 — Executable Agentic Evidence Loop: PASS**
- **M2 — Dataset/provenance tooling: PASS**
- **M3A — Real ONNX/OpenCV DNN path + dataset integrity audit: PASS**
- **M4 — Scene-association mechanics + evaluation harness: PASS**
- **M5 — AWS-ready container scaffold: PASS; live AWS deployment pending**
- **M6 — Deterministic failure matrix: PASS**
- **Trial 001 — Field capture Days 1–6: CLOSED; processing/evaluation continues**

Latest verified competition-runtime evidence:
- OpenCV **5.0.0**
- `opencv-contrib-python-headless==5.0.0.93`
- real `cv2.dnn.readNetFromONNX` load/inference smoke: PASS
- pytest: **77/77 PASS**
- deterministic failure matrix: **9/9 PASS**
- Docker image builds and boots under OpenCV 5
- packaged work-order scan -> OCR -> proof-template path: PASS
- field/evidence and professional-review HTTP credentials are separated
- audit persistence failure rolls back evidence state
- weak scene confidence cannot silently satisfy a proof point
- professional review remains explicit and human-owned
- unbound media cannot silently satisfy a job proof point
- long walkthrough sampling now preserves full-duration coverage

## Trial 001 — real representative evidence

The first real-job trial now has a closed six-day field record from:
- 33 photographed work-order / planning / drawing pages
- Day 1 arrival/setup/pre-install stills + walkthrough video
- Day 2 tapered-insulation / installation media
- Day 3 waterproofing / perimeter / drain-detail media
- Day 4 continued field-progress media
- Day 5 raw photos + one raw video
- Day 6 final raw field capture: 30 received JPEGs archived in Drive; the final ten await independent review

No Day 7 or later data will be provided for this work order. PeakLogic must treat the current Trial 001 dataset as the complete available field record.

Representative field-trial findings:
- 26/26 stills passed current deterministic image-quality thresholds
- no still pair crossed the strict average-hash near-duplicate threshold
- strong repeated-view ORB/RANSAC scene matches were observed
- a real walkthrough truncation defect was found, repaired, regression-tested, and merged
- the work-order page contains explicit photo-documentation requirements, including critical anchorage-point photo evidence and pre-departure photo submission

See:
- `docs/trials/TRIAL_001_REAL_JOB_ORIENTATION.md`
- `docs/trials/TRIAL_001_DAYS_1_3_REVIEW_AND_HANDOFF_2026_09_24.md`
- `docs/trials/TRIAL_001_FIELD_CAPTURE_COMPLETE_2026_09_25.md`
- GitHub Issue #20 for closed field intake and Issue #23 for the open technical evaluation
- `docs/trials/TRIAL_001_OPENCV5_REPRESENTATIVE_RUNTIME_PROOF_2026_09_26.md` for the pinned-wheel representative quality/association probe (not an end-to-end measurement)

## Primary credibility bottleneck

**One source-grounded representative OpenCV 5 measurement proven end-to-end, then the same narrow path live on AWS.**

The next meaningful competition evidence must now come from the closed Trial 001 record:
1. implement the minimal persistent Job Progress State,
2. bind one source-grounded Sarnabar requirement to a real component/zone,
3. run the measurement in the exact pinned OpenCV 5 container,
4. preserve scale derivation, detections, measurement, uncertainty and next action,
5. include an abstain/failure case,
6. produce representative evaluation evidence,
7. run the same narrow path on live AWS,
8. build the judge-facing demo around that exact chain.

Do not broaden the product until that evidence exists.

## Evaluation integrity

Dataset candidates default to **unverified** rights/provenance/consent until reviewed.

Run strict audit before training/final evaluation:

```bash
python scripts/audit_dataset_manifest.py path/to/manifest.jsonl --strict
```

Frames from the same video or related job group may not cross train/validation/test boundaries.

## Midpoint commands

```bash
peaklogic-evidence doctor
peaklogic-evidence trace-demo --trace outputs/agentic_trace_demo.jsonl
python scripts/run_failure_matrix.py --output outputs/failure_matrix.json
pytest
```

Important: proof-point labels in the current mechanics demo are controlled inputs until a representative classifier is trained and evaluated. They must not be described as model predictions.

See:
- `docs/MIDPOINT_DEMO_RUNBOOK.md`
- `docs/MIDPOINT_BUILD_PLAN.md`
- `docs/REPRESENTATIVE_MEDIA_CAPTURE_PROTOCOL.md`
- `docs/DATASET_GUIDE.md`
- `docs/EVALUATION_PROTOCOL.md`
- `docs/FAILURE_MATRIX.md`
- `docs/DOMAIN_REFERENCE_ANCHOR_DOCUMENTATION.md`
- `docs/JOB_ORIENTATION_AND_EVIDENCE_CONTRACT.md`
- `docs/AWS_DEPLOYMENT_PLAN.md`
- `docs/BUILD_GATES.md`

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -e ".[dev]"
peaklogic-evidence doctor
pytest
```

The competition runtime is pinned to `opencv-contrib-python-headless==5.0.0.93`.

## Safety boundary

The prototype validates evidence readiness. It does **not** certify a fall-protection anchor, workmanship, code compliance, manufacturer compliance, warranty status, structural capacity, or safe use. Professional approval remains human-owned.
