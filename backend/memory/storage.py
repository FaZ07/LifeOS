"""SQLite persistence for LifeOS runs.

Kept intentionally tiny — just enough so the UI can show history and so users
can see how their real behaviour drifts vs. the strategy they chose last week.
"""
from __future__ import annotations

import json
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Iterator

DB_PATH = Path(__file__).resolve().parent / "lifeos.sqlite3"


_SCHEMA = """
CREATE TABLE IF NOT EXISTS runs (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    created_at    TEXT    NOT NULL DEFAULT (datetime('now')),
    inputs_json   TEXT    NOT NULL,
    result_json   TEXT    NOT NULL
);
"""


@contextmanager
def _conn() -> Iterator[sqlite3.Connection]:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_db() -> None:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    with _conn() as c:
        c.executescript(_SCHEMA)


def save_run(inputs: dict[str, Any], result: dict[str, Any]) -> int:
    with _conn() as c:
        cur = c.execute(
            "INSERT INTO runs(inputs_json, result_json) VALUES (?, ?)",
            (json.dumps(inputs), json.dumps(result)),
        )
        return int(cur.lastrowid)


def list_runs(limit: int = 25) -> list[dict[str, Any]]:
    with _conn() as c:
        rows = c.execute(
            "SELECT id, created_at, inputs_json, result_json "
            "FROM runs ORDER BY id DESC LIMIT ?",
            (int(limit),),
        ).fetchall()
    return [
        {
            "id": r["id"],
            "created_at": r["created_at"],
            "inputs": json.loads(r["inputs_json"]),
            "result": json.loads(r["result_json"]),
        }
        for r in rows
    ]


def get_run(run_id: int) -> dict[str, Any] | None:
    with _conn() as c:
        row = c.execute(
            "SELECT id, created_at, inputs_json, result_json FROM runs WHERE id = ?",
            (int(run_id),),
        ).fetchone()
    if row is None:
        return None
    return {
        "id": row["id"],
        "created_at": row["created_at"],
        "inputs": json.loads(row["inputs_json"]),
        "result": json.loads(row["result_json"]),
    }
