# Midpoint Demo Runbook

Target: September 21–October 2 check-in

## Goal
Show that the architecture is alive and auditable without overstating representative vision performance.

## 1. Runtime proof
Run:

```bash
peaklogic-evidence doctor
```

Show:
- OpenCV 5.0.0
- DNN available
- image hashing available
- competition runtime OK

## 2. Agentic Evidence Loop mechanics
Run:

```bash
peaklogic-evidence trace-demo --trace outputs/agentic_trace_demo.jsonl
```

Explain clearly:
- image-quality detection is real OpenCV processing,
- the bad capture changes the next action to RETAKE,
- the concealment stage changes the next action to REMIND_CRITICAL_PROOF,
- the evidence packet remains pending professional review,
- proof-point labels in this mechanics demo are controlled inputs until the measured classifier is ready.

Do not call controlled labels predictions.

## 3. Failure handling
Run:

```bash
python scripts/run_failure_matrix.py --output outputs/failure_matrix.json
```

Show the expected safe outcomes:
- blur -> retake
- duplicate -> reject duplicate
- unsupported / low confidence -> targeted proof request
- weak scene -> targeted proof request and not accepted
- missed concealed proof -> human escalation
- classifier unavailable -> human escalation
- trace persistence failure -> state rollback
- explicit human review -> audited human event

## 4. Container / AWS-ready artifact
Show CI or run:

```bash
docker build -t peaklogic-field-evidence-loop .
docker run --rm peaklogic-field-evidence-loop python -m peaklogic_field_evidence.service --check
```

State precisely:
- the deployable artifact is containerized and verified under OpenCV 5,
- AWS deployment is still pending unless a live AWS endpoint exists by the call.

## 5. Representative vision status
If the real/staged media and model are not ready:
Say so directly.

Current true statement:
> The OpenCV DNN adapter and evaluation harness are ready, but proof-point model performance will not be claimed until representative labeled field media is collected, the ONNX model is trained/exported, and held-out metrics are measured.

If a representative model is ready before the call, add:
- real input example,
- OpenCV DNN classification,
- confidence / UNKNOWN behavior,
- changed next action,
- confusion matrix / macro-F1,
- one meaningful failure case.

## 6. Human authority
End the technical demonstration by showing:
- evidence completeness is not professional approval,
- explicit human review is a separate recorded event,
- missing proof after concealment cannot be fabricated or backfilled.

## Suggested spoken summary
> We started from a field problem: evidence often becomes hidden before the office realizes it is missing. The current build scans the work order, tracks approved proof points, uses OpenCV 5 to evaluate incoming media, changes the next workflow action when evidence is weak or missing, and records that chain in an auditable trace. We have deliberately separated evidence readiness from professional approval. The next credibility gate is representative field media and measured proof-point recognition, which we are treating as an evaluation problem rather than a demo claim.
