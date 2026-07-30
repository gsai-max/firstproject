import os
import json
import pytest
from src.app.analysis.validator import CrossSourceValidator
from src.app.models.domain import Insight, ProcessedFeedbackRecord, RepresentativeQuote


def test_validator_corroboration_and_coverage():
    validator = CrossSourceValidator()

    insights = [
        Insight(
            id="insight_01",
            title="Habitual Grocery Tunnel Vision",
            statement="Users buy groceries habitually.",
            evidence_strength="strong",
            sources_corroborating=["play_store", "app_store"],
            source_count=2,
            supporting_themes=["mega_theme_01"],
            representative_quotes=[
                RepresentativeQuote(record_id="rec_01", text="only buy milk", source="play_store")
            ],
            research_questions_addressed=["Q1", "Q2", "Q3", "Q4", "Q5", "Q6", "Q7", "Q8"],
            user_segment="Habitual Buyers",
            recommended_action="Cross-category add-ons",
            impact_potential="high",
            priority_rank=1,
        )
    ]

    records = [
        ProcessedFeedbackRecord(
            id="rec_01",
            source="play_store",
            text="only buy milk",
            text_clean="only buy milk",
            rating=4.0,
            date="2026-06-01",
            sentiment="neutral",
            sentiment_score=0.5,
            categories=["groceries"],
            topics=["habit"],
            behaviour_signals=[],
            word_count=8,
            scraped_at="2026-06-01T10:00:00Z",
        )
    ]

    report = validator.validate_insights(insights, records)
    assert report["total_insights_validated"] == 1
    assert report["passed_insights"] == 1
    assert report["research_questions_coverage"]["coverage_percentage"] == "100.0%"


def test_validator_report_persisted(tmp_path, monkeypatch):
    from src.app.config import settings
    monkeypatch.setattr(settings, "INSIGHTS_DIR", str(tmp_path))

    validator = CrossSourceValidator()
    insights = [
        Insight(
            id="insight_01",
            title="Single Source Insight",
            statement="Only supported by one source.",
            evidence_strength="strong",
            sources_corroborating=["play_store"],
            source_count=1,
            supporting_themes=[],
            representative_quotes=[],
            research_questions_addressed=["Q1"],
            user_segment="Single Source Users",
            recommended_action="Test",
            impact_potential="medium",
            priority_rank=1,
        )
    ]

    report = validator.validate_insights(insights, [])
    assert report["insights_with_warnings"] >= 1

    report_file = os.path.join(str(tmp_path), "validation_report.json")
    assert os.path.exists(report_file)
