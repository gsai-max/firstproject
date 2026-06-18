import os
import pytest
from unittest.mock import MagicMock, patch
from src.state.database import init_db, get_db_connection, complete_run
from src.pipeline.orchestrator import run_weekly_pulse
from src.ingestion.models import RawReview

TEST_DB = "test_orch.db"


@pytest.fixture(autouse=True)
def setup_and_teardown_db():
    if os.path.exists(TEST_DB):
        os.remove(TEST_DB)
    yield
    if os.path.exists(TEST_DB):
        os.remove(TEST_DB)


def test_orchestrator_skips_if_already_completed():
    init_db(TEST_DB)
    
    # Pre-populate a completed run
    conn = get_db_connection(TEST_DB)
    conn.execute(
        """
        INSERT INTO runs (run_id, product, iso_week, status, window_weeks, started_at)
        VALUES ('groww-2026-W25-abc', 'groww', '2026-W25', 'completed', 10, '2026-06-18T10:00:00Z')
        """
    )
    conn.commit()
    conn.close()
    
    # Execute the orchestrator
    with patch("src.pipeline.orchestrator.PlayStoreMCPClient") as mock_client:
        res = run_weekly_pulse("groww", "2026-W25", dry_run=True, db_path=TEST_DB)
        
        # Verify it skipped execution
        assert res["status"] == "skipped"
        assert "Run already completed" in res["message"]
        # Client should not have been instantiated
        mock_client.assert_not_called()


@pytest.mark.anyio
async def test_orchestrator_runs_successfully_and_records():
    init_db(TEST_DB)
    
    # Create raw reviews (need at least 20 unique reviews to avoid abort)
    raw_reviews = []
    for i in range(25):
        raw_reviews.append(
            RawReview(
                text=f"This is a long and detailed review number {i} for Groww",
                score=5,
                date="2026-06-18T12:00:00Z",
                id=f"id_{i}"
            )
        )
        
    mock_themes = [
        {
            "theme_name": "Performance",
            "summary": "App runs fine.",
            "quotes": ["app runs fine"],
            "action_ideas": [{"title": "UX", "detail": "keep it up"}],
            "avg_rating": 4.5,
            "size": 15
        }
    ]
    
    # Mock Ingestion fetch_reviews
    async def mock_fetch(*args, **kwargs):
        return raw_reviews

    with patch("src.pipeline.orchestrator.PlayStoreMCPClient") as mock_client_cls, \
         patch("src.pipeline.orchestrator.ReviewSummarizer") as mock_summarizer_cls, \
         patch("src.pipeline.orchestrator.append_to_google_doc") as mock_doc_delivery, \
         patch("src.pipeline.orchestrator.send_email_teaser_draft") as mock_email_delivery:
         
        # Set up mock client instance
        mock_client = MagicMock()
        mock_client.fetch_reviews = mock_fetch
        mock_client_cls.return_value = mock_client
        
        # Set up mock summarizer instance
        mock_summarizer = MagicMock()
        mock_summarizer.run_pipeline.return_value = mock_themes
        mock_summarizer_cls.return_value = mock_summarizer
        
        # Set up mock delivery responses
        mock_doc_delivery.return_value = {
            "status": "success",
            "response": {"documentId": "google-doc-id-123", "headingId": "heading_abc"}
        }
        mock_email_delivery.return_value = {
            "status": "success",
            "response": {"id": "draft_xyz"}
        }
        
        # Run orchestrator
        res = run_weekly_pulse("groww", "2026-W25", dry_run=False, db_path=TEST_DB)
        
        assert res["status"] == "completed"
        assert res["review_count"] == 25
        
        # Verify run is marked completed in DB
        conn = get_db_connection(TEST_DB)
        run_row = conn.execute("SELECT * FROM runs WHERE iso_week = '2026-W25'").fetchone()
        delivery_rows = conn.execute("SELECT * FROM deliveries WHERE run_id = ?", (run_row["run_id"],)).fetchall()
        conn.close()
        
        assert run_row["status"] == "completed"
        assert len(delivery_rows) == 2
        assert delivery_rows[0]["channel"] == "google_doc"
        assert delivery_rows[0]["external_id"] == "heading_abc"
        assert delivery_rows[1]["channel"] == "gmail"
        assert delivery_rows[1]["external_id"] == "draft_xyz"


def test_orchestrator_aborts_on_low_reviews_and_records_failure():
    init_db(TEST_DB)
    
    # Create less than 20 raw reviews (e.g. 5 reviews)
    raw_reviews = []
    for i in range(5):
        raw_reviews.append(
            RawReview(
                text=f"Short review {i}",
                score=4,
                date="2026-06-18T12:00:00Z",
                id=f"id_{i}"
            )
        )
        
    async def mock_fetch(*args, **kwargs):
        return raw_reviews

    with patch("src.pipeline.orchestrator.PlayStoreMCPClient") as mock_client_cls:
        mock_client = MagicMock()
        mock_client.fetch_reviews = mock_fetch
        mock_client_cls.return_value = mock_client
        
        with pytest.raises(ValueError, match="below the minimum required"):
            run_weekly_pulse("groww", "2026-W25", dry_run=True, db_path=TEST_DB)
            
        # Verify database recorded the failure
        conn = get_db_connection(TEST_DB)
        row = conn.execute("SELECT * FROM runs WHERE iso_week = '2026-W25'").fetchone()
        conn.close()
        
        assert row is not None
        assert row["status"] == "failed"
        assert "below the minimum required" in row["error_message"]
