import pytest
from fastapi.testclient import TestClient
from src.app.api_server import app

client = TestClient(app)


def test_health_endpoint():
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "timestamp" in data
    assert data["version"] == "1.0.0"


def test_insights_list_endpoint():
    response = client.get("/api/v1/insights")
    assert response.status_code == 200
    data = response.json()
    assert "total" in data
    assert "insights" in data
    assert isinstance(data["insights"], list)
    assert data["total"] == len(data["insights"])


def test_insights_rq_filter():
    response = client.get("/api/v1/insights?research_question=Q1")
    assert response.status_code == 200
    data = response.json()
    assert data["meta"]["filter_applied"] == "Q1"
    for ins in data["insights"]:
        assert "Q1" in ins["research_questions_addressed"]


def test_insight_by_id_endpoint():
    # First get list
    list_res = client.get("/api/v1/insights")
    insights = list_res.json().get("insights", [])
    if insights:
        ins_id = insights[0]["id"]
        res = client.get(f"/api/v1/insights/{ins_id}")
        assert res.status_code == 200
        assert res.json()["id"] == ins_id


def test_insight_not_found():
    response = client.get("/api/v1/insights/non_existent_id_9999")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


def test_themes_endpoint():
    response = client.get("/api/v1/themes")
    assert response.status_code == 200
    data = response.json()
    assert "total_sources" in data
    assert "total_themes" in data
    assert "themes_by_source" in data
    assert "consolidated_themes" in data


def test_themes_source_filter():
    response = client.get("/api/v1/themes?source=play_store")
    assert response.status_code == 200
    data = response.json()
    assert "play_store" in data["themes_by_source"]


def test_analytics_summary_endpoint():
    response = client.get("/api/v1/analytics/summary")
    assert response.status_code == 200
    data = response.json()
    assert "total_raw_reviews" in data
    assert "total_normalized_reviews" in data
    assert "source_breakdown" in data


def test_analytics_categories_endpoint():
    response = client.get("/api/v1/analytics/categories")
    assert response.status_code == 200
    data = response.json()
    assert "categories_distribution" in data
    assert "total_categories_tagged" in data


def test_analytics_sentiment_endpoint():
    response = client.get("/api/v1/analytics/sentiment")
    assert response.status_code == 200
    data = response.json()
    assert "overall_sentiment" in data
    assert "source_sentiment_breakdown" in data


def test_pipeline_status_endpoint():
    response = client.get("/api/v1/pipeline/status")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] in ["completed", "running", "failed"]
    assert "records_processed" in data


# ─── Phase 5 Endpoint Tests ───

def test_behavior_graph_endpoint():
    response = client.get("/api/v1/behavior-graph")
    assert response.status_code == 200
    data = response.json()
    assert "summary" in data
    assert "nodes" in data
    assert "edges" in data
    assert isinstance(data["nodes"], list)
    assert isinstance(data["edges"], list)


def test_archetypes_endpoint():
    response = client.get("/api/v1/archetypes")
    assert response.status_code == 200
    data = response.json()
    assert data["agent"] == "SegmentAgent"
    assert "consumer_archetypes" in data
    assert isinstance(data["consumer_archetypes"], list)


def test_agent_theme_endpoint():
    response = client.get("/api/v1/agents/theme")
    assert response.status_code == 200
    data = response.json()
    assert data["agent"] == "ThemeAgent"
    assert "themes" in data
    assert isinstance(data["themes"], list)


def test_agent_emotion_endpoint():
    response = client.get("/api/v1/agents/emotion")
    assert response.status_code == 200
    data = response.json()
    assert data["agent"] == "EmotionAgent"
    assert "emotion_profiles" in data
    assert isinstance(data["emotion_profiles"], list)


def test_agent_habit_endpoint():
    response = client.get("/api/v1/agents/habit")
    assert response.status_code == 200
    data = response.json()
    assert data["agent"] == "HabitAgent"
    assert "habit_loops" in data
    assert isinstance(data["habit_loops"], list)


def test_agent_jtbd_endpoint():
    response = client.get("/api/v1/agents/jtbd")
    assert response.status_code == 200
    data = response.json()
    assert data["agent"] == "JTBDAgent"
    assert "jtbd_items" in data
    assert isinstance(data["jtbd_items"], list)


def test_agent_contradiction_endpoint():
    response = client.get("/api/v1/agents/contradiction")
    assert response.status_code == 200
    data = response.json()
    assert data["agent"] == "ContradictionAgent"
    assert "contradictions" in data
    assert isinstance(data["contradictions"], list)


def test_validation_report_endpoint():
    response = client.get("/api/v1/validation/report")
    assert response.status_code == 200
    data = response.json()
    assert "consensus_report" in data
    assert "validation_report" in data
    assert "human_audit_report" in data
