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

- [ ] Write one failing test for one observable behavior before each implementation slice.
- [ ] Keep each slice vertical: test, minimal implementation, then refactor.
- [ ] Test public interfaces only: API contracts, service boundaries, and user-visible UI behavior.
- [ ] Do not write all tests upfront.
- [ ] Do not call live Groq models from automated tests.
- [ ] Keep model-dependent tests stubbed and deterministic.
- [ ] Make one small commit per completed slice where practical.

## Initial Stack Decisions

- [ ] Backend runtime: `Python 3.11+`
- [ ] Backend web layer: `FastAPI`
- [ ] Backend schemas: `Pydantic v2`
- [ ] Persistence: `SQLAlchemy` + `Alembic`
- [ ] Local DB default: `SQLite`, with schema designed to stay `Postgres`-compatible
- [ ] Async execution: `ARQ` + `Redis`, with an inline runner for tests
- [ ] Model provider SDK: `groq`
- [ ] LLM programming layer: `dspy`
- [ ] Frontend runtime: `Next.js` App Router + `TypeScript`
- [ ] Frontend data fetching: `TanStack Query`
- [ ] Frontend styling: `Tailwind CSS`
- [ ] Frontend visualization: `Recharts` or equivalent charting library

## Public Interfaces To Lock First

### Backend API

- [ ] `POST /api/v1/analysis/runs`
  Purpose: submit pasted text or a PDF upload for analysis
- [ ] `GET /api/v1/analysis/runs/{run_id}`
  Purpose: poll run status and fetch the versioned final result payload using the externally visible async run identifier
- [ ] `GET /api/v1/scripts/{script_id}/runs?revision_id=...&status=...`
  Purpose: list run history for a script across revisions, with optional filters for revision and status
- [ ] `GET /api/v1/scripts/{script_id}/compare?base_run_id=...&target_run_id=...`
  Purpose: compare two selected runs from the same script lineage, typically representing two revisions, and return deltas

### Frontend Routes

- [ ] `/`
  Purpose: paste text or upload PDF and start analysis
- [ ] `/runs/[runId]`
  Purpose: view analysis dashboard for one run
- [ ] `/scripts/[scriptId]/history`
  Purpose: browse run history for a script, filter by revision or status, and reopen prior runs
- [ ] `/scripts/[scriptId]/compare`
  Purpose: compare two selected runs from the same script lineage

## Deep Modules To Build

- [ ] `ScriptNormalizer`
  Input adapters for raw text and extracted PDF text, outputting one canonical script schema
- [ ] `AnalysisWorkflow`
  Orchestrates multi-agent execution, retries, partial failures, and aggregation behind one interface
- [ ] `LLMGateway`
  Provider abstraction for Groq-backed calls and future fallback models
- [ ] `DSPyProgramRegistry`
  Owns DSPy signatures and programs for summary, emotion, engagement, suggestions, and cliffhanger analysis
- [ ] `AnalysisEvaluator`
  Validates schema correctness, evidence grounding, score bounds, and partial-result acceptance
- [ ] `RevisionComparisonService`
  Computes metric deltas, changed recommendations, changed evidence, and revision lineage metadata between two selected runs

## Domain Model Checklist

- [ ] `scripts`
  Stable script identity across revisions
- [ ] `script_revisions`
  Revision lineage, input source type, and normalization metadata
- [ ] `normalized_scripts`
  Canonical scenes, dialogue turns, characters, and source spans persisted per revision for grounding, reruns, and compare flows
- [ ] `source_documents`
  Uploaded files and extraction provenance
- [ ] `analysis_runs`
  Durable async job or run state, timestamps, and versioned result contract exposed to the API
- [ ] `agent_runs`
  Per-agent execution metadata, latency, warnings, and failures
- [ ] `analysis_artifacts`
  Structured outputs from agents and final aggregation payloads
- [ ] `compare_views` or computed compare payloads
  Decide whether compare responses are persisted or generated on demand

## Repo Shape To Create

- [ ] `backend/app/api`
- [ ] `backend/app/core`
- [ ] `backend/app/db`
- [ ] `backend/app/domain`
- [ ] `backend/app/services`
- [ ] `backend/app/agents`
- [ ] `backend/app/evaluation`
- [ ] `backend/tests`
- [ ] `frontend/`
- [ ] `frontend/src/app`
- [ ] `frontend/src/components`
- [ ] `frontend/src/lib`
- [ ] `frontend/tests`

