from __future__ import annotations

from fastapi.testclient import TestClient

from app.main import create_app


def test_assistant_requests_queue_reviews(monkeypatch, tmp_path) -> None:
    database_path = tmp_path / "cloud-ai-console.sqlite3"
    monkeypatch.setenv("APP_DB_PATH", str(database_path))

    app = create_app()
    with TestClient(app) as client:
        response = client.post(
            "/api/assistant",
            json={
                "prompt": "Plan a supplier intake review flow with Oracle Fusion and AI review.",
                "workflow_id": "supplier-onboarding",
            },
        )
        assert response.status_code == 200

        response_body = response.json()
        assert response_body["review_status"] == "pending"
        assert response_body["review_id"]

        reviews_response = client.get("/api/reviews")
        activity_response = client.get("/api/activity")

    assert reviews_response.status_code == 200
    reviews = reviews_response.json()
    assert len(reviews) == 1
    assert reviews[0]["status"] == "pending"
    assert reviews[0]["workflow_title"] == "Supplier Onboarding Triage"
    assert reviews[0]["response"]["review_status"] == "pending"

    assert activity_response.status_code == 200
    activity_items = activity_response.json()
    assert any(item["kind"] == "review" for item in activity_items)


def test_review_actions_update_status(monkeypatch, tmp_path) -> None:
    database_path = tmp_path / "cloud-ai-console.sqlite3"
    monkeypatch.setenv("APP_DB_PATH", str(database_path))

    app = create_app()
    with TestClient(app) as client:
        assistant_response = client.post(
            "/api/assistant",
            json={
                "prompt": "Plan a supplier intake review flow with Oracle Fusion and AI review.",
                "workflow_id": "supplier-onboarding",
            },
        )
        review_id = assistant_response.json()["review_id"]

        approval_response = client.post(
            f"/api/reviews/{review_id}/approve",
            json={"reviewer": "finance-ops", "note": "Approved for pilot"},
        )
        approved_reviews_response = client.get("/api/reviews?status=approved")
        activity_response = client.get("/api/activity")

    assert approval_response.status_code == 200
    approval_body = approval_response.json()
    assert approval_body["status"] == "approved"
    assert approval_body["reviewer"] == "finance-ops"
    assert approval_body["decision_note"] == "Approved for pilot"
    assert approval_body["reviewed_at"]

    assert approved_reviews_response.status_code == 200
    approved_reviews = approved_reviews_response.json()
    assert len(approved_reviews) == 1
    assert approved_reviews[0]["status"] == "approved"
    assert approved_reviews[0]["response"]["review_status"] == "approved"

    assert activity_response.status_code == 200
    activity_items = activity_response.json()
    assert any(item["kind"] == "review" and "approved" in item["title"].lower() for item in activity_items)
