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
**ADAPTER IN PROGRESS / MODEL + REPRESENTATIVE EVALUATION PENDING**

The OpenCV 5 DNN ONNX adapter may be implemented and unit-tested before real data exists.
Gate 2 passes only when:
- representative labeled media exists
- a bounded classifier is trained
- model is exported to ONNX
- inference runs through OpenCV 5 DNN
- macro-F1/confusion matrix are reported
- UNKNOWN/unsupported behavior is tested
- no fake rule/filename classifier is substituted

## Gate 3 - Scene association
Measure related/unrelated scene pairs with explicit confidence and failure handling. Registration remains optional.

## Gate 4 - End-to-end agent trace
**MECHANICS PASS**

OpenCV quality and duplicate results already change later actions in an auditable trace.
Final competition-quality Gate 4 requires representative classifier output to participate in the same loop.

## Gate 5 - Representative evaluation
Run on staged/representative roofing media; report false-ready rate, missed-reminder rate, proof-point recall, video reduction, and failure cases.

## Gate 6 - AWS
**DEPLOYMENT SCAFFOLD IN PROGRESS / NO AWS RESOURCE CLAIMED YET**

Deploy a meaningful component on AWS with reproducible instructions, logs, bounded cost, privacy controls, and durable enough state for the demo.
