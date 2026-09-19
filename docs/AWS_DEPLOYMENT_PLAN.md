# AWS Deployment Plan

Status: SCAFFOLD READY / NOT YET DEPLOYED

## Goal
Deploy the smallest meaningful PeakLogic Evidence Loop component on AWS without spending grant credits on unnecessary infrastructure.

## Proposed first deployment
Containerized HTTP service on an AWS-managed container runtime such as App Runner or ECS/Fargate.

The container exposes:
- `GET /health` (health only)
- `POST /v1/evidence/image?media_id=...`
- `POST /v1/evidence/stage`
- `GET /v1/evidence/review`
- `POST /v1/review/decision` for explicit human-owned review status

The current service:
- runs the OpenCV evidence-quality pipeline
- performs duplicate handling within the active process
- updates EvidenceState
- produces a next action
- writes an append-only JSONL trace
- preserves professional approval as human-owned
- supports bearer-token protection for evidence endpoints
- returns a service-unavailable response if required audit persistence fails

When the measured proof-point ONNX model is available, the same service can load it through OpenCV 5 DNN using:
- `PROOF_MODEL_PATH`
- `PROOF_MODEL_LABELS`

## Initial AWS architecture

```text
Client / demo operator
        |
        v
HTTPS endpoint
        |
        v
Container service (OpenCV 5)
        |
        +--> object storage for source/selected media (planned)
        |
        +--> evidence state / job state store (planned)
        |
        +--> structured logs / metrics (planned)
        |
        +--> authenticated professional reviewer action
```

## Why container first
- same pinned OpenCV 5 wheel as CI
- easy local reproduction
- no Lambda package-size gymnastics
- straightforward path to Graviton/Arm benchmarking later if COOL becomes worthwhile

## Environment controls
- `MAX_UPLOAD_BYTES` defaults to 10 MiB
- `TRACE_PATH` defaults to an ephemeral local path; cloud deployment should redirect traces to durable storage/logging
- `EVIDENCE_API_KEY` enables bearer-token protection and is required before exposing evidence endpoints beyond a private/dev environment
- no proof-point model is loaded unless explicitly configured
- without a classifier, the service requests targeted proof rather than pretending to recognize a proof point

## Fail-closed rules
- classifier/tool failure is traced and escalated rather than treated as proof
- audit persistence failure rolls back the associated state transition
- human professional review changes only through an explicit review action
- incomplete evidence may only be human-approved with an explicit review note, preserving the override in the trace

## CI deployment-artifact check
GitHub Actions builds the Docker image after Python and failure-matrix tests pass and runs:
```bash
python -m peaklogic_field_evidence.service --check
```
inside that image.

## Deployment gates
Before calling AWS deployment complete:
1. container builds reproducibly
2. container health check reports OpenCV 5
3. HTTPS endpoint is reachable
4. evidence endpoints require authentication
5. upload size is bounded
6. media retention is documented
7. evidence state and trace are durable enough for the demo
8. logs show perception -> decision -> action
9. audit-storage failure is visible and fail-closed
10. cost/credit usage is recorded

## Not yet
- no AWS resource has been launched from this repository
- no grant credit has been spent by this scaffold
- no COOL benchmark is claimed
