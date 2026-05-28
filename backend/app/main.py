from __future__ import annotations

import os
import time

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.data import INTEGRATIONS, WORKFLOWS
from app.models import (
    AssistantRequest,
    AssistantResponse,
    ActivityRecord,
    AutomationFlow,
    DocumentAnalysis,
    DocumentRequest,
    Integration,
    Overview,
    PromptEvaluation,
    PromptEvaluationRequest,
)
from app.observability import (
    initialize_observability_state,
    observability_middleware_factory,
    setup_logging,
)
from app.services import analyze_document, evaluate_prompt, get_overview, plan_assistant_reply
from app.storage import initialize_storage, list_activity


def create_app() -> FastAPI:
    app = FastAPI(
        title="Cloud AI Integration Console API",
        version="0.1.0",
        description="REST API for cloud integration, AI workflow planning, and document triage.",
    )

    setup_logging()
    allowed_origins = [
        origin.strip()
        for origin in os.getenv("ALLOWED_ORIGINS", "http://localhost:5173").split(",")
        if origin.strip()
    ]
    app.add_middleware(
        CORSMiddleware,
        allow_origins=allowed_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    initialize_observability_state(app)
    request_logger = observability_middleware_factory(app)

    @app.middleware("http")
    async def log_requests(request, call_next):
        return await request_logger(request, call_next)

    @app.on_event("startup")
    def startup() -> None:
        initialize_storage()

    @app.get("/api/health")
    def health() -> dict[str, str]:
        return {"status": "ok", "environment": os.getenv("API_ENV", "development")}

    @app.get("/api/metrics")
    def metrics() -> dict[str, float | int]:
        started_at = app.state.metrics["started_at"]
        return {
            "requests_total": app.state.metrics["requests_total"],
            "requests_failed": app.state.metrics["requests_failed"],
            "uptime_seconds": round(time.time() - started_at, 2),
        }

    @app.get("/api/overview", response_model=Overview)
    def overview() -> Overview:
        return get_overview()

    @app.get("/api/integrations", response_model=list[Integration])
    def integrations() -> list[Integration]:
        return INTEGRATIONS

    @app.get("/api/workflows", response_model=list[AutomationFlow])
    def workflows() -> list[AutomationFlow]:
        return WORKFLOWS

    @app.get("/api/activity", response_model=list[ActivityRecord])
    def activity(limit: int = 20) -> list[ActivityRecord]:
        return list_activity(limit=limit)

    @app.post("/api/assistant", response_model=AssistantResponse)
    def assistant(request: AssistantRequest) -> AssistantResponse:
        return plan_assistant_reply(request.prompt, request.workflow_id)

    @app.post("/api/documents/analyze", response_model=DocumentAnalysis)
    def document_analysis(request: DocumentRequest) -> DocumentAnalysis:
        return analyze_document(request.title, request.content)

    @app.post("/api/prompts/evaluate", response_model=PromptEvaluation)
    def prompt_evaluation(request: PromptEvaluationRequest) -> PromptEvaluation:
        return evaluate_prompt(request.prompt)

    return app


app = create_app()
