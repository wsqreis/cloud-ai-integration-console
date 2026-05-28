from __future__ import annotations

from fastapi.testclient import TestClient

import app.main as main_module
import app.openai_service as openai_service
from app.errors import AppError
from app.main import create_app


def test_validation_errors_use_standard_shape(monkeypatch, tmp_path) -> None:
    database_path = tmp_path / "cloud-ai-console.sqlite3"
    monkeypatch.setenv("APP_DB_PATH", str(database_path))

    app = create_app()
    with TestClient(app) as client:
        response = client.post("/api/assistant", json={"prompt": "short"})

    assert response.status_code == 422
    payload = response.json()
    assert payload["error"]["code"] == "validation_error"
    assert payload["error"]["message"] == "Request validation failed."
    assert payload["error"]["details"]
    assert payload["error"]["request_id"]
    assert response.headers["x-request-id"]


def test_application_errors_use_standard_shape(monkeypatch, tmp_path) -> None:
    database_path = tmp_path / "cloud-ai-console.sqlite3"
    monkeypatch.setenv("APP_DB_PATH", str(database_path))

    def raise_app_error(*args, **kwargs) -> None:
        raise AppError(
            code="integration_unavailable",
            message="Integration temporarily unavailable.",
            status_code=503,
            details={"system": "Oracle Fusion"},
        )

    monkeypatch.setattr(main_module, "evaluate_prompt", raise_app_error)

    app = create_app()
    with TestClient(app) as client:
        response = client.post(
            "/api/prompts/evaluate",
            json={
                "prompt": "Goal: reduce manual review. Use Oracle Fusion and return JSON with risks.",
            },
        )

    assert response.status_code == 503
    payload = response.json()
    assert payload["error"]["code"] == "integration_unavailable"
    assert payload["error"]["details"] == {"system": "Oracle Fusion"}
    assert payload["error"]["request_id"]


def test_openai_requests_retry_transient_failures(monkeypatch) -> None:
    monkeypatch.setattr(openai_service, "OPENAI_REQUEST_MAX_ATTEMPTS", 3)
    monkeypatch.setattr(openai_service, "OPENAI_REQUEST_TIMEOUT_SECONDS", 0.01)
    monkeypatch.setattr(openai_service.time, "sleep", lambda seconds: None)

    class FakeResponses:
        def __init__(self) -> None:
            self.calls = 0

        def create(self, **kwargs):
            self.calls += 1
            if self.calls < 3:
                raise TimeoutError("timeout")
            return type("Response", (), {"output_text": '{"answer": "ok"}'})()

    fake_responses = FakeResponses()
    fake_client = type("Client", (), {"responses": fake_responses})()
    monkeypatch.setattr(openai_service, "_get_client", lambda: fake_client)

    result = openai_service._responses_json("instructions", "user input")

    assert result == {"answer": "ok"}
    assert fake_responses.calls == 3
