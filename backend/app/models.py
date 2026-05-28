from __future__ import annotations

from typing import Any
from typing import Literal

from pydantic import BaseModel, Field


class Integration(BaseModel):
    id: str
    name: str
    category: str
    status: Literal["healthy", "degraded", "planned"]
    latency_ms: int
    last_sync: str
    description: str
    capabilities: list[str]


class WorkflowStep(BaseModel):
    title: str
    owner: str
    status: Literal["ready", "review", "blocked", "planned"]


class AutomationFlow(BaseModel):
    id: str
    title: str
    summary: str
    business_value: str
    systems: list[str]
    steps: list[WorkflowStep]


class OverviewMetric(BaseModel):
    label: str
    value: str
    trend: str


class Overview(BaseModel):
    metrics: list[OverviewMetric]
    capability_map: dict[str, list[str]]
    recommended_next_actions: list[str]


class AssistantRequest(BaseModel):
    prompt: str = Field(min_length=8, max_length=2000)
    workflow_id: str | None = None


class AssistantResponse(BaseModel):
    answer: str
    assumptions: list[str]
    suggested_steps: list[str]
    quality_checks: list[str]
    confidence: Literal["low", "medium", "high"]
    review_id: int | None = None
    review_status: Literal["pending", "approved", "rejected", "published"] = "pending"


class DocumentRequest(BaseModel):
    title: str = Field(min_length=2, max_length=120)
    content: str = Field(min_length=20, max_length=6000)


class DocumentAnalysis(BaseModel):
    summary: str
    detected_systems: list[str]
    action_items: list[str]
    risks: list[str]
    automation_opportunities: list[str]


class PromptEvaluationRequest(BaseModel):
    prompt: str = Field(min_length=8, max_length=2000)


class PromptEvaluation(BaseModel):
    score: int = Field(ge=0, le=100)
    strengths: list[str]
    gaps: list[str]
    improved_prompt: str


class PromptVersionRecord(BaseModel):
    id: int
    kind: Literal["assistant", "document", "prompt"]
    title: str
    workflow_id: str | None = None
    version: int
    prompt: str
    response_summary: str
    response_payload: dict[str, Any]
    created_at: str


class AuditTrailRecord(BaseModel):
    id: int
    actor: str
    action: str
    subject_type: str
    subject_id: str
    summary: str
    details: dict[str, Any]
    created_at: str


class ReviewActionRequest(BaseModel):
    reviewer: str = Field(default="local-operator", min_length=2, max_length=80)
    note: str | None = Field(default=None, max_length=500)


class PublishActionRequest(BaseModel):
    publisher: str = Field(default="local-operator", min_length=2, max_length=80)
    note: str | None = Field(default=None, max_length=500)


class ReviewRecord(BaseModel):
    id: int
    workflow_id: str | None = None
    workflow_title: str
    prompt: str
    status: Literal["pending", "approved", "rejected", "published"]
    reviewer: str | None = None
    decision_note: str | None = None
    published_by: str | None = None
    published_note: str | None = None
    published_at: str | None = None
    response: AssistantResponse
    created_at: str
    reviewed_at: str | None = None


class ActivityRecord(BaseModel):
    id: int
    kind: Literal["assistant", "document", "prompt", "review", "audit"]
    title: str
    summary: str
    workflow_id: str | None = None
    created_at: str
