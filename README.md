# Script Insights

Multi-agent script intelligence platform for short-form story analysis.  
The system accepts pasted text or PDF uploads, normalizes input into a canonical script structure, runs specialized analysis agents, and exposes run dashboards, history, and revision comparison.

## What This Builds

- Next.js frontend for text/PDF submission, run dashboards, run history, and revision compare.
- FastAPI backend for ingestion, orchestration, retrieval, and worker control.
- Agentic analysis workflow for `summary`, `emotion`, `engagement`, `recommendations`, and `cliffhanger`.
- Durable SQLite persistence through SQLAlchemy repositories and codecs.
- Optional DSPy plus Groq live inference, with deterministic heuristic fallback always available.

## Architecture

- `backend/` (`FastAPI`, Python): API contracts, orchestration, normalization, evaluator/guardrails, queue semantics, history + compare services.
- `frontend/` (`Next.js`, TypeScript): analysis workspace, run dashboard, history dashboard, and compare view.
- Agent outputs are structured and versioned (`result_version: "v1"`).
- Workflow stages:
1. Ingest (`text` or `pdf`) and normalize.
2. Run specialist programs (`summary`, `emotion`, `engagement`, `recommendations`, `cliffhanger`).
3. Evaluate outputs and apply partial-result guardrails.
4. Persist run/artifact state and expose API views.

Architecture diagram:
- [docs/architecture/script-insights-agentic-system.html](docs/architecture/script-insights-agentic-system.html)

## Local Prerequisites

- Python `3.11+`
- `uv`
- Node `20+` (`24` also works)
- npm

## Run Locally

### 1. Start the backend

```bash
cd backend
uv sync
uv run uvicorn app.main:app --reload
```

Backend base URL:
- `http://localhost:8000`
- API root: `http://localhost:8000/api/v1`

### 2. Start the frontend

Open a second terminal:

```bash
cd frontend
npm install
npm run dev
```

Frontend URL:
- `http://localhost:3000`

### 3. Open the app

- Navigate to `http://localhost:3000`
- Paste script text or upload a PDF
- Review results at the run dashboard
- Use history and compare views from the dashboard links

## Local Execution Modes

### Inline mode

This is the default local mode. Submission runs are processed immediately inside the API process.

```bash
cd backend
uv run uvicorn app.main:app --reload
```

### Queued mode

Queued mode persists submitted runs and processes them through the worker runtime.

Backend terminal:

```bash
cd backend
$env:EXECUTION_MODE="queued"
uv run uvicorn app.main:app --reload
```

Worker terminal:

```bash
cd backend
$env:EXECUTION_MODE="queued"
uv run python -m app.workers.cli --poll-interval 1.0
```

One-shot worker drain:

```bash
cd backend
$env:EXECUTION_MODE="queued"
uv run python -m app.workers.cli --once
```

For bash or zsh, use:

```bash
cd backend
EXECUTION_MODE=queued uv run python -m app.workers.cli --poll-interval 1.0
```

## DSPy and Groq

- DSPy is integrated via `backend/app/agents/dspy_programs.py` and `backend/app/agents/registry.py`.
- Current v1 behavior is deterministic-first: heuristic fallbacks are always available and are used when DSPy LM configuration is absent or fails.
- Groq is the intended external provider for DSPy LM configuration in non-test environments.
- Tests never call live LLMs; they validate contracts and behavior with deterministic outputs.

## Backend Setup

Prerequisites:
- Python `3.11+`
- `uv` package manager

Commands:

```bash
cd backend
uv sync
uv run uvicorn app.main:app --reload
```

API base URL: `http://localhost:8000/api/v1`

Backend environment variables:
- `EXECUTION_MODE` = `inline` or `queued` (default `inline`)
- `DATABASE_URL` (optional; default `sqlite:///./script_insights.db`)
- `CORS_ORIGINS` (optional; comma-separated, default `http://localhost:3000`)
- `GROQ_API_KEY` (optional; enables DSPy LM config through Groq)
- `GROQ_MODEL` (optional; default `groq/llama-3.3-70b-versatile`)

Key endpoints:
- `POST /analysis/runs` (paste text)
- `POST /analysis/runs/upload` (PDF upload)
- `GET /analysis/runs/{run_id}`
- `GET /scripts/{script_id}/runs`
- `GET /scripts/{script_id}/compare`
- `POST /analysis/workers/drain` (process queued runs in queued mode)

Observability:
- Structured JSON request logs with correlation IDs.
- Incoming `x-request-id` is propagated; when missing, the backend generates one and returns it in response headers.

Worker process:

```bash
cd backend
EXECUTION_MODE=queued uv run python -m app.workers.cli --once
```

Use `--poll-interval 1.0` without `--once` to run a long-lived local worker loop.

## Frontend Setup

Commands:

```bash
cd frontend
npm install
npm run dev
```

Frontend default URL: `http://localhost:3000`

Environment variable:
- `NEXT_PUBLIC_API_BASE_URL` (optional, default `http://localhost:8000`)

Routes:
- `/` analysis workspace (paste/upload + submission state)
- `/runs/[runId]` run results dashboard
- `/scripts/[scriptId]/history` run history dashboard
- `/scripts/[scriptId]/compare` revision compare view

The home page accepts `?script_id=<uuid>` so the UI can submit a new revision into an existing script lineage.

## Build And Test Locally

### Backend tests

```bash
cd backend
uv run pytest -q
```

### Frontend tests

```bash
cd frontend
npm test
```

### Frontend production build

```bash
cd frontend
npm run build
```

### Full local validation

Run the commands below before considering a local change complete:

```bash
cd backend
uv run pytest -q
```

```bash
cd frontend
npm test
npm run build
```

Notes:
- The backend is a Python service, so there is no separate compiled build artifact step beyond dependency install and runtime/test validation.
- The frontend build validates the Next.js production bundle and TypeScript integration.

## Testing Scope

Current automated coverage includes:
- Backend API contracts and workflow slices (submit, normalization, summary, emotion, engagement, recommendations/cliffhanger, guardrails, PDF ingestion, queue semantics, history/compare).
- Backend golden fixture smoke test for schema-valid end-to-end outputs and SQLite persistence tests across app instances.
- Frontend flow tests for submit, dashboard rendering, PDF upload path, history filters, and compare deltas.

## Demo Fixtures

- Text fixture: [demo/fixtures/sample_script.txt](demo/fixtures/sample_script.txt)
- PDF fixture: [demo/fixtures/sample_script.pdf](demo/fixtures/sample_script.pdf)
- PDF generator: [demo/scripts/generate_sample_pdf.py](demo/scripts/generate_sample_pdf.py)

## Known Limitations

- Agent execution metadata is not yet exposed through an API surface.
- DSPy/Groq live model wiring is intentionally not exercised in automated tests.
- Authentication/authorization is not included in v1.
