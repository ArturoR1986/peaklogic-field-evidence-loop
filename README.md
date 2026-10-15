# PeakLogic Field Evidence Loop

**OpenCV 5 evidence processing with a persistent, work-order-led job record.**

Field crews capture photographs and walkthrough video, but the office still has
to establish where they belong, what changed, and whether the requested
information was documented before work concealed it. PeakLogic connects field
media to source-linked requirements, preserves unresolved evidence, and records
the next review action without confusing a finished-looking roof with verified
workmanship.

```text
Work order / approved requirement
  -> correctly bound field media
  -> OpenCV observation or evidence-quality decision
  -> persistent job/evidence state
  -> changed next action, abstention or human-review request
  -> auditable event trace and report
```

**This README is the single reviewer entry point.** The implementation, tests,
committed field-event packets and saved verification results are in this branch;
no email attachment, Drive download or separate briefing ZIP is required to
reproduce the software path. This is a bounded engineering review, not a
production release.

**Handoff completeness:** the code-and-evidence path is available here. The new
visual-report PDFs have **not yet been copied into this branch**, so the complete
visual handoff is not ready. Their exact pending-file identities are recorded in
[the handoff manifest](docs/review/handoff_manifest.json); no external links are
presented as repository copies.

[Run the demonstration](#run-this-first) · [Inspect the results](#what-to-inspect)
· [Verified evidence](#verified-evidence) · [Reporting format](#reporting-format)
· [Limitations and AWS](#limitations-and-aws) · [Review questions](#review-questions)

## What is implemented

| Capability | Implementation and boundary |
| --- | --- |
| Image suitability | OpenCV decoding, Laplacian sharpness and luminance measurements. Quality changes the next action; these thresholds are heuristics, not a calibrated blur classifier. |
| Document vision | Page contour detection, perspective rectification and cleanup, followed by Tesseract OCR and constrained template matching. This is not general interpretation of a complete construction drawing set. |
| Video and redundancy | Bounded frame sampling, hashes and visual redundancy reduction. Multiple frames are not independent proof of a physical component. |
| Scene association | ORB descriptors, Hamming matching and RANSAC geometry. Scores are uncalibrated and do not independently establish a roof zone or physical scale. |
| Persistent job record | SQLite transactions, frozen source identities, idempotent events, source/zone checks, amendments, replay, separate-process reload and atomic database export. Reports derive from stored state. |
| Next actions | Retake while intake is open, duplicate rejection, targeted proof requests, closed-record exceptions and human escalation. Usable imagery alone cannot satisfy an installation requirement. |
| DNN interface | ONNX loading/inference through OpenCV DNN, exercised with a small synthetic model. No representative roofing-classifier accuracy is claimed. |

The primary demonstration uses **controlled requirement, job/zone-binding and
closure inputs**. OpenCV measures image pixels and changes quality actions; this
run does not automatically interpret the complete work order, roof layout or
installation sequence. The HTTP service remains a separate **in-memory** adapter;
it is not backed by the SQLite job store.

Implementation: [production source](src/peaklogic_field_evidence) ·
[persistent contract](docs/PERSISTENT_JOB_LOOP.md) ·
[requirement resolver](docs/REQUIREMENT_RESOLVER.md).

## Run this first

Use an authorized checkout of **`review/phill-handoff`**, not the older default
`main`. Linux/Bash and Python **3.13** were verified. Windows, WSL and macOS were
not independently verified in this review. A branch URL does not grant access.

```bash
git clone --branch review/phill-handoff --single-branch https://github.com/ArturoR1986/peaklogic-field-evidence-loop.git
cd peaklogic-field-evidence-loop
git rev-parse HEAD
python3.13 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e '.[dev]'
peaklogic-evidence doctor
python scripts/verify_review.py --output-dir outputs/review-first
```

Dependencies are pinned in [pyproject.toml](pyproject.toml), including
`opencv-contrib-python-headless==5.0.0.93`. The doctor must exit successfully and
report OpenCV **5.0.0**, `has_dnn: true`, `has_img_hash: true` and
`competition_runtime_ok: true`. Do not substitute OpenCV 4 or bypass the guard.
Initial dependency installation requires package access. The primary run itself
needs no cloud account, API key, external model or raw-field-media download.

The runner requires a **new output directory** and refuses to overwrite one.
Use a different directory name for subsequent runs. It composes the existing
`PersistentJobLoop` API and installed `peaklogic-job-loop` CLI; it is verification
tooling, not a second production engine.

## What to inspect

All paths below are relative to `outputs/review-first/`.

| Stage | Expected behavior | Inspect |
| --- | --- | --- |
| Fresh synthetic image processing | Textured image -> `continue_review`; deliberately smoothed image -> `retake`. Metrics are calculated during this run. | `sharp.png`, `smoothed.png`, `synthetic_before_close.json` |
| Binding and closure | Unknown media identity rejected without mutation. Quality alone cannot satisfy proof. Closing the unresolved fixture produces `escalate_human`, not approval. | `synthetic_after_close.json`, `synthetic_report.md`, `synthetic.trace.jsonl` |
| Durable reload | A separate process reads equivalent state from SQLite. | `synthetic_reloaded.json` |
| Trial 001 frozen replay | 312 events; nine historical evidence exceptions retained; professional acceptance pending. | `trial001.md`, `trial001.json`, `trial001.trace.jsonl` |
| Trial 002 frozen replay | 93 events; unresolved observation bindings retained; professional acceptance pending. | `trial002.md`, `trial002.json`, `trial002.trace.jsonl` |
| Repeatability | No duplicated events; repeated trace byte-identical; logical state matches the committed snapshot except fresh ingestion timestamps. | `verification.json`, per-command `.log` files |

Expected top-level result: `verification.json` reports `"status": "PASS"`.
A pass concerns the specified mechanics, not roofing accuracy or acceptance.

**Fresh vision and historical replay are different evidence classes.** The
synthetic branch demonstrates image-to-action integration, not roof recognition.
The field packets contain historical OpenCV outputs plus manual/source-report
annotations. Replaying them verifies state logic and persistence, not new
processing of the original images or correctness of every annotation.

To inspect Day 6 of the stored Trial 001 record:

```bash
peaklogic-job-loop report --db outputs/review-first/trials.sqlite \
  --job-id Trial-001-Kissling-6956 --from-day 6 --through-day 6 \
  --output outputs/review-first/trial001_day06_manual
```

The output prefix creates `.md`, `.json` and `.trace.jsonl` files. Day ordinals
are not verified calendar dates. These are retrospective projections, not
reminders actually issued during the original job.

Direct replay without the wrapper is also available:

```bash
peaklogic-job-loop replay --db outputs/manual.sqlite \
  --job-id Trial-001-Kissling-6956 \
  --input docs/trials/persistent_replay_2026_10_02_v2/trial001_events.json \
  --output outputs/manual_trial001
```

The underlying CLI can replace output-prefix files; choose a new prefix.

## Engineering checks

```bash
pytest
python scripts/run_failure_matrix.py --output outputs/failure_matrix.json
```

The existing suite contains 95 tests. The separate nine-case failure matrix is a
mechanics check, not nine independent field-accuracy examples.

Optional document-vision example, after installing the **Tesseract executable**
(`tesseract-ocr` on the verified Linux path):

```bash
peaklogic-evidence workorder-demo --output-dir outputs/workorder-demo
```

This generates a synthetic page, detects and rectifies it, runs cleanup and OCR,
and matches a known template. It does **not** automatically populate the
persistent Trial 001/002 records.

To reproduce the container path from the repository root:

```bash
docker build -t peaklogic-field-evidence-loop:review .
docker run --rm peaklogic-field-evidence-loop:review \
  python -m peaklogic_field_evidence.service --check
docker run --rm peaklogic-field-evidence-loop:review \
  peaklogic-evidence workorder-demo --output-dir /tmp/workorder-demo
docker run --rm \
  -v "$PWD/scripts:/review/scripts:ro" \
  -v "$PWD/docs/trials:/review/docs/trials:ro" \
  peaklogic-field-evidence-loop:review \
  python /review/scripts/verify_review.py --output-dir /tmp/reviewer
```

These container commands validate execution; their `/tmp` output is ephemeral.
The first, non-container path keeps the outputs locally for inspection. Docker
must be installed separately. No cloud deployment is part of these commands.

## Verified evidence

The reviewed baseline is `802c9ef28f2158e562adc062708f8ab162c16af9`, incorporating
PR #25 head `1973398e089f37c2539b9c9d68d4e1b350a9c9ec` without merging `main`.
The completed 14 October 2026 CI run **38623807173** checked GitHub's synthetic
PR merge `9e7403b4cb32b77eddb48ced6462fceaccb5fe00` against unchanged main.

| Executed check in that run | Result |
| --- | --- |
| Runtime | Python 3.13.16; OpenCV 5.0.0; DNN and img_hash available |
| Review-branch suite | 95 passed |
| Unchanged main baseline | 77 passed under OpenCV 5 |
| Deterministic failure matrix | 9/9 passed on both baselines |
| Synthetic quality -> persisted state/action/trace | Passed |
| Frozen Trial 001/002 replay, idempotency and separate-process reload | Passed; 312 and 93 events |
| Docker build, service check, synthetic OCR example and persistent reviewer path | Passed |

Saved [runtime](docs/review/evidence/802c9ef/doctor.json),
[test log](docs/review/evidence/802c9ef/pytest.log),
[failure-matrix result](docs/review/evidence/802c9ef/failure_matrix.json),
[reviewer result](docs/review/evidence/802c9ef/verification.json) and
[environment](docs/review/evidence/802c9ef/environment.txt) are committed here.
Their [provenance and checksums](docs/review/evidence/802c9ef/provenance.json)
identify the source run and archive. These are preserved results from that exact
run, not tests newly executed by copying the records.

The earlier reviewer runner failed by comparing Python tuples with JSON lists
at a reload boundary. Commit `5cb803e` corrected the comparison without dropping
fields or changing production behavior. The failure and fix remain documented in
[the engineering review record](docs/review/STATUS.md). Current branch CI checks
remain attached to PR #26; do not infer a new revision passed from this older run.

## Representative Trial 001 and Trial 002 evidence

The [committed field replay](docs/trials/persistent_replay_2026_10_02_v2) contains
source manifests, historical measurements, attributed observations, reports,
states and unresolved decisions.

| Frozen record | Photograph entries / unique byte streams | Stored events | Semantic review pending |
| --- | --- | --- | --- |
| Trial 001: six-day installation | 158 / 148 | 312 | 211 photograph/frame entries |
| Trial 002: service/inspection | 42 / 41 | 93 | 79 photograph/frame entries |

Counts describe inputs, not independently validated components. Trial 001's nine
exceptions are **eight unresolved required-proof items at dataset closure plus
one separately labelled unresolved pre-cover readiness question**. They do not
mean nine construction defects, or that every missing item was concealed.
Trial 002's unbound patch observations are not confirmed leaks.

Field prose, component identities and stage labels remain attributed
human/assistant annotations, not automatic CV predictions. A full raw-media
collection is not bundled; the executable replay uses the committed event
packets, not private-source downloads.

## Reporting format

The Foreman's Daily Field Report is intended to give a short operational account:
what happened, where work progressed, meaningful conditions and practical office
support. Technical verification and professional acceptance remain separate.

The reviewed visual edition has six daily reports, a four-page six-day summary,
selected photographs with captions, and a two-page reusable layout. The Day 5/Day 6
glazed-wall comparison is a reporting interpretation of access and progress, not
an automated scaffold-detection result. The template is not a fillable form.

**Repository copy is pending.** The three PDFs listed in the handoff manifest
are not present in this checkout. The field-event Markdown reports above are
available now, but are not a substitute for the new visual format. No PDF links
are advertised here until the actual bytes are committed and checked.

The visual reports use preserved assistant-written narratives, photographs and
previously supplied field clarifications. First-person wording is an editorial
voice, not a signed foreman statement or a pristine visual-only benchmark.
Office-support panels are recorded or interpreted coordination items, not proof
that an instruction was sent or an action completed. Those PDFs were assembled
separately; **the reviewer command does not generate that PDF layout**.

## Limitations and AWS

**No live AWS execution is established.** Docker checks are not a cloud deployment.
The in-memory HTTP service is not connected to SQLite. Durable HTTP integration,
authentication/access controls and cloud execution evidence remain open; the
[existing AWS plan](docs/AWS_DEPLOYMENT_PLAN.md) is a plan, not run evidence.

Trial 001 retains partial zone/component review, missing or unresolved
anchor-arrow and inspection records, geometry/product-applicability questions,
the historical missing raw Day 1 walkthrough, and uncertain day binding for
`1000051514.mp4`. Trial 002 retains two unresolved observation bindings and
unvalidated possible water-entry candidates. Its original detector misses and
nuisance regions remain in [the recorded probe](docs/trials/TRIAL_002_DAY_01_SOURCE_BOUND_PROBE_2026_09_28.md).
No additional Day 7 capture is assumed for the closed Trial 001 dataset.

Low texture can produce low sharpness without blur. Quality and scene matches do
not prove dryness, hidden attachment, weld strength or physical dimensions.
No workmanship approval, safety/code/manufacturer/warranty compliance, validated
Sarnabar spacing measurement, reliable defect/leak detection, representative
classifier accuracy, complete automatic semantic reconstruction or live
pre-concealment reminder performance is claimed.

SQLite transactions and event IDs support application integrity, not a
cryptographically tamper-proof archive. A recorded reviewer label does not verify
professional qualifications. See [trust boundaries](docs/TRUST_BOUNDARIES.md).

## Review questions

1. Does the separation between vision measurements, attributed annotations and
   evidence acceptance make the implemented workflow clear?
2. Which single bounded real-field CV check would most strengthen the existing
   state/action loop, with a defensible success criterion and abstention case?
3. What evaluation would make scene association or a Sarnabar geometry probe
   credible without implying unmeasured physical accuracy?
4. What minimal AWS execution would demonstrate the same path without adding
   unnecessary infrastructure?
5. What would make the reporting output more useful without conflating readable
   narration with technical validation?

## Repository and disclosure boundary

Everything required for the software review is versioned here. Historical
[development records](docs/development/history/README.md), [tests](tests),
[failure cases](docs/FAILURE_MATRIX.md) and [trial evidence](docs/trials) remain
visible rather than being hidden behind a polished demo.

This repository is private. Preparing a review branch does not invite a reviewer,
change permissions or merge either PR. Other branches and Git history have not
been cleared for repository-wide external disclosure. Source manifests retain
private pointers and job identifiers. The pending PDFs embed real site images
and identifiers; private source links do not prevent a PDF recipient seeing
those embedded images. External access/distribution requires the owner's
separate approval. No new license or redistribution rights are granted here.
