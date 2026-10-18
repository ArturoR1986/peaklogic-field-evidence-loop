# F03 — Private persistent-image execution

Owner: Aurelian / engineering. Tracker: existing GitHub Issue #4.
Baseline inspected: `5dc56b4896c3f2c33d4f64aee4005546d45e9d2b`.
Status: IMPLEMENTATION CANDIDATE. Cloud execution, credits, and AWS access remain unverified.
Main retains F01 target selection, F02 integration and technical acceptance. No automatic merge.

## Narrow implementation, not a new architecture

The existing HTTP service and SQLite adapter are separate. For the first F03 path,
run the existing container as a **private command-line job**, invoking
`python -m peaklogic_field_evidence.f03_runner` instead of the default HTTP CMD.
It calls the unchanged `PersistentJobLoop.measure_image()` and derives the report,
requirement action and trace from the same SQLite revision. It starts no listener.
This does NOT implement HTTP-to-SQLite persistence or claim it already exists.
Main must accept this entry point for the demonstration; do not independently change
job contracts or substitute this image-quality baseline for a source-grounded F01 case.

Candidate AWS footprint: one already-authorized x86_64 EC2 host in `eu-north-1`,
using Docker and a directory on encrypted EBS for the sandbox SQLite DB/results.
Use existing suitable resources first. No load balancer, NAT gateway, public API,
new database service, GPU, Spot interruption dependency or multi-worker system.
The application container needs no AWS IAM role/keys and runs with no network.
Host management uses an already-approved Systems Manager Session Manager route;
verify its agent, scoped operator access and endpoint connectivity rather than
creating new IAM roles, public ingress, NAT or VPC endpoints silently.

## Hard boundaries before resource use

1. Use the user's securely authenticated operator environment (console CloudShell
   or a separately authorized executor). Never paste secret keys into chat/email.
2. Run `aws sts get-caller-identity --region eu-north-1` or the read-only preflight
   script. Confirm the expected account. STS success is not deployment permission.
3. Verify actual remaining promotional credits, expiry and eligible services in
   the billing console. A zero-spend alert is a notification, not a spending cap.
4. Record an approved numeric session ceiling, maximum active hours, exact
   instance/volume configuration, and shutdown owner. **No amounts are defaulted
   as approved.** Pending account inventory means no credible final quote yet.
5. Confirm media rights, job/zone/component context, and the authorized sandbox DB
   with Main. Never upload raw private client photos or the DB into a public repo.
6. No plan upgrade, public exposure, broad permission grant, spend beyond verified
   credit coverage, significant recurring cost or destructive change is authorized
   by these files. Stop at those boundaries.

`deployment/f03/aws_preflight.py` is deliberately read-only: STS plus EC2 inventory
filtered to Project=PeakLogic-F03. It prints no keys, writes no cloud resources,
and cannot grant deployment approval. A missing instance does not trigger creation.

## Resource/cost envelope to fill from the real account

Prefer an existing suitable instance with at least 2 GiB host RAM; the bounded
application container is limited to 1 GiB and one CPU. Verify that the existing
Docker build fits before choosing a larger host. Docker building needs network,
package download and additional temporary disk; application execution does not.
Keep only one active host/container. Do not enable burst-credit Unlimited mode
without accounting for it. Compare the exact Linux/x86 price in Stockholm before
choosing a type; do not copy a US region's rate or assume Free Plan eligibility.

Cost estimate worksheet (USD, before credits/tax):
`active_hours * regional_compute_rate + allocated_EBS_GiB * regional_GiB_month_rate
 * allocated_hours / billing_month_hours + actual_IP/network/log/storage_charges`.
Record quoted rates, timestamp, SKU/region, allowance and conservative contingency.
Record wall time/resource IDs now; reconcile actual AWS billing when it becomes
available rather than presenting the estimate as a measured bill. Stopping EC2
ends compute usage charges, not EBS/snapshot/IP retention costs. Delete nothing
until evidence is exported and retention/deletion is explicitly approved.

## Build and synthetic controls (no field claims)

From a clean checkout of the reviewed F03 commit:

```bash
set -euo pipefail
COMMIT=$(git rev-parse HEAD)
docker build -t peaklogic-f03:"$COMMIT" .
IMAGE_ID=$(docker image inspect --format '{{.Id}}' peaklogic-f03:"$COMMIT")
mkdir -p "$PWD/outputs/f03"
docker run --rm --network none --read-only --cap-drop ALL \
  --security-opt no-new-privileges --user "$(id -u):$(id -g)" \
  --memory 1g --cpus 1 --pids-limit 128 \
  --tmpfs /tmp:rw,noexec,nosuid,size=128m \
  -e OMP_NUM_THREADS=1 -e OPENBLAS_NUM_THREADS=1 \
  --mount "type=bind,source=$PWD/scripts,target=/review/scripts,readonly" \
  --mount "type=bind,source=$PWD/outputs/f03,target=/evidence" \
  "$IMAGE_ID" python /review/scripts/f03_smoke.py run \
  --output-dir /evidence/run --source-commit "$COMMIT"
# Separate container; existing state mount is read-only.
docker run --rm --network none --read-only \
  --mount "type=bind,source=$PWD/scripts,target=/review/scripts,readonly" \
  --mount "type=bind,source=$PWD/outputs/f03,target=/evidence,readonly" \
  "$IMAGE_ID" python /review/scripts/f03_smoke.py verify --output-dir /evidence/run
```

