from __future__ import annotations

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

