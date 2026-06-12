# AI QA Framework: Complete Overview and Architecture

## 1. Executive Summary

AI QA Framework is an AI-native automation platform for exploring enterprise web applications, understanding UI structure and workflows, generating manual and automated test assets, executing generated automation, and learning from execution outcomes.

The framework is designed to reduce manual QA and automation engineering effort by combining:
- browser-driven application exploration
- DOM and UI intelligence
- AI-based reasoning and scenario generation
- automated Robot Framework asset generation
- execution, failure analysis, and healing scaffolding
- persistent application knowledge

Today, the framework provides a working end-to-end baseline that can:
- authenticate into a target application
- analyze pages and UI elements
- generate locator intelligence
- explore visible application paths
- use AI to generate test scenarios
- generate manual test cases
- generate Robot Framework automation assets
- execute generated Robot suites
- analyze failures and produce healing suggestions

This document explains the framework from scratch so that engineering teams, QA teams, leadership, and new contributors can understand what has been built, how it works, what its current scope is, and where it is heading.

---

## 2. Why This Framework Exists

Traditional enterprise test automation often suffers from the same recurring problems:
- heavy manual effort to understand applications
- high maintenance cost for automation assets
- brittle selectors and unstable scripts
- poor traceability between UI changes and broken automation
- limited ability to scale automation coverage quickly
- duplication of effort between manual QA and automation teams

This framework was created to address those problems by shifting from manually authored automation to AI-assisted and eventually AI-driven automation generation.

The core idea is:
- let the framework explore the application
- let the framework collect evidence about pages, elements, and flows
- let AI reason over that evidence
- generate structured QA outputs from what was learned
- execute those outputs and learn from the results

---

## 3. Vision and Long-Term Direction

The long-term goal is to evolve this repository into an end-to-end autonomous testing platform capable of:
- exploring applications automatically
- understanding pages, elements, and workflows
- analyzing DOM structures and UI behavior
- generating locators intelligently
- creating manual test cases automatically
- generating Robot Framework automation assets automatically
- executing generated automation
- analyzing failures and healing broken automation
- continuously learning application knowledge over time

The intended operating loop is:

**Discover -> Interpret -> Model -> Generate -> Validate -> Execute -> Heal -> Learn**

In this model:
- Playwright and deterministic tooling perform the exploration and evidence gathering
- AI performs reasoning, scenario generation, and interpretation
- the framework handles orchestration, persistence, artifact generation, and execution

---

## 4. Current Scope and Status

### Current maturity
The framework is currently a **working AI-driven baseline** rather than a final enterprise-grade autonomous testing platform.

### What is implemented today
The current repository supports:
- configuration-driven browser startup and login
- Playwright-based page analysis and element discovery
- locator ranking and persistence
- shallow autonomous exploration
- workflow transition recording
- AI-generated page and workflow summaries
- AI-generated manual test scenarios
- manual test case artifact generation
- Robot Framework generation with modular assets
- execution of generated Robot tests
- failure analysis and healing suggestion generation
- persistent application knowledge storage

### What is still evolving
The framework still needs improvement in:
- deeper business workflow understanding
- richer and more precise scenario quality
- stronger page-resource and POM-style automation assets
- stronger assertion generation
- deeper exploration and state detection
- richer use of learned locator/action knowledge
- enterprise hardening and governance

---

## 5. Core Capabilities

### 5.1 Application access and login
The framework can:
- start a browser session
- navigate to a configured URL
- perform login using configured selectors
- validate successful authentication

### 5.2 Page and DOM understanding
The framework can:
- extract DOM intelligence from the current page
- classify visible UI elements
- capture screenshots and DOM snapshots
- persist page analysis artifacts

### 5.3 Locator intelligence
The framework can:
- derive candidate locators
- rank locators by stability and preference
- persist best and fallback locators
- use locator knowledge in generated automation

### 5.4 Exploration and workflow discovery
The framework can:
- build exploration candidates from discovered elements
- select next actions using a lightweight navigation strategy
- record transitions between application states
- persist workflow graphs and analytics

### 5.5 AI reasoning and scenario generation
The framework can:
- package exploration evidence for AI consumption
- call the configured AI endpoint
- generate structured test scenarios using AI
- normalize AI-generated scenarios into internal test-case structures

### 5.6 Manual test generation
The framework can:
- convert AI-generated scenarios into manual test case artifacts
- produce JSON and Markdown outputs
- label scenarios by type, category, and risk level

### 5.7 Robot Framework generation
The framework can:
- generate Robot suites from manual test cases
- generate root keyword resources
- generate variable resources
- generate page, flow, and modular suite artifacts
- use SeleniumLibrary-backed generated keywords

