# Implementation Plan: Multi-Agent Script Intelligence Platform

This plan converts the approved PRD into an execution checklist. It is intentionally organized around TDD tracer bullets rather than horizontal phases.

Source PRD: [PRD.md](D:/SWE_DEV_NEW/Script-Insights/docs/PRD.md)

## Locked Decisions

- [x] Build the initial product as a real multi-agent platform, not a single prompt wrapper.
- [x] Use `FastAPI` for the backend.
- [x] Use `Next.js` for the frontend.
- [x] Support both `paste text` and `PDF upload` in `v1`.
- [x] Include a `results dashboard`, `run history dashboard`, and `revision compare view` in `v1`.
- [x] Use `Groq` as the initial model provider.
- [x] Use `DSPy` selectively inside LLM agent programs and evaluation flows.
- [x] Prioritize automated tests for `ingestion/normalization`, `workflow orchestration`, `evaluation/guardrails`, and `API contracts`.

## TDD Working Agreement

- [x] Write one failing test for one observable behavior before each implementation slice.
- [x] Keep each slice vertical: test, minimal implementation, then refactor.
- [x] Test public interfaces only: API contracts, service boundaries, and user-visible UI behavior.
- [x] Do not write all tests upfront.
- [x] Do not call live Groq models from automated tests.
- [x] Keep model-dependent tests stubbed and deterministic.
- [x] Make one small commit per completed slice where practical.

## Initial Stack Decisions

- [x] Backend runtime: `Python 3.11+`
- [x] Backend web layer: `FastAPI`
- [x] Backend schemas: `Pydantic v2`
- [x] Persistence: `SQLAlchemy` + `SQLite`
- [x] Local DB default: `SQLite`, with runtime schema upgrades for local development
- [x] Async execution: repository-backed durable queue + worker drain or worker CLI, with an inline runner for tests and local sync execution
- [x] Model provider SDK: `groq`
- [x] LLM programming layer: `dspy`
- [x] Backend configuration: `.env`-driven `pydantic-settings`
- [x] Frontend runtime: `Next.js` App Router + `TypeScript`
- [x] Frontend data fetching: `TanStack Query`
- [x] Frontend styling: custom CSS design system
- [x] Frontend visualization: custom SVG/CSS score rings, factor bars, delta bars, and evidence panels

## Public Interfaces To Lock First

### Backend API

- [x] `POST /api/v1/analysis/runs`
  Purpose: submit pasted text or a PDF upload for analysis
- [x] `POST /api/v1/analysis/runs/upload`
  Purpose: submit a PDF file with optional `script_id` continuation support
- [x] `GET /api/v1/analysis/runs/{run_id}`
  Purpose: poll run status and fetch the versioned final result payload using the externally visible async run identifier
- [x] `GET /api/v1/scripts/{script_id}/runs?revision_id=...&status=...`
  Purpose: list run history for a script across revisions, with optional filters for revision and status
- [x] `GET /api/v1/scripts/{script_id}/compare?base_run_id=...&target_run_id=...`
  Purpose: compare two selected runs from the same script lineage, typically representing two revisions, and return deltas
- [x] `POST /api/v1/analysis/workers/drain`
  Purpose: drain queued runs in local durable-worker mode

### Frontend Routes

- [x] `/`
  Purpose: paste text or upload PDF and start analysis
- [x] `/runs/[runId]`
  Purpose: view analysis dashboard for one run
- [x] `/scripts/[scriptId]/history`
  Purpose: browse run history for a script, filter by revision or status, and reopen prior runs
- [x] `/scripts/[scriptId]/compare`
  Purpose: compare two selected runs from the same script lineage

## Deep Modules To Build

- [x] `ScriptNormalizer`
  Input adapters for raw text and extracted PDF text, outputting one canonical script schema
- [x] `AnalysisWorkflow`
  Orchestrates multi-agent execution, retries, partial failures, and aggregation behind one interface
