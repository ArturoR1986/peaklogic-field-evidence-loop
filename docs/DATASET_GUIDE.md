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
- provenance
- rights basis
- consent status

Video-derived frames also preserve the original source-media path and source timestamp.

## Rights / privacy rule
Only use media that is owned, staged, or explicitly authorized for the competition build. Do not scrape manufacturer imagery into the training set merely because it is publicly viewable.

## Split rule
Assign train/validation/test splits before final evaluation. Do not tune thresholds against the held-out test split.

## Failure-class rule
`unsupported` is a real class. Unclear or out-of-workflow evidence should not be forced into a valid proof point.
