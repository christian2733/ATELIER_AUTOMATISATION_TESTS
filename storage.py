"""
storage.py
SQLite : sauvegarde et lecture des runs de tests.
"""

import json
import sqlite3
import os

DB_PATH = os.environ.get("DB_PATH", "runs.db")


def _connect():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Crée la table si elle n'existe pas."""
    with _connect() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS runs (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                api         TEXT    NOT NULL,
                timestamp   TEXT    NOT NULL,
                passed      INTEGER,
                failed      INTEGER,
                errors      INTEGER,
                error_rate  REAL,
                availability REAL,
                latency_avg REAL,
                latency_p95 REAL,
                detail_json TEXT
            )
        """)
        conn.commit()


def save_run(run: dict):
    """Sauvegarde un run complet en base."""
    s = run["summary"]
    with _connect() as conn:
        conn.execute("""
            INSERT INTO runs
              (api, timestamp, passed, failed, errors,
               error_rate, availability, latency_avg, latency_p95, detail_json)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            run["api"],
            run["timestamp"],
            s["passed"],
            s["failed"],
            s["errors"],
            s["error_rate"],
            s["availability"],
            s["latency_ms_avg"],
            s["latency_ms_p95"],
            json.dumps(run["tests"], ensure_ascii=False),
        ))
        conn.commit()


def list_runs(limit: int = 20) -> list:
    """Retourne les N derniers runs (du plus récent au plus ancien)."""
    with _connect() as conn:
        rows = conn.execute("""
            SELECT * FROM runs ORDER BY id DESC LIMIT ?
        """, (limit,)).fetchall()
    return [dict(r) for r in rows]


def get_run(run_id: int) -> dict | None:
    """Retourne un run complet par son id."""
    with _connect() as conn:
        row = conn.execute(
            "SELECT * FROM runs WHERE id = ?", (run_id,)
        ).fetchone()
    if row is None:
        return None
    r = dict(row)
    r["tests"] = json.loads(r["detail_json"])
    return r