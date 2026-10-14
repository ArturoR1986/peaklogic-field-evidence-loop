# Reviewer guide

This is the reproducible review path for `review/phill-handoff`. No cloud account,
API key, raw field-media download or external model is needed for the primary run.
The repository is private; a branch URL does not grant access.

## 1. Install the pinned runtime

From an authorized checkout (Linux with Bash was verified; WSL was not separately tested):

```bash
git clone --branch review/phill-handoff --single-branch https://github.com/ArturoR1986/peaklogic-field-evidence-loop.git
cd peaklogic-field-evidence-loop
git rev-parse HEAD
python3.13 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e '.[dev]'
peaklogic-evidence doctor
```

Expected: `opencv_version: "5.0.0"`, `has_dnn: true`, `has_img_hash: true`,
`competition_runtime_ok: true`. The doctor must exit successfully; do not substitute
OpenCV 4 or bypass the version check. Dependencies are in `pyproject.toml`.
Only the optional document/OCR example below also requires the **Tesseract binary**.

## 2. Execute the primary reviewer check

```bash
python scripts/verify_review.py --output-dir outputs/review-first
```

This thin verification script calls the existing `PersistentJobLoop` API and
installed `peaklogic-job-loop` implementation. It does not add production behavior.
It writes into a **new** directory and fails rather than overwrite one.

| Stage | Expected result | Inspect |
| --- | --- | --- |
| Fresh synthetic vision | Textured image → `continue_review`; deliberately smoothed image → `retake`. Exact metrics are measured now, not read from a fixture. | `synthetic_before_close.json`, generated PNGs |
| Binding and closure | Unknown media identity rejected without mutation; quality alone cannot satisfy proof; closed unresolved fixture → `escalate_human` and a quality exception instead of a future retake. | `synthetic_after_close.json`, `synthetic_report.md`, `synthetic.trace.jsonl` |
| Durable reload | A separate process reads the same synthetic state from SQLite. | `synthetic_reloaded.json` |
| Frozen Trial 001 replay | 312 events; nine historical exceptions retained; professional acceptance pending. | `trial001.md`, `trial001.json`, `trial001.trace.jsonl` |
| Frozen Trial 002 replay | 93 events; unresolved component bindings remain; professional acceptance pending. | `trial002.md`, `trial002.json`, `trial002.trace.jsonl` |
| Repeat and reload | No extra events; byte-identical repeated trace; logical state matches the committed snapshot excluding only fresh `ingested_at` timestamps. | `verification.json` and per-command `.log` files |

The real-field packets contain **historical OpenCV outputs plus manual/source-report
annotations**. Replaying them verifies state logic and persistence, not current
image processing, annotation correctness or complete review of the underlying job.
The synthetic branch demonstrates live image-to-action integration, not roofing
recognition. Its work order and closure are openly controlled inputs.

## 3. Read one real-field report and its trace

```bash
peaklogic-job-loop report --db outputs/review-first/trials.sqlite \
  --job-id Trial-001-Kissling-6956 --from-day 6 --through-day 6 \
  --output outputs/review-first/trial001_day06_manual
```

The output prefix creates `.md`, `.json` and `.trace.jsonl`. Day ordinals are not
verified calendar dates. Effective-day reports are retrospective projections;
they must not be described as a live, as-known-at-that-time capture reminder.

For a direct replay without the verification wrapper:

```bash
peaklogic-job-loop replay --db outputs/manual.sqlite \
  --job-id Trial-001-Kissling-6956 \
  --input docs/trials/persistent_replay_2026_10_02_v2/trial001_events.json \
  --output outputs/manual_trial001
```

The underlying CLI can replace output-prefix files; choose a new prefix. The
verification wrapper above adds the new-directory safeguard.

## 4. Run the engineering checks

```bash
pytest
python scripts/run_failure_matrix.py --output outputs/failure_matrix.json
```

The existing suite has 95 tests. The nine-case failure matrix is a separate
mechanics check, not nine independent real-world accuracy cases. CI also runs the
reviewer sequence and retains its generated results as an artifact.

Optional document-vision example, after installing `tesseract-ocr`:

```bash
peaklogic-evidence workorder-demo --output-dir outputs/workorder-demo
```

This generates a synthetic page and runs document detection, rectification,
cleanup, Tesseract OCR and known-template matching. It does **not** automatically
populate the persistent trial job record. The ONNX tests similarly exercise a
small generated model, not a trained roofing classifier.

## 5. Review the limits before judging readiness

Read [STATUS.md](docs/review/STATUS.md) for the PR #25 assessment, verification
scope and unresolved trial issues. Then [PERSISTENT_JOB_LOOP.md](docs/PERSISTENT_JOB_LOOP.md)
for the actual contract and [TRUST_BOUNDARIES.md](docs/TRUST_BOUNDARIES.md).

No cloud or public sharing step is part of this guide. Do not expose the HTTP
service or distribute private source media as part of a local reproduction.
