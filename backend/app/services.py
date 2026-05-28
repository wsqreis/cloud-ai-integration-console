from __future__ import annotations

import re

from app.data import CAPABILITY_MAP, INTEGRATIONS, METRICS, WORKFLOWS
from app.models import (
    AssistantResponse,
    DocumentAnalysis,
    Overview,
    PromptEvaluation,
)
from app.openai_service import (
    generate_assistant_payload,
    generate_document_analysis_payload,
    generate_prompt_evaluation_payload,
)


SYSTEM_KEYWORDS = {
    "Oracle Fusion": ["fusion", "procurement", "supplier", "finance"],
    "JD Edwards": ["jde", "jd edwards", "erp", "inventory", "order"],
    "OCI Generative AI": ["oci", "generative", "llm", "prompt", "summary"],
    "Oracle Digital Assistant": ["assistant", "chatbot", "intent", "conversation"],
    "REST API": ["rest", "api", "webhook", "endpoint"],
    "SQL": ["sql", "database", "table", "query"],
}

RISK_TERMS = {
    "missing": "Missing information may block automation.",
    "manual": "Manual handling is a candidate for workflow automation.",
    "delay": "Delay signals should be surfaced in the dashboard.",
    "failed": "Failure states need retry and escalation behavior.",
    "approval": "Approval rules should be explicit before integration.",
    "security": "Security requirements should be reviewed before rollout.",
}


def get_overview() -> Overview:
    return Overview(
        metrics=METRICS,
        capability_map=CAPABILITY_MAP,
        recommended_next_actions=[
            "Validate degraded connector retry behavior.",
            "Review AI-generated actions before publishing workflow changes.",
            "Add customer-specific mappings after the prototype is approved.",
        ],
    )


def find_workflow_title(workflow_id: str | None) -> str:
    if not workflow_id:
        return "a new integration prototype"
    workflow = next((item for item in WORKFLOWS if item.id == workflow_id), None)
    return workflow.title if workflow else "a new integration prototype"


def plan_assistant_reply(prompt: str, workflow_id: str | None = None) -> AssistantResponse:
    normalized = prompt.strip()
    workflow_title = find_workflow_title(workflow_id)
    detected = detect_systems(normalized)
    confidence = "high" if len(normalized) > 120 and detected else "medium" if detected else "low"

    suggested_steps = [
        "Define the source event, target system, and success criteria.",
        "Map required fields and identify missing data handling.",
        "Prototype the REST request and mock error responses.",
        "Use AI output only after a human review checkpoint.",
        "Document setup, rollback, and support ownership.",
    ]

    if "document" in normalized.lower() or "notes" in normalized.lower():
        suggested_steps.insert(2, "Add document extraction with structured output validation.")

    openai_payload = generate_assistant_payload(normalized, workflow_title)
    if openai_payload is not None:
        try:
            return AssistantResponse.model_validate(openai_payload)
        except Exception:
            pass

    return AssistantResponse(
        answer=(
            f"For {workflow_title}, start with a narrow proof of concept that proves the data "
            "path, the AI review step, and the operational handoff before expanding scope."
        ),
        assumptions=[
            "The prototype should run without direct access to production systems.",
            "AI-generated recommendations require review before customer-facing use.",
            "Connector behavior should be observable through API health and logs.",
        ],
        suggested_steps=suggested_steps,
        quality_checks=[
            "Does the prompt name the business outcome?",
            "Are source and target systems explicit?",
            "Is there a fallback when the AI response is incomplete?",
            "Can the result be explained to a non-developer stakeholder?",
        ],
        confidence=confidence,
    )


def analyze_document(title: str, content: str) -> DocumentAnalysis:
    detected_systems = detect_systems(f"{title} {content}")
    action_items = extract_action_items(content)
    risks = extract_risks(content)
    opportunities = extract_automation_opportunities(content)

    openai_payload = generate_document_analysis_payload(title, content)
    if openai_payload is not None:
        try:
            return DocumentAnalysis.model_validate(openai_payload)
        except Exception:
            pass

    return DocumentAnalysis(
        summary=build_summary(title, content, detected_systems),
        detected_systems=detected_systems,
        action_items=action_items,
        risks=risks,
        automation_opportunities=opportunities,
    )


