# API Reference

Base URL: `http://localhost:8000`

When `OPENAI_API_KEY` is set, the assistant, prompt evaluation, and document analysis endpoints can use the OpenAI SDK. Without it, they fall back to deterministic local logic.

OpenAI calls use bounded timeouts and a small retry loop controlled by `OPENAI_REQUEST_TIMEOUT_SECONDS`, `OPENAI_REQUEST_MAX_ATTEMPTS`, and `OPENAI_RETRY_BACKOFF_SECONDS`.

Errors return a consistent JSON shape:

```json
{
  "error": {
    "code": "validation_error",
    "message": "Request validation failed.",
    "details": []
  }
}
```

## Health

`GET /api/health`

Returns service status and active environment.

## Metrics

`GET /api/metrics`

Returns basic request counters and uptime for lightweight observability.

## Overview

`GET /api/overview`

Returns summary metrics, delivery capabilities, and recommended next actions.

## Integrations

`GET /api/integrations`

Returns connector metadata, status, latency, sync recency, and capabilities.

## Workflows

`GET /api/workflows`

Returns prototype automation flows with business value, systems, and delivery steps.

## Assistant

`POST /api/assistant`

Request:

```json
{
  "prompt": "Plan a supplier onboarding automation flow with REST APIs and AI review.",
  "workflow_id": "supplier-onboarding"
}
```

Response includes an answer, assumptions, suggested steps, quality checks, and confidence.

## Document Analysis

`POST /api/documents/analyze`

Request:

```json
{
  "title": "Supplier intake notes",
  "content": "Finance needs to validate missing tax fields before the ERP update."
}
```

Response includes a summary, detected systems, action items, risks, and automation opportunities.

## Prompt Evaluation

`POST /api/prompts/evaluate`

Request:

```json
{
  "prompt": "Goal: reduce manual review. Use Oracle Fusion and REST APIs. Return JSON with risks."
}
```

Response includes a score, strengths, gaps, and an improved prompt.