## Execution Order

### Slice 0: Bootstrap The Test Harness

- [x] RED: add a failing backend API test for app startup and health access
- [x] GREEN: create the FastAPI app factory and minimal test runner setup
- [x] REFACTOR: centralize settings and test fixtures

### Slice 1: Submit A Text Script For Analysis

- [ ] RED: add a contract test proving `POST /api/v1/analysis/runs` accepts pasted text and returns `202` with stable identifiers plus an explicit contract version
- [ ] GREEN: implement the minimal submission route, persistence for a new run, and inline execution mode for tests
- [ ] REFACTOR: extract a `RunSubmissionService` behind the route

### Slice 2: Normalize Text Into A Canonical Script Schema

- [ ] RED: add an integration test proving a submitted text script becomes a normalized structure with scenes, dialogue blocks, and warnings
- [ ] GREEN: implement the first `ScriptNormalizer` path for raw text
- [ ] REFACTOR: isolate normalization helpers and source span mapping

### Slice 3: Return A Summary From The First Agent

- [ ] RED: add a test proving a completed run returns a structured summary with evidence spans
- [ ] GREEN: implement the first DSPy summary program, stub LM wiring, and result serialization
- [ ] REFACTOR: extract `LLMGateway` and `DSPyProgramRegistry` boundaries

### Slice 4: Add Emotion Analysis

- [ ] RED: add a test proving the result includes dominant emotions, valence or arousal metadata, and an emotional arc
- [ ] GREEN: implement the DSPy emotion program and response mapping
- [ ] REFACTOR: share evidence and confidence mapping utilities

### Slice 5: Add Engagement Scoring

- [ ] RED: add a test proving the result includes `overall_engagement_score` plus factor scores for hook, conflict, tension, pacing, stakes, and payoff
- [ ] GREEN: implement the rubric-based DSPy engagement program and score normalization
- [ ] REFACTOR: extract a reusable scoring schema and normalization service

### Slice 6: Add Recommendations And Cliffhanger Detection

- [ ] RED: add a test proving the result includes categorized recommendations and a cliffhanger section
- [ ] GREEN: implement the DSPy recommendation and cliffhanger programs
- [ ] REFACTOR: deepen the aggregation layer so agent outputs are composed behind one interface

### Slice 7: Add Guardrails And Partial-Failure Handling

- [ ] RED: add a test proving malformed agent output yields warnings and a partial result instead of a total run failure
- [ ] GREEN: implement `AnalysisEvaluator`, schema validation, and partial-result acceptance rules
- [ ] REFACTOR: move acceptance policy and warning generation behind stable evaluator interfaces

### Slice 8: Add PDF Ingestion

- [ ] RED: add a test proving a PDF upload reaches the same normalized script schema and surfaces extraction warnings when needed
- [ ] GREEN: implement upload handling, document extraction using `pymupdf4llm`, and the PDF normalization adapter
- [ ] REFACTOR: standardize input adapters so text and PDF paths converge cleanly

### Slice 9: Replace Inline Execution With The Real Async Path

- [ ] RED: add a test proving queued execution preserves status transitions and final retrieval semantics
- [ ] GREEN: integrate `ARQ` and `Redis`, while keeping inline execution available for tests
- [ ] REFACTOR: separate orchestration from transport so workers and tests use the same workflow service

### Slice 10: Add Run History Retrieval

- [ ] RED: add an API contract test proving `GET /api/v1/scripts/{script_id}/runs` returns ordered history with revision lineage plus revision and status filtering
- [ ] GREEN: implement history queries, ordering rules, and lightweight filtering
- [ ] REFACTOR: extract a `RunHistoryService`

### Slice 11: Add Revision Compare Retrieval

- [ ] RED: add an API contract test proving the compare endpoint returns metric deltas, changed recommendations, changed evidence spans, and revision lineage metadata for two selected runs
- [ ] GREEN: implement `RevisionComparisonService`
- [ ] REFACTOR: isolate diff generation helpers and delta formatting

### Slice 12: Add The Analysis Workspace UI

- [ ] RED: add a frontend test proving a user can paste text, submit analysis, and reach a pending run state
- [ ] GREEN: implement the landing page, submission form, and API client
- [ ] REFACTOR: extract reusable query and mutation hooks

