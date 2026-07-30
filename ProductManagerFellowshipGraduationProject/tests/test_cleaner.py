"""
Phase 3 Unit Tests — Data Cleaner & Deduplicator

Validates text cleaning, normalization, HTML unescaping, length filtering,
exact hash deduplication, and near-duplicate Jaccard similarity detection.
"""
from datetime import datetime, timezone
from src.app.models.domain import ProcessedFeedbackRecord, RawFeedbackRecord
from src.app.processing.cleaner import DataCleaner
from src.app.processing.deduplicator import Deduplicator


class TestDataCleaner:
    """Test suite for DataCleaner."""

    def test_cleaner_normalizes_text(self):
        cleaner = DataCleaner()
        raw = RawFeedbackRecord(
            id="test_01",
            source="play_store",
            platform="Google Play Store",
            text="GREAT App! <p>Check out http://blinkit.com</p> &amp; buy fresh milk every single morning.",
            rating=5.0,
            date="2026-07-28",
            author="User1",
            scraped_at=datetime.now(timezone.utc).isoformat(),
        )
        proc = cleaner.clean(raw)
        assert proc is not None
        assert proc.text_clean == "great app! check out & buy fresh milk every single morning."
        assert "http" not in proc.text_clean
        assert "<p>" not in proc.text_clean
        assert proc.word_count >= 8

    def test_cleaner_filters_short_text(self):
        cleaner = DataCleaner()
        # 7 words review -> should be filtered out (< 8 words)
        raw = RawFeedbackRecord(
            id="test_02",
            source="play_store",
            platform="Google Play Store",
            text="Blinkit app is really good and fast",
            rating=5.0,
            date="2026-07-28",
            author="User2",
            scraped_at=datetime.now(timezone.utc).isoformat(),
        )
        proc = cleaner.clean(raw)
        assert proc is None

    def test_cleaner_filters_emojis(self):
        cleaner = DataCleaner()
        raw = RawFeedbackRecord(
            id="test_03",
            source="play_store",
            platform="Google Play Store",
            text="Good Discount and fast delivery easy to selected item 👌 super app experience",
            rating=5.0,
            date="2026-07-28",
            author="User3",
            scraped_at=datetime.now(timezone.utc).isoformat(),
        )
        proc = cleaner.clean(raw)
        assert proc is None

    def test_cleaner_filters_other_languages(self):
        cleaner = DataCleaner()
        raw = RawFeedbackRecord(
            id="test_04",
            source="play_store",
            platform="Google Play Store",
            text="घर बैठे वक्त पर सामान मिल जाता है डिलीवरी बॉय का व्यवहार भी बहुत अच्छा है",
            rating=5.0,
            date="2026-07-28",
            author="User4",
            scraped_at=datetime.now(timezone.utc).isoformat(),
        )
        proc = cleaner.clean(raw)
        assert proc is None

    def test_cleaner_retains_valid_english_reviews(self):
        cleaner = DataCleaner()
        raw = RawFeedbackRecord(
            id="test_05",
            source="play_store",
            platform="Google Play Store",
            text="Quick delivery as promised. I wish there was a clear New Categories banner on top.",
            rating=5.0,
            date="2026-07-28",
            author="User5",
            scraped_at=datetime.now(timezone.utc).isoformat(),
        )
        proc = cleaner.clean(raw)
        assert proc is not None
        assert proc.word_count >= 8



class TestDeduplicator:
    """Test suite for Deduplicator."""

    def test_deduplicator_removes_exact_duplicates(self):
        dedup = Deduplicator()
        rec1 = ProcessedFeedbackRecord(
            id="proc_01",
            source="play_store",
            text="Blinkit 10 min delivery is awesome for milk and groceries.",
            text_clean="blinkit 10 min delivery is awesome for milk and groceries.",
            rating=5.0,
            date="2026-07-28",
            sentiment="positive",
            sentiment_score=0.9,
            word_count=10,
            scraped_at=datetime.now(timezone.utc).isoformat(),
        )
        rec2 = ProcessedFeedbackRecord(
            id="proc_02",
            source="play_store",
            text="Blinkit 10 min delivery is awesome for milk and groceries.",
            text_clean="blinkit 10 min delivery is awesome for milk and groceries.",
            rating=5.0,
            date="2026-07-28",
            sentiment="positive",
            sentiment_score=0.9,
            word_count=10,
            scraped_at=datetime.now(timezone.utc).isoformat(),
        )
        unique = dedup.deduplicate([rec1, rec2])
        assert len(unique) == 1
        assert unique[0].id == "proc_01"

    def test_deduplicator_removes_near_duplicates(self):
        dedup = Deduplicator()
        rec1 = ProcessedFeedbackRecord(
            id="proc_01",
            source="play_store",
            text="Blinkit 10 min delivery is super fast for ordering fresh groceries every morning.",
            text_clean="blinkit 10 min delivery is super fast for ordering fresh groceries every morning.",
            rating=5.0,
            date="2026-07-28",
            sentiment="positive",
            sentiment_score=0.9,
            word_count=12,
            scraped_at=datetime.now(timezone.utc).isoformat(),
        )
        rec2 = ProcessedFeedbackRecord(
            id="proc_02",
            source="play_store",
            text="Blinkit 10 min delivery is super fast for ordering fresh groceries every morning!",
            text_clean="blinkit 10 min delivery is super fast for ordering fresh groceries every morning!",
            rating=5.0,
            date="2026-07-28",
            sentiment="positive",
            sentiment_score=0.9,
            word_count=12,
            scraped_at=datetime.now(timezone.utc).isoformat(),
        )
        unique = dedup.deduplicate([rec1, rec2])
        assert len(unique) == 1
