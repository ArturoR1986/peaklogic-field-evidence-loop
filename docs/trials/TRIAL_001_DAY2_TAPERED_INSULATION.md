# Trial 001 — Day 2 Installation Evidence Run

Date: 2026-09-23
Stage: top-roof tapered-insulation installation

## Input

27 Day 2 still images supplied by the field user.

Chronology:
- wet-start / preparation context
- tapered-insulation design reference
- insulation placement / fitting
- chimney / penetration fitting
- broad field coverage
- before-cover / perimeter detail context

## Deterministic quality run

Using the repository's current image-quality mechanics on the representative Day 2 media:

- images processed: 27
- usable: 26
- unusable: 1
- low-resolution failures: 0
- underexposure failures: 0
- overexposure failures: 0
- near-duplicate pairs at average-hash Hamming <= 14: 0

Representative failure:
- `1000051469.jpg`
- sharpness: ~2.46
- failure: blurred
- required action: RETAKE / DO NOT COUNT AS PROOF

This is a real field failure, not a synthetic fixture.

## Scene-association mechanics

Strong repeated-view geometry appears in multiple same-job pairs.

Examples:
- `1000051465.jpg` <-> `1000051470.jpg`: 137 good ORB matches / 123 RANSAC inliers / heuristic score ~0.898
- `1000051462.jpg` <-> `1000051478.jpg`: 171 / 145 / ~0.848
- `1000051447.jpg` <-> `1000051448.jpg`: 76 / 64 / ~0.842
- `1000051461.jpg` <-> `1000051462.jpg`: 100 / 84 / ~0.840

The score remains an uncalibrated heuristic, not a probability.

## Evidence-role organization

Human-reviewed / controlled roles:

### Design reference
- 1000051456
- 1000051457

### Wet start / preparation
- 1000051442
- 1000051443
- 1000051444

### Tapered-insulation progress
- 1000051445
- 1000051446
- 1000051447
- 1000051448
- 1000051449
- 1000051459
- 1000051460
- 1000051461
- 1000051462
- 1000051463
- 1000051464
- 1000051465
- 1000051467

### Before-cover / detail / perimeter
- 1000051470
- 1000051471
- 1000051472
- 1000051474
- 1000051475
- 1000051476
- 1000051477
- 1000051478

### Quality failure
- 1000051469 -> RETAKE

These role assignments are not presented as model predictions.

## Evidence-state result

Previous state:
- arrival / setup / pre-install baseline

Day 2 state:
- INSTALLATION IN PROGRESS

Supported:
- tapered-insulation installation underway
- engineered/tapered system visually present
- K/thickness references visible
- field placement and fitting visible
- chimney/penetration fitting visible
- broad field coverage visible
- same-job scene continuity visible

Partially supported:
- exact design-to-position correspondence for every board
- final slope achievement
- complete drain/overflow details
- complete perimeter/interface details
- substrate dryness before all placement

Not supported:
- drying operation itself
- objective dryness measurement
- final waterproofing
- seam inspection
- final anchorage-point photo requirement
- completion / closeout
- professional approval

## False-ready test

PASS.

The system must advance the job to installation-in-progress, but must not mark it complete or professionally approved.

## Next action

CONTINUE CAPTURING INSTALLATION / BEFORE-COVER PROOF.

Priority:
- drain / overflow details before concealment
- anchorage-point evidence required by the work order
- perimeter / wall interfaces before covering
- applicable fastening / adhesive / attachment evidence
- broad field immediately before membrane concealment
- waterproofing / seam / completion evidence

## Runtime note

The exact per-image field measurements above were executed in the current analysis environment using OpenCV 4.13.0 with the same deterministic algorithms implemented by the repository.

The mechanics themselves remain verified under OpenCV 5.0.0 in GitHub CI.

Representative field media should be rerun in the exact OpenCV 5 container before final competition performance claims.

## Trust boundary

This run supports visible process evidence and evidence-state handling. It does not certify workmanship, slope tolerance, drainage performance, substrate dryness, manufacturer compliance, code compliance, warranty status, structural capacity or safe use.
