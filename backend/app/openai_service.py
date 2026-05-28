from __future__ import annotations

import json
import logging
import os
import re
import time
from typing import Any

logger = logging.getLogger(__name__)


def _get_float_env(name: str, default: float) -> float:
    raw_value = os.getenv(name, str(default)).strip()
    try:
        return float(raw_value)
    except ValueError:
        return default


def _get_int_env(name: str, default: int) -> int:
    raw_value = os.getenv(name, str(default)).strip()
    try:
        return int(raw_value)
    except ValueError:
        return default


OPENAI_REQUEST_TIMEOUT_SECONDS = _get_float_env("OPENAI_REQUEST_TIMEOUT_SECONDS", 20.0)
OPENAI_REQUEST_MAX_ATTEMPTS = max(1, _get_int_env("OPENAI_REQUEST_MAX_ATTEMPTS", 3))
OPENAI_RETRY_BACKOFF_SECONDS = _get_float_env("OPENAI_RETRY_BACKOFF_SECONDS", 0.5)


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

    return OpenAI(api_key=api_key, timeout=OPENAI_REQUEST_TIMEOUT_SECONDS, max_retries=0)


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


def _is_retryable_exception(exc: Exception) -> bool:
    error_name = exc.__class__.__name__.lower()
    error_text = f"{error_name} {exc}".lower()
    return any(
        token in error_text
        for token in (
            "timeout",
            "connection",
            "temporarily",
            "rate limit",
            "server error",
            "service unavailable",
        )
    )


def _run_with_retries(client: Any, instructions: str, user_input: str) -> dict[str, Any] | None:
    last_exception: Exception | None = None

    for attempt in range(1, OPENAI_REQUEST_MAX_ATTEMPTS + 1):
        try:
            response = client.responses.create(
                model=get_openai_model(),
                instructions=instructions,
                input=user_input,
                timeout=OPENAI_REQUEST_TIMEOUT_SECONDS,
            )
            output_text = getattr(response, "output_text", "") or ""
            parsed = _load_json(output_text)
            if parsed is None:
                logger.warning(
                    "openai_response_invalid_json",
                    extra={"attempt": attempt, "max_attempts": OPENAI_REQUEST_MAX_ATTEMPTS},
                )
            return parsed
        except Exception as exc:  # pragma: no cover - provider-specific exception shape
            last_exception = exc
            retryable = _is_retryable_exception(exc)
            if not retryable or attempt >= OPENAI_REQUEST_MAX_ATTEMPTS:
                logger.warning(
                    "openai_request_failed",
                    extra={
                        "attempt": attempt,
                        "max_attempts": OPENAI_REQUEST_MAX_ATTEMPTS,
                        "retryable": retryable,
                        "error_type": exc.__class__.__name__,
                    },
                )
                return None

            sleep_seconds = OPENAI_RETRY_BACKOFF_SECONDS * (2 ** (attempt - 1))
            logger.info(
                "openai_request_retrying",
                extra={
                    "attempt": attempt,
                    "max_attempts": OPENAI_REQUEST_MAX_ATTEMPTS,
                    "sleep_seconds": sleep_seconds,
                    "error_type": exc.__class__.__name__,
                },
            )
            time.sleep(sleep_seconds)

    if last_exception is not None:
        logger.warning(
            "openai_request_exhausted",
            extra={"error_type": last_exception.__class__.__name__},
        )
    return None


def _responses_json(instructions: str, user_input: str) -> dict[str, Any] | None:
    client = _get_client()
    if client is None:
        return None

    return _run_with_retries(client, instructions, user_input)


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
