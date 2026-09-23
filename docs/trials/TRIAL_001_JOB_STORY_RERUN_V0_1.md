# Trial 001 — System Re-run / Job Story Baseline v0.1

Date: 2026-09-23

## Objective

Re-run Trial 001 around the clarified product objective:

> What happened on this job, where did it happen, how far did the work progress, what is still unfinished, and what evidence supports that story?

This is broader than proving isolated requirements.

## Inputs

- Stage 0: 33 work-order / planning / drawing images
- Day 1: 26 stills + ~98-second walkthrough video
- Day 2: 27 stills

## Current automation boundary

Automated/deterministic:
- image quality
- duplicate screening
- video reduction
- ORB/RANSAC scene association
- job/media binding
- Requirement Resolver state/action logic

Human-reviewed semantic synthesis is still used for:
- work-state naming
- completion/incomplete interpretation
- plan-to-field interpretation
- narrative chronology

The full Job Progress Narrator is not yet automated.

## Quality rerun

### Day 1
- 26/26 usable
- min sharpness ~192.36
- median sharpness ~1309.90
- luminance ~119.74–171.34

### Day 2
- 26/27 usable
- `1000051469.jpg` rejected as blurred
- sharpness ~2.46
- action: RETAKE / do not count as reliable story evidence
- median sharpness ~430.35
- luminance ~127.00–190.59

## Cross-day scene continuity

Representative same-roof progression:

`1000051368.jpg` (Day 1 pre-install)
<-> `1000051465.jpg` (Day 2 insulation field)

ORB/RANSAC:
- 180 good matches
- 168 inliers
- heuristic inlier ratio ~0.933

This supports same-area chronology:
pre-install baseline -> later insulation field.

Score is an uncalibrated heuristic.

## Current job story

### Stage 0
Expected work includes flat-roof installation context, tapered-insulation planning, drainage/overflow work, perimeter/detail interfaces, and photo-documentation obligations.

### Day 1
Observed:
- materials delivered/staged
- roof/setup/access context
- pre-install roof baseline
- penetrations/details visible

End state:
**PRE-INSTALL BASELINE / SETUP**

### Day 2
Observed:
- moisture/wet conditions early
- insulation placement underway
- tapered design reference
- labeled/variable-thickness tapered pieces
- piece fitting and broad field progression
- chimney/penetration insulation fitting
- drain/opening context
- perimeter/detail work in progress

End state:
**INSTALLATION IN PROGRESS**

Substates:
- top roof insulation field: substantially covered visually
- tapered insulation: in progress / coherent with design process
- chimney/penetration: insulation fitting observed
- drainage: openings/context observed; final detail not established
- perimeter/corners: work in progress; completion not established
- roof dryness: uncertain
- waterproofing: not yet established
- professional review: pending

## Quantity/area boundary

The current evidence does not support a defensible exact quantity such as `30 m² completed`.

A reliable area claim should require:
- known plan dimensions
- spatial registration to roof regions
- progress state per region

Current safe wording:
> Most of the visible upper roof field appears covered with insulation by the later Day 2 images.

## Product finding

The existing mechanics can support the job story, but the missing core layer is a persistent **Job Progress State / Process Narrator**.

Proposed next model:
- area/component ID
- previous state
- observed state
- completion state
- evidence basis
- confidence/uncertainty
- supporting media
- quantity/area when defensible
- unresolved next work

Requirement Resolver remains useful as source context, but should support rather than dominate the narrative.

## Next gate

Before Day 3 becomes another isolated daily report, define the minimal Job Progress State so Day 3 updates the same evolving job story.

## Trust boundary

Do not invent quantities, completion states, dryness, or compliance where the plan/media do not support them.
