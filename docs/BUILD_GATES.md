# Build Gates

## Gate 0 - Exact runtime
Pass only when `peaklogic-evidence doctor` reports OpenCV major 5 in the build/CI environment.
Pinned target: `opencv-contrib-python-headless==5.0.0.93`.

## Gate 1 - Deterministic evidence mechanics
- work-order page detection/perspective correction
- OCR handoff + known-template mapping
- image quality gate
- bounded video sampling/redundancy reduction
- evidence-state + critical-proof reminder/exception policy

## Gate 2 - Proof-point recognition
Requires representative labeled media. Train a bounded classifier, export ONNX, run inference through OpenCV 5 DNN, measure macro-F1/confusion matrix. No fake rule/filename classifier.

## Gate 3 - Scene association
Measure related/unrelated scene pairs with explicit confidence and failure handling. Registration remains optional.

## Gate 4 - End-to-end agent trace
OpenCV result must change a later action: rescan, retake, reject duplicate, request proof/context, critical reminder, exception/human review, or review-packet preparation.

## Gate 5 - Representative evaluation
Run on staged/representative roofing media; report false-ready rate, missed-reminder rate, proof-point recall, video reduction, and failure cases.

## Gate 6 - AWS
Deploy a meaningful component on AWS with reproducible instructions, logs, bounded cost, and privacy controls.
