# Multi-Agent Script Intelligence Platform

## Problem Statement

Creators and internal story reviewers need a fast, reliable way to evaluate short scripted content without depending on fully manual review. The current assignment asks for script summary, emotional analysis, engagement scoring, and improvement suggestions, but a stronger product direction is to build this as a reusable multi-agent analysis platform rather than a one-off prompt wrapper.

The platform must accept either pasted script text or uploaded PDFs, extract and normalize the source into a canonical script representation, run specialized analysis agents, and return structured insights that are grounded in the source material. The system should feel trustworthy: outputs must be explainable, schema-stable, and resilient to model variation or partial failures.

## Solution

Build a web-based script intelligence platform with a Next.js frontend and a FastAPI backend. The frontend provides a polished analysis workspace for paste-text and PDF upload flows, analysis run tracking, rich result exploration, a script-scoped run history dashboard, and a revision compare experience. The backend provides asynchronous job processing, a canonical script normalization layer, and a multi-agent orchestration engine that coordinates specialized LLM workers.

The multi-agent backend will run a staged workflow:

1. Ingestion and normalization convert pasted text or PDF content into a canonical script schema.
2. A structuring agent extracts scenes, characters, dialogue turns, and source spans.
3. Specialized analysis agents run in parallel for summary, emotional tone and arc, engagement scoring, improvement suggestions, and cliffhanger detection.
4. A critic and guardrail stage validates schema correctness, evidence grounding, and score consistency.
5. An aggregation stage assembles the final response for the API and frontend.

Groq will be the initial model provider behind a provider abstraction, and DSPy will be used selectively for structured LLM programs, rubric-driven prompting, and evaluation or optimization of agent prompts. DSPy will not own job orchestration or system state; those remain explicit backend concerns.

## User Stories

1. As a creator, I want to paste a short script directly into the product, so that I can analyze drafts quickly without file preparation.
2. As a creator, I want to upload a PDF version of a script, so that I can analyze scripts that already exist in review-ready form.
3. As a creator, I want the system to normalize either input path into the same analysis experience, so that output quality is consistent regardless of format.
4. As a creator, I want to see whether the script was parsed successfully and where extraction may be noisy, so that I can judge whether the analysis is trustworthy.
5. As a creator, I want a concise three-to-four-line summary of the story, so that I can quickly verify the system understood the material.
6. As a creator, I want the dominant emotions called out clearly, so that I can understand the primary affective tone of the script.
7. As a creator, I want the emotional arc to show how feeling changes through the scene, so that I can assess whether the story lands with the intended progression.
8. As a creator, I want an overall engagement score with named contributing factors, so that I can understand why the script may or may not hold audience attention.
9. As a creator, I want the engagement score broken into interpretable dimensions such as hook, tension, conflict, pacing, and payoff, so that I can revise with precision.
10. As a creator, I want several concrete improvement suggestions focused on storytelling craft, so that I can improve pacing, dialogue, conflict, and emotional impact.
11. As a creator, I want the system to identify the most suspenseful or cliffhanger moment when one exists, so that I can understand where the script creates curiosity or unresolved tension.
12. As a creator, I want each major claim to reference supporting source spans, so that the analysis feels grounded rather than invented.
13. As a creator, I want to rerun analysis after revising the script, so that I can compare whether changes improved the storytelling.
14. As a creator, I want to see the history of prior analysis runs for a script, so that I can track how the script evolved over time.
15. As a creator, I want to compare two revisions side by side by selecting the analysis run that represents each revision, so that I can see which changes improved or hurt engagement and emotional impact.
16. As a creator, I want the compare view to highlight metric deltas and changed recommendations between two selected runs in the same script lineage, so that I can revise with confidence instead of rereading every section manually.
17. As a reviewer, I want to submit scripts and retrieve results through a stable API, so that the platform can integrate into internal tooling and review workflows.
18. As a reviewer, I want to see job status and progress, so that I know whether a long-running multi-agent analysis is still healthy.
19. As a reviewer, I want partial results or actionable failure messages when one agent fails, so that a single subtask failure does not collapse the whole workflow.
20. As a reviewer, I want confidence signals and extraction warnings surfaced in the response, so that I can decide when human judgment should override model output.
21. As a product engineer, I want each analysis capability implemented as a pluggable agent module, so that new story-analysis skills can be added without rewriting the system.
22. As a product engineer, I want orchestration to support parallel agent execution, retries, and fallback policies, so that the system remains reliable under model or network instability.
23. As a product engineer, I want the model provider to be abstracted behind a gateway, so that Groq can be used now without hard-coding the platform to one vendor forever.
24. As a prompt engineer, I want DSPy-compatible signatures and evaluation datasets, so that prompts and structured programs can be tuned systematically instead of by guesswork.
25. As a QA engineer, I want schema-stable outputs from all agents, so that regressions are detectable even when models change.
26. As a QA engineer, I want deterministic test fixtures for text and PDF inputs, so that normalization and orchestration behavior can be validated repeatedly.
27. As a platform engineer, I want analysis runs, agent runs, revision lineage, and artifacts persisted separately, so that failures can be debugged, compared, and retried without losing provenance.
28. As a platform engineer, I want guardrails to reject malformed or weakly grounded agent outputs, so that low-quality intermediate steps do not contaminate the final result.
29. As a platform engineer, I want observability for latency, token usage, retries, and failure modes, so that the system can be tuned for cost and reliability.
30. As a frontend user, I want a polished results view instead of a raw JSON dump, so that the system feels like a product rather than a demo script.
31. As a frontend user, I want a run history dashboard that lets me reopen earlier runs for a script and filter by revision, status, or recency, so that I can navigate my work without losing context.
32. As a frontend user, I want the upload, history, compare, and results experience to work well on desktop and mobile, so that the product is usable in a realistic review workflow.
33. As a project evaluator, I want the codebase to be cleanly modular with explicit boundaries, so that the implementation demonstrates sound engineering judgment.
34. As a future team member, I want the initial build to establish reusable deep modules for ingestion, orchestration, evaluation, and revision analysis, so that the platform can grow into broader content intelligence workflows.

