# Autonomous Crawling and Safety Policy

## Purpose

This document defines how the framework should explore applications safely while minimizing manual effort.

The crawler must not behave like a blind click bot. It should operate with controlled autonomy, risk awareness, and clear escalation rules.

## Objectives

- discover pages, elements, and workflows efficiently
- minimize harmful or irreversible actions
- support enterprise-safe autonomous exploration
- allow human validation only where risk or confidence requires it

## Core policy

The crawler should classify actions before execution and apply policy decisions based on risk.

## Action risk classes

### Safe
Examples:
- open menus
- navigate to pages
- expand or collapse sections
- switch tabs
- search with harmless input
- filter and sort
- paginate tables
- inspect read-only details

Policy:
- allowed for autonomous execution
- should still be logged and linked to state transitions

### Caution
Examples:
- edit forms
- save draft
- upload files
- trigger asynchronous refresh actions
- open multi-step wizards
- create temporary records in controlled environments

Policy:
- allowed only in approved non-production environments
- requires test-data or rollback strategy where relevant
- confidence threshold should be higher than safe actions

### Restricted
Examples:
- submit final transaction
- approve or reject
- delete
- terminate
- deactivate
- publish
- pay
- irreversible or business-impacting actions

Policy:
- blocked by default
- only allowed with explicit environment and policy approval
- should require a traceable reason and elevated confidence

## Exploration rules

### Rule 1: Prefer navigation before mutation
The crawler should maximize read-only discovery before attempting state-changing actions.

### Rule 2: Record state before acting
Before each significant action, capture enough evidence to explain:
- current page/state
- candidate element
- intended action
- risk class
- expected outcome

### Rule 3: Avoid repeated loops
The crawler should use workflow memory and loop detection to prevent repeated low-value traversal.

### Rule 4: Respect confidence thresholds
Low-confidence element/action interpretations should not trigger risky actions.

### Rule 5: Prefer sandboxed/test environments
Autonomous exploration should be limited to approved QA/UAT/sandbox environments unless explicitly authorized.

### Rule 6: Do not hide uncertainty
If the system cannot confidently explain what an action will do, it should classify it conservatively.

## Suggested decision flow

1. detect visible interactable element
2. infer action type and likely intent
3. assign risk class
4. check environment policy
5. check confidence threshold
6. check loop/repetition history
7. execute or skip
8. record transition and evidence

## Environment policy expectations

### Non-production
- safe actions: allowed
- caution actions: conditionally allowed
- restricted actions: approval required

### Production
- safe actions: highly constrained
- caution actions: blocked by default
- restricted actions: blocked

## Human validation triggers

Human review should be required when:
- confidence is below threshold
- action is destructive or business-critical
- new module/workflow is discovered with ambiguous meaning
- generated asset could impact many downstream tests
- healing affects a critical workflow

## Evidence requirements

For auditability, each exploration step should store:
- timestamp
- page URL/title
- screenshot path when relevant
- element metadata
- locator used
- risk classification
- confidence score
- result status

## Near-term implementation guidance

For this repo, the first concrete implementation should add:
- explicit risk classification metadata on discovered actions
- environment-aware policy config
- skip/block behavior for restricted actions
- evidence fields in workflow and execution artifacts
- confidence thresholds for autonomous action execution
