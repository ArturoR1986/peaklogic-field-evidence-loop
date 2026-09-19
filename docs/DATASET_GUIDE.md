# Dataset and Labeling Guide

## Purpose
Build a small, rights-aware, representative dataset for the bounded fall-protection-anchor demonstration workflow.

## Labels
- `location_context`
- `product_identification`
- `substrate_context`
- `critical_attachment`
- `process_before_cover`
- `finished_detail`
- `finished_context`
- `unsupported`

## Folder convention

```text
data/
  representative/
    raw/
      photos/
      videos/
    candidates/
    manifests/
    splits/
```

Do not commit sensitive customer/jobsite media to GitHub unless its use and repository visibility are explicitly approved. The default competition workflow should keep representative media outside Git history and commit only manifests/examples that are safe to share.

## Manifest
JSONL records are defined by `DatasetRecord` in `src/peaklogic_field_evidence/dataset.py`.

Required concepts:
- stable `record_id`
- media path
- media type
- proof-point label
- split
- `group_id` or equivalent source/job grouping
- provenance
- rights basis
- consent status

Video-derived frames also preserve the original source-media path and source timestamp.

## Conservative rights defaults
New candidate records default to:
- provenance: `unverified`
- rights basis: `unverified`
- consent status: `unverified`

Those values must be reviewed before a strict training/evaluation manifest is accepted. The system should never silently assume that publicly visible or field-collected media is authorized for model training.

## Split-leakage rule
The **group**, not the individual frame, is the minimum split unit.

All frames from one walkthrough video must stay in one of:
- train
- validation
- test

Likewise, images from the same job/site capture session should use a stable `group_id` or `job_reference` so closely related media does not leak into held-out evaluation.

Do not:
- put frame 001 from one video in train and frame 002 from the same video in test,
- put near-duplicate captures from one job across train/test,
- tune thresholds against the held-out test split.

## Dataset audit
Run:

```bash
python scripts/audit_dataset_manifest.py path/to/manifest.jsonl --strict
```

Strict audit fails when it finds:
- a group spanning multiple finalized splits,
- unresolved rights/provenance/consent,
- finalized records with no grouping context,
- duplicate media paths,
- unassigned records.

This audit is an evaluation-integrity gate, not a model-quality score.

## Rights / privacy rule
Only use media that is owned, staged, or explicitly authorized for the competition build. Do not scrape manufacturer imagery into the training set merely because it is publicly viewable.

## Failure-class rule
`unsupported` is a real class. Unclear or out-of-workflow evidence should not be forced into a valid proof point.
