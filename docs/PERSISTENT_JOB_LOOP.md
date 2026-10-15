# Persistent Job Loop v0.2

The persistent adapter replays Trial 001 and Trial 002 through the same contract.
It reuses `JobEvidenceRecord`,
the existing source-grounded requirement types/resolver, OpenCV quality analysis,
video sampler and ORB/RANSAC scene association. No second CV engine or service was
introduced. SQLite adds the missing durable job history.

## Contract

`PersistentJobLoop.create(record, manifest)` freezes source identities and
provenance. `append(job_id, event_id, kind, payload, day=..., captured_at=...)`
stores an event only after validating its prospective state. SQLite transactions
serialize writers and roll back invalid mutations. Event IDs are idempotency
keys. Single-file rollback journaling avoids omitted WAL sidecars at workspace/
bundle boundaries. `export_database(path)` uses SQLite's backup API and atomic
replacement; a separate-process test verifies exported state.
Conflicting reuse fails. Requirement amendments and link corrections retain
the original history. Work-order, requirement and observation sources must belong
to the frozen job manifest.

Each event stores effective day ordinal, optional timezone-aware capture timestamp,
actual ingest timestamp and sequence. An ordinal does not establish a calendar
date. Unknown capture times stay null. Frozen replays sort known day ordinals;
unknown-day video observations remain separate. Fresh database ingestion receives
fresh ingest timestamps; logical state equality excludes only those timestamps.

Supported evidence requires an attributed observation, component/zone binding,
appropriate modality, explicit human confirmation and usable visual input when
applicable. Nonvisual requirements need recorded nonvisual confirmation. Partial
requirements cannot be closed by a visual image alone. A pre-cover link needs
verified capture provenance and an earlier day than the recorded concealment;
same-day order is held unresolved. Late credible pre-cover evidence may resolve
current evidence state but cannot erase the previous exception.

Physical progress is stored per component and zone. It neither closes evidence
requirements nor grants professional acceptance. A declared qualified human review
is a separate event. This CLI records review attribution; it does not authenticate
or independently validate professional qualifications. This CLI is a local
workflow. The existing HTTP service has separate access controls and in-memory
state; it is not wired to this SQLite adapter.

Unreviewed media and unresolved bindings receive human-review actions. Exact byte
duplicates do not increase supporting evidence counts. The inherited quality
threshold is a triage gate, not a calibrated diagnosis of every low-texture image.
Closed-record missing proof creates exceptions and human reconciliation actions;
it never requests a future Trial 001 Day 07 capture.

## Replay and reports

Install the repository with its pinned OpenCV 5 dependencies, then:

```bash
peaklogic-job-loop replay --db trial.sqlite --job-id Trial-001-Kissling-6956 \
  --input docs/trials/persistent_replay_2026_10_02_v2/trial001_events.json \
  --output trial001
peaklogic-job-loop report --db trial.sqlite --job-id Trial-001-Kissling-6956 \
  --through-day 6 --from-day 6 --output trial001_day06
```

The output prefix produces JSON state, Markdown report and stored event trace.
Reports are projections of the database, with period observations and cumulative
progress/evidence state. `--from-day 1 --through-day 6` produces the first-week
view. Omitting the period produces the current record report. Effective-day views
are retrospective: later ingested evidence can appear at its verified earlier
effective day. Original ingest-time history remains in the trace.

`scripts/build_persistent_trial_packets.py` is a controlled real-media fixture
builder, with explicitly manual semantic annotations. Its inputs are the archived
Drive inventory, a local `{id,name,path}` media index supplied with `--media-index`,
and `--workspace` containing Trial 002's preserved intake manifest/Drive IDs and
raw video files. It reruns OpenCV and the existing video/scene functions. It is
not a new automatic component detector. Portable frozen event packets require no
raw media download to replay the already recorded measurements; rerunning the CV
measurements does require the source files and their matching hashes.

## Acceptance limits

The runtime, durable reload/replay, idempotency, spatial retention, temporal gaps,
modality boundaries, amendments and state-derived reports are demonstrated.
Component-level semantic review is partial. The original Day 1 walkthrough raw
file is unavailable in the located archive; one retrieved Trial 001 video has an
unresolved day binding. No full semantic coverage, learned detector accuracy,
manufacturer compliance, workmanship acceptance or live AWS execution is claimed.
