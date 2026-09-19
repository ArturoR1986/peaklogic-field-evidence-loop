# PeakLogic Field Evidence Loop

Competition build for **Process-Evidence Intelligence for Field Quality Workflows**.

> PeakLogic makes sure the office gets the proof it needs before the work hides it.

## Current build status

**Build Gate 0 — Exact OpenCV 5 runtime: PASS**

Verified in GitHub Actions:
- OpenCV 5.0.0
- `opencv-contrib-python-headless==5.0.0.93`
- DNN available
- image hashing available
- 15/15 foundation tests passing

### Active build branch

`build/m1-agentic-trace-and-dataset-tooling`

Local branch validation:
- executable EvidenceLoop orchestration
- append-only JSONL audit trace
- OpenCV quality result -> RETAKE action
- concealment boundary -> critical-proof reminder
- low-confidence proof -> targeted recapture
- duplicate evidence -> rejected as new proof
- complete evidence -> review packet
- professional review remains pending
- dataset manifest/provenance tooling
- 25/25 local tests passing before OpenCV 5 CI review

## Build Increment 0 foundation

- work-order document detection, perspective correction, cleanup, OCR handoff
- approved demo Proof-Point Template matching
- deterministic image quality analysis
- bounded video frame sampling and near-duplicate reduction
- typed evidence state
- critical-proof reminder and missed-proof exception policy
- strict OpenCV 5 runtime doctor

## Midpoint commands

```bash
peaklogic-evidence doctor
peaklogic-evidence trace-demo --trace outputs/agentic_trace_demo.jsonl
pytest
```

Important: proof-point labels in the current mechanics demo are controlled inputs until a representative classifier is trained and evaluated. They must not be described as model predictions.

See:
- `docs/AGENTIC_VISION_GAP_REVIEW.md`
- `docs/MIDPOINT_BUILD_PLAN.md`
- `docs/DATASET_GUIDE.md`
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

## Quick commands

```bash
peaklogic-evidence doctor
peaklogic-evidence analyze-image path/to/photo.jpg
peaklogic-evidence sample-video path/to/walkthrough.mp4
peaklogic-evidence scan-work-order path/to/work_order.jpg --output-cleaned outputs/cleaned.png
peaklogic-evidence trace-demo --trace outputs/agentic_trace_demo.jsonl
```

## Safety boundary

The prototype validates evidence readiness. It does **not** certify a fall-protection anchor, workmanship, code compliance, manufacturer compliance, or safe use. See `docs/TRUST_BOUNDARIES.md`.
