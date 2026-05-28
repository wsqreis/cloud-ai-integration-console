from __future__ import annotations

import json
import logging
import time
import uuid
from collections.abc import Callable

from fastapi import Request, Response


logger = logging.getLogger("cloud_ai_console")


def setup_logging() -> None:
    logging.basicConfig(level=logging.INFO, format="%(message)s")


def initialize_observability_state(app) -> None:
    app.state.metrics = {
        "requests_total": 0,
        "requests_failed": 0,
        "started_at": time.time(),
    }


def observability_middleware_factory(app):
    async def middleware(request: Request, call_next: Callable[[Request], Response]) -> Response:
        request_id = request.headers.get("x-request-id") or str(uuid.uuid4())
        started_at = time.perf_counter()
        app.state.metrics["requests_total"] += 1

        try:
            response = await call_next(request)
        except Exception:
            app.state.metrics["requests_failed"] += 1
            logger.exception(
                json.dumps(
                    {
                        "event": "request_failed",
                        "request_id": request_id,
                        "method": request.method,
                        "path": request.url.path,
                    }
                )
            )
            raise

        duration_ms = round((time.perf_counter() - started_at) * 1000, 2)
        if response.status_code >= 500:
            app.state.metrics["requests_failed"] += 1

        response.headers["X-Request-ID"] = request_id
        response.headers["X-Response-Time-ms"] = str(duration_ms)
        logger.info(
            json.dumps(
                {
                    "event": "request_completed",
                    "request_id": request_id,
                    "method": request.method,
                    "path": request.url.path,
                    "status_code": response.status_code,
                    "duration_ms": duration_ms,
                }
            )
        )
        return response

    return middleware