- [x] `LLMGateway`
  Provider abstraction for Groq-backed calls and future fallback models
- [x] `DSPyProgramRegistry`
  Owns DSPy signatures and programs for summary, emotion, engagement, suggestions, and cliffhanger analysis
- [x] `ExecutionFingerprintService`
  Computes exact execution fingerprints and normalized-content fingerprints for safe reuse and candidate detection
- [x] `AnalysisEvaluator`
  Validates schema correctness, evidence grounding, score bounds, and partial-result acceptance
- [x] `RevisionComparisonService`
  Computes metric deltas, changed recommendations, changed evidence, and revision lineage metadata between two selected runs

## Domain Model Checklist

- [x] `scripts`
  Stable script identity across revisions
- [x] `script_revisions`
  Revision lineage, input source type, and normalization metadata
- [x] `normalized_scripts`
  Canonical scenes, dialogue turns, characters, and source spans persisted per revision for grounding, reruns, and compare flows
- [x] `source_documents`
  Uploaded files and extraction provenance
- [x] `analysis_runs`
  Durable async job or run state, timestamps, and versioned result contract exposed to the API
- [x] `agent_runs`
  Per-agent execution metadata, latency, warnings, and failures
- [x] `analysis_artifacts`
  Structured outputs from agents and final aggregation payloads
- [x] `compare_views` or computed compare payloads
  Decide whether compare responses are persisted or generated on demand

## Repo Shape To Create

- [x] `backend/app/api`
- [x] `backend/app/core`
- [x] `backend/app/db`
- [x] `backend/app/domain`
- [x] `backend/app/services`
- [x] `backend/app/agents`
- [x] `backend/app/evaluation`
- [x] `backend/tests`
- [x] `frontend/`
- [x] `frontend/src/app`
- [x] `frontend/src/components`
- [x] `frontend/src/lib`
- [x] `frontend/tests`

## Execution Order

### Slice 0: Bootstrap The Test Harness

- [x] RED: add a failing backend API test for app startup and health access
- [x] GREEN: create the FastAPI app factory and minimal test runner setup
- [x] REFACTOR: centralize settings and test fixtures

### Slice 1: Submit A Text Script For Analysis

- [x] RED: add a contract test proving `POST /api/v1/analysis/runs` accepts pasted text and returns `202` with stable identifiers plus an explicit contract version
- [x] GREEN: implement the minimal submission route, persistence for a new run, and inline execution mode for tests
- [x] REFACTOR: extract a `RunSubmissionService` behind the route

### Slice 2: Normalize Text Into A Canonical Script Schema

- [x] RED: add an integration test proving a submitted text script becomes a normalized structure with scenes, dialogue blocks, and warnings
- [x] GREEN: implement the first `ScriptNormalizer` path for raw text
- [x] REFACTOR: isolate normalization helpers and source span mapping

### Slice 3: Return A Summary From The First Agent

- [x] RED: add a test proving a completed run returns a structured summary with evidence spans
- [x] GREEN: implement the first DSPy summary program, stub LM wiring, and result serialization
- [x] REFACTOR: extract `LLMGateway` and `DSPyProgramRegistry` boundaries

### Slice 4: Add Emotion Analysis

- [x] RED: add a test proving the result includes dominant emotions, valence or arousal metadata, and an emotional arc
- [x] GREEN: implement the DSPy emotion program and response mapping
- [x] REFACTOR: share evidence and confidence mapping utilities

### Slice 5: Add Engagement Scoring

- [x] RED: add a test proving the result includes `overall_engagement_score` plus factor scores for hook, conflict, tension, pacing, stakes, and payoff
- [x] GREEN: implement the rubric-based DSPy engagement program and score normalization
- [x] REFACTOR: extract a reusable scoring schema and normalization service

### Slice 6: Add Recommendations And Cliffhanger Detection

- [x] RED: add a test proving the result includes categorized recommendations and a cliffhanger section
- [x] GREEN: implement the DSPy recommendation and cliffhanger programs
- [x] REFACTOR: deepen the aggregation layer so agent outputs are composed behind one interface

