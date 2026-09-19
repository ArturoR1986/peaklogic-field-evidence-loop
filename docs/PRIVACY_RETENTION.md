# Privacy and Media Retention Controls

## Principle
Jobsite imagery can contain customer property, people, labels, locations, or commercially sensitive details. PeakLogic should collect only what is necessary to prove the configured work step.

## Current controls
- no continuous surveillance
- short task-bounded photos/clips/walkthroughs
- raw representative media excluded from Git history by default
- upload size bounded by the service
- bearer-token protection available for evidence endpoints
- professional review uses a separate reviewer credential in the HTTP service
- evidence packet keeps selected evidence references instead of treating every video frame as evidence
- professional approval remains human-owned
- raw image bytes are not written to ordinary application logs

## AWS deployment requirements
Before storing real customer/jobsite media:
- choose a specific AWS region
- use private storage by default
- encrypt storage and transport
- require authentication for evidence endpoints
- use a distinct reviewer authorization path for professional decisions
- keep credentials in an AWS-managed secret/configuration mechanism, never in Git
- define who can access source media and evidence packets
- document source-video retention separately from selected evidence-frame retention
- define deletion/expiration behavior
- avoid logging raw image bytes
- do not put customer/jobsite identifiers into public logs or public demo artifacts

## Competition demo preference
Use staged or explicitly authorized media whenever possible. A strong demo does not require exposing a real customer's private jobsite.
