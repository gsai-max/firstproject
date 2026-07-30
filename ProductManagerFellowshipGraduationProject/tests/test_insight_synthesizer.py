import os
import json
import pytest
from src.app.analysis.insight_synthesizer import InsightSynthesizer
from src.app.models.domain import Insight, Theme, RepresentativeQuote


def test_insight_synthesizer_fallback():
    synthesizer = InsightSynthesizer(llm_client=None)

    themes_by_source = {
        "play_store": [
            Theme(
                id="theme_ps_001",
                name="Grocery Habit Focus",
                description="Users only buy groceries",
                frequency="high",
                category_relevance="high",
                source="play_store",
                representative_quotes=[
                    RepresentativeQuote(record_id="ps_01", text="only buy milk", source="play_store")
                ],
                research_question_mapping=["Q1", "Q4"],
            )
        ],
        "app_store": [
            Theme(
                id="theme_as_001",
                name="Hidden Categories UI",
                description="Category navigation hides pet care",
                frequency="high",
                category_relevance="high",
                source="app_store",
                representative_quotes=[
                    RepresentativeQuote(record_id="as_01", text="hidden pet food", source="app_store")
                ],
                research_question_mapping=["Q2", "Q3"],
            )
        ],
    }

    consolidated = synthesizer.consolidate_themes(themes_by_source)
    assert len(consolidated) >= 1

    insights = synthesizer.synthesize_insights(consolidated)
    assert len(insights) >= 8

    # Verify ranking and fields
    for idx, ins in enumerate(insights, 1):
        assert isinstance(ins, Insight)
        assert ins.priority_rank == idx
        assert len(ins.research_questions_addressed) > 0
        assert ins.impact_potential in ["high", "medium", "low"]


def test_insights_persisted(tmp_path, monkeypatch):
    from src.app.config import settings
    monkeypatch.setattr(settings, "INSIGHTS_DIR", str(tmp_path))

    synthesizer = InsightSynthesizer(llm_client=None)
    insights = synthesizer.synthesize_insights([])

    final_file = os.path.join(str(tmp_path), "insights_final.json")
    assert os.path.exists(final_file)

    with open(final_file, "r", encoding="utf-8") as f:
        data = json.load(f)
        assert len(data) >= 8
