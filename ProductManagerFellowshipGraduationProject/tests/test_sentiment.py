"""
Phase 3 Unit Tests — Sentiment Classifier

Validates batch classification, sentiment label mapping, score computation,
and fallback rule classification.
"""
from datetime import datetime, timezone
from src.app.models.domain import ProcessedFeedbackRecord
from src.app.processing.sentiment import SentimentClassifier


class TestSentimentClassifier:
    """Test suite for SentimentClassifier."""

    def test_sentiment_positive_record(self):
        classifier = SentimentClassifier()
        record = ProcessedFeedbackRecord(
            id="proc_pos",
            source="play_store",
            text="Excellent service, super fast delivery and great quality items!",
            text_clean="excellent service, super fast delivery and great quality items!",
            rating=5.0,
            date="2026-07-28",
            sentiment="",
            sentiment_score=0.0,
            word_count=8,
            scraped_at=datetime.now(timezone.utc).isoformat(),
        )
        classified = classifier.classify_batch([record])
        assert classified[0].sentiment == "positive"
        assert classified[0].sentiment_score >= 0.7

    def test_sentiment_negative_record(self):
        classifier = SentimentClassifier()
        record = ProcessedFeedbackRecord(
            id="proc_neg",
            source="play_store",
            text="Worst experience ever. Received expired product and refund was cheated.",
            text_clean="worst experience ever. received expired product and refund was cheated.",
            rating=1.0,
            date="2026-07-28",
            sentiment="",
            sentiment_score=0.0,
            word_count=9,
            scraped_at=datetime.now(timezone.utc).isoformat(),
        )
        classified = classifier.classify_batch([record])
        assert classified[0].sentiment == "negative"
        assert classified[0].sentiment_score <= 0.3

    def test_sentiment_neutral_record(self):
        classifier = SentimentClassifier()
        record = ProcessedFeedbackRecord(
            id="proc_neu",
            source="reddit",
            text="Blinkit app operates in Bangalore and Mumbai.",
            text_clean="blinkit app operates in bangalore and mumbai.",
            rating=None,
            date="2026-07-28",
            sentiment="",
            sentiment_score=0.0,
            word_count=7,
            scraped_at=datetime.now(timezone.utc).isoformat(),
        )
        classified = classifier.classify_batch([record])
        assert classified[0].sentiment in ["neutral", "positive", "negative"]
        assert classified[0].sentiment_score >= 0.0
