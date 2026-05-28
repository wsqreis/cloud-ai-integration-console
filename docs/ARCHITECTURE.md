# Architecture

The console is split into a React client and a Python API.

The current MVP focus is supplier onboarding triage from supplier intake notes into Oracle Fusion Cloud.

## Frontend

- React and TypeScript power the operational dashboard.
- Vite provides local development and production bundling.
- The UI calls the API through a small typed client and falls back to seeded data if the API is unavailable.
- The interface includes connector health, workflow review, prompt evaluation, and document triage.

## Backend

- FastAPI exposes REST endpoints for integrations, workflows, AI planning, prompt scoring, and document analysis.
- A catalog adapter loads the active integrations and workflow seed from JSON when available, with a static fallback for local development.
- Service logic uses the OpenAI SDK when credentials are present and falls back to deterministic behavior otherwise.
- External AI calls are wrapped with bounded retries and timeouts, while API errors are normalized into a consistent JSON shape.
- Lightweight observability adds request IDs, duration headers, request counters, and a metrics endpoint.
- The AI-style responses model practical LLM concerns: assumptions, confidence, structured outputs, and review checkpoints.

## Integration Model

The prototype models common enterprise integration patterns:

- REST orchestration between cloud applications and supporting services.
- Health and latency monitoring for connector readiness.
- AI-assisted summarization and workflow planning.
- Human review checkpoints before automated changes are promoted.

## Extension Points

- Replace deterministic services with hosted model calls.
- Swap the default model and prompts as customer needs evolve.
- Add OAuth-backed connector adapters.
- Persist workflow state in a relational database.
- Add audit logs for prompt inputs, generated outputs, and reviewer decisions.
