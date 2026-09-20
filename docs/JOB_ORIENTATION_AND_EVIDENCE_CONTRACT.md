# Job Orientation and Evidence Contract

## Core rule

Every PeakLogic Field Evidence Loop starts from the work order.

The work order is the job-orientation source that describes what work is expected. Field media and other attached job files are evidence of what was actually executed.

PeakLogic compares expected work against the available evidence. It does not treat images as isolated classification tasks.

## Canonical job flow

Work order / job order
-> document scan and OCR
-> extract job identity, task, location/context, and referenced work
-> map to an approved Proof-Point Template
-> create a Job Evidence Record
-> ingest all files attached to that work order
-> classify each attachment by evidence role
-> compare required proof points against observed evidence
-> request missing / weak / better-targeted proof where needed
-> preserve missed-proof exceptions after concealment
-> prepare a traceable review packet
-> qualified human performs professional review

## Source-of-intent vs source-of-evidence

### Work order = source of intent
The work order may establish:
- job/work-order identifier
- customer/site/job context
- task or scope of work
- known components or locations
- referenced instructions/documents
- expected workflow or job type

The work order does not automatically prove that the work was performed.

### Attached media/files = source of execution evidence
Job attachments may include:
- photos
- video or proof clips
- walkthrough video
- drawings
- reference documents
- completion documents
- other files linked to the job

These attachments are evaluated in the context of the work order and the approved proof template.

## Comparison question

The system should answer:

> Given what this work order says should be done, what evidence is present that the expected work/process was documented, what evidence is missing or uncertain, and what should happen next?

It should not answer:

> Is this work definitely safe, compliant, or professionally approved?

## Job Evidence Record

Each job should maintain one parent record containing at minimum:
- job_id / work_order_id
- source work-order artifact(s)
- extracted task/scope fields
- selected proof-template id/version
- attached media/files
- evidence observations
- accepted proof points
- missing proof points
- missed-proof exceptions
- next actions
- trace events
- professional review status

All media belongs to a job context before it can satisfy a proof point.

## Attachment association rule

An attachment may count toward a proof point only if:
1. it belongs to the correct work order/job context,
2. the media itself is usable,
3. it is not merely a duplicate,
4. its proof-point assignment is sufficiently supported,
5. scene/work-area association is adequate when relevant,
6. the proof opportunity has not been fabricated after concealment.

If job association is uncertain, request context or human confirmation.

## Stage 0

Stage 0 is orientation, not proof of completion.

The Stage 0 packet can contain:
- work order
- drawings
- detail sheets
- manufacturer/reference documents
- existing-condition/context images

Stage 0 should produce:
- normalized job context
- selected proof-template candidate
- required proof checklist
- critical proof-before-concealment reminders
- unresolved questions for human confirmation

## Trust boundary

PeakLogic may compare evidence against an approved documentation requirement.

PeakLogic does not independently certify:
- workmanship
- structural capacity
- hidden conditions
- manufacturer compliance
- code/regulatory compliance
- safe-for-use status
- warranty approval

Professional approval remains externally owned by a qualified human.