## Implementation Decisions

- The product will be implemented as a two-application system: a FastAPI backend for APIs, orchestration, and job execution, and a Next.js frontend for the user-facing application.
- The backend will be designed as a multi-agent platform from day one, not as a single prompt wrapped in an endpoint.
- The canonical domain model will include script-level metadata, normalized script structures such as scenes, dialogue turns, extractable narrative beats, characters, and source spans, analysis runs, agent runs, and final analysis artifacts.
- The canonical domain model will also include revision lineage so multiple versions of the same script can be linked, browsed historically, and compared.
- Input support in v1 will include pasted text and PDF upload. Both paths must converge into the same normalization pipeline and canonical script schema.
- PDF ingestion will use a document extraction layer that preserves text provenance and surfaces extraction warnings, with `pymupdf4llm` as the likely initial extraction utility.
- Normalized script structures and extraction provenance will be persisted as first-class records, not only embedded inside final analysis artifacts, so reruns, evidence grounding, and compare flows can reuse them reliably.
- The orchestration layer will execute a directed workflow with explicit dependencies: ingestion, structuring, parallel specialist analysis, critic or guardrail validation, and final aggregation.
- The initial specialist agent set will include summary, emotion analysis, engagement scoring, improvement suggestion generation, and cliffhanger detection.
- A critic or evaluator stage will validate schema compliance, required evidence links, score ranges, and internal consistency before outputs are accepted into the final response.
- Each agent must return structured JSON with typed fields, bounded enumerations where appropriate, evidence references, and confidence or warning metadata.
- The engagement analysis will be rubric-based rather than a single opaque score. The overall score will be derived from named factors such as hook strength, conflict, pacing, tension, and payoff.
- The emotional analysis will produce both dominant emotions and an arc over the scene or story progression, not just a flat sentiment label.
- Improvement suggestions will be category-aware and actionable, with focus areas including pacing, conflict, dialogue, emotional impact, and clarity.
- The system will preserve partial execution semantics. If a non-critical agent fails, the workflow should still return a bounded response with explicit missing sections and warnings.
- In v1, `analysis_run` will be the externally visible asynchronous job identity. The system will not split user-visible jobs and runs into separate concepts until there is a clear operational need.
- FastAPI will expose asynchronous job-oriented APIs rather than only synchronous request-response endpoints, so that multi-agent execution remains scalable and inspectable.
- The core API contract will include job submission, job status retrieval, and final result retrieval. The response model must be stable and versioned, with an explicit contract version field in payloads.
- The core API contract in v1 will also include script-scoped run history retrieval and compare retrieval between two selected runs from the same script lineage, typically representing two revisions, so the frontend dashboard does not depend on ad hoc client-side stitching.
- The frontend will use Next.js rather than a minimal React scaffold because routing, loading states, result pages, and future extensibility are first-class concerns.
- The frontend experience in v1 will include an analysis workspace with paste and upload entry points, progress tracking, extraction warnings, sectioned result views for summary, emotion, engagement, recommendations, and cliffhanger, a script-scoped run history dashboard with revision and status filters, and a revision compare view built from two selected runs with metric deltas and changed evidence.
- Groq will be the initial model provider, but all model calls will route through a provider abstraction so future vendors or fallback models can be added safely.
- DSPy will be used selectively for structured agent programs, prompt signatures, few-shot or rubric optimization, and evaluation workflows. DSPy will not replace the backend job system, persistence layer, or API contracts.
- Persistence will separate transient execution state from durable artifacts. A relational store should hold analysis runs, agent runs, normalized structures, extraction provenance, and final outputs, while a queue or cache layer should handle asynchronous execution and retry coordination.
- Persistence must support script identity, revision lineage, run chronology, and compare-friendly retrieval so history and delta views can be rendered efficiently.
- Uploaded source files should be stored with traceable references so analysis provenance can be maintained across reruns and debugging workflows.
- Observability is part of the initial design. The platform should record job timings, per-agent latency, retry counts, model identifiers, and cost-relevant usage metrics.
- Reliability controls should include timeouts, retry policies, fallback models or fallback prompt variants where appropriate, idempotent job handling, and strict validation at module boundaries.
- The backend should expose a deep orchestration module with a small interface, so the complexity of multi-agent coordination is encapsulated behind a stable contract.
- The evaluation and guardrail module should also be treated as a deep module with its own interfaces for validation, scoring normalization, and response acceptance.

