from __future__ import annotations

from fastapi.testclient import TestClient

from app.main import create_app


def test_audit_trail_records_request_approval_and_publish(monkeypatch, tmp_path) -> None:
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
        publish_response = client.post(
            f"/api/reviews/{review_id}/publish",
            json={"publisher": "finance-ops", "note": "Published to downstream ops"},
        )
        audit_response = client.get("/api/audit-trail")
        published_reviews_response = client.get("/api/reviews?status=published")

    assert approval_response.status_code == 200
    assert publish_response.status_code == 200

    assert audit_response.status_code == 200
    audit_entries = audit_response.json()
    actions = [entry["action"] for entry in audit_entries]
    assert "review_published" in actions
    assert "review_approved" in actions
    assert "assistant_requested" in actions

    assert published_reviews_response.status_code == 200
    published_reviews = published_reviews_response.json()
    assert len(published_reviews) == 1
    published_review = published_reviews[0]
    assert published_review["status"] == "published"
    assert published_review["published_by"] == "finance-ops"
    assert published_review["published_note"] == "Published to downstream ops"
    assert published_review["response"]["review_status"] == "published"