The three controls use generated sharp/blurred/undecodable inputs and explicitly
synthetic human annotations. Sharp input may support the synthetic requirement;
unusable inputs keep the closed-record requirement open and escalate. No real
workmanship, semantics, field target, AWS host or professional approval is inferred.
Running these on GitHub Actions is CI/container proof, NOT AWS or real-field proof.

## Main's input contract for the real run

Main supplies/reviews: exact tested commit and image ID; sandbox DB exported with
`PersistentJobLoop.export_database()` from the approved record; job ID; requirement
ID; original photo/frame ID and path; frozen expected image SHA-256; source-provenance
and approved manual binding/annotation where applicable; selected input basis;
expected outcome, negative/abstention outcome, current state hash and privacy scope.

The manifest must bind the image hash before processing. The selected requirement
must already exist. The runner creates neither a new requirement nor a semantic
observation, link, component mapping or human approval. Image quality alone cannot
establish any technical dimension or nonvisual requirement. Explicit human review
in a supplied record stays labeled as such, never as an OpenCV prediction.

If that media ID already has a quality event, matching reuse is **not fresh CV**.
A different stored OpenCV version or conflicting bytes blocks execution. Do not
delete or overwrite the old event. Main should prepare an explicitly labeled,
traceable sandbox measurement packet, retaining lineage to the frozen source,
when historical quality events would prevent a genuinely fresh measurement.
Record packet derivation and which historical CV events were excluded from the
sandbox; the canonical historical record remains untouched. Do not fabricate
missing original measurements, binding or approvals during packet preparation.

Obtain the current state hash with:
`python -m peaklogic_field_evidence.f03_runner snapshot --db <db> --job-id <job>`.
Run `deployment/f03/run_private_container.sh` after binding its required variables.
The shell exposes no ports, passes no AWS keys, and runs the same pinned image a
second time with the persistent state read-only. It publishes nothing to judges.

## Reopen and failure verification

Every successful run writes state.json, trace.jsonl, report.md (with state hash),
receipt.json and reopen.json. The receipt includes before/after decisions and the
actual OpenCV/wheel/NumPy versions. Artifact hashes bind the report to the state.
The subprocess verifier performs a fresh read-only reopen. The shell's second
container additionally demonstrates survival of container deletion/recreation.
Neither test implies survival of EC2 termination, volume deletion or cloud disaster.

The runner serializes its own invocations, but all writers to that sandbox must
respect the single-writer rule. Unknown concurrent writers are not allowed. A
stale state hash blocks execution. An export failure after the event committed
produces an INCOMPLETE failure record, not a claim of rollback. Inspect the DB,
obtain the current state hash and retry into a new output directory; reused CV
is marked as reuse. A retry never overwrites the original evidence bundle.

## What closes F03 — and what does not

Collect the actual AWS account/operator confirmation privately, region and
instance/volume IDs, image ID and tested Git commit, start/stop timestamps,
Main-approved input/requirement binding, fresh-measurement receipt, saved
state/action/trace, negative control and separate-container reopen output.
Capture host identity via the approved operator/SSM session or AWS control plane.
The application receipt intentionally says `cloud_execution_proven: false`:
it cannot attest where it runs. Supplement it with the actual AWS resource/run
record. An environment variable saying AWS is not proof of AWS execution.

For F04, give Helper the exact state hash, generated report, trace and selected
source IDs. These are existing markdown exports, not a new photo-PDF engine.
For F05/F06, review exact claims and private judge-access arrangements. F03 remains
open until the agreed meaningful path is actually exercised on AWS with durable
state and evidence. A container build, synthetic smoke or health endpoint alone
never closes it. Reuse Issue #4 for checkpoints and Main's F01–F07 tracker.

## Official source notes (checked 2026-10-18)

- Session Manager provides node access without opening inbound ports; setup and
  scoped permissions are required: https://docs.aws.amazon.com/systems-manager/latest/userguide/session-manager.html
- STS caller identity reports the authenticated principal, not its resource authority:
  https://docs.aws.amazon.com/cli/latest/reference/sts/get-caller-identity.html
- Stopped EBS-backed instances retain EBS storage charges:
  https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/ec2-instance-lifecycle.html
- Quote regional compute and account for separate costs:
  https://aws.amazon.com/ec2/pricing/on-demand/

These sources establish platform behavior, not this account's credit balance,
actual resources, spend approval or successful deployment.
