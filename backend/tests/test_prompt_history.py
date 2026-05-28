from __future__ import annotations

from fastapi.testclient import TestClient

from app.main import create_app


def test_prompt_history_tracks_versions_and_kinds(monkeypatch, tmp_path) -> None:
    database_path = tmp_path / "cloud-ai-console.sqlite3"
    monkeypatch.setenv("APP_DB_PATH", str(database_path))

    app = create_app()
    with TestClient(app) as client:
        first_assistant = client.post(
            "/api/assistant",
            json={
                "prompt": "Plan a supplier intake review flow with Oracle Fusion and AI review.",
                "workflow_id": "supplier-onboarding",
            },
        )
        second_assistant = client.post(
            "/api/assistant",
            json={
                "prompt": "Plan a supplier intake review flow with Oracle Fusion and AI review.",
                "workflow_id": "supplier-onboarding",
            },
        )
        prompt_evaluation = client.post(
            "/api/prompts/evaluate",
            json={
                "prompt": "Goal: reduce manual review. Use Oracle Fusion and return JSON with risks.",
            },
        )
        prompt_history = client.get("/api/prompt-history")
        assistant_history = client.get(
            "/api/prompt-history",
            params={"kind": "assistant", "workflow_id": "supplier-onboarding"},
        )

    assert first_assistant.status_code == 200
    assert second_assistant.status_code == 200
    assert prompt_evaluation.status_code == 200

    assert prompt_history.status_code == 200
    prompt_items = prompt_history.json()
    assert len(prompt_items) == 3
    assert {item["kind"] for item in prompt_items} == {"assistant", "prompt"}

    assert assistant_history.status_code == 200
    assistant_items = assistant_history.json()
    assert len(assistant_items) == 2
    assert [item["version"] for item in assistant_items] == [2, 1]
    assert assistant_items[0]["response_summary"]
    assert assistant_items[0]["response_payload"]["review_status"] == "pending"
