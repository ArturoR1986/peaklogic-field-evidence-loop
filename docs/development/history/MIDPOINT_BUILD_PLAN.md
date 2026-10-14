# Midpoint Build Plan

Updated: 2026-09-19
Target window: September 21–October 2 midpoint check-in

## Midpoint objective

Demonstrate a real, auditable Agentic Vision loop while clearly separating working mechanics from representative model performance.

## Current verified state

### Runtime
**PASS**
- OpenCV 5.0.0 in GitHub Actions
- DNN + img_hash available

### M1 — Agentic trace loop
**PASS**
- evidence observations change later actions
- JSONL audit trace
- stage-aware critical reminders
- missed-proof escalation
- explicit human review event

### M2 — Dataset tooling
**PASS / field media pending**
- labels and manifests
- provenance/rights/consent
- video candidate extraction
- representative-media capture protocol

### M3A — DNN plumbing and dataset integrity
**PASS**
- real ONNX graph loaded through `cv2.dnn.readNetFromONNX`
- inference runs through production classifier adapter
- group-aware split leakage audit
- conservative unverified rights defaults
- strict evaluation-readiness audit

### M3 — Representative proof-point classifier
**PRIMARY BLOCKER**
Still required:
- representative labeled media
- training
- ONNX model artifact
- held-out macro-F1 / confusion matrix
- representative UNKNOWN/low-confidence failures

### M4 — Scene association
**MECHANICS PASS / representative calibration pending**
- ORB/Hamming/RANSAC metrics
- heuristic score clearly labeled uncalibrated
- representative same-area/different-area pair evaluation still needed

### M5 — AWS
**CONTAINER SCAFFOLD PASS / LIVE DEPLOYMENT PENDING**
- Docker/OpenCV 5 artifact verified
- bounded uploads
- field authentication
- separate reviewer authorization
- fail-closed audit behavior
Still required:
- actual AWS resource
- durable state/trace
- logs/metrics
- cost/credit evidence

### M6 — Failure handling
**PASS for deterministic mechanics**
- 64/64 latest tests pass
- 9/9 failure matrix cases pass
- red-team defects repaired

## Midpoint demonstration

Use `docs/MIDPOINT_DEMO_RUNBOOK.md`.

Truthful current story:
1. OpenCV 5 runtime is proven.
2. bad media changes next action.
3. critical proof timing changes next action.
4. uncertainty / weak scene / tool failure fails safe.
5. state and human-review boundaries are auditable.
6. a real ONNX model can be loaded and inferred through OpenCV 5.
7. representative proof-point accuracy is intentionally not claimed yet.

## Next action

**Representative media -> rights/label review -> strict dataset audit -> training -> ONNX export -> OpenCV 5 DNN -> held-out metrics -> representative agent trace.**

## Stop conditions

Do not:
- broaden into generic construction QA,
- add other trades,
- call heuristic scene scores calibrated probabilities,
- call controlled labels predictions,
- call containerized software AWS-deployed,
- treat synthetic mechanics tests as representative performance,
- pursue COOL until the representative core loop is stable.
