import pytest
from src.app.agents import (
    ThemeAgent, EmotionAgent, HabitAgent, JTBDAgent, SegmentAgent, ContradictionAgent
)


@pytest.fixture
def sample_records():
    return [
        {
            "id": "rec_001",
            "text": "I buy milk every morning in 10 mins. Never tried personal care because return process is unclear.",
            "text_clean": "I buy milk every morning in 10 mins. Never tried personal care because return process is unclear.",
            "rating": 4.0,
            "categories": ["groceries"],
            "topics": ["habit", "trust"]
        },
        {
            "id": "rec_002",
            "text": "Wish Blinkit had better electronics accessories recommendations during checkout.",
            "text_clean": "Wish Blinkit had better electronics accessories recommendations during checkout.",
            "rating": 3.0,
            "categories": ["electronics"],
            "topics": ["discovery"]
        }
    ]


def test_theme_agent(sample_records):
    agent = ThemeAgent()
    res = agent.process(sample_records)
    assert res["agent"] == "ThemeAgent"
    assert "themes" in res
    assert res["theme_count"] > 0


def test_emotion_agent(sample_records):
    agent = EmotionAgent()
    res = agent.process(sample_records)
    assert res["agent"] == "EmotionAgent"
    assert "emotion_profiles" in res
    assert res["emotion_count"] > 0


def test_habit_agent(sample_records):
    agent = HabitAgent()
    res = agent.process(sample_records)
    assert res["agent"] == "HabitAgent"
    assert "habit_loops" in res
    assert res["habit_loop_count"] > 0


def test_jtbd_agent(sample_records):
    agent = JTBDAgent()
    res = agent.process(sample_records)
    assert res["agent"] == "JTBDAgent"
    assert "jtbd_items" in res
    assert res["jtbd_count"] > 0


def test_segment_agent(sample_records):
    agent = SegmentAgent()
    res = agent.process(sample_records)
    assert res["agent"] == "SegmentAgent"
    assert "consumer_archetypes" in res
    assert res["archetype_count"] > 0


def test_contradiction_agent(sample_records):
    agent = ContradictionAgent()
    res = agent.process(sample_records)
    assert res["agent"] == "ContradictionAgent"
    assert "contradictions" in res
    assert res["contradiction_count"] > 0
