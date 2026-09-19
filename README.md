# PeakLogic Field Evidence Loop

Competition build for **Process-Evidence Intelligence for Field Quality Workflows**.

> PeakLogic makes sure the office gets the proof it needs before the work hides it.

## Current build status

### Build Gate 0 — Exact OpenCV 5 runtime: PASS
Verified in GitHub Actions:
- OpenCV 5.0.0
- `opencv-contrib-python-headless==5.0.0.93`
- DNN available
- image hashing available

### M1 — Executable Agentic Evidence Loop: PASS
### M2 — Dataset / provenance tooling: PASS (representative media still needed)
### M3 — OpenCV DNN adapter: PASS; trained representative model still pending
### M4 — Scene-association mechanics + evaluation harness: PASS; representative threshold still pending
### M5 — AWS-ready container scaffold: PASS; no live AWS resource claimed yet
### M6 — Deterministic red-team failure matrix: PASS

Latest verified build:
- pytest: **58/58 passing** under OpenCV 5.0.0
- failure matrix: **9/9 passing**
- Docker image builds and boots under OpenCV 5
- field/evidence and professional-review HTTP credentials are separated
- failed audit persistence rolls back evidence state
- professional review remains explicit and human-owned

## Main credibility bottleneck

Representative field media and measured proof-point vision performance.

The next competition evidence must come from:
1. real or safely staged fall-protection-anchor / roofing media,
2. reviewed labels and rights/provenance,
3. a bounded classifier trained/exported to ONNX,
4. inference through OpenCV 5 DNN,
5. held-out confusion matrix / macro-F1,
6. representative scene-pair and failure testing,
7. a live AWS execution trace.

Do not broaden the product until that evidence exists.

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
- `docs/AGENTIC_VISION_GAP_REVIEW.md`
- `docs/MIDPOINT_BUILD_PLAN.md`
- `docs/DATASET_GUIDE.md`
- `docs/REPRESENTATIVE_MEDIA_CAPTURE_PROTOCOL.md`
- `docs/EVALUATION_PROTOCOL.md`
- `docs/FAILURE_MATRIX.md`
- `docs/BUILD_GATES.md`

## Setup

```bash
python -m venv .venv
# Linux/macOS
source .venv/bin/activate
# Windows PowerShell
# .venv\\Scripts\\Activate.ps1
pip install --upgrade pip
pip install -e ".[dev]"
peaklogic-evidence doctor
pytest
```

The competition runtime is pinned to `opencv-contrib-python-headless==5.0.0.93`. Install only one OpenCV wheel family in an environment.

System dependency for the current OCR adapter: Tesseract OCR.

## Safety boundary

The prototype validates evidence readiness. It does **not** certify a fall-protection anchor, workmanship, code compliance, manufacturer compliance, warranty status, or safe use. See `docs/TRUST_BOUNDARIES.md`.
