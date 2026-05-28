from __future__ import annotations

import os
import time

import logging

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.errors import AppError
from app.models import (
    AssistantRequest,
    AssistantResponse,
    ActivityRecord,
    AuditTrailRecord,
    AutomationFlow,
    DocumentAnalysis,
    DocumentRequest,
    Integration,
    Overview,
    PromptEvaluation,
    PromptEvaluationRequest,
    PromptVersionRecord,
    PublishActionRequest,
    ReviewActionRequest,
    ReviewRecord,
)
from app.catalog import get_catalog_adapter
from app.observability import (
    initialize_observability_state,
    observability_middleware_factory,
    setup_logging,
)
from app.services import analyze_document, evaluate_prompt, get_overview, plan_assistant_reply
from app.storage import (
    initialize_storage,
    list_activity,
    list_audit_events,
    list_prompt_versions,
    list_reviews,
    record_audit_event,
    record_activity,
    publish_review,
    update_review,
)


logger = logging.getLogger(__name__)


def create_app() -> FastAPI:
    catalog = get_catalog_adapter()
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

    @app.exception_handler(AppError)
    async def app_error_handler(request: Request, exc: AppError) -> JSONResponse:
        request_id = getattr(request.state, "request_id", None)
        return JSONResponse(
            status_code=exc.status_code,
            content=exc.to_response(request_id=request_id),
        )

    @app.exception_handler(RequestValidationError)
    async def validation_error_handler(
        request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        request_id = getattr(request.state, "request_id", None)
        return JSONResponse(
            status_code=422,
            content={
                "error": {
                    "code": "validation_error",
                    "message": "Request validation failed.",
                    "details": exc.errors(),
                    "request_id": request_id,
                }
            },
        )

    @app.exception_handler(Exception)
    async def generic_error_handler(request: Request, exc: Exception) -> JSONResponse:
        request_id = getattr(request.state, "request_id", None)
        logger.exception(
            "unhandled_application_error",
            extra={"request_id": request_id, "error_type": exc.__class__.__name__},
        )
        return JSONResponse(
            status_code=500,
            content={
                "error": {
                    "code": "internal_server_error",
                    "message": "An unexpected error occurred.",
                    "request_id": request_id,
                }
            },
        )

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
        return get_overview(catalog)

    @app.get("/api/integrations", response_model=list[Integration])
    def integrations() -> list[Integration]:
        return catalog.get_integrations()

    @app.get("/api/workflows", response_model=list[AutomationFlow])
    def workflows() -> list[AutomationFlow]:
        return catalog.get_workflows()

    @app.get("/api/activity", response_model=list[ActivityRecord])
    def activity(limit: int = 20) -> list[ActivityRecord]:
        return list_activity(limit=limit)

    @app.get("/api/audit-trail", response_model=list[AuditTrailRecord])
    def audit_trail(limit: int = 20) -> list[AuditTrailRecord]:
        return list_audit_events(limit=limit)

    @app.get("/api/prompt-history", response_model=list[PromptVersionRecord])
    def prompt_history(
        kind: str | None = None,
        workflow_id: str | None = None,
        limit: int = 20,
    ) -> list[PromptVersionRecord]:
        if kind is not None and kind not in {"assistant", "document", "prompt"}:
            raise AppError(
                code="invalid_prompt_history_kind",
                message="Prompt history kind must be assistant, document, or prompt.",
                status_code=400,
                details={"kind": kind},
            )
        return list_prompt_versions(limit=limit, kind=kind, workflow_id=workflow_id)

    @app.get("/api/reviews", response_model=list[ReviewRecord])
    def reviews(status: str | None = None) -> list[ReviewRecord]:
        if status is not None and status not in {"pending", "approved", "rejected", "published"}:
            raise AppError(
                code="invalid_review_status",
                message="Review status must be pending, approved, rejected, or published.",
                status_code=400,
                details={"status": status},
            )
        return list_reviews(status=status)

    @app.post("/api/reviews/{review_id}/approve", response_model=ReviewRecord)
    def approve_review(review_id: int, request: ReviewActionRequest) -> ReviewRecord:
        review = update_review(
            review_id=review_id,
            status="approved",
            reviewer=request.reviewer,
            decision_note=request.note,
        )
        if review is None:
            raise AppError(
                code="review_not_found",
                message="Review item not found.",
                status_code=404,
                details={"review_id": review_id},
            )
        record_activity(
            kind="review",
            title=f"Review approved: {review.workflow_title}",
            summary=f"Approved by {request.reviewer}.",
            input_payload={"review_id": review_id, "reviewer": request.reviewer, "note": request.note},
            output_payload=review.model_dump(),
            workflow_id=review.workflow_id,
        )
        record_audit_event(
            actor=request.reviewer,
            action="review_approved",
            subject_type="review",
            subject_id=str(review_id),
            summary=f"Approved {review.workflow_title}.",
            details={"review_id": review_id, "workflow_id": review.workflow_id, "note": request.note},
        )
        return review

    @app.post("/api/reviews/{review_id}/reject", response_model=ReviewRecord)
    def reject_review(review_id: int, request: ReviewActionRequest) -> ReviewRecord:
        review = update_review(
            review_id=review_id,
            status="rejected",
            reviewer=request.reviewer,
            decision_note=request.note,
        )
        if review is None:
            raise AppError(
                code="review_not_found",
                message="Review item not found.",
                status_code=404,
                details={"review_id": review_id},
            )
        record_activity(
            kind="review",
            title=f"Review rejected: {review.workflow_title}",
            summary=f"Rejected by {request.reviewer}.",
            input_payload={"review_id": review_id, "reviewer": request.reviewer, "note": request.note},
            output_payload=review.model_dump(),
            workflow_id=review.workflow_id,
        )
        record_audit_event(
            actor=request.reviewer,
            action="review_rejected",
            subject_type="review",
            subject_id=str(review_id),
            summary=f"Rejected {review.workflow_title}.",
            details={"review_id": review_id, "workflow_id": review.workflow_id, "note": request.note},
        )
        return review

    @app.post("/api/reviews/{review_id}/publish", response_model=ReviewRecord)
    def publish_review_route(review_id: int, request: PublishActionRequest) -> ReviewRecord:
        existing_review = next((item for item in list_reviews() if item.id == review_id), None)
        if existing_review is None:
            raise AppError(
                code="review_not_found",
                message="Review item not found.",
                status_code=404,
                details={"review_id": review_id},
            )
        if existing_review.status != "approved":
            raise AppError(
                code="review_not_publishable",
                message="Only approved review items can be published.",
                status_code=409,
                details={"review_id": review_id, "status": existing_review.status},
            )

        review = publish_review(
            review_id=review_id,
            publisher=request.publisher,
            publish_note=request.note,
        )
        if review is None:
            raise AppError(
                code="review_not_found",
                message="Review item not found.",
                status_code=404,
                details={"review_id": review_id},
            )
        record_activity(
            kind="audit",
            title=f"Review published: {review.workflow_title}",
            summary=f"Published by {request.publisher}.",
            input_payload={"review_id": review_id, "publisher": request.publisher, "note": request.note},
            output_payload=review.model_dump(),
            workflow_id=review.workflow_id,
        )
        record_audit_event(
            actor=request.publisher,
            action="review_published",
            subject_type="review",
            subject_id=str(review_id),
            summary=f"Published {review.workflow_title}.",
            details={"review_id": review_id, "workflow_id": review.workflow_id, "note": request.note},
        )
        return review

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