### Slice 7: Add Guardrails And Partial-Failure Handling

- [x] RED: add a test proving malformed agent output yields warnings and a partial result instead of a total run failure
- [x] GREEN: implement `AnalysisEvaluator`, schema validation, and partial-result acceptance rules
- [x] REFACTOR: move acceptance policy and warning generation behind stable evaluator interfaces

### Slice 8: Add PDF Ingestion

- [x] RED: add a test proving a PDF upload reaches the same normalized script schema and surfaces extraction warnings when needed
- [x] GREEN: implement upload handling, document extraction using `pymupdf4llm`, and the PDF normalization adapter
- [x] REFACTOR: standardize input adapters so text and PDF paths converge cleanly

### Slice 9: Replace Inline Execution With The Real Async Path

- [x] RED: add a test proving queued execution preserves status transitions and final retrieval semantics
- [x] GREEN: integrate queue-style execution semantics while keeping inline execution available for tests
- [x] REFACTOR: separate orchestration from transport so workers and tests use the same workflow service

### Slice 10: Add Run History Retrieval

- [x] RED: add an API contract test proving `GET /api/v1/scripts/{script_id}/runs` returns ordered history with revision lineage plus revision and status filtering
- [x] GREEN: implement history queries, ordering rules, and lightweight filtering
- [x] REFACTOR: extract a `RunHistoryService`

### Slice 11: Add Revision Compare Retrieval

- [x] RED: add an API contract test proving the compare endpoint returns metric deltas, changed recommendations, changed evidence spans, and revision lineage metadata for two selected runs
- [x] GREEN: implement `RevisionComparisonService`
- [x] REFACTOR: isolate diff generation helpers and delta formatting

### Slice 12: Add The Analysis Workspace UI

- [x] RED: add a frontend test proving a user can paste text, submit analysis, and reach a pending run state
- [x] GREEN: implement the landing page, submission form, and API client
- [x] REFACTOR: extract reusable query and mutation hooks

### Slice 13: Add The Results Dashboard UI

- [x] RED: add a frontend test proving the run page renders the summary, engagement scorecards, emotional arc, recommendations, cliffhanger, and warnings
- [x] GREEN: implement the results dashboard and metric visualization components
- [x] REFACTOR: create reusable scorecard, chart, and evidence panel components

### Slice 14: Add The PDF Upload UI

- [x] RED: add a frontend test proving a user can upload a PDF and see extraction warnings on the results page
- [x] GREEN: implement the upload flow and validation
- [x] REFACTOR: unify text and file submission state management

### Slice 15: Add The Run History Dashboard UI

- [x] RED: add a frontend test proving a user can view run history, filter it, and reopen an earlier run
- [x] GREEN: implement the history page and history list components
- [x] REFACTOR: extract shared table, timeline, or card components as needed

### Slice 16: Add The Revision Compare View UI

- [x] RED: add a frontend test proving a user can compare two runs and see score deltas plus changed recommendations
- [x] GREEN: implement the compare view and delta visualizations
- [x] REFACTOR: extract reusable delta cards and compare helpers

### Slice 17: Add Observability, Regression Fixtures, And Docs

- [x] RED: add smoke tests proving the golden fixture set still produces schema-valid end-to-end results
- [x] GREEN: add structured logging, trace or correlation ids, fixture scripts, and README setup instructions
- [x] REFACTOR: prune dead paths, remove temporary scaffolding, and simplify configuration

## Completed Extensions After Slice 17