### 5.8 Execution and learning
The framework can:
- run generated Robot suites
- store execution reports and outputs
- analyze failures
- generate healing suggestions
- update knowledge from execution results

---

## 6. Technology Stack

The framework uses the following technologies.

### Python
Primary implementation language for orchestration, analysis, generation, persistence, and execution logic.

### Playwright
Used for application entry, navigation, login, DOM interaction, and browser-driven exploration.

### Robot Framework
Used as the generated automation execution layer.

### SeleniumLibrary
Used by generated Robot assets for browser actions such as clicking, typing, navigation, and assertions.

### YAML
Used for framework configuration including:
- application configuration
- browser configuration
- AI configuration
- locator configuration
- assertion configuration

### Requests
Used for integration with the AI endpoint.

### GAINS AI API
Used as the current AI provider for:
- page summaries
- workflow summaries
- AI-driven scenario generation

### JSON artifacts
Used for:
- knowledge persistence
- execution results
- workflow graphs
- AI outputs
- generated test assets

---

## 7. High-Level Architecture

The framework can be understood as a set of cooperating layers.

### 7.1 Configuration layer
Responsible for loading, resolving, and exposing framework settings.

### 7.2 Browser and exploration layer
Responsible for:
- browser management
- login
- DOM extraction
- page analysis
- exploration and workflow capture

### 7.3 Knowledge layer
Responsible for:
- storing pages, elements, locators, transitions, failures, and healing data
- providing reusable application memory across runs

### 7.4 AI reasoning layer
Responsible for:
- page and workflow summaries
- scenario generation from evidence
- conversion of evidence into structured AI inputs

### 7.5 Test generation layer
Responsible for:
- manual test case generation
- Robot suite/resource generation
- modular asset creation

### 7.6 Execution layer
Responsible for:
- running generated Robot tests
- collecting execution outputs
- parsing failures

### 7.7 Healing layer
Responsible for:
- generating healing suggestions
- applying guarded healing changes
- retrying generated automation when appropriate

---

## 8. End-to-End Runtime Flow

The main entry point is:
- `libraries/run_autonomous_pipeline.py`

The runtime flow is:

1. load config files
2. initialize artifact directories
3. create framework services and managers
4. start the browser
5. navigate to the application
6. perform authentication
7. analyze the current page
8. enrich page knowledge semantically
9. generate locator intelligence
10. run a self-healing smoke lookup
11. explore the application and capture workflow transitions
12. persist workflow graph and exploration analytics
13. generate AI summaries
14. generate AI-driven scenarios
15. generate manual test case artifacts
16. generate Robot Framework assets
17. execute generated Robot tests
18. analyze failures
19. generate healing suggestions
20. persist application knowledge and execution result

---

## 9. Repository Structure

### `libraries/`
Contains the primary framework implementation and orchestration logic.

### `models/`
Contains structured models used by the framework for execution, pages, locators, workflows, and knowledge.

### `utils/`
Contains helper utilities for logging, file operations, JSON handling, and artifact management.

### `config/`
Contains YAML configuration files for the framework.

### `config/environments/`
Contains environment-specific configuration seeds.

### `data/prompts/`
Contains AI prompt templates used for page summary, workflow summary, and scenario generation.

### `docs/`
Contains architecture, roadmap, policy, and implementation documentation.

### `artifacts/`
Contains runtime outputs generated by the framework.

---

## 10. Major Components and Their Purpose

This section explains the most important files in the framework and how they are used.

### `libraries/run_autonomous_pipeline.py`
This is the main orchestrator of the framework.

Responsibilities:
- initialize all services and managers
- execute the end-to-end automation pipeline
- coordinate discovery, generation, execution, and persistence
- store final execution results

This is the primary trigger point for running the framework.

### `libraries/config_loader.py`
Loads and resolves YAML configuration.

Responsibilities:
- load config files from `config/`
- support environment variable overrides for selected fields
- expose merged config to the rest of the framework

### `libraries/browser_manager.py`
Handles browser startup and navigation.

Responsibilities:
- launch Playwright browser
- create page and context
- navigate to target URLs
- capture screenshots
- close resources

### `libraries/authenticator.py`
Executes the configured login flow.

Responsibilities:
- optionally execute a pre-login click
- enter username and password
- submit the login form
- validate successful login

### `libraries/dom_understanding_engine.py`
Extracts UI structure from the DOM.

Responsibilities:
- inspect current page DOM
- capture visible and interactive elements
- derive attributes and UI structure information
- classify elements into categories

### `libraries/page_analyzer.py`
Builds a structured page snapshot.

