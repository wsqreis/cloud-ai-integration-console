from __future__ import annotations

import json
import os
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Iterator, Literal

from app.models import ActivityRecord, AssistantResponse, PromptVersionRecord, ReviewRecord


ActivityKind = Literal["assistant", "document", "prompt", "review"]
PromptVersionKind = Literal["assistant", "document", "prompt"]


def get_database_path() -> Path:
    return Path(os.getenv("APP_DB_PATH", "./data/cloud-ai-console.sqlite3"))


def initialize_storage() -> None:
    database_path = get_database_path()
    database_path.parent.mkdir(parents=True, exist_ok=True)

    with connect() as connection:
        connection.execute("PRAGMA journal_mode=WAL;")
        connection.execute("PRAGMA foreign_keys=ON;")
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS activity_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                kind TEXT NOT NULL,
                title TEXT NOT NULL,
                summary TEXT NOT NULL,
                workflow_id TEXT,
                input_json TEXT NOT NULL,
                output_json TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT (datetime('now'))
            )
            """
        )
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS review_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                workflow_id TEXT,
                workflow_title TEXT NOT NULL,
                prompt TEXT NOT NULL,
                response_json TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'pending',
                reviewer TEXT,
                decision_note TEXT,
                created_at TEXT NOT NULL DEFAULT (datetime('now')),
                reviewed_at TEXT
            )
            """
        )
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS prompt_versions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                kind TEXT NOT NULL,
                title TEXT NOT NULL,
                workflow_id TEXT,
                version INTEGER NOT NULL,
                prompt_text TEXT NOT NULL,
                response_summary TEXT NOT NULL,
                response_json TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT (datetime('now'))
            )
            """
        )


@contextmanager
def connect() -> Iterator[sqlite3.Connection]:
    database_path = get_database_path()
    database_path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(database_path)
    connection.row_factory = sqlite3.Row
    try:
        yield connection
        connection.commit()
    finally:
        connection.close()


def record_activity(
    kind: ActivityKind,
    title: str,
    summary: str,
    input_payload: dict[str, Any],
    output_payload: dict[str, Any],
    workflow_id: str | None = None,
) -> None:
    initialize_storage()
    with connect() as connection:
        connection.execute(
            """
            INSERT INTO activity_records (kind, title, summary, workflow_id, input_json, output_json)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                kind,
                title,
                summary,
                workflow_id,
                json.dumps(input_payload, ensure_ascii=False),
                json.dumps(output_payload, ensure_ascii=False),
            ),
        )


def list_activity(
    limit: int = 20,
    kind: ActivityKind | None = None,
) -> list[ActivityRecord]:
    initialize_storage()
    with connect() as connection:
        if kind is None:
            rows = connection.execute(
                """
                SELECT id, kind, title, summary, workflow_id, created_at
                FROM activity_records
                ORDER BY id DESC
                LIMIT ?
                """,
                (limit,),
            ).fetchall()
        else:
            rows = connection.execute(
                """
                SELECT id, kind, title, summary, workflow_id, created_at
                FROM activity_records
                WHERE kind = ?
                ORDER BY id DESC
                LIMIT ?
                """,
                (kind, limit),
            ).fetchall()

    return [ActivityRecord.model_validate(dict(row)) for row in rows]


def record_review(
    workflow_id: str | None,
    workflow_title: str,
    prompt: str,
    response_payload: dict[str, Any],
) -> ReviewRecord:
    initialize_storage()
    with connect() as connection:
        cursor = connection.execute(
            """
            INSERT INTO review_records (workflow_id, workflow_title, prompt, response_json)
            VALUES (?, ?, ?, ?)
            """,
            (
                workflow_id,
                workflow_title,
                prompt,
                json.dumps(response_payload, ensure_ascii=False),
            ),
        )
        row = connection.execute(
            """
            SELECT id, workflow_id, workflow_title, prompt, response_json, status,
                   reviewer, decision_note, created_at, reviewed_at
            FROM review_records
            WHERE id = ?
            """,
            (cursor.lastrowid,),
        ).fetchone()

    return _row_to_review_record(row)


def list_reviews(status: str | None = None) -> list[ReviewRecord]:
    initialize_storage()
    with connect() as connection:
        if status is None:
            rows = connection.execute(
                """
                SELECT id, workflow_id, workflow_title, prompt, response_json, status,
                       reviewer, decision_note, created_at, reviewed_at
                FROM review_records
                ORDER BY id DESC
                """
            ).fetchall()
        else:
            rows = connection.execute(
                """
                SELECT id, workflow_id, workflow_title, prompt, response_json, status,
                       reviewer, decision_note, created_at, reviewed_at
                FROM review_records
                WHERE status = ?
                ORDER BY id DESC
                """,
                (status,),
            ).fetchall()

    return [_row_to_review_record(row) for row in rows]


