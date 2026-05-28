from __future__ import annotations

import json
import os
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Iterator, Literal

from app.models import ActivityRecord


ActivityKind = Literal["assistant", "document", "prompt"]


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