- [x] Refactor backend settings to be `.env`-driven with `pydantic-settings` and example configuration
- [x] Deepen the DSPy runtime behind a shared execution template and parse-strategy layer
- [x] Deepen SQLAlchemy persistence behind a shared gateway and codec layer
- [x] Add exact execution fingerprint reuse for completed or partial prior runs
- [x] Add normalized-content fingerprint detection for structurally similar prior runs without auto-reusing evidence offsets
- [x] Add single-flight dedupe for exact queued or running matches while preserving separate run lineage records
- [x] Surface reuse provenance in the submit workspace and run dashboard via `reused_from_run_id` and `normalized_candidate_run_id`
- [x] Persist `agent_runs` and expose them in run detail responses and the dashboard
- [x] Add a critic-style evaluator and surface `critic_assessment` in the API and UI
- [x] Harden partial-result workflow semantics so non-critical agent failures degrade to `partial` instead of failing the full run
- [x] Harden `LLMGateway` lifecycle handling for deterministic test resets and model reconfiguration
- [x] Redesign the frontend with a stronger dashboard visual system, motion polish, empty states, and richer compare deltas
- [x] Align the root `README.md` with `TASK.md`, including approach, model interaction design, limitations, and future improvements

## DSPy-Specific Checklist

- [x] Define DSPy signatures for `summary`, `emotion`, `engagement`, `recommendations`, and `cliffhanger`
- [x] Keep DSPy programs behind an internal registry so the rest of the app does not depend on DSPy directly
- [x] Configure DSPy to use the Groq-backed model interface
- [x] Create deterministic test doubles for DSPy program outputs
- [x] Build a small evaluation fixture set for prompt iteration and regression checks
- [x] Add a critic-style DSPy or non-DSPy evaluator only if it improves measurable output quality

## API Response Contract Checklist

- [x] Stable run identifiers: `run_id`, `script_id`, `revision_id`
- [x] Explicit contract version field such as `result_version`
- [x] `run_id` doubles as the externally visible async job identifier in `v1`
- [x] Explicit run status: `queued`, `running`, `completed`, `partial`, `failed`
- [x] Reuse provenance metadata: `reused_from_run_id` and `normalized_candidate_run_id`
- [x] Summary payload with evidence
- [x] Emotion payload with arc points and dominant emotions
- [x] Engagement payload with overall score, factor scores, rationale, and confidence
- [x] Recommendations payload grouped by category
- [x] Cliffhanger payload with cited evidence
- [x] Warning payload for extraction noise, low confidence, or rejected agent output
- [x] History payload with ordering metadata
- [x] Compare payload with deltas and changed evidence

## Test Inventory Checklist

- [x] Backend contract tests for submit, poll, history, and compare endpoints
- [x] Backend integration tests for text normalization
- [x] Backend integration tests for PDF ingestion
- [x] Backend workflow tests for agent fan-out and aggregation
- [x] Backend evaluator tests for malformed outputs and partial-failure behavior
- [x] Backend persistence tests for revision lineage and run ordering
- [x] Backend persistence tests for normalized script structure and evidence provenance
- [x] Backend reuse tests for exact-result reuse, normalized candidate detection, and single-flight in-flight dedupe
- [x] Frontend tests for submit flow
- [x] Frontend tests for results dashboard rendering
- [x] Frontend tests for history dashboard behavior
- [x] Frontend tests for compare view behavior
- [x] Frontend tests for reuse provenance states in the workspace and run dashboard
- [x] Golden fixture smoke tests for end-to-end schema validity

## Release Readiness Checklist

- [x] `README.md` explains architecture, setup, environment variables, how DSPy and Groq are used, and the assignment-specific sections requested in `TASK.md`
- [x] Demo fixture scripts exist for both text and PDF paths
- [x] The system can run locally without calling live models during tests
- [x] The results dashboard is usable on desktop and mobile
- [x] Run history and revision compare work from persisted data, not only in-memory state
- [x] Duplicate exact submissions are deduplicated safely through execution fingerprints and durable reuse metadata
- [x] Failure states are visible and explainable
- [x] The repo is organized so the next engineer can extend the agent set safely

## Recommended First Slice To Start Next

- [x] Start with `Slice 0: Bootstrap The Test Harness`
  Reason: it gives us the minimum test and app scaffolding needed to execute the rest of the TDD slices cleanly without reworking the setup later.
