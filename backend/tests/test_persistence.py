from __future__ import annotations

import sqlite3

from fastapi.testclient import TestClient

from app.main import create_app
from app.services import evaluate_prompt


def test_service_calls_are_persisted(monkeypatch, tmp_path) -> None:
    database_path = tmp_path / "cloud-ai-console.sqlite3"
    monkeypatch.setenv("APP_DB_PATH", str(database_path))

    result = evaluate_prompt("Goal: reduce manual review. Use Oracle Fusion and return JSON.")

    with sqlite3.connect(database_path) as connection:
        row = connection.execute(
            "SELECT kind, title, summary, output_json FROM activity_records ORDER BY id DESC LIMIT 1"
        ).fetchone()

    assert row[0] == "prompt"
    assert row[1] == "Prompt evaluation"
    assert row[2] == f"Score {result.score}/100"
    assert "improved_prompt" in row[3]


def test_activity_endpoint_returns_recent_records(monkeypatch, tmp_path) -> None:
    database_path = tmp_path / "cloud-ai-console.sqlite3"
    monkeypatch.setenv("APP_DB_PATH", str(database_path))

    app = create_app()
    with TestClient(app) as client:
        response = client.post(
            "/api/assistant",
            json={
                "prompt": "Plan a supplier intake review flow with Oracle Fusion.",
                "workflow_id": "supplier-onboarding",
            },
        )
        assert response.status_code == 200

        activity_response = client.get("/api/activity")

    assert activity_response.status_code == 200
    activity_items = activity_response.json()
    assert activity_items
    assert activity_items[0]["kind"] == "assistant"
    assert activity_items[0]["title"] == "Supplier Onboarding Triage"