Responsibilities:
- coordinate DOM extraction
- persist page screenshots and analysis JSON
- build structured page analysis models

### `libraries/semantic_enricher.py`
Adds semantic hints to pages, elements, and transitions.

Responsibilities:
- infer page type
- infer business-purpose hints
- infer element intent
- infer risk level hints
- enrich workflow transitions with semantic labels

### `libraries/locator_ranker.py`
Generates and ranks locator candidates.

Responsibilities:
- derive best and fallback locators
- rank selectors based on configured strategy
- persist locator intelligence artifacts

### `libraries/self_healing_locator.py`
Provides locator resolution logic with fallback behavior.

Responsibilities:
- attempt to resolve elements using ranked locators
- support a self-healing style lookup process

### `libraries/workflow_agent.py`
Builds exploration candidates from discovered elements.

### `libraries/navigation_predictor.py`
Selects the next candidate action during exploration.

### `libraries/intelligent_explorer.py`
Executes autonomous exploration.

Responsibilities:
- attempt interactions on discovered elements
- record results
- coordinate with workflow memory and loop detection

### `libraries/workflow_memory.py`
Stores workflow transitions and persists workflow graphs.

### `libraries/exploration_analytics.py`
Builds and persists exploration summary artifacts.

### `libraries/gains_ai_client.py`
Encapsulates communication with the GAINS AI API.

Responsibilities:
- prepare AI query payloads
- call the configured endpoint
- parse response text
- support mock mode when configured

### `libraries/ai_summary_service.py`
Generates page and workflow summaries using AI.

### `libraries/ai_scenario_service.py`
Generates structured scenarios using AI from exploration evidence.

Responsibilities:
- build AI prompt input from evidence
- call the AI client
- parse JSON scenario payloads
- normalize AI output into scenario structures

### `libraries/scenario_intelligence.py`
Coordinates AI-driven scenario generation.

Responsibilities:
- build evidence packages per page
- invoke AI scenario generation
- enrich normalized scenarios with page and module metadata
- deduplicate scenarios

### `libraries/manual_test_case_generator.py`
Converts AI scenarios into manual test case artifacts.

Responsibilities:
- build JSON manual test case output
- build Markdown manual test case output
- assign identifiers and metadata

### `libraries/robot_test_generator.py`
Generates Robot Framework automation assets.

Responsibilities:
- generate root Robot suite
- generate keyword resource
- generate variable resource
- generate page resources
- generate flow resources
- generate modular suites
- map scenario steps into Robot actions and assertions

### `libraries/robot_executor.py`
Runs generated Robot suites.

Responsibilities:
- execute the `robot` CLI
- store run outputs
- capture stdout/stderr

### `libraries/robot_failure_analyzer.py`
Parses Robot execution outputs.

Responsibilities:
- inspect Robot output XML
- extract failed tests and messages
- classify failures

### `libraries/healing_suggester.py`
Generates healing suggestions based on failure analysis and known locators.

### `libraries/healing_applier.py`
Applies a guarded healing action to generated Robot resources and supports retry execution.

### `libraries/knowledge_store.py`
Persists structured application knowledge.

Responsibilities:
- load existing knowledge
- upsert pages, elements, locators, transitions, executions, failures, and healing suggestions
- persist canonical and snapshot knowledge files

### `models/knowledge_models.py`
Defines the structured knowledge entities used by the framework.

### `utils/artifact_manager.py`
Creates and manages artifact directory paths used by the framework.

---

## 11. Key Configuration Files

### `config/framework_config.yaml`
Primary application and framework execution configuration.

Defines:
- application name and base URL
- authentication selectors and credentials
- execution flags
- feature toggles

### `config/browser_config.yaml`
Defines browser-related configuration.

### `config/ai_config.yaml`
Defines AI endpoint behavior, token environment variable, retry behavior, and model settings.

### `config/locator_config.yaml`
Defines locator ranking preferences and strategies.

### `config/assertion_config.yaml`
Defines assertion-related settings.

### `config/framework_config.example.yaml`
Provides a safer example configuration pattern for environment-variable-driven configuration.

---

## 12. Artifacts Generated by the Framework

The framework generates runtime artifacts under `artifacts/`.

### `artifacts/page_data/`
Contains page DOM and analysis JSON files.

### `artifacts/screenshots/`
Contains screenshots captured during execution.

### `artifacts/locator_intelligence/`
Contains locator repository outputs.

### `artifacts/workflow_data/`
Contains workflow graph JSON files.

### `artifacts/analytics/`
Contains exploration summaries and AI-generated summaries.

### `artifacts/knowledge_graph/`
Contains `application_knowledge.json` and knowledge snapshots.

