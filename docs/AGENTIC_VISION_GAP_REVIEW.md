# Agentic Vision Gap Review

Date: 2026-09-19
Competition target: OpenCV AI Competition 2026
Primary path: Agentic Vision
Current branch: main

## Current strengths

- OpenCV 5.0.0 runtime is verified in GitHub Actions.
- 15/15 tests pass in the competition runtime.
- Work-order scan / perspective correction / OCR handoff exists.
- Approved proof-point templates exist.
- Image quality analysis and bounded video frame reduction exist.
- Evidence state and deterministic next-action policy exist.
- Critical-proof reminder and missed-proof exception behavior exist.
- Professional approval remains human-owned.

## Agentic Vision rubric gap map

### 1. Substantive OpenCV 5 + agent integration — 30%
Current: PARTIAL

Working:
- image quality metrics
- video sampling / novelty reduction
- document scan
- OpenCV runtime verification

Missing:
- learned proof-point recognition
- measured scene association
- one executable agent/orchestrator that consumes OpenCV outputs and records the resulting action

Pass condition:
- OpenCV output changes the next action in a recorded end-to-end trace
- proof-point recognition runs through OpenCV 5 DNN
- no simulated classifier output in the final evaluation

### 2. Orchestration + appropriate autonomy — 25%
Current: PARTIAL / STRONG FOUNDATION

Working:
- deterministic policy supports retake, duplicate rejection, targeted proof request, critical reminder, human escalation, review-packet preparation

Missing:
- executable orchestration loop
- persisted action/decision trace
- explicit tool/action boundary for human approval

Pass condition:
- one command/API call can run media -> perception -> state update -> next action -> trace
- human-only decisions are blocked from autonomous approval

### 3. Task effectiveness + evaluation — 20%
Current: WEAK / SYNTHETIC ONLY

Missing:
- representative roofing/safety-anchor dataset
- proof-point confusion matrix / macro-F1
- false-ready rate
- missed-reminder rate
- scene-association evaluation
- representative video reduction evaluation

Pass condition:
- predeclared dataset split and metrics
- failure cases reported, not hidden
- no performance claims from synthetic fixtures

### 4. Failure handling, observability, security, human control — 15%
Current: PARTIAL / GOOD TRUST BOUNDARY

Working:
- missed-proof exception
- uncertainty routes to targeted recapture or human escalation
- professional approval is human-owned

Missing:
- structured trace log
- AWS logs/metrics
- privacy/retention configuration
- bounded media size/duration controls
- security notes for upload/storage

Pass condition:
- every decision has evidence, confidence, reason, and action
- sensitive media retention is explicit
- missed proof cannot be backfilled or silently passed

### 5. UX, documentation, demonstration — 10%
Current: PARTIAL

Working:
- README, build packet, trust docs, CI

Missing:
- field-facing capture flow
- office review packet UI/output
- <=5 minute judge demo
- architecture + trace screenshots from the actual running system

Pass condition:
- judge can understand the loop in under 60 seconds
- worker interaction remains minimal
- report is reviewable without reconstructing the job

## Overall competition gaps

Highest-value missing evidence:
1. real proof-point vision
2. real agent trace
3. representative evaluation
4. AWS deployment + observability
5. judge-readable UX/demo

## Strategic rule

Do not add new product features until the core Evidence Loop is measurable end to end.

Core loop:
work order -> proof template -> photo/video -> OpenCV 5 perception -> evidence state -> agent next action -> human review/trace.

COOL remains optional until this loop is stable.
