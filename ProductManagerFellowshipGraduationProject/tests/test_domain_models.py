"""
Phase 1 Unit Tests — Domain Models & Configuration Loader

Validates that all Pydantic domain models and the configuration loader
instantiate and serialize/deserialize properly.
"""
from datetime import datetime, timezone
from src.app.config import settings, Settings
from src.app.models.domain import (
    RawFeedbackRecord,
    ProcessedFeedbackRecord,
    RepresentativeQuote,
    Theme,
    Insight,
    InsightReport,
    PipelineStatus,
)


class TestConfigLoader:
    """Test configuration loader defaults and env loading."""

    def test_settings_instantiation(self):
        s = Settings()
        assert s.LLM_PROVIDER == "groq"
        assert s.RAW_DATA_DIR == "data/raw"
        assert s.PROCESSED_DATA_DIR == "data/processed"
        assert s.INSIGHTS_DIR == "data/insights"
        assert s.MAX_REVIEWS_PLAY_STORE == 30000
        assert s.MAX_REVIEWS_APP_STORE == 15000
        assert s.SENTIMENT_BATCH_SIZE == 50
        assert s.THEME_BATCH_SIZE == 100
        assert s.LLM_TIMEOUT_SECONDS == 10.0


    def test_global_settings_imported(self):
        assert settings is not None
        assert hasattr(settings, "LLM_MODEL")


class TestDomainModels:
    """Test instantiation and field assertions for all domain models."""

    def test_raw_feedback_record(self):
        record = RawFeedbackRecord(
            id="ps_12345",
            source="play_store",
            platform="Google Play Store",
            text="Blinkit is great for groceries but missing electronics.",
            rating=4.0,
            date="2026-07-28",
            author="JohnDoe",
            metadata={"version": "12.4.1"},
            scraped_at=datetime.now(timezone.utc).isoformat(),
        )
        assert record.id == "ps_12345"
        assert record.source == "play_store"
        assert record.rating == 4.0
        assert record.metadata["version"] == "12.4.1"

    def test_processed_feedback_record(self):
        record = ProcessedFeedbackRecord(
            id="proc_12345",
            source="play_store",
            text="Blinkit is great for groceries but missing electronics.",
            text_clean="blinkit is great for groceries but missing electronics.",
            rating=4.0,
            date="2026-07-28",
            sentiment="neutral",
            sentiment_score=0.5,
            categories=["groceries", "electronics"],
            topics=["discovery", "missing_product"],
            behaviour_signals=["category_exploration"],
            word_count=9,
            source_url="https://play.google.com/store/apps/details?id=com.grofers.customerapp",
            scraped_at=datetime.now(timezone.utc).isoformat(),
        )
        assert record.sentiment == "neutral"
        assert "groceries" in record.categories
        assert record.word_count == 9

    def test_representative_quote(self):
        quote = RepresentativeQuote(
            record_id="proc_12345",
            text="missing electronics category",
            source="play_store",
        )
        assert quote.record_id == "proc_12345"
        assert quote.source == "play_store"

    def test_theme(self):
        quote = RepresentativeQuote(
            record_id="proc_12345",
            text="missing electronics category",
            source="play_store",
        )
        theme = Theme(
            id="theme_01",
            name="Electronics Category Gap",
            description="Users report frustration over inability to find basic electronics on Blinkit.",
            frequency="high",
            category_relevance="high",
            source="play_store",
            representative_quotes=[quote],
            research_question_mapping=["Q1", "Q3"],
        )
        assert theme.id == "theme_01"
        assert theme.frequency == "high"
        assert len(theme.representative_quotes) == 1

    def test_insight(self):
        quote = RepresentativeQuote(
            record_id="proc_12345",
            text="missing electronics category",
            source="play_store",
        )
        insight = Insight(
            id="ins_01",
            title="Expand Non-Grocery Inventory",
            statement="Users view Blinkit primarily as a grocery app due to limited electronics assortment.",
            evidence_strength="strong",
            sources_corroborating=["play_store", "reddit"],
            source_count=2,
            supporting_themes=["theme_01"],
            representative_quotes=[quote],
            research_questions_addressed=["Q1", "Q3"],
            user_segment="Tech-savvy urban shoppers",
            recommended_action="Introduce curated electronics carousel on homepage.",
            impact_potential="high",
            priority_rank=1,
        )
        assert insight.priority_rank == 1
        assert insight.evidence_strength == "strong"
        assert insight.source_count == 2

    def test_insight_report(self):
        report = InsightReport(insights=[], meta={"total_insights": 0})
        assert report.meta["total_insights"] == 0
        assert len(report.insights) == 0

    def test_pipeline_status(self):
        status = PipelineStatus(
            stage="scrape",
            status="completed",
            started_at="2026-07-28T12:00:00Z",
            completed_at="2026-07-28T12:05:00Z",
            records_processed=5000,
        )
        assert status.status == "completed"
        assert status.records_processed == 5000
