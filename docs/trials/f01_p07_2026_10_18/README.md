# F01 / F02 — Trial 001 photo-package readiness

Operation: `PL-F01-F02-20261018-01`. Base implementation: `5dc56b4896c3f2c33d4f64aee4005546d45e9d2b`.
Existing tracking: [Trial 001 evaluation, issue #23](https://github.com/ArturoR1986/peaklogic-field-evidence-loop/issues/23); [AWS execution, issue #4](https://github.com/ArturoR1986/peaklogic-field-evidence-loop/issues/4).

## F01 decision

Select **EC5 P-07: pre-departure documentation photographs** for the first fresh real-field image-to-persistent-action increment.

The original Work Order 6956 page 001, lower-right yellow instruction, states:

> Vor Abfahrt und bevor die Baustelle beräumt wird müssen Fotos an den Bauleiter gesendet werden.

This explicitly requires photographs to be sent to the site manager before departure/site clearance. It does not specify an accepted photo count, an exact shot list, or an automatic visual-acceptance rule. The requirement is **partly visual**: photo quality can be measured, but dispatch, coverage and timeliness need separate evidence.

Basis: the saved [EC5 Project / Proof Map v0.1](https://docs.google.com/document/d/1ejgW2ICX_HG7zwGbXsZsQ_oTkwzFiqM_szC4jYlilyY/edit), P-07 and C; direct visual inspection of the original instruction and the two selected originals; frozen Trial 001 manifest identities. EC5's other findings are not reclassified as new measurements.

P-05 anchor-arrow documentation remains a stronger feature-specific candidate **if a correctly bound image is found**, but EC5 has not identified one. This is not a finding that every raw image lacks an anchor. Sarnabar is a technical/QC opportunity, not an explicit photo obligation on this source page. Scaffold association has not been freshly established in this task. None is a presumed fallback.

## Exact private inputs

Use the original bytes from authorized Drive access. **Do not commit raw images or work-order scans.**

| Input | Source ID | Role |
| --- | --- | --- |
| `stage0_prejob_001_1000051280.jpg` | `153GDXD67F1n26RkgNnyQmBd0uV-5TBQ9` | Work-order instruction, page 001 |
| `1000051390.jpg` | `1cyFrX0e5sthJ6Usz7hHbnSlFZ6OrZZHG` | Day 1, Z-U1 upper-roof overview; zone from EC5 and assistant review |
| `1000051469.jpg` | `1WpUk9lFRciHzZtFwdCsMigLNPZvR5RPT` | Day 2 blurred photo; job/day from manifest, exact zone deliberately unresolved |

[case.json](case.json) fixes original hashes, sizes, bindings, source wording, declared expectations and nonclaims. The three original-byte hashes match the committed Trial 001 manifest. The photos are from different recorded days; this is **not** a before/after scene-registration pair or a complete final photo set. Unknown capture timestamps remain unknown.

Expected before execution: clear image → continue review; blurred image in the closed record → quality exception; unresolved package transmission → human review; professional acceptance → pending. If the image-quality heuristic disagrees with visual inspection, retain that disagreement and review both images. Do not tune thresholds after seeing the result merely to obtain a pass.

## F02 execution path

After installing the repository's pinned environment, place the three original input files in one private directory:

```bash
peaklogic-evidence doctor
python scripts/run_field_readiness.py \
  --case docs/trials/f01_p07_2026_10_18/case.json \
  --input-dir /private/trial001-inputs \
  --output-dir /durable/field-readiness/run-001
```

Use a new output directory each time. The runner checks OpenCV 5.0.0, required modules, input boundaries and original hashes **before creating the output directory**. It calls the existing `PersistentJobLoop.measure_image()` and report/CLI APIs. No HTTP adapter, job schema, classifier, manufacturer rule or report engine is changed.

It creates `EVAL-F01-T001-P07-v1`, an explicitly isolated **derived evaluation** of `Trial-001-Kissling-6956`. This is not a second authoritative job record and does not amend the historical event packet. Closure is loaded before quality processing, so this current closed-record evaluation never requests a new site capture. The original byte measurements are fresh, not replayed metrics. Requirement text and scene labels are attributed source interpretations, not automated extraction/predictions.

Inspect `result.json`, `before_quality.json`, `state.json`, `report.md`, `events.trace.jsonl`, `job.sqlite` and `job_export.sqlite`. The report identifies the exact saved-state SHA-256. This is an engineering review output for F04 to check, not an automatically generated visual PDF.

Use the existing CLI after the first process exits:

```bash
peaklogic-job-loop report \
  --db /durable/field-readiness/run-001/job.sqlite \
  --job-id EVAL-F01-T001-P07-v1 \
  --output /durable/field-readiness/run-001/after-restart
```

Compare `after-restart.json` with `state.json`. Never rerun ingestion into that same output directory. Repeated processing inside the runner is an explicit idempotency check; it does not inflate proof weight.

## First observed local result

An actual isolated OpenCV **5.0.0** environment was installed and checked. The initial package download failed because this container could not resolve the package host. A temporary branch-only GitHub Actions job obtained a pinned offline wheelhouse; its archive and every wheel hash were checked before local installation. No version guard was bypassed. No private media was sent to that job.

| Original photo | Fresh Laplacian variance | Saved quality decision |
| --- | ---: | --- |
| `1000051390.jpg` | 1241.4416226553299 | `continue_review` |
| `1000051469.jpg` | 2.464922865640643 | `record_quality_exception` |

Both decoded at 1536 × 1152. These are image-quality measurements, **not physical roof measurements or calibrated classifier performance**. P-07 remains unresolved and its next action is `escalate_human`; professional acceptance remains `pending`. No photo package or reminder was sent.

The nine-event derived record reopened unchanged in a separate Python process and from the exported SQLite copy. Repeating the measurements did not add events. Unbound media and a wrong-file attempt were rejected without changing stored events.

## F05 checks and remaining work

Locally executed under OpenCV 5.0.0: the existing 95 tests; 10 new synthetic preflight tests (105 total); the separate existing 9/9 failure matrix; the existing synthetic-plus-frozen-replay reviewer runner; and the six named checks in this real-media runner. Additional separate controls verified a retake decision with an explicitly open test record, controlled duplicate rejection and rollback after an injected SQLite insert failure. Those controls are not historical field actions.

Final commit-specific result records must identify the exact runner hash and source revision; do not infer a new code revision passed from this first-run description alone. F05 is **partial**: cloud restart, cloud permissions/cost/storage, independent reproduction by the deployment owner and final F04 report review are not established here.

## F02/F03 interface — no architecture redesign

Run the same script, case, original input hashes and pinned OpenCV environment on AWS. Provide the script and case explicitly: the existing image does not package `scripts/` or `docs/trials/`. Bind a durable output directory outside a disposable container. Override the default HTTP-service command with this runner; a service health check is not this demonstration. After process/container restart, invoke the existing report CLI on the same database and compare the saved JSON revision. Record actual AWS logs/resource/cost evidence separately.

This work does not launch AWS resources or change deployment ownership. Do not substitute an in-memory service or frozen event replay for this fresh-image path. Source inputs remain in their existing private home. Do not grant public access or send credentials as part of transferring them.

## Boundaries

No full six-day reinspection, automatic zone mapping, anchor-arrow detection, Sarnabar spacing, leak detection, dispatch confirmation, workmanship approval or live pre-concealment reminder is established. The original Trial 001/002 exceptions remain unchanged. The current output supports review of two selected photos inside one explicit work-order obligation; it does not prove that the whole photo package was complete or delivered.
