# Local Validation Report - Build Increment 0

Date: 2026-08-31
Work order: VEG-2026-0001

## Result
**Functional scaffold: PASS for local development**
**Competition OpenCV 5 runtime gate: BLOCKED in this execution container, correctly rejected by doctor**

## Tests
- 15/15 pytest tests passed under the locally available OpenCV 4.13.0 runtime.
- Python compileall passed.
- Git working tree clean after commit.

## Work-order scanner smoke test
Synthetic photographed work order:
- document detected: yes
- perspective correction: yes
- OCR task: `INSTALL SAFETY ANCHOR`
- normalized job id: `A-101`
- known template: `fall_protection_anchor_demo_v1`
- quality-critical workflow flag: true
- next action: load approved template

## Agentic policy smoke trace
1. Blurred capture -> `RETAKE`
2. At `before_cover` with missing critical proof -> `REMIND_CRITICAL_PROOF`
3. All required visual proofs accepted -> `PREPARE_REVIEW_PACKET`
4. Professional review status remains `pending`

## Exact runtime gate
Local `doctor` output:
- OpenCV: 4.13.0
- DNN available: yes
- competition runtime OK: false

This is expected and intentionally blocking. The competition target is pinned to:
`opencv-contrib-python-headless==5.0.0.93`

OpenCV 5.0.0 and corresponding Python wheels are publicly released. This container cannot reach PyPI directly, so exact-runtime execution must occur in a clean connected environment or CI before Gate 0 is marked PASS.

## Not yet evidence
- learned proof-point classification
- representative roofing/safety-anchor dataset performance
- scene-association accuracy
- false-ready rate on representative packets
- AWS deployment/performance

No claim should imply those are complete.
