# Requirement Resolver v1

## Purpose

Requirement Resolver converts approved job sources into bounded evidence questions.

It is not an autonomous construction-code interpreter and it does not invent installation rules.

Canonical flow:

work order / approved source
-> source-grounded evidence requirement
-> expected visible proof
-> field attachment bound to the same job
-> visual observation / human review
-> requirement status
-> next action
-> auditable job review packet

## Allowed authority sources

A requirement must point to one of:
- work order
- approved drawing/detail
- manufacturer guide
- specification
- explicit human confirmation

Every requirement records:
- source document
- source locator
- source excerpt / reviewed source note
- requirement statement
- evidence question
- visual checkability
- capture deadline when concealment matters
- expected capture guidance
- visual limitations

## Visual checkability

### visual
The relevant condition can reasonably be assessed from suitable imagery.

Examples:
- required visible indicator is present
- fastener candidates are visible
- termination bar and corner geometry are visible
- board labels / thickness markings are visible
- drain/opening context is visible

### partial
Some aspects can be observed visually, but the source requirement includes properties pixels cannot establish alone.

Example:
- spacing may be estimated if geometry/scale is adequate, but hidden embedment cannot be established.

### nonvisual
The requirement needs a human/nonvisual record.

Examples may include:
- actual torque
- hidden substrate capacity
- chemical cure state
- concealed embedment not visible in the capture

## Requirement states

- supported
- uncertain
- missing
- missed_opportunity
- human_confirmation_required

## Agent actions

supported
-> continue

uncertain
-> request targeted proof

missing before deadline
-> request targeted proof

missing after concealment deadline
-> escalate human / missed-proof exception

nonvisual
-> escalate human / request nonvisual confirmation

## Job-binding rule

Evidence may support a requirement only if the media is already bound to the same JobEvidenceRecord.

Free-floating media cannot satisfy job requirements.

## Source-grounding rule

If the source is absent, unreadable, ambiguous, or not approved:

DO NOT create a precise requirement from memory or general construction knowledge.

Instead:
- mark source resolution pending,
- request the approved source,
- or ask for qualified human confirmation.

## Termination-bar example

If a manufacturer guide later states a specific:
- screw spacing,
- concrete-nail spacing,
- fastener sequence,
- corner treatment,
- edge distance,
- or substrate-specific fastening rule,

PeakLogic may create an EvidenceRequirement sourced to that exact guide/location.

The visual system may then ask:
- is the termination bar visible?
- are fastener candidates visible?
- is the image perpendicular/clear enough for spacing analysis?
- is a scale/reference available?
- are corner conditions visible?

It must not claim hidden embedment, torque, substrate capacity, or compliance beyond what the source and pixels support.

## Trial 001 role

Trial 001 already provides real source-grounded obligations from the work-order packet, including photo-documentation requirements.

Requirement Resolver v1 is intended to replace the earlier assumption that one hard-coded safety-anchor template defines the product.

The safety-anchor scenario remains one useful proof-before-concealment case, not the product boundary.
