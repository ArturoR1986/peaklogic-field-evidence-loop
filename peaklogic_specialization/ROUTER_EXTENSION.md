# Field Evidence Router Extension

## Entry Signals
- work order + field media
- job progress review
- missing-evidence question
- daily/weekly/completion reporting
- bounded technical/QC request attached to a job

## Default Routing
```text
new media
→ Media Binder
→ Living Job Record binding update
→ Field Narrator when operational interpretation is needed
→ Work-Order Evidence Reviewer when requirement reconciliation is needed
→ Technical/QC Analyst only for an explicitly bounded technical question
→ Evidence Steward reconciliation
→ Report Composer only when a report artifact is requested/triggered
```

Do not force every module through every task.

## Core Handoff Rule
All specialists return structured contributions to the same Living Job Record. No specialist owns a separate final truth.

## Stop Rule
Stop when the requested state update/report/action exists and unresolved items are recorded.
