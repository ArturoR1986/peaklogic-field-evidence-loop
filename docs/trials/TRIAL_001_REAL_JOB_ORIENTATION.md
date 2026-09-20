# Trial 001 — Real Job Orientation and Evidence Contract

Date: 2026-09-20

## Source packet

Trial 001 is based on the real user-provided job packet:
- 33 photographed work-order / planning / drawing pages
- Day 1 arrival/setup/material stills
- pre-install roof stills
- one ~98-second walkthrough video

Primary work-order page:
`stage0_prejob_001_1000051280.jpg`

## Job orientation

Visible work-order fields:
- execution date: 24.08.2026
- project number: 6956
- job: Kissling, St. Augustin
- Peter Gerber work-preparation packet
- attached slope plans / floor plans / visualizations / details

Supporting Stage 0 documents include WeberHaus site documents and RYGOL tapered-insulation proposals/layouts.

## Evidence requirements visible in the work order

The work-order packet does more than describe materials. It explicitly creates documentation obligations.

### Critical / proof-sensitive items

- seam inspection / seam control is listed
- drains / emergency-overflow details are called out
- wall connection is to follow the attached detail
- PV penetrations / conduit length / overflow cut-outs are explicit checks
- anchorage points are to be sealed with Alutrix, not Eurasol
- anchorage-point documentation must show the arrow so the embedment-depth indication is recognizable in the photo
- before departure / site clearance, photos must be sent to the site manager
- the highlighted instruction states that without photos as evidence, WeberHaus may not be invoiced

This is direct operational support for the Evidence Loop thesis:
the evidence requirement already exists; the product's job is to make sure the correct proof is captured, bound to the work order, checked, and surfaced before it is too late.

## Day 1 evidence state

Supported:
- job orientation
- arrival / setup
- materials onsite and staged
- access / scaffold / lifting context
- pre-install roof baseline
- broad same-job scene association

Pending:
- installation execution
- critical proof-before-concealment
- completion
- professional approval

## Quantitative Trial 001 findings

Local representative-media mechanics run:
- 26/26 Day 1 stills passed current deterministic quality thresholds
- minimum sharpness ~192.36 vs threshold 45
- luminance ~119.74–171.34 vs accepted 25–235
- zero still-image pairs crossed the strict average-hash near-duplicate threshold (Hamming <= 14)

Real repeated-view scene geometry examples:
- 1000051390 <-> 1000051392: 285 good ORB matches, 263 RANSAC inliers, heuristic score ~0.923
- 1000051390 <-> 1000051391: 375 good matches, 315 inliers, score ~0.840

Scene scores remain uncalibrated heuristics.

## Defect found by real walkthrough

The original video sampler could stop when it retained `max_candidates`, causing the end of a long walkthrough to be silently excluded.

On the real ~98.07-second walkthrough, the pre-fix path stopped around 81.9 seconds.

Repair:
- widen sampling stride across the full video when candidate cap would otherwise truncate coverage
- regression test requires near-end coverage

Merged with OpenCV 5 validation:
- commit `1f477be867437c04b4c9d3c3e294f83145b61c13`
- 69/69 tests PASS under OpenCV 5.0.0
- Docker/service/work-order demo PASS

## Job binding rule

Trial 001 also forced a product correction:

> Free-floating media cannot satisfy job evidence.

Canonical implementation now includes:
- `JobEvidenceRecord`
- `JobEvidenceSession`
- work_order_id / job_id
- source work-order artifacts
- extracted context
- bound attachments
- evidence state
- traceable review packet

Unbound media is rejected before it can change evidence state.

## False-ready result

PASS.

Day 1 media remains incomplete/pending. It cannot make the job complete or professionally approved.

## Next field evidence

Continue the same Trial 001 job record with:
- insulation placement and layout
- close / medium / wide views of the same operation
- fastening / adhesive process where applicable
- drains / emergency overflows before concealment
- wall/perimeter interfaces before concealment
- anchorage-point photo evidence required by the work order
- final completion media

## Trust boundary

Some work-order lines are abbreviated or partially obscured. Do not invent missing wording.

Where exact installation requirements matter, use the exact work order, approved attached detail, current manufacturer instructions, and qualified human review.

PeakLogic validates evidence readiness and traceability. It does not certify workmanship, structural capacity, manufacturer compliance, code compliance, warranty status or safe use.
