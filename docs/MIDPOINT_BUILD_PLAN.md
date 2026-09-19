# Midpoint Build Plan

Date: 2026-09-19
Target window: September 21–October 2 midpoint check-in

## Midpoint objective

Show one real execution of:

media -> OpenCV 5 -> evidence observation -> agent/state decision -> action or human escalation -> trace

The midpoint demo does not need the final UI. It must prove the architecture is alive.

## Build sequence

### M1 — Agentic trace runner
Status: PASS / OPEN CV 5 CI VERIFIED

Implemented:
1. known proof-template loading
2. photo ingestion
3. OpenCV quality + duplicate checks
4. EvidenceState update
5. deterministic next-action policy
6. append-only JSONL audit trace
7. review-packet generation
8. CLI demo command
9. tests for retake, reminder, escalation, duplicate rejection, low-confidence targeting, missed-proof exception consistency, and review-ready state

CI result:
- OpenCV 5.0.0
- 26/26 tests passed

Important boundary:
Proof-point labels in the mechanics demo are controlled inputs until M3 supplies a measured classifier. They are not represented as model predictions.

### M2 — Dataset tooling
Status: TOOLING PASS / REPRESENTATIVE MEDIA PENDING

Implemented:
- dataset folder convention
- label schema for the anchor workflow
- train/validation/test/unassigned manifest support
- provenance + rights + consent fields
- video-to-candidate-frame extraction utility
- raw/candidate media protected from Git history by default

Initial labels:
- location_context
- product_identification
- substrate_context
- critical_attachment
- process_before_cover
- finished_detail
- finished_context
- unsupported

### M3 — First real proof-point classifier
Status: BLOCKED ON REPRESENTATIVE LABELED MEDIA

Deliverables:
- bounded classifier
- ONNX export
- OpenCV 5 DNN inference adapter
- confidence threshold + UNKNOWN behavior
- confusion matrix + macro-F1
- test proving low-confidence output does not satisfy a proof point

### M4 — Scene association
Only after proof-point recognition is working.

Deliverables:
- same-area / different-area pair benchmark
- confidence output
- failure handling
- no dependency on geometric registration

### M5 — AWS midpoint deployment
Deploy the smallest meaningful cloud slice.

Minimum target:
- upload/request endpoint
- OpenCV 5 processing service
- evidence-state persistence
- structured logs
- bounded media size and retention notes

Do not optimize cost or COOL until the core loop works.

## Midpoint demo script

1. Scan/load a known work order.
2. Show the approved proof template.
3. Submit a blurred image -> RETAKE.
4. Submit corrected evidence -> state update.
5. Reach a concealment boundary with missing critical proof -> REMIND_CRITICAL_PROOF.
6. Submit proof -> state updates.
7. Demonstrate one low-confidence/unsupported case -> REQUEST_TARGETED_PROOF or ESCALATE_HUMAN.
8. Produce review packet + trace.
9. State clearly: professional approval remains pending.

## Evidence to show OpenCV

- OpenCV 5 runtime doctor output
- image quality metrics
- duplicate evidence handling
- video reduction/frame timestamps where used
- proof-point classifier output once M3 is ready
- action trace showing a later decision changed because of OpenCV output

## Success threshold for midpoint

PASS if:
- end-to-end trace runs without hand-editing state
- at least one OpenCV result changes the next action
- the trace is auditable
- human approval boundary is preserved
- one AWS-hosted component is running or deployment is demonstrably in progress

## Stop conditions

Do not:
- build generic construction QA
- add more trades
- build final customer prose
- claim workmanship certification
- pursue COOL before the core loop is stable
