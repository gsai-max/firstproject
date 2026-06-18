import os
import logging
import datetime
from pathlib import Path
from typing import Dict, Any, Optional, List

from src.config import load_config, ROOT_DIR
from src.ingestion.client import PlayStoreMCPClient
from src.ingestion.models import Review
from src.pipeline.summarizer import ReviewSummarizer
from src.delivery.client import (
    generate_markdown_report,
    generate_email_teaser,
    append_to_google_doc,
    send_email_teaser_draft
)
from src.state.database import (
    init_db,
    get_completed_run,
    start_run,
    complete_run,
    fail_run
)

logger = logging.getLogger(__name__)


def run_weekly_pulse(
    product_name: str,
    iso_week: Optional[str] = None,
    dry_run: bool = False,
    db_path: Optional[str] = None
) -> Dict[str, Any]:
    """
    Orchestrates the entire Weekly Review Pulse pipeline with state tracking and idempotency checks.
    
    Args:
        product_name: The product identifier (e.g., 'groww')
        iso_week: ISO 8601 week label (e.g., '2026-W25'). Defaults to the current week.
        dry_run: If True, executes pipeline and saves output files locally, bypassing remote MCP writes.
        db_path: Path to the SQLite DB file. Defaults to ROOT_DIR / 'db.sqlite'.
        
    Returns:
        A dictionary containing run execution results.
    """
    # 1. Setup Database Path and Initialize
    if db_path is None:
        db_path = str(ROOT_DIR / "db.sqlite")
    
    init_db(db_path)
    
    # 2. Determine ISO week
    if not iso_week:
        today = datetime.date.today()
        iso_year, iso_week_num, _ = today.isocalendar()
        iso_week = f"{iso_year}-W{iso_week_num:02d}"
        
    logger.info(f"Orchestrating Weekly Review Pulse for product='{product_name}' and week='{iso_week}' (dry_run={dry_run})")
    
    # 3. Check for previous successful run (Idempotency)
    completed_run = get_completed_run(db_path, product_name, iso_week)
    if completed_run:
        logger.info(f"Idempotency Triggered: Run already completed for {product_name} on week {iso_week}.")
        return {
            "status": "skipped",
            "run_id": completed_run["run_id"],
            "message": f"Run already completed for {product_name} on week {iso_week}.",
            "run": completed_run
        }
        
    # 4. Initialize Run in Database
    timestamp_suffix = int(datetime.datetime.now(datetime.timezone.utc).timestamp())
    run_id = f"{product_name}-{iso_week}-{timestamp_suffix}"
    
    # Load configuration
    try:
        config = load_config(product_name)
    except Exception as e:
        logger.error(f"Failed to load configuration for product {product_name}: {e}")
        raise e
        
    window_weeks = config.product.ingestion.window_weeks
    start_run(db_path, run_id, product_name, iso_week, window_weeks)
    
    # 5. Execute Pipeline Stages
    try:
        # Ingestion
        logger.info("Executing Ingestion Stage...")
        ingestion_client = PlayStoreMCPClient(app_id=config.product.play_store.app_id)
        raw_reviews = asyncio_run_shim(ingestion_client.fetch_reviews(
            window_weeks=window_weeks,
            max_reviews=config.product.ingestion.max_reviews
        ))
        
        # Unique review count constraint check
        # Deduplicate and extract Review models
        seen = set()
        reviews: List[Review] = []
        for r in raw_reviews:
            # Clean normalization comparison key
            # Standard: hash text, rating, date
            pub_date = r.published_at.isoformat() if hasattr(r.published_at, "isoformat") else str(r.published_at)
            key = (" ".join(r.text.split()).lower(), r.rating, pub_date)
            if key not in seen:
                seen.add(key)
                # Apply word count and basic normalization/filter checks
                from src.ingestion.normalizer import clean_and_normalize
                cleaned_text = clean_and_normalize(r.text)
                if cleaned_text:
                    reviews.append(Review(text=cleaned_text, rating=r.rating))
                    
        review_count = len(reviews)
        logger.info(f"Ingested {len(raw_reviews)} raw reviews. Normalized and filtered down to {review_count} reviews.")
        
        # Abort if review count is below minimum threshold (default: 20)
        min_reviews = config.product.ingestion.min_reviews
        if review_count < min_reviews:
            error_msg = f"Review count ({review_count}) is below the minimum required ({min_reviews}) to run clustering."
            logger.error(error_msg)
            raise ValueError(error_msg)
            
        # Analysis (Clustering & Summarization)
        logger.info("Executing Analysis (Clustering & Summarization) Stage...")
        summarizer = ReviewSummarizer(config=config)
        themes = summarizer.run_pipeline(reviews)
        logger.info(f"Generated {len(themes)} themes from clustering.")
        
        # Rendering
        logger.info("Executing Rendering Stage...")
        utc_now = datetime.datetime.now(datetime.timezone.utc)
        ist_now = utc_now + datetime.timedelta(hours=5, minutes=30)
        generated_date_str = f"{ist_now.strftime('%Y-%m-%d')} IST"
        
        markdown_report = generate_markdown_report(
            display_name=config.product.display_name,
            window_weeks=window_weeks,
            themes=themes,
            generated_date_str=generated_date_str
        )
        
        # Add heading_id deep link capability by extracting heading info or creating default link
        doc_id = config.product.delivery.google_doc_id
        
        # Delivery
        deliveries = []
        
        if dry_run:
            logger.info("Executing dry-run delivery (local fallback files only)...")
            
            # Save report file
            reports_dir = Path("data/reports")
            reports_dir.mkdir(parents=True, exist_ok=True)
            fallback_report_path = reports_dir / f"weekly_report_{product_name}_{iso_week}.md"
            with open(fallback_report_path, "w", encoding="utf-8") as f:
                f.write(markdown_report)
                
            deliveries.append({
                "channel": "google_doc",
                "external_id": "dry_run_doc_heading",
                "url": f"file:///{fallback_report_path.absolute()}",
                "idempotency_key": f"{product_name}-{iso_week}-doc"
            })
            
            # Save email file
            email_teaser = generate_email_teaser(
                display_name=config.product.display_name,
                iso_week=iso_week,
                themes=themes,
                doc_id=doc_id
            )
            emails_dir = Path("data/emails")
            emails_dir.mkdir(parents=True, exist_ok=True)
            fallback_email_path = emails_dir / f"email_teaser_{product_name}_{iso_week}.json"
            
            import json
            with open(fallback_email_path, "w", encoding="utf-8") as f:
                json.dump(email_teaser, f, indent=2)
                
            deliveries.append({
                "channel": "gmail",
                "external_id": "dry_run_draft_id",
                "url": f"file:///{fallback_email_path.absolute()}",
                "idempotency_key": f"{product_name}-{iso_week}-email"
            })
            
        else:
            logger.info("Executing live delivery (remote Google Workspace MCP)...")
            
            # 1. Google Doc Append
            doc_res = append_to_google_doc(
                doc_id=doc_id,
                content=markdown_report,
                iso_week=iso_week
            )
            
            doc_status = doc_res.get("status")
            if doc_status == "success":
                # Extract details
                response_data = doc_res.get("response", {})
                heading_id = response_data.get("headingId", "top_heading")
                actual_doc_id = response_data.get("documentId", doc_id)
                doc_url = f"https://docs.google.com/document/d/{actual_doc_id}#heading={heading_id}"
                external_id = heading_id
            else:
                # Fallback path
                doc_url = f"file:///{Path(doc_res.get('path')).absolute()}"
                external_id = "local_fallback_id"
                
            deliveries.append({
                "channel": "google_doc",
                "external_id": external_id,
                "url": doc_url,
                "idempotency_key": f"{product_name}-{iso_week}-doc"
            })
            
            # 2. Email Teaser Draft
            email_teaser = generate_email_teaser(
                display_name=config.product.display_name,
                iso_week=iso_week,
                themes=themes,
                doc_id=doc_id
            )
            
            recipients = ", ".join(config.product.delivery.email.recipients)
            gmail_res = send_email_teaser_draft(
                to=recipients,
                subject=email_teaser["subject"],
                body=email_teaser["text_body"],
                iso_week=iso_week
            )
            
            gmail_status = gmail_res.get("status")
            if gmail_status == "success":
                response_data = gmail_res.get("response", {})
                draft_id = response_data.get("id", "unknown_draft")
                gmail_url = f"https://mail.google.com/mail/#drafts/{draft_id}"
                external_id = draft_id
            else:
                gmail_url = f"file:///{Path(gmail_res.get('path')).absolute()}"
                external_id = "local_fallback_id"
                
            deliveries.append({
                "channel": "gmail",
                "external_id": external_id,
                "url": gmail_url,
                "idempotency_key": f"{product_name}-{iso_week}-email"
            })
            
        # Complete run
        complete_run(db_path, run_id, review_count, deliveries)
        
        return {
            "status": "completed",
            "run_id": run_id,
            "review_count": review_count,
            "deliveries": deliveries
        }
        
    except Exception as e:
        logger.error(f"Pipeline run {run_id} failed with error: {e}")
        fail_run(db_path, run_id, str(e))
        raise e


def asyncio_run_shim(coro):
    """
    Helper to run asynchronous coroutines from synchronous context.
    """
    import asyncio
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
    if loop.is_running():
        # If loop is already running (e.g. under pytest with async plugins or other contexts),
        # use a task runner or running thread pool if needed.
        # But for stdio clients and standard subprocess calls, we can run it synchronously
        # via an executor or similar if nested loop isn't supported, 
        # or nesting it with nest_asyncio if available.
        # Let's try to run it using asyncio.run_coroutine_threadsafe.
        import concurrent.futures
        with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
            future = executor.submit(asyncio.run, coro)
            return future.result()
    else:
        return loop.run_until_complete(coro)
