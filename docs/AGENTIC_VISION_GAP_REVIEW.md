# Agentic Vision Gap Review

Updated: 2026-09-19
Competition target: OpenCV AI Competition 2026
Primary path: Agentic Vision
Current branch: main

## Current verified strengths

- OpenCV 5.0.0 runtime verified in GitHub Actions.
- DNN + img_hash available.
- latest canonical suite: 64/64 tests passing.
- deterministic failure matrix: 9/9 cases passing.
- packaged work-order scan -> OCR -> proof-template path verified.
- executable Evidence Loop with JSONL audit trace.
- OpenCV quality / duplicate / uncertainty results change later actions.
- explicit missed-proof escalation and human-review event.
- real ONNX graph load/inference path through cv2.dnn.readNetFromONNX.
- dataset integrity / group-safe split audit mechanics.
- scene-association mechanics with ORB/Hamming/RANSAC and uncalibrated score labeling.
- Docker/OpenCV 5 artifact builds and boots.
- field/evidence and professional-review credentials are separated.
- audit persistence failure rolls back evidence state.
- professional approval remains human-owned.

## Supervisory alignment

CONVERGE BEFORE EXPANDING.

The architecture is not the current problem. The credibility bottleneck is representative field media and measured visual performance.

Working cycle:
BUILD -> RUN -> OBSERVE -> BREAK -> TRACE -> REPAIR -> RETEST -> MEASURE -> DOCUMENT

New-component filter:
"What competition requirement or measurable project need does this satisfy, and what evidence will prove it?"

If the answer is unclear, defer it.

## Agentic Vision rubric gap map

### 1. Substantive OpenCV 5 + agent integration — 30%
Current: STRONG MECHANICS / REPRESENTATIVE VISION PENDING

Proven:
- work-order document vision
- image quality analysis
- bounded video reduction
- duplicate handling
- ONNX/OpenCV DNN load/inference path
- scene-association mechanics
- OpenCV outputs can change later actions in the Evidence Loop

Still missing:
- trained proof-point classifier on representative field media
- held-out proof-point performance
- representative scene-pair results

Pass condition for competition-quality evidence:
- representative field input enters OpenCV 5
- bounded visual observation is produced
- EvidenceState changes
- later action or human escalation changes because of that observation
- result survives at least one meaningful failure case
- trace is reproducible and understandable

### 2. Orchestration + appropriate autonomy — 25%
Current: MECHANICS PASS

Proven:
- executable Evidence Loop
- retake, duplicate rejection, targeted proof request, critical reminder, human escalation, review-packet preparation
- append-only decision trace
- explicit human review event
- incomplete/missed proof cannot be silently backfilled

Still required:
- representative classifier output participating in the same loop
- AWS-hosted execution trace

### 3. Task effectiveness + evaluation — 20%
Current: EVALUATION INFRASTRUCTURE PASS / REPRESENTATIVE RESULTS PENDING

Proven:
- predeclared metrics
- strict dataset audit mechanics
- group-safe split logic
- failure matrix
- false-ready / missed-reminder metric definitions
- scene-association and classification evaluation harnesses

Still missing:
- representative proof-point confusion matrix / macro-F1
- representative UNKNOWN / low-confidence failures
- representative scene association
- representative video-reduction retention results
- real operational burden comparison

### 4. Failure handling, observability, security, human control — 15%
Current: STRONG MECHANICS

Proven:
- 9/9 deterministic failure cases passing
- blur -> retake
- duplicate -> reject duplicate
- unsupported / low-confidence -> targeted proof
- weak scene -> targeted proof
- missed pre-concealment proof -> human escalation
- classifier/service/tool failure -> fail safe
- audit persistence failure -> state rollback
- explicit human override/review trace
- auth separation and privacy/retention documentation

Still missing:
- AWS-hosted logs/metrics
- representative failure media
- durable cloud state/trace evidence

### 5. UX, documentation, demonstration — 10%
Current: MIDPOINT DEMO READY AT MECHANICS LEVEL

Proven:
- midpoint runbook
- work-order demo
- trace demo
- failure matrix
- review packet
- Drive + GitHub project organization

Still missing:
- representative media in the demo
- final judge-facing UI polish
- <=5 minute final video
- final technical report / screenshots from live AWS execution

## Highest-value remaining evidence

1. representative field media
2. reviewed labels / rights / provenance
3. trained bounded proof-point classifier
4. ONNX export + OpenCV 5 inference on held-out media
5. macro-F1 / confusion matrix / UNKNOWN failures
6. representative scene-pair testing
7. real AWS-hosted execution trace
8. final judge-readable demo

## Expansion stop condition

Do not substantially broaden the product until a representative field input:
- enters OpenCV 5,
- produces a bounded visual observation,
- changes EvidenceState,
- causes an appropriate later action or human escalation,
- survives a meaningful failure case,
- and leaves an auditable trace another reviewer can reproduce.

## Strategic rule

Protect the narrow fall-protection-anchor / proof-before-concealment demo.

COOL remains optional until the representative core Evidence Loop is stable.
