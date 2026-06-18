import sqlite3
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional


def get_db_connection(db_path: str) -> sqlite3.Connection:
    """
    Creates and returns a SQLite connection with row factory configured.
    Enforces foreign key support.
    """
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


def init_db(db_path: str) -> None:
    """
    Initializes the SQLite database tables for runs and deliveries.
    """
    conn = get_db_connection(db_path)
    try:
        with conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS runs (
                    run_id TEXT PRIMARY KEY,
                    product TEXT NOT NULL,
                    iso_week TEXT NOT NULL,
                    status TEXT NOT NULL CHECK(status IN ('pending', 'completed', 'failed')),
                    review_count INTEGER,
                    window_weeks INTEGER,
                    started_at TEXT NOT NULL,
                    completed_at TEXT,
                    error_message TEXT
                );
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS deliveries (
                    run_id TEXT NOT NULL,
                    channel TEXT NOT NULL CHECK(channel IN ('google_doc', 'gmail')),
                    external_id TEXT NOT NULL,
                    url TEXT NOT NULL,
                    idempotency_key TEXT,
                    FOREIGN KEY (run_id) REFERENCES runs(run_id) ON DELETE CASCADE
                );
            """)
    finally:
        conn.close()


def get_completed_run(db_path: str, product: str, iso_week: str) -> Optional[Dict[str, Any]]:
    """
    Checks if a completed run exists for the given product and iso_week.
    If it exists, returns a dict with the run details and its deliveries.
    Otherwise, returns None.
    """
    conn = get_db_connection(db_path)
    try:
        # Check runs
        run_row = conn.execute(
            "SELECT * FROM runs WHERE product = ? AND iso_week = ? AND status = 'completed' LIMIT 1",
            (product, iso_week)
        ).fetchone()

        if not run_row:
            return None

        run_data = dict(run_row)
        run_id = run_data["run_id"]

        # Fetch deliveries
        delivery_rows = conn.execute(
            "SELECT channel, external_id, url, idempotency_key FROM deliveries WHERE run_id = ?",
            (run_id,)
        ).fetchall()

        run_data["deliveries"] = [dict(row) for row in delivery_rows]
        return run_data
    finally:
        conn.close()


def start_run(db_path: str, run_id: str, product: str, iso_week: str, window_weeks: int) -> None:
    """
    Inserts a run with status 'pending' and records start time.
    """
    started_at = datetime.now(timezone.utc).isoformat()
    conn = get_db_connection(db_path)
    try:
        with conn:
            conn.execute(
                """
                INSERT INTO runs (run_id, product, iso_week, status, window_weeks, started_at)
                VALUES (?, ?, ?, 'pending', ?, ?)
                """,
                (run_id, product, iso_week, window_weeks, started_at)
            )
    finally:
        conn.close()


def complete_run(db_path: str, run_id: str, review_count: int, deliveries: List[Dict[str, Any]]) -> None:
    """
    Updates the run status to 'completed', records completion time, and inserts deliveries.
    """
    completed_at = datetime.now(timezone.utc).isoformat()
    conn = get_db_connection(db_path)
    try:
        with conn:
            # Update run status
            conn.execute(
                """
                UPDATE runs
                SET status = 'completed', review_count = ?, completed_at = ?
                WHERE run_id = ?
                """,
                (review_count, completed_at, run_id)
            )
            # Insert deliveries
            for d in deliveries:
                conn.execute(
                    """
                    INSERT INTO deliveries (run_id, channel, external_id, url, idempotency_key)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (run_id, d["channel"], d["external_id"], d["url"], d.get("idempotency_key"))
                )
    finally:
        conn.close()


def fail_run(db_path: str, run_id: str, error_message: str) -> None:
    """
    Updates the run status to 'failed', records completion time and error message.
    """
    completed_at = datetime.now(timezone.utc).isoformat()
    conn = get_db_connection(db_path)
    try:
        with conn:
            conn.execute(
                """
                UPDATE runs
                SET status = 'failed', completed_at = ?, error_message = ?
                WHERE run_id = ?
                """,
                (completed_at, error_message, run_id)
            )
    finally:
        conn.close()
