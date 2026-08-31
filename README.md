# PeakLogic Field Evidence Loop

Competition build scaffold for **Process-Evidence Intelligence for Field Quality Workflows**.

> PeakLogic makes sure the office gets the proof it needs before the work hides it.

## Build Increment 0

This repo currently implements the deterministic foundation:

- work-order document detection, perspective correction, cleanup, OCR handoff
- approved demo Proof-Point Template matching
- deterministic image quality analysis
- bounded video frame sampling and near-duplicate reduction
- typed evidence state
- critical-proof reminder and missed-proof exception policy
- strict OpenCV 5 runtime doctor

**Not yet implemented:** learned proof-point recognition, representative scene association benchmark, AWS deployment, UI, final report generator.

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

The competition runtime is pinned to `opencv-contrib-python-headless==5.0.0.93`. OpenCV publishes CPU-only headless wheels for server/cloud use; install only one OpenCV wheel family in an environment.

System dependency for the current OCR adapter: Tesseract OCR.

## Quick commands

```bash
peaklogic-evidence doctor
peaklogic-evidence analyze-image path/to/photo.jpg
peaklogic-evidence sample-video path/to/walkthrough.mp4
peaklogic-evidence scan-work-order path/to/work_order.jpg --output-cleaned outputs/cleaned.png
```

## Safety boundary

The prototype validates evidence readiness. It does **not** certify a fall-protection anchor, workmanship, code compliance, manufacturer compliance, or safe use. See `docs/TRUST_BOUNDARIES.md`.
