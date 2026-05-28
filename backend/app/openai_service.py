from __future__ import annotations

import json
import os
import re
from typing import Any


def get_openai_model() -> str:
    model = os.getenv("OPENAI_MODEL", "gpt-5.5").strip()
    return model or "gpt-5.5"


def _get_client() -> Any | None:
    api_key = os.getenv("OPENAI_API_KEY", "").strip()
    if not api_key:
        return None

    try:
        from openai import OpenAI
    except ImportError:
        return None

    return OpenAI(api_key=api_key)


def _strip_code_fences(text: str) -> str:
    stripped = text.strip()
    if stripped.startswith("```"):
        stripped = re.sub(r"^```(?:json)?\s*", "", stripped, flags=re.IGNORECASE)
        stripped = re.sub(r"\s*```$", "", stripped)
    return stripped.strip()


def _load_json(text: str) -> dict[str, Any] | None:
    try:
        parsed = json.loads(_strip_code_fences(text))
    except json.JSONDecodeError:
        return None

    return parsed if isinstance(parsed, dict) else None


def _responses_json(instructions: str, user_input: str) -> dict[str, Any] | None:
    client = _get_client()
    if client is None:
        return None

    try:
        response = client.responses.create(
            model=get_openai_model(),
            instructions=instructions,
            input=user_input,
        )
    except Exception:
        return None

    output_text = getattr(response, "output_text", "") or ""
    return _load_json(output_text)


def generate_assistant_payload(prompt: str, workflow_title: str) -> dict[str, Any] | None:
    return _responses_json(
        instructions=(
            "You are helping design an enterprise integration workflow. "
            "Return only valid JSON with the keys answer, assumptions, suggested_steps, "
            "quality_checks, and confidence. Confidence must be one of low, medium, or high."
        ),
        user_input=(
            f"Workflow title: {workflow_title}\n"
            f"User prompt: {prompt}\n"
            "Keep the answer concise, actionable, and suitable for a delivery review."
        ),
    )


def generate_document_analysis_payload(title: str, content: str) -> dict[str, Any] | None:
    return _responses_json(
        instructions=(
            "You analyze implementation notes for enterprise automation. "
            "Return only valid JSON with the keys summary, detected_systems, action_items, "
            "risks, and automation_opportunities."
        ),
        user_input=(
            f"Title: {title}\n"
            f"Content: {content}\n"
            "Extract the most useful review summary and keep the output concise."
        ),
    )


def generate_prompt_evaluation_payload(prompt: str) -> dict[str, Any] | None:
    return _responses_json(
        instructions=(
            "You review prompts for enterprise integration workflows. "
            "Return only valid JSON with the keys score, strengths, gaps, and improved_prompt. "
            "Score must be an integer from 0 to 100."
        ),
        user_input=f"Prompt: {prompt}",
    )
