# AI QA Framework

An AI-native automation framework for discovering, understanding, modeling, generating, executing, and healing enterprise application tests.

## Product direction

This repository is evolving toward an end-to-end autonomous testing platform that can:

- explore applications automatically
- understand business flows, pages, and UI elements
- analyze DOM structures
- generate locators intelligently
- create manual test cases automatically
- generate Robot Framework automation scripts
- perform self-healing automation
- learn workflows dynamically
- build a persistent knowledge graph of applications
- execute generated automation and continuously improve from results

## Core operating loop

**Discover -> Interpret -> Model -> Generate -> Validate -> Execute -> Heal -> Learn**

## Current repository focus

Today, the repository already contains early building blocks for:

- Playwright-based browser automation
- authentication and session setup
- DOM understanding and page analysis
- intelligent locator ranking
- self-healing locator resolution
- autonomous exploration and workflow memory
- AI-assisted summaries and prompt-driven generation hooks

## Important note

The current implementation is stronger on the exploration, analysis, locator, and workflow-learning side than on fully operational Robot generation and execution. Robot-related capabilities exist as part of the target direction and should be treated as a key downstream generation and execution layer.

## Key code areas

- `libraries/` - core Python orchestration and framework logic
- `models/` - structured models for analysis, locators, workflows, and execution
- `config/` - framework, browser, locator, AI, and environment configuration
- `prompts/` - prompt templates for generation and repair tasks
- `artifacts/` - runtime outputs such as screenshots, workflow data, and analytics
- `tests/` and `resources/` - automation assets and Robot-facing scaffolding

## Architecture and planning docs

See:

- `docs/target-architecture-and-roadmap.md`
- `docs/knowledge-model.md`
- `docs/autonomous-crawling-policy.md`
- `docs/implementation-backlog.md`

These documents define the intended platform architecture, phased roadmap, knowledge model direction, safe exploration policy, and practical implementation tracks for this repository.

## Implemented foundation

The autonomous pipeline now persists a lightweight application knowledge store to:

- `artifacts/knowledge_graph/application_knowledge.json`

This knowledge artifact currently captures:
- discovered pages
- semantic page classification and business-purpose hints
- discovered UI elements
- element intent and risk classification
- generated locator records
- workflow transitions with semantic labels
- execution history

The pipeline now also generates manual test case artifacts to:
- `artifacts/testcases/generated_manual_test_cases.json`
- `artifacts/testcases/generated_manual_test_cases.md`

Manual test generation is now AI-first where enabled:
- Playwright discovery and persisted knowledge are packaged as exploration evidence
- AI generates structured scenarios from evidence using prompt-driven reasoning
- the framework validates, normalizes, stores, and converts those scenarios into manual tests
- fallback smoke-only generation is used only when AI scenario output is unavailable

The manual test generation layer now expands discovered knowledge into richer scenario sets such as:
- positive scenarios
- negative scenarios
- edge and validation scenarios
- search, authentication, workflow, and data-entry scenarios

The pipeline can generate Robot Framework assets to:
- `artifacts/generated_robot_tests/generated_workflows.robot`
- `artifacts/generated_robot_tests/generated_keywords.resource`
- `artifacts/generated_robot_tests/generated_variables.resource`
- `artifacts/generated_robot_tests/pages/*.resource`
- `artifacts/generated_robot_tests/flows/*.resource`
- `artifacts/generated_robot_tests/suites/*.robot`

The generated Robot resource is now locator-aware at a foundation level and includes:
- learned locator variables derived from persisted knowledge
- generated action keywords for discovered page elements
- page-aware reusable keyword scaffolding
- action-aware keyword generation for click, input, and assert style interactions
- SeleniumLibrary-backed interaction keywords for learned locator execution
- generated SeleniumLibrary suite setup, teardown, and session bootstrap
- generated variable resource for base URL and login selectors
- generated page resources for discovered page actions
- page-specific open and visible-state keywords
- page-specific action keywords derived from learned locators and intents
- semantic page keywords for login, search, form submission, cancel, and primary assertions
- generated flow resources grouped by workflow type
- generated modular suites grouped by scenario category

Robot generation is controlled by `config/framework_config.yaml`:
- `features.enable_robot_generation: true|false`

If the `robot` CLI is available in the execution environment and Robot generation is enabled, the pipeline executes the generated suite and stores outputs under:
- `artifacts/execution/robot_runs/`

The execution stage now also analyzes Robot failures and persists failure knowledge, including:
- failed test names
- failure messages
- basic failure classification
- suspected locator-related failures

The pipeline now also generates healing suggestion artifacts for locator-related failures at:
- `artifacts/healing/healing_suggestions.json`

When a sufficiently confident healing suggestion is available, the pipeline can now:
- apply the top suggestion to the generated Robot resource in a guarded way
- create a backup of the original generated resource
- retry the generated Robot suite once
- persist retry execution artifacts and failure analysis

## Near-term engineering priorities

1. stabilize the current exploration pipeline
2. externalize sensitive configuration and credentials
3. define persistent application knowledge models
4. generate manual test cases from discovered workflows
5. generate and execute Robot Framework assets as first-class outputs
6. add confidence scoring, risk controls, and approval gates for enterprise-safe autonomy

## Configuration note

The current checked-in `config/framework_config.yaml` should be treated as environment-specific and not as the long-term secure pattern.

A safe example configuration has been added at:

- `config/framework_config.example.yaml`

The config loader now supports environment-variable based secret injection and overrides for key framework settings.

Supported overrides:

- `APP_BASE_URL`
- `APP_ENVIRONMENT`
- `APP_LOGIN_URL`
- `APP_USERNAME`
- `APP_PASSWORD`

It also resolves placeholder values in YAML when written as `${ENV_VAR}`.

Example:

```bash
export APP_USERNAME="my-user"
export APP_PASSWORD="my-password"
python libraries/run_autonomous_pipeline.py
```
