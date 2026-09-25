# Trial 001 — Days 1–3 Review, Lessons Learned and Next Handoff

Date: 2026-09-24

## Product center

Primary question:

> What happened on this job, where did it happen, how far did the work progress, what is still unfinished, and what evidence supports that story?

Secondary technical question:

> Where can computer vision make a bounded, measurable, source-grounded observation rather than merely describe a photo?

## Source hierarchy

Project-specific requirements:
1. approved work order / approved project drawing or detail
2. current manufacturer guidance / product data
3. approved company method / Gerber practice
4. instructor explanation
5. field observation
6. unresolved / verify

Product identity:
1. approved work order / drawings
2. delivery note / shipping manifest
3. packaging / product labels
4. field appearance

## Day 1

Stage: MOBILIZATION + PRE-INSTALL / PRE-COVER BASELINE.

Learned:
- Day 1 is a before-concealment evidence opportunity, not merely logistics.
- surface readiness should be evaluated while visible.
- image alone cannot prove objective dryness or hidden moisture.
- delivery labels are useful, but a Lieferschein is a stronger identity source.

Could improve:
- targeted surface-readiness capture
- dryness confirmation
- delivery note / manifest
- deliberate product-label capture

## Day 2

Stage: INSULATION / TAPERED-INSULATION INSTALLATION.

Learned:
- visible wet/moisture-affected condition existed before installation progressed.
- drying / objective dryness was not documented before concealment.
- later installation cannot retroactively prove earlier dryness.
- tapered-insulation process can be narrated without claiming exact design compliance.
- 1000051469.jpg correctly failed quality and should not count as evidence.

Failure: MISSED / UNCERTAIN PRE-COVER DRYNESS EVIDENCE.

## Day 3

Stage: WATERPROOFING + PERIMETER RESTRAINT + DRAIN / DETAIL INTEGRATION.

Learned:
- membrane field substantially advanced.
- Sarnabar and visible fasteners create a real measurement target.
- drain before/during/after evidence is strong.
- seam-control / trial-weld evidence is not sufficiently documented.
- final details remain partly in progress.

## What worked

- moved from proof-point-centric logic to evolving job story
- preserved source authority
- separated visual, partial and nonvisual proof
- kept professional approval human-owned
- allowed quality failure to change action
- identified measurable CV tasks
- recognized work order as technical authority
- recognized delivery documents as stronger product-identity evidence

## What could improve

- Requirement Resolver was too central before Job Progress State
- early reports overfocused on description vs stage-appropriate evidence needs
- delivery note was not requested early
- spatial roof zones were not formalized early
- exact OpenCV 5 runtime must be used for representative measurement evidence
- seam-control / trial-weld capture should have been anticipated

## What failed

1. Pre-cover dryness proof was not conclusively captured.
2. One Day 2 image was unusably blurred.
3. Delivery traceability is incomplete without Lieferschein.
4. Persistent Job Progress State is not yet implemented.
5. Some exploratory calculations were not run in exact pinned OpenCV 5 runtime.

## CV opportunity priorities

### Priority A — Sarnabar fastener spacing
Use known 25 mm profile hole pitch as visual scale where perspective permits.

Pipeline:
- rail detection
- hole detection
- local pixel/mm scale
- perspective correction
- fastener-head detection
- center-to-center spacing
- compare to source-bound requirement
- report measurement + uncertainty

### Priority B — Drain low-point / recess geometry
Use calibrated/low-angle image geometry to estimate relative drain recess against surrounding plane.

### Other candidates
- seam width / overlap
- four-way joint detection
- bevel length
- corner progress state
- drain/penetration before-after association
- product-label OCR
- area/progress mapping
- wet/standing-water segmentation
- seam-control process recognition

## Next continuation point

Do not restart Days 1–3 analysis.

Next:
1. Build persistent Job Progress State v0.1.
2. Bind work-order/project requirements to roof zones/components.
3. Locate/request Trial 001 delivery note / Lieferschein.
4. Build and execute Sarnabar spacing measurement in exact OpenCV 5 runtime.
5. Preserve full measurement trace and uncertainty.
6. Attempt drain low-point geometry.
7. Rerun Days 1–3 into the persistent state.
8. Process Day 3 video separately for process/seam-control evidence.

## Stop condition

Do not broaden until at least one source-grounded OpenCV measurement works end-to-end on real Trial 001 media with exact OpenCV 5 runtime, reproducible trace and human-review boundary.

## Status update — 2026-09-25

This document is now historical context for Days 1–3 only.

Trial 001 field capture has since continued through Day 6 and is now CLOSED. No Day 7 or later field data will be provided for this work order.

Continue from:
- `docs/trials/TRIAL_001_FIELD_CAPTURE_COMPLETE_2026_09_25.md`
- GitHub Issue #20

Do not wait for additional field media. Any unresolved proof after processing must remain unresolved, abstained, or escalated under the existing human-review boundary.
