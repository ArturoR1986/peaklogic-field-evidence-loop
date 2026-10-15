# Reviewer-readiness record

Scope: existing competition implementation; no product redesign, merge or access
change. This branch is prepared for technical review, not declared production-ready.

## Audited sources

| Reference | Exact revision | Position |
| --- | --- | --- |
| Default `main` | `b1a21103543f266ab3a86d88595b2fc9771a336e` | Earlier 77-test implementation and stale reviewer entry point |
| PR #25 head | `1973398e089f37c2539b9c9d68d4e1b350a9c9ec` | Persistent SQLite adapter and real-field frozen replay; chosen baseline for this branch |
| Historical PR CI checkout | `540342f24b1100c520cfe26dd23075deaf087573` | Synthetic merge against the above main; 95-test/OpenCV 5 log inspected |

The complete main archive reconstructed tree
`239dc0b5a7ffb9a9cf061823d556c4f4083d8c0b`. Main plus the PR-linked review bundle
reconstructed tree `ac284fd0cba84e4f11017062eb8d421fbc4838ca`, exactly matching PR
#25's GitHub tree. This verified the whole source snapshot, not selected files.

PR #25 is more than a newer document: it adds transactional event persistence,
idempotent replay, frozen-source validation, amendments/corrections, zone-specific
progress and separate-process database export checks. The 95-test claim is
supported by the inspected [CI run](https://github.com/ArturoR1986/peaklogic-field-evidence-loop/actions/runs/37012031318).
No review approvals were recorded when inspected. Its implementation is a useful
review baseline; its limitations do not disappear with a green suite.

## Verification scope

The historical CI log records OpenCV 5.0.0, 95 passing tests, the 9/9 deterministic
failure matrix, and successful Docker health and synthetic work-order checks.
These are historical results inspected during consolidation, not fresh local runs.

The local environment supplied OpenCV 4.13.0 and lacked Docker/ONNX. No local
OpenCV 5 pass is claimed. Local database-only replay reproduced both frozen states,
312 + 93 events, repeat-idempotency and separate-process reload. Only ingestion
timestamps were excluded from comparison; no field-image measurements were rerun.

The branch CI executes the pinned OpenCV 5 test suite, reviewer verification script,
and Docker checks. Its `reviewer-verification-<commit>` artifact contains exact
runtime, test logs, freshly measured synthetic outputs and replay verification.
A workflow definition is not execution evidence: consult the completed run for the
exact branch revision. Failed checks must remain visible and be corrected before
calling that revision ready.

## Fresh verification — 14 October 2026

Reviewed implementation commit: `5cb803eb5549881aa5b0e4fbd925b3fbc3748b2e`.
[Successful PR CI run 38622950505](https://github.com/ArturoR1986/peaklogic-field-evidence-loop/actions/runs/38622950505)
checked synthetic merge `2a8e623ed1fddf2902176109cf343105b04d9829` against unchanged main.
The subsequent documentation-only consolidation does not change production source,
tests, the reviewer runner or dependency pins; its CI remains visible on the PR.

| Executed check | Observed result |
| --- | --- |
| Pinned installation and doctor | Python 3.13.16; OpenCV 5.0.0; NumPy 2.3.2; DNN and img_hash available |
| Existing PR #25-based suite | 95 passed in 4.29 seconds |
| Unchanged main baseline | 77 passed under OpenCV 5.0.0 |
| Deterministic failure matrix | 9/9 passed on both baselines |
| Fresh synthetic quality → SQLite/action/trace | Passed; sharp input continues review, smoothed input requests retake; closed unresolved fixture escalates without acceptance |
| Invalid media binding | Rejected; stored event sequence unchanged |
| Frozen Trial 001 and Trial 002 replays | 312 and 93 events; logical snapshots match excluding only fresh ingestion timestamps |
| Replay idempotency and separate-process reload | Passed; repeat trace byte-identical, no duplicated events |
| Docker build and service check | Passed |
| Container synthetic document scan/OCR/template demo | Passed |
| Same persistent reviewer path inside Docker | Passed with read-only mounted scripts and frozen trial records |

Artifact `11922930594` contains the Python-run results, environment and logs;
ZIP SHA-256: `422436b214a5144796b984d87f0a0960882e5797bccee7e984a05e27de488e6a`.
Recorded synthetic sharpness values were 26733.09 and 1.38; these illustrate the
configured quality gate, not real-field classifier performance.

### Preserved failure and correction

The [first reviewer run](https://github.com/ArturoR1986/peaklogic-field-evidence-loop/actions/runs/38622491983)
on `f5e1387f4975d451bf413444a6497de64a44d81f` passed 95 tests and the failure matrix,
then failed the new synthetic reload comparison. The harness compared in-memory
tuples against JSON lists in three decision fields. Saved and reloaded JSON states
were equal. Fix `5cb803e` compares the serialized JSON contract without dropping
state fields. No production persistence code was changed. The failed run and its
artifact `11922193763` remain traceable; it is not reported as an end-to-end pass.

### Static checks

Both original source trees and the prepared reviewer tree matched Git object
hashes. All eleven relocations were byte-identical. Relative Markdown links and
`git diff --check` passed. The prepared tree has 151 tracked files; the largest is
454,781 bytes. `src/`, existing tests, dependency pins and frozen trial records are
unchanged from PR #25. External/private source-link availability and the full Git
history were not audited. The local OpenCV 4 runtime was rejected by the new
reviewer command, as intended; no local OpenCV 5 override was used.

## Demonstration boundaries

- Fresh image processing in the primary reviewer command is **synthetic quality
  triage** through existing production APIs. The requirement, zone and closure are
  controlled; no scaffold, anchor or roof-stage classifier is implied.
- Trial 001/002 are real-field-derived, portable **frozen event replays**. Their
  measurements were made in the historical run; raw source media is not bundled
  or freshly fetched by the reviewer command.
- Source-based and manual semantic annotations are distinguished in the events.
  Quality, duplicates, sampling and geometric matches are not professional findings.
- The HTTP adapter remains in-memory; SQLite-backed CLI/API behavior does not imply
  persisted HTTP sessions. Authentication of professional qualifications is not
  implemented by recording a reviewer label.
- SQLite transactions and event IDs provide application integrity, not a
  cryptographically tamper-proof audit archive or production multi-user security.

## Unresolved Trial 001 / Trial 002 issues

Trial 001 keeps 211 photo/frame entries awaiting semantic review. Nine exceptions
remain: eight required-proof closure exceptions plus a separately identified,
unresolved pre-cover readiness question. Anchor-arrow/material proof, seam-control
records, photo-delivery acknowledgement, drain/overflow geometry, applicable wall
and penetration details, exact installed variants and component totals are open.
Later surface appearance does not recover concealed proof.

The historical raw Day 1 walkthrough was not located in the PR's archive.
`1000051514.mp4` has unresolved day binding. Unknown capture timestamps stay unknown;
`1000052003.jpg` was not supplied and is not invented. Zone/component annotations
remain partial and have not been independently revalidated in this consolidation.

Trial 002 keeps 79 photo/frame entries awaiting semantic review and two unresolved
observation bindings. The 2097/2094 patch candidates are not validated leak paths;
repair stage, exact work-order location and before/after association remain open.
The recorded generic dark-feature detector's misses and nuisance regions remain
in [the original probe](../trials/TRIAL_002_DAY_01_SOURCE_BOUND_PROBE_2026_09_28.md).

Low sharpness can reflect low texture rather than blur. Image eligibility does not
establish dryness, hidden attachment, weld strength, physical dimensions, code,
manufacturer or warranty compliance. Sarnabar catalogue geometry is contextual;
no validated physical spacing measurement is established by this branch.

## Source and repository hygiene

The checked working tree contains no raw field photo/video collection. The static
scan found no private-key headers, AWS access-key patterns or GitHub-token patterns;
credential-like literals were test fixtures. This is a bounded working-tree scan,
**not** a full-history secret audit or security certification.

Source manifests retain private Drive pointers and limited job identifiers for
traceability. Do not republish these as an open dataset. No permissions, visibility,
license or reviewer invitations were changed. The repository has no license file;
this task does not grant new redistribution rights.

**External-access gate:** repository access includes more than this branch. Existing
history and other branches have not been privacy-cleared for the intended reviewer.
In particular, a separate specialization branch exists. Moving historical documents
out of the root does not make their contents inaccessible. Owner approval of the
repository-wide disclosure boundary is required before granting new access. A
branch snapshot is a separate option only after its contents and distribution are
authorized; it would not grant access to private raw media.

## Changes and review recommendation

README and START_HERE give one path. `scripts/verify_review.py` composes existing
APIs/CLI calls as verification only; it introduces no detector, store, service or
new product contract. Production `src/`, existing `tests/`, requirements and frozen
trial bytes remain unchanged from PR #25. CI now exercises persistence/replays in
addition to the existing checks. The history index lists relocation-only files.

Old 77-test/latest-state wording and the unimplemented-persistence statement no
longer describe this branch. Historical counts and failures remain in their dated
records. The earlier separate 50-test local patch is **not** imported or added to
this suite's count.

Recommendation: **READY WITH DISCLOSURES for bounded technical review of the
verified implementation; NOT CLEARED for repository-wide external disclosure.**
No merge recommendation is based solely on age or test count. Main remains
unchanged pending explicit owner approval. Live AWS, representative model
performance, full semantic reconciliation and professional acceptance remain open.