def update_review(
    review_id: int,
    status: str,
    reviewer: str,
    decision_note: str | None = None,
) -> ReviewRecord | None:
    initialize_storage()
    with connect() as connection:
        connection.execute(
            """
            UPDATE review_records
            SET status = ?, reviewer = ?, decision_note = ?, reviewed_at = datetime('now')
            WHERE id = ?
            """,
            (status, reviewer, decision_note, review_id),
        )
        row = connection.execute(
            """
            SELECT id, workflow_id, workflow_title, prompt, response_json, status,
                   reviewer, decision_note, created_at, reviewed_at
            FROM review_records
            WHERE id = ?
            """,
            (review_id,),
        ).fetchone()

    if row is None:
        return None
    return _row_to_review_record(row)


def _row_to_review_record(row: sqlite3.Row) -> ReviewRecord:
    response_payload = json.loads(row["response_json"])
    response = AssistantResponse.model_validate(response_payload).model_copy(
        update={"review_id": row["id"], "review_status": row["status"]}
    )
    return ReviewRecord.model_validate(
        {
            "id": row["id"],
            "workflow_id": row["workflow_id"],
            "workflow_title": row["workflow_title"],
            "prompt": row["prompt"],
            "status": row["status"],
            "reviewer": row["reviewer"],
            "decision_note": row["decision_note"],
            "response": response.model_dump(),
            "created_at": row["created_at"],
            "reviewed_at": row["reviewed_at"],
        }
    )


def record_prompt_version(
    kind: PromptVersionKind,
    title: str,
    prompt: str,
    response_summary: str,
    response_payload: dict[str, Any],
    workflow_id: str | None = None,
) -> PromptVersionRecord:
    initialize_storage()
    with connect() as connection:
        if workflow_id is None:
            version_row = connection.execute(
                """
                SELECT COALESCE(MAX(version), 0) + 1 AS next_version
                FROM prompt_versions
                WHERE kind = ? AND title = ? AND workflow_id IS NULL
                """,
                (kind, title),
            ).fetchone()
        else:
            version_row = connection.execute(
                """
                SELECT COALESCE(MAX(version), 0) + 1 AS next_version
                FROM prompt_versions
                WHERE kind = ? AND title = ? AND workflow_id = ?
                """,
                (kind, title, workflow_id),
            ).fetchone()

        version = int(version_row["next_version"]) if version_row is not None else 1
        cursor = connection.execute(
            """
            INSERT INTO prompt_versions (kind, title, workflow_id, version, prompt_text, response_summary, response_json)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                kind,
                title,
                workflow_id,
                version,
                prompt,
                response_summary,
                json.dumps(response_payload, ensure_ascii=False),
            ),
        )
        row = connection.execute(
            """
            SELECT id, kind, title, workflow_id, version, prompt_text, response_summary,
                   response_json, created_at
            FROM prompt_versions
            WHERE id = ?
            """,
            (cursor.lastrowid,),
        ).fetchone()

    return _row_to_prompt_version_record(row)


def list_prompt_versions(
    limit: int = 20,
    kind: PromptVersionKind | None = None,
    workflow_id: str | None = None,
) -> list[PromptVersionRecord]:
    initialize_storage()
    with connect() as connection:
        query = """
            SELECT id, kind, title, workflow_id, version, prompt_text, response_summary,
                   response_json, created_at
            FROM prompt_versions
        """
        parameters: list[Any] = []
        clauses: list[str] = []
        if kind is not None:
            clauses.append("kind = ?")
            parameters.append(kind)
        if workflow_id is not None:
            clauses.append("workflow_id = ?")
            parameters.append(workflow_id)
        if clauses:
            query += " WHERE " + " AND ".join(clauses)
        query += " ORDER BY id DESC LIMIT ?"
        parameters.append(limit)
        rows = connection.execute(query, parameters).fetchall()

    return [_row_to_prompt_version_record(row) for row in rows]


def _row_to_prompt_version_record(row: sqlite3.Row) -> PromptVersionRecord:
    response_payload = json.loads(row["response_json"])
    return PromptVersionRecord.model_validate(
        {
            "id": row["id"],
            "kind": row["kind"],
            "title": row["title"],
            "workflow_id": row["workflow_id"],
            "version": row["version"],
            "prompt": row["prompt_text"],
            "response_summary": row["response_summary"],
            "response_payload": response_payload,
            "created_at": row["created_at"],
        }
    )
