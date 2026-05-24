# backend/cache.py
# ─────────────────────────────────────────────────────────────────────────────
# SQLite caching layer for the Privacy Policy Analyzer.
#
# Why cache?
#   Fetching and analyzing a privacy policy takes 5–15 seconds.
#   If a user analyzes the same URL twice, we return the saved result instantly.
#   The cache also powers the /api/history endpoint on the dashboard.
#
# Database: analyzer_cache.db (auto-created in the backend/ folder)
# Table:    results
# ─────────────────────────────────────────────────────────────────────────────

import sqlite3
import json
import os

DB_PATH = os.path.join(os.path.dirname(__file__), 'analyzer_cache.db')


def _connect() -> sqlite3.Connection:
    """Opens a connection with row_factory for dict-style row access."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    """
    Creates the results table if it doesn't already exist.
    Called once at Flask startup.
    """
    with _connect() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS results (
                id              INTEGER PRIMARY KEY AUTOINCREMENT,
                url             TEXT NOT NULL,
                analyzed_at     TEXT NOT NULL,
                risk_score      INTEGER NOT NULL,
                risk_label      TEXT NOT NULL,
                total_sentences INTEGER NOT NULL,
                total_findings  INTEGER NOT NULL,
                category_counts TEXT NOT NULL,   -- JSON string
                findings        TEXT NOT NULL,   -- JSON string
                created_at      DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()
    print("[cache] Database initialized:", DB_PATH)


def save_result(result: dict) -> int:
    """
    Inserts a new analysis result into the cache.

    Args:
        result -- Dict produced by app._result_to_dict()

    Returns:
        The new row ID
    """
    with _connect() as conn:
        cursor = conn.execute("""
            INSERT INTO results
                (url, analyzed_at, risk_score, risk_label,
                 total_sentences, total_findings, category_counts, findings)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            result['url'],
            result['analyzed_at'],
            result['risk_score'],
            result['risk_label'],
            result['total_sentences'],
            result['total_findings'],
            json.dumps(result['category_counts']),
            json.dumps(result['findings']),
        ))
        conn.commit()
        return cursor.lastrowid


def get_result(url: str = None, result_id: int = None) -> dict | None:
    """
    Fetches a cached result by URL or by row ID.

    Args:
        url       -- Look up the most recent result for this URL
        result_id -- Look up by primary key

    Returns:
        Dict with full result data, or None if not found
    """
    with _connect() as conn:
        if url:
            row = conn.execute(
                "SELECT * FROM results WHERE url = ? ORDER BY created_at DESC LIMIT 1",
                (url,)
            ).fetchone()
        elif result_id:
            row = conn.execute(
                "SELECT * FROM results WHERE id = ?",
                (result_id,)
            ).fetchone()
        else:
            return None

    return _deserialize(row) if row else None


def list_results(limit: int = 10) -> list[dict]:
    """
    Returns the most recently analyzed policies (summary only, no findings).

    Args:
        limit -- Maximum number of results to return

    Returns:
        List of dicts with id, url, risk_score, risk_label, analyzed_at
    """
    with _connect() as conn:
        rows = conn.execute("""
            SELECT id, url, risk_score, risk_label, total_sentences,
                   total_findings, analyzed_at
            FROM results
            ORDER BY created_at DESC
            LIMIT ?
        """, (limit,)).fetchall()

    return [dict(row) for row in rows]


def delete_result_by_id(result_id: int) -> bool:
    """Deletes a single row by primary key. Returns True if a row was removed."""
    with _connect() as conn:
        cur = conn.execute("DELETE FROM results WHERE id = ?", (result_id,))
        conn.commit()
        return cur.rowcount > 0


def delete_results_by_ids(result_ids: list[int]) -> int:
    """
    Deletes multiple rows. Unknown IDs are ignored.
    Returns the number of rows actually deleted.
    """
    if not result_ids:
        return 0
    ids = [int(x) for x in result_ids]
    placeholders = ",".join("?" * len(ids))
    with _connect() as conn:
        cur = conn.execute(
            f"DELETE FROM results WHERE id IN ({placeholders})",
            ids,
        )
        conn.commit()
        return cur.rowcount


def _deserialize(row: sqlite3.Row) -> dict:
    """Converts a DB row back to a full result dict, parsing JSON fields."""
    d = dict(row)
    d['category_counts'] = json.loads(d['category_counts'])
    d['findings']        = json.loads(d['findings'])
    return d
