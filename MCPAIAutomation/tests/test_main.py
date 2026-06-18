import pytest
from unittest.mock import MagicMock, patch, call
from src.main import (
    validate_iso_week,
    get_weeks_range,
    cmd_run,
    cmd_backfill,
    cmd_status
)


def test_validate_iso_week():
    assert validate_iso_week("2026-W25") is True
    assert validate_iso_week("1999-W01") is True
    assert validate_iso_week("2026-W53") is True  # standard matches format
    assert validate_iso_week("26-W25") is False
    assert validate_iso_week("2026W25") is False
    assert validate_iso_week("2026-W2") is False
    assert validate_iso_week("abc") is False


def test_get_weeks_range_simple():
    weeks = get_weeks_range("2026-W23", "2026-W25")
    assert weeks == ["2026-W23", "2026-W24", "2026-W25"]


def test_get_weeks_range_single():
    assert get_weeks_range("2026-W25", "2026-W25") == ["2026-W25"]


def test_get_weeks_range_year_boundary():
    # 2025 ends with W52, 2026 starts with W01
    weeks = get_weeks_range("2025-W52", "2026-W02")
    assert weeks == ["2025-W52", "2026-W01", "2026-W02"]


def test_get_weeks_range_errors():
    with pytest.raises(ValueError, match="format YYYY-Www"):
        get_weeks_range("abc", "2026-W25")
    with pytest.raises(ValueError, match="Start week.*cannot be after"):
        get_weeks_range("2026-W25", "2026-W24")


def test_cmd_run_success():
    args = MagicMock()
    args.product = "groww"
    args.iso_week = "2026-W25"
    args.command = "run"
    args.dry_run = False
    args.db_path = "some-db.sqlite"

    with patch("src.main.run_weekly_pulse") as mock_pulse:
        mock_pulse.return_value = {
            "status": "completed",
            "run_id": "groww-run-123",
            "review_count": 100,
            "deliveries": [{"channel": "google_doc", "url": "http://doc", "external_id": "hd1"}]
        }
        
        exit_code = cmd_run(args)
        assert exit_code == 0
        mock_pulse.assert_called_once_with(
            product_name="groww",
            iso_week="2026-W25",
            dry_run=False,
            db_path="some-db.sqlite"
        )


def test_cmd_run_skipped():
    args = MagicMock()
    args.product = "groww"
    args.iso_week = "2026-W25"
    args.command = "dry-run"
    args.dry_run = True
    args.db_path = None

    with patch("src.main.run_weekly_pulse") as mock_pulse:
        mock_pulse.return_value = {
            "status": "skipped",
            "message": "Run already completed"
        }
        
        exit_code = cmd_run(args)
        assert exit_code == 0
        mock_pulse.assert_called_once_with(
            product_name="groww",
            iso_week="2026-W25",
            dry_run=True,
            db_path=None
        )


def test_cmd_backfill_success():
    args = MagicMock()
    args.product = "groww"
    args.from_week = "2026-W23"
    args.to_week = "2026-W24"
    args.dry_run = True
    args.db_path = "test.db"
    args.stop_on_failure = False

    with patch("src.main.run_weekly_pulse") as mock_pulse:
        mock_pulse.return_value = {"status": "completed"}
        
        exit_code = cmd_backfill(args)
        assert exit_code == 0
        
        assert mock_pulse.call_count == 2
        mock_pulse.assert_has_calls([
            call(product_name="groww", iso_week="2026-W23", dry_run=True, db_path="test.db"),
            call(product_name="groww", iso_week="2026-W24", dry_run=True, db_path="test.db")
        ])


def test_cmd_status_no_record():
    args = MagicMock()
    args.product = "groww"
    args.iso_week = "2026-W25"
    args.db_path = "non_existent.db"

    # Mock DB calls to return no records
    with patch("src.main.os.path.exists", return_value=True), \
         patch("src.main.init_db"), \
         patch("src.main.get_db_connection") as mock_conn_cls:
         
        mock_conn = MagicMock()
        mock_conn.execute.return_value.fetchone.return_value = None
        mock_conn_cls.return_value = mock_conn
        
        exit_code = cmd_status(args)
        assert exit_code == 0
        
        # Verify query was called
        mock_conn.execute.assert_called_once_with(
            "SELECT * FROM runs WHERE product = ? AND iso_week = ? ORDER BY started_at DESC LIMIT 1",
            ("groww", "2026-W25")
        )
