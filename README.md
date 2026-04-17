# Script Insights

Multi-agent script intelligence platform for short-form story analysis.  
The system accepts pasted text or PDF uploads, normalizes input into a canonical script structure, runs specialized analysis agents, and exposes run dashboards, history, and revision comparison.

## Architecture

- `backend/` (`FastAPI`, Python): API contracts, orchestration, normalization, evaluator/guardrails, queue semantics, history + compare services.
- `frontend/` (`Next.js`, TypeScript): analysis workspace, run dashboard, history dashboard, and compare view.
- Agent outputs are structured and versioned (`result_version: "v1"`).
- Workflow stages:
1. Ingest (`text` or `pdf`) and normalize.
2. Run specialist programs (`summary`, `emotion`, `engagement`, `recommendations`, `cliffhanger`).
3. Evaluate outputs and apply partial-result guardrails.
4. Persist run/artifact state and expose API views.

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

Prerequisites:
- Node `20+` (tested with Node `24`)

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

## Testing

Backend:

```bash
cd backend
uv run pytest -q
```

Frontend:

```bash
cd frontend
npm test
```

Current test coverage includes:
- Backend API contracts and workflow slices (submit, normalization, summary, emotion, engagement, recommendations/cliffhanger, guardrails, PDF ingestion, queue semantics, history/compare).
- Backend golden fixture smoke test for schema-valid end-to-end outputs and SQLite persistence tests across app instances.
- Frontend flow tests for submit, dashboard rendering, PDF upload path, history filters, and compare deltas.

## Demo Fixtures

- Text fixture: [demo/fixtures/sample_script.txt](/D:/SWE_DEV_NEW/Script-Insights/demo/fixtures/sample_script.txt)
- PDF fixture: [demo/fixtures/sample_script.pdf](/D:/SWE_DEV_NEW/Script-Insights/demo/fixtures/sample_script.pdf)
- PDF generator: [demo/scripts/generate_sample_pdf.py](/D:/SWE_DEV_NEW/Script-Insights/demo/scripts/generate_sample_pdf.py)

## Known Limitations

- Agent execution metadata is not yet exposed through an API surface.
- DSPy/Groq live model wiring is intentionally not exercised in automated tests.
- Authentication/authorization is not included in v1.