### `artifacts/testcases/`
Contains generated manual test case JSON and Markdown files.

### `artifacts/generated_robot_tests/`
Contains generated Robot assets including:
- root suite
- keyword resource
- variable resource
- page resources
- flow resources
- modular suites

### `artifacts/execution/robot_runs/`
Contains Robot execution outputs such as:
- `output.xml`
- `log.html`
- `report.html`
- stdout/stderr

### `artifacts/healing/`
Contains generated healing suggestions.

---

## 13. Current Capabilities in Practical Terms

Today the framework can be used as:
- an application discovery accelerator
- a UI smoke scenario generator
- a manual test generation assistant
- a Robot automation bootstrap generator
- a generated test execution and analysis baseline

A realistic current use case is:
- authenticate into an enterprise web app
- analyze the landing page and visible UI controls
- generate AI-driven smoke and action-oriented scenarios
- generate Robot assets from those scenarios
- run the generated suite and capture results

---

## 14. Current Limitations

Even though the framework is now operational, it still has important limitations.

### 14.1 Business understanding is still limited
The framework is still better at understanding visible UI behavior than deep business meaning.

### 14.2 Exploration depth is limited
Exploration currently captures shallow flows more reliably than deep multi-step workflows.

### 14.3 Generated page resources need to become richer
Page resources exist, but they are not yet full page models with strong reusable business behavior.

### 14.4 Assertions need to become stronger
Some generated automation is still smoke-oriented and must evolve toward more meaningful validations.

### 14.5 Scenario quality depends on exploration evidence quality
Because AI reasoning is driven by collected evidence, limited evidence leads to shallow scenarios.

### 14.6 Enterprise hardening is still pending
The framework still needs additional work around:
- governance
- confidence scoring
- approval flows
- safety controls for sensitive actions

---

## 15. Current Maturity Assessment

The framework should currently be positioned as:

**A working AI-driven baseline for autonomous UI exploration, scenario generation, and generated Robot execution.**

It is beyond prototype stage because:
- it runs end to end
- it uses a real AI endpoint
- it generates and executes automation
- it persists knowledge and execution evidence

It is not yet a final enterprise-grade product because:
- business-flow depth is still limited
- generated assets still need stronger action/assertion quality
- semantics and page modeling still need improvement

---

## 16. Future Roadmap

### Near-term improvements
- enrich exploration evidence
- improve scenario specificity and quality
- strengthen page-level Robot resources
- strengthen locator-backed action and assertion mapping
- improve business-semantic understanding

### Mid-term improvements
- deeper workflow discovery
- stronger page and flow models
- stronger failure-to-healing mapping
- more realistic business-flow validations

### Long-term improvements
- robust self-healing automation
- enterprise-safe exploration and approval controls
- stronger confidence-based execution governance
- multi-application and broader enterprise scalability

---

## 17. How to Run the Framework Locally

### Prerequisites
- Python environment with dependencies installed
- Playwright installed and working
- Robot Framework and SeleniumLibrary installed if Robot generation/execution is enabled
- valid GAINS AI token when running with real AI mode

### Configure
Update:
- `config/framework_config.yaml`
- `config/ai_config.yaml`

Set environment variables as needed, for example:

```bash
export DEVEX_AI_TOKEN="your-token"
```

### Run
From the repository root:

```bash
python -m libraries.run_autonomous_pipeline
```

### Inspect outputs
After a run, inspect:
- `artifacts/knowledge_graph/application_knowledge.json`
- `artifacts/testcases/generated_manual_test_cases.md`
- `artifacts/generated_robot_tests/`
- `artifacts/execution/robot_runs/`

---

## 18. How Teams Can Use the Framework Today

### QA teams
Can use the framework to:
- accelerate smoke coverage design
- generate starter manual test cases
- bootstrap Robot automation

### Automation engineers
Can use the framework to:
- discover locator intelligence
- generate baseline automation assets
- reduce initial test authoring effort

### Product and engineering teams
Can use the framework to:
- understand key visible workflows faster
- inspect generated knowledge and automation artifacts
- assess application UI state through artifacts and reports

---

## 19. Summary

AI QA Framework is an AI-native automation platform under active evolution.

Its current value lies in the fact that it already provides a working loop across:
- exploration
- AI reasoning
- scenario generation
- manual test generation
- Robot generation
- execution
- analysis

The framework is not yet the final form of an enterprise-grade autonomous testing platform, but it now provides a strong operational baseline from which that goal can be pursued systematically.

The next phase of work should focus less on infrastructure and more on improving the quality, depth, and business relevance of generated outputs.
