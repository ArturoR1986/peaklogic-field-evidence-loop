# Midpoint Build Plan

Date: 2026-09-19
Target window: September 21–October 2 midpoint check-in

## Midpoint objective

Show one real execution of:

media -> OpenCV 5 -> evidence observation -> EvidenceState -> next action or human escalation -> auditable trace

## Current build state

### M1 — Agentic trace runner
**PASS / OpenCV 5 CI verified**

- executable EvidenceLoop
- JSONL audit trace
- retake / duplicate / reminder / escalation / review-packet actions
- explicit human review event
- trace persistence failure rolls back associated state

### M2 — Dataset tooling
**TOOLING PASS / representative media pending**

- proof-point labels
- manifest schema
- provenance / rights / consent fields
- video candidate-frame extraction
- raw/candidate media excluded from Git by default
- representative media capture protocol

### M3 — Proof-point recognition
**OpenCV DNN adapter PASS / trained model pending**

Ready:
- ONNX/OpenCV DNN adapter
- confidence threshold / unsupported behavior
- model-vs-controlled-input provenance

Blocked on:
- representative labeled media
- trained model
- ONNX artifact
- held-out metrics

### M4 — Scene association
**MECHANICS PASS / representative calibration pending**

Ready:
- ORB feature extraction
- Hamming matching
- RANSAC geometry metrics
- explicit heuristic score

Still needed:
- same-area/different-area representative pairs
- validation-set threshold selection
- held-out results

### M5 — AWS
**Container scaffold PASS / live AWS deployment pending**

Ready:
- containerized OpenCV 5 service
- bounded uploads
- evidence API authentication
- separate professional-review credential
- Docker CI health check

Still needed:
- live AWS resource
- durable state/trace
- logs/metrics
- cost/credit evidence

### M6 — Failure handling
**DETERMINISTIC MATRIX PASS**

Verified under OpenCV 5:
- 58/58 tests passing
- 9/9 deterministic failure scenarios passing

Red-team caught and fixed:
- weak scene confidence was previously able to enter accepted proof before a recapture decision
- professional review initially shared a credential with field/evidence actions

## Midpoint demonstration

Use `docs/MIDPOINT_DEMO_RUNBOOK.md`.

Minimum credible midpoint:
1. OpenCV 5 runtime proof
2. blurred input -> RETAKE
3. concealment boundary -> REMIND_CRITICAL_PROOF
4. unsupported / weak-scene input -> targeted proof
5. missed proof -> human escalation
6. audit trace
7. explicit professional-review boundary
8. Docker/OpenCV 5 service artifact
9. truthful statement of representative-model status

## Primary next move

Representative media -> label review -> split/leakage audit -> train/export ONNX -> OpenCV 5 DNN -> measured results -> representative Agentic Vision trace.

## Stop conditions

Do not:
- broaden into generic construction QA
- add other trades
- treat heuristic scene score as calibrated probability
- call controlled labels model predictions
- call containerized software AWS-deployed
- pursue COOL before representative core-loop evidence is stable
