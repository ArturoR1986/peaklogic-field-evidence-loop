# PeakLogic Field Evidence Loop

**OpenCV 5 evidence processing and a persistent, work-order-led job record.**

Field crews capture photos and short videos, but the office still has to determine
where they belong, what changed, and whether the requested documentation exists.
PeakLogic connects that media to source-linked requirements and records the next
review action without equating a finished-looking roof with verified workmanship.

```text
Work order / requirement → job-bound media → OpenCV quality or observation
 → persisted job/evidence state → next action or human review → event trace
```

**Start with [START_HERE.md](START_HERE.md).** It gives one reproducible command
sequence, expected outputs, and the distinction between fresh image processing and
replaying historical measurements. This branch consolidates PR #25; it is not a
production release or an AWS deployment.

## What runs today

| Capability | Implementation and boundary |
| --- | --- |
| Image suitability | OpenCV decoding, Laplacian sharpness and luminance measurements; quality changes the next action. Thresholds are conservative heuristics, not a calibrated blur classifier. |
| Documents and video | OpenCV document contour/perspective cleanup with Tesseract OCR; bounded video sampling and visual redundancy reduction. Task/template matching is constrained, not general work-order understanding. |
| Scene association | ORB descriptors, Hamming matching and RANSAC geometry. Scores are uncalibrated and do not independently establish a roof zone or physical scale. |
| Persistent job record | SQLite transactions, frozen source identities, idempotent events, source/zone checks, corrections and amendments, reload/replay and atomic database export. Reports derive from stored state. |
| Evidence actions | Retake while intake is open, duplicate rejection, targeted proof requests, closed-record exceptions and human review. Usable imagery alone does not satisfy a requirement. |
| DNN interface | ONNX loading/inference through OpenCV DNN is exercised using a small synthetic test model. No representative roofing-classifier accuracy is claimed. |

The production code is in [src/peaklogic_field_evidence](src/peaklogic_field_evidence).
The [persistent contract](docs/PERSISTENT_JOB_LOOP.md) explains source and timing
rules. The HTTP service remains a separate **in-memory** evidence adapter with a
JSONL trace; PR #25 does not connect its endpoints to the SQLite job store.

## Run this first

Use Python **3.13**, a fresh virtual environment, and the repository checkout:

```bash
python3.13 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e '.[dev]'
peaklogic-evidence doctor
python scripts/verify_review.py --output-dir outputs/review-first
```

`doctor` must report OpenCV **5.0.0**, DNN and `img_hash`; it fails on OpenCV 4.
The pinned wheel is `opencv-contrib-python-headless==5.0.0.93`.
The reviewer runner uses existing APIs and CLI commands, not a new vision engine:

1. Fresh synthetic images cause different quality actions in the SQLite workflow.
   Unbound media is rejected; unresolved proof remains open; closing the fixture
   creates a human-review action, not approval.
2. Trial 001 and Trial 002 frozen packets are replayed, reloaded in separate
   processes and replayed again to test idempotency. **This does not rerun their
   historical OpenCV measurements or read private field images.**

Inspect `outputs/review-first/verification.json`, `synthetic_report.md`,
`trial001.md`, `trial002.md` and the adjacent `.trace.jsonl` files.
Use a new output directory on each run; the reviewer runner refuses to overwrite.

## Verification and real-field evidence

PR #25's recorded CI run verified **95 tests** under OpenCV 5.0.0 and the separate
**9-case deterministic failure matrix**, plus Docker health and synthetic document
processing. See the [verification record](docs/review/STATUS.md) for the precise
source commits, rerun evidence and remaining limitations. Test counts are not
classifier accuracy or field acceptance.

The committed [October 2 field replay](docs/trials/persistent_replay_2026_10_02_v2)
contains source manifests, historical measurements, attributed observations and
traceable unresolved decisions:

| Frozen record | Photo entries / unique bytes | Stored events | Semantic review still pending |
| --- | --- | --- | --- |
| Trial 001: six-day roof installation | 158 / 148 | 312 | 211 photo/frame entries |
| Trial 002: service/inspection | 42 / 41 | 93 | 79 photo/frame entries |

Counts refer to inputs, not independent components. Trial 001 retains **nine
exceptions**: eight unresolved required-proof closure exceptions and one separately
labelled, unresolved pre-cover readiness question. Trial 002 retains unbound patch
observations; they are not confirmed leaks. Field prose and component/stage labels
are attributed human/assistant annotations, **not automatic CV predictions**.

Raw field media is not bundled. Frozen packets preserve provenance references for
authorized review; they are not a public dataset. The source-based replay and the
fresh synthetic integration check demonstrate different things deliberately.

## Limits, AWS and further work

**No live AWS execution is established by this branch.** Docker build/service
checks demonstrate a deployable artifact, not a deployed cloud workflow. Durable
HTTP integration, AWS resources, access controls and cloud execution evidence
remain open; see the [deployment plan](docs/AWS_DEPLOYMENT_PLAN.md).

No workmanship approval, safety/code/manufacturer/warranty compliance, validated
Sarnabar spacing measurement, reliable defect/leak detector, representative model
accuracy or full automatic six-day semantic reconstruction is claimed.
Professional review remains separate. See [trust boundaries](docs/TRUST_BOUNDARIES.md).

Navigation: [reviewer guide](START_HERE.md) · [verification and open work](docs/review/STATUS.md)
· [tests](tests) · [failure cases](docs/FAILURE_MATRIX.md)
· [field trial records](docs/trials) · [development history](docs/development/history/README.md).
Old build instructions are retained as history, not current assignments.
