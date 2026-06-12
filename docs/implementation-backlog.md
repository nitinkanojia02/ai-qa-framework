# Implementation Backlog

This backlog translates the target architecture into practical implementation tracks for this repository.

## Track 1: Foundation and hardening

### 1.1 Config and secrets
- [ ] Move hardcoded credentials out of `config/framework_config.yaml`
- [ ] Support environment-variable overrides for sensitive values
- [ ] Add a checked-in safe example config for local setup
- [ ] Document secret handling in the README

### 1.2 Artifact hygiene
- [ ] Define which runtime artifacts should be committed vs ignored
- [ ] Add cleanup/retention guidance for screenshots, logs, and run outputs
- [ ] Standardize artifact naming and metadata fields

### 1.3 Documentation
- [ ] Keep architecture docs aligned with code changes
- [ ] Add a repository runbook describing the current execution path

## Track 2: Exploration and understanding

### 2.1 Exploration reliability
- [ ] Improve page state detection after actions
- [ ] Strengthen loop detection heuristics
- [ ] Add action risk classification to exploration candidates
- [ ] Add environment-aware exploration guards

### 2.2 Semantic understanding
- [ ] Add page type classification
- [ ] Add action intent classification
- [ ] Add module/business capability inference
- [ ] Add confidence scoring for inferred semantics

## Track 3: Knowledge model

### 3.1 Schema
- [ ] Define normalized schemas for page, element, locator, workflow, execution, and healing entities
- [ ] Add serializers/mappers from current artifacts into the knowledge model
- [ ] Version knowledge schemas

### 3.2 Persistence
- [ ] Create a knowledge store abstraction
- [ ] Persist cross-run memory separate from transient artifacts
- [ ] Support querying by page, workflow, and element identity

## Track 4: Test design generation

### 4.1 Manual test cases
- [ ] Generate manual test cases from workflow knowledge
- [ ] Include preconditions, steps, and expected results
- [ ] Add priority/risk tagging
- [ ] Add validation workflow for low-confidence test cases

### 4.2 Scenario modeling
- [ ] Create reusable scenario definitions independent of Robot output
- [ ] Link scenarios to workflows and business entities

## Track 5: Robot generation and execution

### 5.1 Generation
- [ ] Define Robot generation templates and conventions
- [ ] Generate pages, flows, resources, and suites from knowledge
- [ ] Reuse locator repository outputs in generated assets

### 5.2 Execution
- [ ] Add Robot execution as a first-class pipeline stage
- [ ] Parse Robot results back into execution records
- [ ] Link failures to workflows, pages, and locators

## Track 6: Healing and adaptive repair

### 6.1 Locator healing
- [ ] Track locator success/failure history across runs
- [ ] Update locator rankings from execution feedback
- [ ] Persist healing outcomes into the knowledge model

### 6.2 Script repair
- [ ] Add minimal patch generation for brittle Robot assets
- [ ] Require approval for high-risk repairs
- [ ] Record all repairs in an audit-friendly format

## Track 7: Governance and autonomy controls

### 7.1 Confidence model
- [ ] Define confidence thresholds by capability
- [ ] Separate autonomous thresholds for exploration, generation, and healing

### 7.2 Approval model
- [ ] Define human review queues for low-confidence or high-risk outputs
- [ ] Add approval metadata into generated artifacts and knowledge entities

### 7.3 Enterprise safety
- [ ] Add action policy config for safe/caution/restricted actions
- [ ] Add stronger constraints for production-like environments

## Suggested implementation order

1. Config/secrets hardening
2. Exploration risk classification and guards
3. Knowledge model schemas and persistence
4. Manual test case generation
5. Robot generation
6. Robot execution feedback
7. Healing and confidence/approval loop
