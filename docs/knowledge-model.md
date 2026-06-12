# Application Knowledge Model

## Purpose

This document defines the persistent knowledge model for the AI-native automation framework.

The goal of the knowledge model is to turn one-time exploration outputs into reusable application memory that supports:

- better exploration decisions
- workflow understanding
- locator stability improvement
- manual test case generation
- Robot Framework generation
- execution traceability
- self-healing and adaptive learning

## Design principles

1. Persist knowledge across runs.
2. Separate raw observations from inferred meaning.
3. Track confidence for all AI-derived interpretations.
4. Version knowledge as the application changes.
5. Link generated assets back to source evidence.
6. Record approval state for human-validated artifacts.
7. Keep execution and healing history attached to the same graph.

## Core entity types

### Application
Represents the target system under test.

Suggested fields:
- `application_id`
- `name`
- `environment`
- `base_url`
- `authentication_type`
- `status`
- `last_explored_at`

### Module
Represents a logical product area discovered during crawling.

Suggested fields:
- `module_id`
- `name`
- `description`
- `parent_application_id`
- `discovery_confidence`
- `validation_status`

### Page
Represents a distinct application page or state.

Suggested fields:
- `page_id`
- `name`
- `title`
- `url`
- `url_pattern`
- `page_type`
- `business_purpose`
- `module_id`
- `entry_conditions`
- `exit_conditions`
- `discovery_confidence`
- `validation_status`

### Element
Represents a visible or interactable UI element.

Suggested fields:
- `element_id`
- `page_id`
- `element_type`
- `semantic_role`
- `text`
- `attributes`
- `is_interactable`
- `is_visible`
- `risk_class`
- `stability_score`

### Locator
Represents a candidate or approved selector strategy for an element.

Suggested fields:
- `locator_id`
- `element_id`
- `strategy_type`
- `selector_value`
- `ranking_score`
- `fallback_order`
- `historical_success_rate`
- `last_verified_at`
- `status`

### Action
Represents a user action the framework can attempt.

Suggested fields:
- `action_id`
- `source_page_id`
- `element_id`
- `action_type`
- `intent`
- `risk_class`
- `expected_outcome`
- `confidence`

### Workflow
Represents a business flow discovered through transitions and interpretation.

Suggested fields:
- `workflow_id`
- `name`
- `description`
- `workflow_type`
- `business_entity`
- `preconditions`
- `postconditions`
- `criticality`
- `confidence`
- `validation_status`

### Workflow Step
Represents a step within a workflow.

Suggested fields:
- `workflow_step_id`
- `workflow_id`
- `sequence_number`
- `page_id`
- `action_id`
- `expected_result`
- `branch_condition`

### Business Entity
Represents a domain concept inferred from the application.

Suggested fields:
- `entity_id`
- `name`
- `description`
- `related_modules`
- `related_pages`
- `crud_capabilities`
- `confidence`

### Manual Test Case
Represents a human-readable validation asset generated from workflow knowledge.

Suggested fields:
- `test_case_id`
- `title`
- `objective`
- `preconditions`
- `steps`
- `expected_results`
- `workflow_id`
- `priority`
- `risk_level`
- `confidence`
- `validation_status`

### Automation Asset
Represents an executable generated artifact.

Suggested fields:
- `asset_id`
- `asset_type`
- `path`
- `workflow_id`
- `test_case_id`
- `generation_version`
- `status`

### Execution Record
Represents an automation execution instance.

Suggested fields:
- `execution_id`
- `asset_id`
- `environment`
- `started_at`
- `completed_at`
- `status`
- `evidence_paths`
- `failure_classification`

### Healing Record
Represents a repair or adaptation attempt.

Suggested fields:
- `healing_id`
- `execution_id`
- `target_asset_id`
- `target_locator_id`
- `root_cause`
- `repair_action`
- `before_state`
- `after_state`
- `confidence`
- `approval_status`
- `outcome`

## Relationship model

Examples of important graph links:

- `Application -> has_module -> Module`
- `Module -> has_page -> Page`
- `Page -> contains -> Element`
- `Element -> has_locator -> Locator`
- `Page -> allows_action -> Action`
- `Action -> transitions_to -> Page`
- `Workflow -> includes_step -> Workflow Step`
- `Workflow Step -> uses_action -> Action`
- `Workflow -> validates_entity -> Business Entity`
- `Manual Test Case -> covers_workflow -> Workflow`
- `Automation Asset -> automates -> Manual Test Case`
- `Execution Record -> executed -> Automation Asset`
- `Healing Record -> repairs -> Locator`
- `Healing Record -> updates -> Automation Asset`

## Evidence model

Each inferred entity should be traceable back to evidence such as:
- DOM snapshot path
- screenshot path
- page analysis artifact
- workflow graph artifact
- execution report artifact
- LLM reasoning summary

## Confidence and validation

All inferred knowledge should support:
- `confidence_score`
- `validation_status` (`pending`, `approved`, `rejected`, `auto-approved`)
- `validated_by`
- `validated_at`

## Suggested persistence approach

Near term:
- JSON artifacts backed by normalized repository schemas

Mid term:
- graph-oriented persistence layer for entity relationships

Long term:
- centralized knowledge service supporting versioning, querying, and cross-run learning

## Minimum viable implementation for this repo

The first implementation should persist at least:
- applications
- pages
- elements
- locators
- actions
- workflows
- manual test cases
- automation assets
- execution records
- healing records

A practical next step is to introduce versioned schema files and serializers that connect current artifacts under `artifacts/` into a reusable knowledge representation.