## Testing Decisions

- Good tests will verify externally visible behavior, contracts, and failure semantics rather than internal prompt wording or implementation details.
- Good tests will rely on deterministic fixtures, stubbed model responses, and stable schemas so failures indicate a real regression in system behavior.
- The highest-priority automated tests will cover ingestion and normalization, workflow orchestration, evaluation and guardrails, and API contracts.
- Ingestion and normalization tests should validate that pasted text and representative PDF fixtures produce the expected canonical script schema, preserve source provenance, and surface extraction warnings when content is ambiguous.
- Workflow orchestration tests should validate dependency ordering, parallel execution fan-out, retry behavior, partial-failure behavior, and idempotent reruns from the user-facing contract.
- Evaluation and guardrail tests should validate schema enforcement, rejection of malformed agent outputs, score-bound enforcement, evidence-link validation, and aggregation behavior when one agent produces unusable output.
- API contract tests should validate job submission, status polling, final result retrieval, and structured error payloads across success, partial success, and failure cases.
- API contract tests should also validate run history listing and revision compare responses, including stable ordering, lineage metadata, and delta payload structure.
- Agent-module tests may exist, but they should focus on contract compliance and mapping behavior around stubbed LLM responses rather than brittle assertions on the exact language of generated prose.
- A small golden evaluation set of scripts should be maintained for smoke validation of the full pipeline, but the assertions should target rubric ranges and structural correctness rather than exact text match.
- There is effectively no meaningful prior test art in the current codebase today. The test suite created for this project should establish the baseline patterns for fixtures, model stubs, contract tests, and orchestration tests.
- The recommended test stack is `pytest` for backend behavior, HTTP contract testing for the FastAPI surface, and frontend tests focused on the upload, job status, run history, revision compare, and results-display flows.

## Out of Scope

- DOCX, Final Draft, Fountain, or other advanced screenplay format support beyond pasted text and PDF in the initial build
- Real-time collaborative editing or multi-user annotation workflows
- Enterprise-grade authentication, authorization, tenancy, and role management
- Human-in-the-loop review queues or moderation operations tooling
- Batch portfolio analysis across large script catalogs
- Model fine-tuning, reinforcement learning, or custom pretraining
- Full experiment management for prompt or model research beyond the minimum needed to support DSPy-based evaluation
- Native mobile applications
- Localization and deep multilingual analysis beyond English-first support
- Production deployment hardening for massive traffic before the core platform behavior is proven

## Further Notes

- The current repository is effectively greenfield, with only a skeletal backend and no established frontend or test architecture. This PRD assumes the repo will be shaped around the platform described here.
- The assignment itself can be satisfied with a much simpler implementation, but this PRD intentionally frames the work as a reusable content-intelligence platform because that is the direction requested.
- The most important engineering risk is not raw model capability; it is reliability of structured outputs across multiple agent stages. The architecture therefore prioritizes canonical schemas, evidence grounding, orchestration transparency, and strict validation.
- The most important product risk is overbuilding infrastructure without proving output quality. The implementation should therefore ship early with a narrow but real agent set and a curated evaluation fixture set that can be used to improve quality over time.
