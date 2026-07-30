import os
import json
import pytest
from src.app.analysis.theme_extractor import ThemeExtractor
from src.app.models.domain import ProcessedFeedbackRecord, Theme


def test_theme_extractor_fallback():
    extractor = ThemeExtractor(llm_client=None)

    sample_records = [
        ProcessedFeedbackRecord(
            id="ps_test_01",
            source="play_store",
            text="I only buy milk and bread on Blinkit. Didn't know electronics exist.",
            text_clean="only buy milk and bread on blinkit didnt know electronics exist",
            rating=4.0,
            date="2026-06-01",
            sentiment="neutral",
            sentiment_score=0.5,
            categories=["groceries", "electronics"],
            topics=["habit", "discovery"],
            behaviour_signals=["repeat_purchase"],
            word_count=12,
            scraped_at="2026-06-01T10:00:00Z",
        ),
        ProcessedFeedbackRecord(
            id="ps_test_02",
            source="play_store",
            text="Category navigation could be much better; pet supplies are hidden.",
            text_clean="category navigation could be much better pet supplies are hidden",
            rating=3.0,
            date="2026-06-01",
            sentiment="negative",
            sentiment_score=0.3,
            categories=["pet_supplies"],
            topics=["ui_navigation", "discovery"],
            behaviour_signals=[],
            word_count=10,
            scraped_at="2026-06-01T10:00:00Z",
        ),
    ]

    themes = extractor.extract_themes_by_source(sample_records)
    assert "play_store" in themes
    assert len(themes["play_store"]) >= 1

    t = themes["play_store"][0]
    assert isinstance(t, Theme)
    assert t.source == "play_store"
    assert len(t.research_question_mapping) > 0
    assert len(t.representative_quotes) > 0


def test_themes_persisted(tmp_path, monkeypatch):
    from src.app.config import settings
    monkeypatch.setattr(settings, "INSIGHTS_DIR", str(tmp_path))

    extractor = ThemeExtractor(llm_client=None)
    sample_records = [
        ProcessedFeedbackRecord(
            id="as_test_01",
            source="app_store",
            text="App crashes on checkout for beauty items.",
            text_clean="app crashes on checkout for beauty items",
            rating=2.0,
            date="2026-06-01",
            sentiment="negative",
            sentiment_score=0.2,
            categories=["beauty"],
            topics=["ui_navigation"],
            behaviour_signals=[],
            word_count=8,
            scraped_at="2026-06-01T10:00:00Z",
        )
    ]
    extractor.extract_themes_by_source(sample_records)

    output_file = os.path.join(str(tmp_path), "themes_by_source.json")
    assert os.path.exists(output_file)

    with open(output_file, "r", encoding="utf-8") as f:
        data = json.load(f)
        assert "app_store" in data
