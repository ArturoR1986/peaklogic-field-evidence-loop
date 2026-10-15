# Agentic Evidence Loop Failure Matrix

Status: deterministic mechanics; real-media failure observations are preserved
separately in the October 2 persistent replay. Neither is a calibrated field
classifier evaluation.

## Why this exists
The competition rewards failure handling, observability, and appropriate human control. PeakLogic should not demonstrate only the happy path.

Executable command:

```bash
python scripts/run_failure_matrix.py --output outputs/failure_matrix.json
```

## Current deterministic cases

| Failure | Expected safe behavior |
|---|---|
| blurred media | RETAKE |
| duplicate evidence | REJECT_DUPLICATE |
| unsupported evidence | REQUEST_TARGETED_PROOF |
| low-confidence proof classification | REQUEST_TARGETED_PROOF |
| weak/wrong scene association | REQUEST_TARGETED_PROOF and do not accept proof |
| critical proof missed after concealment | ESCALATE_HUMAN |
| classifier unavailable | ESCALATE_HUMAN and record perception error |
| audit trace persistence unavailable | roll back state; do not silently commit evidence |
| explicit human review | record a human-owned review event |

## Human authority
Professional review can be recorded only through an explicit human-review method/action. It is never created by the evidence policy automatically.

If a human explicitly approves an incomplete evidence packet, an explanatory review note is required and the override remains in the trace.

## Representative failure work still required
Extend the representative evaluation beyond the current exploratory records with:
- true motion blur
- glare/shadow
- occlusion
- low texture
- confusingly similar roof areas
- incorrect model predictions
- low-confidence model output
- changed viewpoints
- missing proof after concealment
- short walkthroughs that appear comprehensive but omit the critical detail

Those results belong in the final evaluation report, not in this mechanics document.
