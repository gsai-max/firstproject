import pytest
from src.app.analysis.multi_llm_consensus import MultiLLMConsensusEngine


@pytest.fixture
def sample_insights():
    return [
        {
            "id": "insight_1",
            "title": "Risk Perception Blocks Personal Care",
            "statement": "Users stick to groceries due to fear of unreturnable personal care items.",
            "evidence_strength": "strong",
            "sources_corroborating": ["play_store", "reddit"],
            "source_count": 2,
            "representative_quotes": [{"text": "Sample quote", "source": "reddit"}]
        },
        {
            "id": "insight_2",
            "title": "Habit Loop Checkout Lock-In",
            "statement": "Users repeat grocery orders in 1-click without category browsing.",
            "evidence_strength": "moderate",
            "sources_corroborating": ["app_store", "twitter"],
            "source_count": 2,
            "representative_quotes": [{"text": "Sample quote 2", "source": "twitter"}]
        }
    ]


def test_multi_llm_consensus_engine(sample_insights):
    engine = MultiLLMConsensusEngine()
    res = engine.evaluate_insights(sample_insights)
    assert res["total_insights_evaluated"] == 2
    assert res["approved_insights_count"] > 0
    assert "evaluations" in res
    assert res["evaluations"][0]["consensus_passed"] is True
    assert res["evaluations"][0]["total_votes"] >= 2
