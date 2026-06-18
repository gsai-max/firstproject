import os
import sqlite3
import pytest
from src.state.database import (
    init_db,
    get_db_connection,
    get_completed_run,
    start_run,
    complete_run,
    fail_run
)

DB_PATH = "test_run_ledger.db"


@pytest.fixture(autouse=True)
def setup_and_teardown_db():
    # Teardown any leftover test database before running test
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
        
    yield
    
    # Teardown test database after test
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)


def test_init_db_creates_tables():
    init_db(DB_PATH)
    assert os.path.exists(DB_PATH)
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Check runs table exists
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='runs'")
    assert cursor.fetchone() is not None
    
    # Check deliveries table exists
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='deliveries'")
    assert cursor.fetchone() is not None
    
    conn.close()


def test_runs_tracking_flow():
    init_db(DB_PATH)
    
    run_id = "test-prod-2026-W25-12345"
    product = "test-prod"
    iso_week = "2026-W25"
    window_weeks = 10
    
    # 1. Start a run (pending)
    start_run(DB_PATH, run_id, product, iso_week, window_weeks)
    
    # Should not show as completed yet
    assert get_completed_run(DB_PATH, product, iso_week) is None
    
    # Connect and verify pending status
    conn = get_db_connection(DB_PATH)
    row = conn.execute("SELECT * FROM runs WHERE run_id = ?", (run_id,)).fetchone()
    conn.close()
    
    assert row is not None
    assert row["status"] == "pending"
    assert row["product"] == product
    assert row["iso_week"] == iso_week
    assert row["window_weeks"] == window_weeks
    assert row["started_at"] is not None
    assert row["completed_at"] is None
    assert row["error_message"] is None
    
    # 2. Complete the run
    deliveries = [
        {
            "channel": "google_doc",
            "external_id": "heading_123",
            "url": "https://docs.google.com/document/d/doc-id#heading=heading_123",
            "idempotency_key": "test-prod-2026-W25-doc"
        },
        {
            "channel": "gmail",
            "external_id": "draft_456",
            "url": "https://mail.google.com/mail/#drafts/draft_456",
            "idempotency_key": "test-prod-2026-W25-email"
        }
    ]
    
    complete_run(DB_PATH, run_id, review_count=42, deliveries=deliveries)
    
    # Verify completed run exists and returns correct fields
    completed = get_completed_run(DB_PATH, product, iso_week)
    assert completed is not None
    assert completed["run_id"] == run_id
    assert completed["status"] == "completed"
    assert completed["review_count"] == 42
    assert completed["completed_at"] is not None
    
    assert len(completed["deliveries"]) == 2
    assert completed["deliveries"][0]["channel"] == "google_doc"
    assert completed["deliveries"][0]["external_id"] == "heading_123"
    assert completed["deliveries"][0]["idempotency_key"] == "test-prod-2026-W25-doc"
    assert completed["deliveries"][1]["channel"] == "gmail"
    assert completed["deliveries"][1]["external_id"] == "draft_456"
    assert completed["deliveries"][1]["idempotency_key"] == "test-prod-2026-W25-email"


def test_runs_tracking_failure_flow():
    init_db(DB_PATH)
    
    run_id = "test-prod-fail-12345"
    product = "test-prod-fail"
    iso_week = "2026-W25"
    
    start_run(DB_PATH, run_id, product, iso_week, window_weeks=10)
    fail_run(DB_PATH, run_id, "Something went wrong in the pipeline API call")
    
    # Should not show as completed
    assert get_completed_run(DB_PATH, product, iso_week) is None
    
    # Connect and verify failed status
    conn = get_db_connection(DB_PATH)
    row = conn.execute("SELECT * FROM runs WHERE run_id = ?", (run_id,)).fetchone()
    conn.close()
    
    assert row is not None
    assert row["status"] == "failed"
    assert row["error_message"] == "Something went wrong in the pipeline API call"
    assert row["completed_at"] is not None
