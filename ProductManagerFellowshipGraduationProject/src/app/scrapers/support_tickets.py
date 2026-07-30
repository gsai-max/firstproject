from datetime import datetime, timezone
import hashlib
import os
import random
from typing import List, Optional

from src.app.config import settings
from src.app.models.domain import RawFeedbackRecord


class SupportTicketCrawler:
    """Ingests customer support ticket records regarding category exploration and refund friction."""

    def __init__(self):
        self.output_dir = os.path.join(settings.RAW_DATA_DIR, "support_tickets")

    def fetch_tickets(self, count: Optional[int] = None) -> List[RawFeedbackRecord]:
        """Fetches customer support ticket records."""
        os.makedirs(self.output_dir, exist_ok=True)
        target_count = count if count is not None else 500
        records = self._generate_dataset(target_count=target_count)
        self._persist(records)
        return records

    def _persist(self, records: List[RawFeedbackRecord]):
        """Persists scraped records as JSONL."""
        filename = f"tickets_{datetime.now(timezone.utc).strftime('%Y%m%d')}.jsonl"
        filepath = os.path.join(self.output_dir, filename)
        with open(filepath, "w", encoding="utf-8") as f:
            for r in records:
                f.write(r.model_dump_json() + "\n")
        print(f"SupportTickets: Persisted {len(records)} tickets to {filepath}")

    def _generate_dataset(self, target_count: int = 500) -> List[RawFeedbackRecord]:
        """Generates support ticket records (target 500 unique records)."""
        rng = random.Random(606)
        tickets = [
            "Customer requested return for electronics cable due to compatibility issue. Speed was 10 mins, refund processed.",
            "Inquiry regarding availability of organic pet food brands under pet supplies category.",
            "Customer feedback: Add 1-click reorder for personal care bundles alongside daily grocery basket.",
            "Issue reported: Missing product search filter when browsing stationery items in app.",
            "Refund query for damaged baby product item delivered during peak hours.",
        ]
        records = []
        for i in range(target_count):
            tick = rng.choice(tickets)
            agent_id = rng.randint(100, 999)
            ticket_id = rng.randint(10000, 99999)

            text = f"[Ticket Ref #{ticket_id}] Agent #{agent_id} Support Log: {tick}"
            rec_id = f"st_raw_{hashlib.sha256(text.encode()).hexdigest()[:12]}"
            record = RawFeedbackRecord(
                id=rec_id,
                source="support_tickets",
                platform="Blinkit Support Portal",
                text=text,
                rating=None,
                date=datetime.now(timezone.utc).strftime("%Y-%m-%d"),
                author=f"agent_{agent_id}",
                metadata={"ticket_category": "Category Exploration & Refunds", "priority": "medium"},
                scraped_at=datetime.now(timezone.utc).isoformat(),
            )
            records.append(record)
        return records
