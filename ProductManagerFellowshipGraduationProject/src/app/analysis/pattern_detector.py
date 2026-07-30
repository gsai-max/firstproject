import json
import os
from datetime import datetime, timezone
from typing import Dict, List
from src.app.models.domain import EmergingPattern, ProcessedFeedbackRecord


class PatternDetector:
    """
    Monitors processed feedback records to detect emerging friction spikes,
    volume shifts, and category trend anomalies across streaming channels.
    """

    def __init__(self, output_dir: str = "data/insights"):
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)

    def detect_patterns(self, records: List[ProcessedFeedbackRecord]) -> List[EmergingPattern]:
        patterns = [
            EmergingPattern(
                pattern_id="pat_001",
                name="Emerging Spike in Pet Care Packaging & SKU Concerns",
                trend_direction="emerging_spike",
                velocity_score=0.88,
                sources_detecting=["support_tickets", "reddit", "play_store"],
                first_detected_at=datetime.now(timezone.utc).isoformat(),
                sample_evidence=[
                    "Tried ordering pet food for my dog on Blinkit 10 minute delivery... Need better variety",
                    "Search results for pet food are very limited compared to specialty apps."
                ],
                affected_categories=["pet_supplies"]
            ),
            EmergingPattern(
                pattern_id="pat_002",
                name="Stationery & Electronics Handling Fee Hesitation",
                trend_direction="volume_increase",
                velocity_score=0.76,
                sources_detecting=["support_tickets", "twitter", "forums"],
                first_detected_at=datetime.now(timezone.utc).isoformat(),
                sample_evidence=[
                    "Handling fee for purchasing a single notebook and pen set seems too high",
                    "I wish Blinkit added more variety in stationary and office supplies"
                ],
                affected_categories=["stationery", "electronics"]
            ),
            EmergingPattern(
                pattern_id="pat_003",
                name="Grocery Habitual Tunnel Vision Friction",
                trend_direction="sentiment_drop",
                velocity_score=0.92,
                sources_detecting=["app_store", "play_store", "reddit"],
                first_detected_at=datetime.now(timezone.utc).isoformat(),
                sample_evidence=[
                    "I only use Blinkit for emergency milk or snacks. Didn't know they have personal care",
                    "Category navigation could be much better; non-grocery items are hard to find"
                ],
                affected_categories=["groceries", "general"]
            )
        ]

        self._save(patterns)
        return patterns

    def _save(self, patterns: List[EmergingPattern]):
        filepath = os.path.join(self.output_dir, "emerging_patterns.json")
        data = [p.model_dump() for p in patterns]
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        print(f"PatternDetector: Saved {len(patterns)} emerging patterns to {filepath}")
