import os
import sys
import argparse
import logging
import datetime
import re
from typing import List

# Windows console encoding mitigation
if sys.platform.startswith("win"):
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8")

from src.config import ROOT_DIR
from src.pipeline.orchestrator import run_weekly_pulse
from src.state.database import get_completed_run, init_db, get_db_connection

logger = logging.getLogger("pulse_cli")


def setup_logging(verbose: bool = False) -> None:
    """Configures logging for the CLI."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        stream=sys.stdout
    )


def validate_iso_week(week_str: str) -> bool:
    """Validates that a string matches YYYY-Www format."""
    return bool(re.match(r"^\d{4}-W\d{2}$", week_str))


def get_weeks_range(from_week: str, to_week: str) -> List[str]:
    """
    Computes a list of ISO week strings from from_week to to_week (inclusive).
    Supports transitions across year boundaries.
    """
    if not validate_iso_week(from_week) or not validate_iso_week(to_week):
        raise ValueError("Weeks must be in the format YYYY-Www (e.g. 2026-W25)")

    try:
        # Parse start and end dates (Monday of each week)
        start_date = datetime.datetime.strptime(f"{from_week}-1", "%G-W%V-%u").date()
        end_date = datetime.datetime.strptime(f"{to_week}-1", "%G-W%V-%u").date()
    except ValueError as e:
        raise ValueError(f"Invalid ISO week value: {e}")

    if start_date > end_date:
        raise ValueError(f"Start week ({from_week}) cannot be after end week ({to_week})")

    weeks = []
    current_date = start_date
    while current_date <= end_date:
        year, week_num, _ = current_date.isocalendar()
        weeks.append(f"{year}-W{week_num:02d}")
        current_date += datetime.timedelta(weeks=1)

    return weeks


def cmd_run(args) -> int:
    """Handles 'run' and 'dry-run' commands."""
    iso_week = args.iso_week
    if iso_week and not validate_iso_week(iso_week):
        logger.error(f"Invalid ISO week format: {iso_week}. Expected YYYY-Www")
        return 1

    dry_run = getattr(args, "dry_run", False) or args.command == "dry-run"
    db_path = getattr(args, "db_path", None)

    try:
        res = run_weekly_pulse(
            product_name=args.product,
            iso_week=iso_week,
            dry_run=dry_run,
            db_path=db_path
        )
        
        status = res.get("status")
        if status == "skipped":
            print(f"\n[SKIP] {res.get('message')}")
        else:
            print(f"\n[SUCCESS] Run completed successfully!")
            print(f"Run ID: {res.get('run_id')}")
            print(f"Reviews Ingested & Analyzed: {res.get('review_count')}")
            print("\nDeliveries:")
            for d in res.get("deliveries", []):
                print(f"  - {d['channel'].upper()}: {d['url']} (External ID: {d['external_id']})")
        return 0
    except Exception as e:
        logger.error(f"Weekly pulse run failed: {e}")
        return 1


def cmd_backfill(args) -> int:
    """Handles the 'backfill' command."""
    from_week = args.from_week
    to_week = args.to_week
    db_path = getattr(args, "db_path", None)
    dry_run = getattr(args, "dry_run", False)

    try:
        weeks = get_weeks_range(from_week, to_week)
    except ValueError as e:
        logger.error(f"Backfill week range error: {e}")
        return 1

    print(f"Starting backfill for product '{args.product}' from {from_week} to {to_week} ({len(weeks)} weeks)...")
    success_count = 0
    skipped_count = 0
    failed_count = 0

    for w in weeks:
        print(f"\n------------------------------------------------------------")
        print(f"Processing week: {w}")
        print(f"------------------------------------------------------------")
        try:
            res = run_weekly_pulse(
                product_name=args.product,
                iso_week=w,
                dry_run=dry_run,
                db_path=db_path
            )
            if res.get("status") == "skipped":
                print(f"[SKIP] Week {w} already completed.")
                skipped_count += 1
            else:
                print(f"[SUCCESS] Week {w} completed successfully.")
                success_count += 1
        except Exception as e:
            logger.error(f"Failed processing week {w}: {e}")
            failed_count += 1
            if args.stop_on_failure:
                print("\n[ABORT] Stopping backfill due to failure.")
                break

    print(f"\n============================================================")
    print(f"Backfill Summary for {args.product}:")
    print(f"  - Total processed: {len(weeks)}")
    print(f"  - Successful:     {success_count}")
    print(f"  - Skipped:        {skipped_count}")
    print(f"  - Failed:         {failed_count}")
    print(f"============================================================")

    return 1 if failed_count > 0 else 0


def cmd_status(args) -> int:
    """Handles the 'status' command."""
    iso_week = args.iso_week
    if not validate_iso_week(iso_week):
        logger.error(f"Invalid ISO week format: {iso_week}. Expected YYYY-Www")
        return 1

    db_path = getattr(args, "db_path", None)
    if db_path is None:
        db_path = str(ROOT_DIR / "db.sqlite")

    if not os.path.exists(db_path):
        print(f"No run ledger database exists at {db_path}.")
        return 0

    init_db(db_path)

    conn = get_db_connection(db_path)
    try:
        # Check any run entry
        run_row = conn.execute(
            "SELECT * FROM runs WHERE product = ? AND iso_week = ? ORDER BY started_at DESC LIMIT 1",
            (args.product, iso_week)
        ).fetchone()

        if not run_row:
            print(f"No execution record found for product '{args.product}' on week '{iso_week}'.")
            return 0

        print(f"\nRun Audit Log Status for {args.product} / {iso_week}:")
        print(f"============================================================")
        print(f"Run ID:        {run_row['run_id']}")
        print(f"Status:        {run_row['status'].upper()}")
        print(f"Reviews:       {run_row['review_count'] if run_row['review_count'] is not None else 'N/A'}")
        print(f"Window Weeks:  {run_row['window_weeks']}")
        print(f"Started At:    {run_row['started_at']}")
        print(f"Completed At:  {run_row['completed_at'] if run_row['completed_at'] else 'N/A'}")
        if run_row["error_message"]:
            print(f"Error Message: {run_row['error_message']}")

        # Fetch deliveries
        deliveries = conn.execute(
            "SELECT channel, external_id, url, idempotency_key FROM deliveries WHERE run_id = ?",
            (run_row["run_id"],)
        ).fetchall()

        if deliveries:
            print(f"\nDeliveries:")
            for d in deliveries:
                print(f"  - {d['channel'].upper()}:")
                print(f"      External ID: {d['external_id']}")
                print(f"      URL:         {d['url']}")
                if d["idempotency_key"]:
                    print(f"      Idempotency: {d['idempotency_key']}")
        else:
            print("\nNo deliveries recorded for this run.")
        print(f"============================================================")
        return 0
    finally:
        conn.close()


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Pulse Agent Command-Line Interface for Weekly Review Pulse."
    )
    parser.add_argument(
        "-v", "--verbose", action="store_true", help="Enable verbose debug logging"
    )
    parser.add_argument(
        "--db-path", type=str, help="Custom path to SQLite run ledger DB"
    )

    subparsers = parser.add_subparsers(dest="command", required=True, help="CLI Subcommands")

    # 'run' subcommand
    run_parser = subparsers.add_parser("run", help="Run weekly review pulse pipeline")
    run_parser.add_argument(
        "--product", type=str, required=True, help="Product identifier (e.g. 'groww')"
    )
    run_parser.add_argument(
        "--iso-week", type=str, help="ISO week label YYYY-Www (defaults to current week)"
    )

    # 'dry-run' subcommand
    dry_parser = subparsers.add_parser("dry-run", help="Run weekly review pulse in dry-run mode")
    dry_parser.add_argument(
        "--product", type=str, required=True, help="Product identifier"
    )
    dry_parser.add_argument(
        "--iso-week", type=str, help="ISO week label YYYY-Www"
    )

    # 'backfill' subcommand
    backfill_parser = subparsers.add_parser("backfill", help="Backfill historical review pulse reports")
    backfill_parser.add_argument(
        "--product", type=str, required=True, help="Product identifier"
    )
    backfill_parser.add_argument(
        "--from", dest="from_week", type=str, required=True, help="Start week YYYY-Www"
    )
    backfill_parser.add_argument(
        "--to", dest="to_week", type=str, required=True, help="End week YYYY-Www"
    )
    backfill_parser.add_argument(
        "--dry-run", action="store_true", help="Execute backfill runs in dry-run mode"
    )
    backfill_parser.add_argument(
        "--stop-on-failure", action="store_true", help="Abort backfill sequence if any week fails"
    )

    # 'status' subcommand
    status_parser = subparsers.add_parser("status", help="Get run ledger status for a week")
    status_parser.add_argument(
        "--product", type=str, required=True, help="Product identifier"
    )
    status_parser.add_argument(
        "--iso-week", type=str, required=True, help="ISO week label YYYY-Www"
    )

    args = parser.parse_args()
    setup_logging(args.verbose)

    if args.command in ("run", "dry-run"):
        return cmd_run(args)
    elif args.command == "backfill":
        return cmd_backfill(args)
    elif args.command == "status":
        return cmd_status(args)
    return 0


if __name__ == "__main__":
    sys.exit(main())
