# Competition Evaluation Protocol

Status: PREDECLARED BEFORE REPRESENTATIVE MODEL RESULTS

## Purpose
Define the measures before tuning the final model so the competition report distinguishes genuine evaluation from post-hoc storytelling.

## Proof-point recognition
Primary metric:
- macro-F1 across the declared proof-point label set, including `unsupported`

Also report:
- confusion matrix
- per-class precision/recall/F1/support
- overall accuracy
- confidence threshold
- number of low-confidence results routed to `unsupported` / targeted recapture

The held-out test split must not be used for threshold tuning.

## Agentic task effectiveness
Report:
- next-action categorical accuracy against curated expected-action scenarios
- false-READY rate: incomplete evidence packets incorrectly marked ready / all truly incomplete packets
- missed-reminder rate: required pre-concealment reminders not emitted / all cases where reminder was required

False READY is treated as more serious than an unnecessary extra capture.

## Scene association
Create representative pairs:
- same work area, changed viewpoint/lighting/progress
- different but visually similar work areas

Report transparent OpenCV metrics first:
- keypoints
- good matches
- RANSAC inliers
- inlier ratio
- association score

The initial score is explicitly heuristic. A decision threshold is selected only from training/validation data and then frozen before held-out evaluation.

## Duplicate detection
On labeled image pairs report:
- precision
- recall
- false duplicate rate
- false novel-view rate

## Video reduction
For short walkthroughs report:
- decoded/sample candidate count
- retained non-redundant frame count
- reduction ratio
- human-rated proof-point coverage retained after reduction

## Operational / UX measures
For staged workflows record:
- worker interactions/taps
- words typed
- capture time
- targeted recapture count
- office reconstruction/relabeling time
- unresolved proof points at task close

## Performance / cloud
Record on the AWS deployment:
- processing latency p50/p95
- image/video sizes
- runtime/container configuration
- request failure rate
- approximate AWS cost / grant-credit use

## Failure-case policy
Publish meaningful failures:
- low texture
- severe viewpoint shift
- glare/shadow
- occlusion
- visually similar roof areas
- unsupported evidence
- missing proof after concealment

Do not count synthetic fixtures as representative performance evidence.
