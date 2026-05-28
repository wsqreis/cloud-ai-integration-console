# Cloud AI Integration Console

A full-stack integration workspace for prototyping AI-assisted cloud workflows, REST service orchestration, document analysis, and responsive operational dashboards.

The application combines a React interface with a Python API to model the kinds of tools used by innovation teams when validating new integration ideas before customer delivery.
The current MVP focus is supplier onboarding triage from intake notes into Oracle Fusion.

## Capabilities

- Monitor enterprise application connectors and API health.
- Draft prompts for AI-assisted workflow planning.
- Analyze operational notes and documents for actions, risks, and entities.
- Inspect prototype automation flows before implementation.
- Run the stack locally with Docker or with the frontend and backend development servers.

## Tech Stack

- React, TypeScript, and Vite for the responsive client.
- Python and FastAPI for the REST API.
- OpenAI SDK support for live AI responses, with deterministic fallback when no key is set.
- Docker Compose for running the full stack.

## Requirements

- Python 3.11 or newer.
- Node.js 20 or newer.
- Docker, when running the full stack with Compose.

Optional:

- `OPENAI_API_KEY` for live model calls.
- `OPENAI_MODEL` to override the default model (`gpt-5.5`).

## Run With Docker

```bash
docker compose up --build
```

Open `http://localhost:8080`.

The backend persists activity to `backend/data/cloud-ai-console.sqlite3` by default.

## Run The CLI

Backend CLI:

```bash
cd backend
python -m app.cli overview
python -m app.cli prompt --prompt "Goal: reduce manual review. Use Oracle Fusion and return JSON."
python -m app.cli assistant --workflow-id supplier-onboarding --prompt "Plan a supplier intake review flow."
```

If `OPENAI_API_KEY` is set, the CLI uses the OpenAI SDK; otherwise it falls back to the local deterministic services.

## Run For Development

Backend:

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
uvicorn app.main:app --reload
```

Frontend:

```bash
cd frontend
npm install
npm run dev
```

Open `http://localhost:5173`.

## Test

```bash
cd backend
pytest
```

```bash
cd frontend
npm run build
```

## Documentation

- [Architecture](docs/ARCHITECTURE.md)
- [API Reference](docs/API.md)
- [Roadmap](docs/ROADMAP.md)
- [Primary Use Case](docs/USE_CASE.md)
- [MVP Scope](docs/MVP_SCOPE.md)