### Slice 13: Add The Results Dashboard UI

- [ ] RED: add a frontend test proving the run page renders the summary, engagement scorecards, emotional arc, recommendations, cliffhanger, and warnings
- [ ] GREEN: implement the results dashboard and metric visualization components
- [ ] REFACTOR: create reusable scorecard, chart, and evidence panel components

### Slice 14: Add The PDF Upload UI

- [ ] RED: add a frontend test proving a user can upload a PDF and see extraction warnings on the results page
- [ ] GREEN: implement the upload flow and validation
- [ ] REFACTOR: unify text and file submission state management

### Slice 15: Add The Run History Dashboard UI

- [ ] RED: add a frontend test proving a user can view run history, filter it, and reopen an earlier run
- [ ] GREEN: implement the history page and history list components
- [ ] REFACTOR: extract shared table, timeline, or card components as needed

### Slice 16: Add The Revision Compare View UI

- [ ] RED: add a frontend test proving a user can compare two runs and see score deltas plus changed recommendations
- [ ] GREEN: implement the compare view and delta visualizations
- [ ] REFACTOR: extract reusable delta cards and compare helpers

### Slice 17: Add Observability, Regression Fixtures, And Docs

- [ ] RED: add smoke tests proving the golden fixture set still produces schema-valid end-to-end results
- [ ] GREEN: add structured logging, trace or correlation ids, fixture scripts, and README setup instructions
- [ ] REFACTOR: prune dead paths, remove temporary scaffolding, and simplify configuration

## DSPy-Specific Checklist

- [ ] Define DSPy signatures for `summary`, `emotion`, `engagement`, `recommendations`, and `cliffhanger`
- [ ] Keep DSPy programs behind an internal registry so the rest of the app does not depend on DSPy directly
- [ ] Configure DSPy to use the Groq-backed model interface
- [ ] Create deterministic test doubles for DSPy program outputs
- [ ] Build a small evaluation fixture set for prompt iteration and regression checks
- [ ] Add a critic-style DSPy or non-DSPy evaluator only if it improves measurable output quality

## API Response Contract Checklist

- [ ] Stable run identifiers: `run_id`, `script_id`, `revision_id`
- [ ] Explicit contract version field such as `result_version`
- [ ] `run_id` doubles as the externally visible async job identifier in `v1`
- [ ] Explicit run status: `queued`, `running`, `completed`, `partial`, `failed`
- [ ] Summary payload with evidence
- [ ] Emotion payload with arc points and dominant emotions
- [ ] Engagement payload with overall score, factor scores, rationale, and confidence
- [ ] Recommendations payload grouped by category
- [ ] Cliffhanger payload with cited evidence
- [ ] Warning payload for extraction noise, low confidence, or rejected agent output
- [ ] History payload with ordering metadata
- [ ] Compare payload with deltas and changed evidence

## Test Inventory Checklist

- [ ] Backend contract tests for submit, poll, history, and compare endpoints
- [ ] Backend integration tests for text normalization
- [ ] Backend integration tests for PDF ingestion
- [ ] Backend workflow tests for agent fan-out and aggregation
- [ ] Backend evaluator tests for malformed outputs and partial-failure behavior
- [ ] Backend persistence tests for revision lineage and run ordering
- [ ] Backend persistence tests for normalized script structure and evidence provenance
- [ ] Frontend tests for submit flow
- [ ] Frontend tests for results dashboard rendering
- [ ] Frontend tests for history dashboard behavior
- [ ] Frontend tests for compare view behavior
- [ ] Golden fixture smoke tests for end-to-end schema validity

## Release Readiness Checklist

- [ ] `README.md` explains architecture, setup, environment variables, and how DSPy and Groq are used
- [ ] Demo fixture scripts exist for both text and PDF paths
- [ ] The system can run locally without calling live models during tests
- [ ] The results dashboard is usable on desktop and mobile
- [ ] Run history and revision compare work from persisted data, not only in-memory state
- [ ] Failure states are visible and explainable
- [ ] The repo is organized so the next engineer can extend the agent set safely

## Recommended First Slice To Start Next

- [x] Start with `Slice 0: Bootstrap The Test Harness`
  Reason: it gives us the minimum test and app scaffolding needed to execute the rest of the TDD slices cleanly without reworking the setup later.
