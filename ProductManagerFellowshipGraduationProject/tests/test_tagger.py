"""
Phase 3 Unit Tests — Category & Topic Tagger

Validates multi-label tagging across categories, topics, and behaviour signals.
"""
from datetime import datetime, timezone
from src.app.models.domain import ProcessedFeedbackRecord
from src.app.processing.tagger import CategoryTopicTagger


class TestCategoryTopicTagger:
    """Test suite for CategoryTopicTagger."""

    def test_tagger_identifies_categories_and_topics(self):
        tagger = CategoryTopicTagger()
        record = ProcessedFeedbackRecord(
            id="proc_tag_01",
            source="play_store",
            text="Blinkit 10 min delivery is awesome for milk and bread, but why aren't electronics or pet supplies visible on homepage?",
            text_clean="blinkit 10 min delivery is awesome for milk and bread, but why aren't electronics or pet supplies visible on homepage?",
            rating=4.0,
            date="2026-07-28",
            sentiment="positive",
            sentiment_score=0.8,
            word_count=21,
            scraped_at=datetime.now(timezone.utc).isoformat(),
        )
        tagged = tagger.tag_batch([record])
        rec = tagged[0]

        assert len(rec.categories) > 0
        assert any(c in rec.categories for c in ["groceries", "electronics", "pet_supplies"])
        assert len(rec.topics) > 0
        assert any(t in rec.topics for t in ["discovery", "delivery"])

    def test_tagger_fallback_behavior_signals(self):
        tagger = CategoryTopicTagger()
        record = ProcessedFeedbackRecord(
            id="proc_tag_02",
            source="reddit",
            text="I wish Blinkit would add more printer paper and office supplies. I always switch to Amazon for these.",
            text_clean="i wish blinkit would add more printer paper and office supplies. i always switch to amazon for these.",
            rating=None,
            date="2026-07-28",
            sentiment="neutral",
            sentiment_score=0.5,
            word_count=19,
            scraped_at=datetime.now(timezone.utc).isoformat(),
        )
        tagged = tagger.tag_batch([record])
        rec = tagged[0]

        assert "stationery" in rec.categories
        assert any(b in rec.behaviour_signals for b in ["category_switch", "wishlist_request", "repeat_purchase"])
