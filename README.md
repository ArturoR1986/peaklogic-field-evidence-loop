# PeakLogic Field Evidence Loop

Competition build for **Process-Evidence Intelligence for Field Quality Workflows**.

> PeakLogic makes sure the office gets the proof it needs before the work hides it.

## Current build status

### Core mechanics
- **Build Gate 0 — OpenCV 5 runtime: PASS**
- **M1 — Executable Agentic Evidence Loop: PASS**
- **M2 — Dataset/provenance tooling: PASS**
- **M3A — Real ONNX/OpenCV DNN path + dataset integrity audit: PASS**
- **M4 — Scene-association mechanics + evaluation harness: PASS**
- **M5 — AWS-ready container scaffold: PASS; live AWS deployment pending**
- **M6 — Deterministic failure matrix: PASS**

Latest verified competition-runtime evidence:
- OpenCV **5.0.0**
- `opencv-contrib-python-headless==5.0.0.93`
- real `cv2.dnn.readNetFromONNX` load/inference smoke: PASS
- pytest: **64/64 PASS**
- deterministic failure matrix: **9/9 PASS**
- Docker image builds and boots under OpenCV 5
- field/evidence and professional-review HTTP credentials are separated
- audit persistence failure rolls back evidence state
- weak scene confidence cannot silently satisfy a proof point
- professional review remains explicit and human-owned

## Primary credibility bottleneck

**Representative field media and measured proof-point vision performance.**

The next meaningful competition evidence must come from:
1. real or safely staged fall-protection-anchor / roofing media,
2. reviewed rights/provenance and proof-point labels,
3. group-safe train/validation/test splits,
4. a bounded classifier trained and exported to ONNX,
5. inference through OpenCV 5 DNN,
6. held-out confusion matrix / macro-F1,
7. representative scene-pair and failure testing,
8. a real AWS-hosted execution trace.

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
