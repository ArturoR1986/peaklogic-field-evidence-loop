# Build Gates

## Gate 0 - Exact runtime
**PASS**

`peaklogic-evidence doctor` reports OpenCV 5.0.0 in GitHub Actions.
Pinned target: `opencv-contrib-python-headless==5.0.0.93`.

## Gate 1 - Deterministic evidence mechanics
**PASS**

- work-order page detection/perspective correction
- OCR handoff + known-template mapping
- image quality gate
- bounded video sampling/redundancy reduction
- evidence-state + critical-proof reminder/exception policy
- executable audit trace

## Gate 2 - Proof-point recognition
**ADAPTER PASS / MODEL + REPRESENTATIVE EVALUATION PENDING**

The OpenCV 5 DNN ONNX adapter is implemented and tested.
Gate 2 passes only when:
- representative labeled media exists
- a bounded classifier is trained
- model is exported to ONNX
- inference runs through OpenCV 5 DNN
- macro-F1/confusion matrix are reported
- UNKNOWN/unsupported behavior is tested
- no fake rule/filename classifier is substituted

## Gate 3 - Scene association
**MECHANICS PASS / REPRESENTATIVE THRESHOLD PENDING**

OpenCV ORB/Hamming/RANSAC metrics and the evaluation harness exist.
No calibrated or production scene-association threshold is claimed until representative same-area/different-area pairs are evaluated.

## Gate 4 - End-to-end agent trace
**MECHANICS PASS**

OpenCV quality and duplicate results change later actions in an auditable trace.
Final competition-quality Gate 4 requires representative classifier output to participate in the same loop.

## Gate 5 - Representative evaluation
**PROTOCOL PASS / REAL MEDIA PENDING**

The evaluation protocol is predeclared.
Representative media must provide proof-point macro-F1, false-ready rate, missed-reminder rate, scene-pair results, duplicate metrics, video-reduction coverage, and failure cases.

## Gate 5A - Failure handling
**DETERMINISTIC MATRIX IN PROGRESS**

Must prove safe behavior for:
- blurred media
- duplicate evidence
- unsupported/low-confidence proof
- weak scene association
- missed proof after concealment
- unavailable classifier/tool
- failed trace persistence
- explicit human review

Representative field failures are still required later.

## Gate 6 - AWS
**DEPLOYMENT SCAFFOLD PASS / NO AWS RESOURCE CLAIMED YET**

Docker artifact builds and boots under OpenCV 5.
AWS passes only after a meaningful component is actually deployed with reproducible instructions, logs, bounded cost, privacy controls, authentication, and durable enough state for the demo.
