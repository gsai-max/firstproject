import pytest
from src.app.analysis.statistical_validator import StatisticalValidator


def test_statistical_validator():
    validator = StatisticalValidator()
    insights = [
        {
            "id": "insight_1",
            "title": "Low Diversity Insight",
            "sources_corroborating": ["play_store"],
            "evidence_strength": "weak",
            "representative_quotes": []
        },
        {
            "id": "insight_2",
            "title": "High Diversity Insight",
            "sources_corroborating": ["play_store", "reddit", "forums", "twitter"],
            "evidence_strength": "strong",
            "representative_quotes": [{"text": "q1"}, {"text": "q2"}]
        }
    ]

    scored = validator.validate_and_score(insights)
    assert len(scored) == 2
    # High diversity insight should rank #1
    assert scored[0]["id"] == "insight_2"
    assert scored[0]["priority_rank"] == 1
    assert scored[0]["confidence_score"] > scored[1]["confidence_score"]