def detect_systems(text: str) -> list[str]:
    lowered = text.lower()
    matches = [
        system
        for system, keywords in SYSTEM_KEYWORDS.items()
        if any(keyword in lowered for keyword in keywords)
    ]
    return matches or ["General integration"]


def extract_action_items(content: str) -> list[str]:
    sentences = split_sentences(content)
    candidates = [
        sentence
        for sentence in sentences
        if re.search(r"\b(need|needs|should|must|follow up|validate|confirm|create)\b", sentence, re.I)
    ]
    return candidates[:5] or ["Confirm required fields and owner before implementation."]


def extract_risks(content: str) -> list[str]:
    lowered = content.lower()
    risks = [message for term, message in RISK_TERMS.items() if term in lowered]
    return risks or ["No major risk terms detected; review assumptions with a consultant."]


def extract_automation_opportunities(content: str) -> list[str]:
    lowered = content.lower()
    opportunities = []
    if any(term in lowered for term in ["manual", "spreadsheet", "email"]):
        opportunities.append("Replace manual handoffs with an API-triggered workflow.")
    if any(term in lowered for term in ["missing", "validate", "field"]):
        opportunities.append("Use structured extraction to detect missing or inconsistent fields.")
    if any(term in lowered for term in ["approval", "review", "exception"]):
        opportunities.append("Route exceptions to a review queue with evidence summaries.")
    if any(term in lowered for term in ["guide", "documentation", "knowledge"]):
        opportunities.append("Generate draft setup guidance from implementation notes.")
    return opportunities or ["Create a small connector health check before expanding automation."]


def evaluate_prompt(prompt: str) -> PromptEvaluation:
    lowered = prompt.lower()
    score = 35
    strengths = []
    gaps = []

    if any(term in lowered for term in ["goal", "outcome", "business"]):
        score += 15
        strengths.append("States a business goal.")
    else:
        gaps.append("Add the business outcome the AI should optimize for.")

    if any(term in lowered for term in ["system", "api", "fusion", "jde", "database", "oci"]):
        score += 15
        strengths.append("Names the technical context.")
    else:
        gaps.append("Name the source and target systems.")

    if any(term in lowered for term in ["format", "json", "table", "bullets", "schema"]):
        score += 15
        strengths.append("Specifies the output format.")
    else:
        gaps.append("Specify the expected response format.")

    if any(term in lowered for term in ["risk", "validate", "assumption", "confidence"]):
        score += 10
        strengths.append("Asks for review criteria.")
    else:
        gaps.append("Ask the AI to flag risks, assumptions, or confidence.")

    if len(prompt.split()) >= 35:
        score += 10
        strengths.append("Provides enough context for a useful response.")
    else:
        gaps.append("Add more context about constraints, users, and data quality.")

    improved_prompt = (
        "Given the business outcome, source system, target system, constraints, and sample data, "
        "produce a structured recommendation with assumptions, risks, validation steps, and a "
        "clear next action list."
    )

    openai_payload = generate_prompt_evaluation_payload(prompt)
    if openai_payload is not None:
        try:
            return PromptEvaluation.model_validate(openai_payload)
        except Exception:
            pass

    return PromptEvaluation(
        score=min(score, 100),
        strengths=strengths or ["The prompt is a workable starting point."],
        gaps=gaps,
        improved_prompt=improved_prompt,
    )


def build_summary(title: str, content: str, detected_systems: list[str]) -> str:
    words = re.findall(r"\w+", content)
    system_text = ", ".join(detected_systems[:3])
    return (
        f"{title} references {system_text} and contains {len(words)} words. "
        "The note is ready for triage into actions, risks, and automation candidates."
    )


def split_sentences(content: str) -> list[str]:
    sentences = re.split(r"(?<=[.!?])\s+", content.strip())
    return [sentence.strip() for sentence in sentences if sentence.strip()]
