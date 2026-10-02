# Persistent Job Loop — implementation and replay report

2 October 2026 · PeakLogic · For Arturo, Meridian, Mara and Aurelian review

The approved persistent-loop recalibration is implemented. Trial 001 and Trial
002 now use one durable job contract, with source-bound requirements, component/
zone progress, evidence states, exceptions, review actions and reports derived
from stored events. The implementation passes **94 tests under OpenCV 5.0.0**
(`opencv-contrib-python-headless==5.0.0.93`). Installation of the package and its
`peaklogic-job-loop` CLI also passed.

This proves the persistence/replay mechanics. The field replay remains **partial
at the component-level semantic review layer**; it does not establish the stronger
complete-record interpretation or professional acceptance claim.

## Actual execution

| Check | Trial 001 — installation | Trial 002 — service/inspection |
| --- | --- | --- |
| Field photo entries decoded in OpenCV 5 | 158/158 | 42/42 |
| Unique field photo byte streams | 148 | 41 |
| Extra exact duplicate entries | 10 | 1 |
| Work-order/planning images additionally processed | 33 | 3 |
| Retrieved videos processed through existing sampler | 2 | 1 |
| Retained video frames measured | 66 | 39 |
| Persistent event count | 312 | 93 |
| Reopen and fresh database replay | Logical state matches | Logical state matches |
| Professional acceptance | Pending | Pending |

Counts describe inputs, not distinct components or completed work. Trial 001's
158 photo entries include root-folder aliases of organized Day 4 captures. Exact
hashes consolidate ten extra entries; similar/re-encoded views remain preserved.
The unrelated `1000051903.jpg` screenshot is explicitly excluded from job evidence
using the archived Day 5 review, while retaining source provenance.

The original approximately 98-second Day 1 walkthrough raw file was not located
in the searched dataset/upload/reviewed folders. Its historical report remains a
source, and the manifest records raw unavailability. `1000051514.mp4` was decoded
and sampled but its day binding remains unresolved. No capture timestamps were
invented from upload dates. Day 06's unsupplied `1000052003.jpg` is not fabricated
or treated as evidence of a missing required camera-sequence image.

## Work-order findings

Trial 001's stored chronology moves from arrival/setup through insulation and
upper-roof membrane work to perimeter, lower-roof and threshold/drain/wall-interface
work. Direct manual image annotations and archived report annotations are labeled
separately from fresh CV. Upper-roof and lower-roof states remain separate.

The final evidence state holds drain, overflow, wall and penetration criteria
uncertain. The work-order-required anchor arrow/material proof remains unresolved.
Seam-control records and photo-delivery acknowledgement need nonvisual/human
confirmation. Eight required-proof closure exceptions are preserved. One additional
pre-cover readiness review gap is recorded as an **unresolved field-review question**,
not an invented manufacturer requirement. No Day 07 recapture is requested.

Trial 002 retains the four actual ordered tasks: workshop gutter/water-trace/PU
detail, workshop ridge-joint check, sales-room ridge FLK work and connections behind
the entrance roof. The patch candidate in `1000052097.jpg` is recorded as
**suspected water entry point**, with actual leakage and project zone unresolved.
The lifted/prepared edge in `1000052094.jpg` is another conflict candidate. Neither
advances a work-order completion state without location and before/after binding.

## Failures that changed actions

- `1000051469.jpg`: sharpness 2.46, excluded as reliable proof; closed-record quality exception.
- `1000051896.jpg`: sharpness 4.54, excluded as reliable proof; closed-record quality exception.
- `1000051530.jpg`/`1531.jpg` and Trial 002 `2060.jpg`/`2061.jpg` cross the inherited sharpness threshold. They are triage flags; smooth surfaces can score low without proving blur. They cannot close fine-detail visual proof under the current conservative gate.
- Trial 002 `2084.jpg`/`2084b.jpg`: duplicate bytes prevent inflated evidence count.
- The local Trial 002 video copy failed to open; replacing it from the preserved Drive original restored sampling. The restored hash matches the prior recorded original.
- Missing pre-cover readiness proof remains a historical exception after later membrane coverage.
- Unbound patch zones and unreviewed media create human binding/review actions.

The cross-day `1368.jpg` → `1465.jpg` ORB/RANSAC probe produced 105 good matches,
97 inliers and a 0.924 inlier ratio in this configuration. It supports scene
continuity as an uncalibrated heuristic; it does not automatically establish a
project zone or dimensional scale.

## Validation and reuse

Existing job records, requirement types/resolver, image-quality analysis, video
sampling and scene association are reused. SQLite adds the missing persistence
adapter; no new model, UI, CV subsystem or AWS architecture was introduced.

The 94-test suite includes restart/idempotent replay, frozen-source hash checks, invalid-mutation rollback,
duplicate proof counting, late pre-cover evidence without gap erasure, later/unknown
capture rejection, nonvisual boundaries, unresolved bindings, requirement amendments,
corrections, zone retention, out-of-order progress and installed CLI replay/report.
Both real job records were independently rebuilt into a fresh database and reloaded.
Fresh ingestion timestamps differ by design; source identity and logical decisions match.

## Review decision and next execution

The implementation and real intake path are ready for review. First-milestone
acceptance remains human-owned. The preserved record contains 211 Trial 001 and 79
Trial 002 photo/frame entries awaiting component-level semantic review. These are
explicit pending review actions, with no credit toward required proof. This is
the next useful work: resolve source/zone/component bindings and reconcile existing
proof or document exceptions, before stronger CV measurement or live AWS.

Exact installed products, expected component totals, governing project fastening
criteria, seam-test results and final workmanship/acceptance remain unresolved.
The corrected 25 mm adjacent-hole / 50 mm same-size-hole Sarnabar discussion remains
supporting source-reported context; no spacing measurement or installed-variant
conclusion is claimed by this replay.

The companion folder `persistent_replay_2026_10_02_v2` contains the frozen source
manifests, measured event packets, traces, cumulative/daily/weekly reports and
technical execution summaries. The Drive review bundle additionally contains the
verified SQLite database. Historical trial reports retain their original findings.
