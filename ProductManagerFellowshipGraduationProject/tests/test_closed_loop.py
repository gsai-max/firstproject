import pytest
from fastapi.testclient import TestClient

from src.app.analysis.closed_loop_learner import ClosedLoopLearner
from src.app.analysis.hypothesis_engine import HypothesisEngine
from src.app.analysis.pattern_detector import PatternDetector
from src.app.api_server import app
from src.app.models.domain import ExperimentOutcomeSubmission, Insight
from src.app.scrapers.support_tickets import SupportTicketCrawler

client = TestClient(app)


def test_support_ticket_crawler():
    crawler = SupportTicketCrawler()
    tickets = crawler.fetch_tickets(count=5)
    assert len(tickets) == 5
    assert tickets[0].source == "support_tickets"


def test_pattern_detector():
    detector = PatternDetector()
    patterns = detector.detect_patterns([])
    assert len(patterns) > 0
    assert patterns[0].trend_direction in ["emerging_spike", "volume_increase", "sentiment_drop"]


def test_hypothesis_engine():
    engine = HypothesisEngine()
    dummy_insight = Insight(
        id="insight_01",
        title="Test Insight",
        statement="Test Statement",
        evidence_strength="strong",
        sources_corroborating=["play_store", "support_tickets"],
        source_count=2,
        supporting_themes=["theme_001"],
        representative_quotes=[],
        research_questions_addressed=["Q1"],
        user_segment="All Users",
        recommended_action="Test Action",
        impact_potential="high",
        priority_rank=1
    )
    hypotheses, experiments = engine.generate_hypotheses_and_experiments([dummy_insight])
    assert len(hypotheses) > 0
    assert len(experiments) > 0
    assert hypotheses[0].confidence_score > 0


def test_closed_loop_learner():
    learner = ClosedLoopLearner()
    submission = ExperimentOutcomeSubmission(
        experiment_id="exp_001",
        result="win",
        observed_primary_metric_lift="+15.5%",
        statistical_significance=0.99,
        key_learnings="Unit test closed loop learning"
    )
    outcome = learner.record_outcome(submission)
    assert outcome.result == "win"
    assert outcome.confidence_score_delta == "+0.05"


def test_closed_loop_api_endpoints():
    r_pat = client.get("/api/v1/patterns")
    assert r_pat.status_code == 200
    assert "patterns" in r_pat.json()

    r_hypo = client.get("/api/v1/hypotheses")
    assert r_hypo.status_code == 200
    assert "hypotheses" in r_hypo.json()

    r_exp = client.get("/api/v1/experiments")
    assert r_exp.status_code == 200
    assert "experiments" in r_exp.json()

    r_out = client.post(
        "/api/v1/experiments/exp_001/outcome",
        json={
            "experiment_id": "exp_001",
            "result": "win",
            "observed_primary_metric_lift": "+12.0%",
            "key_learnings": "API outcome submission test"
        }
    )
    assert r_out.status_code == 200
    assert r_out.json()["status"] == "success"
