from typing import Optional
from fastapi import APIRouter, HTTPException, Query, BackgroundTasks
from src.app.analysis.closed_loop_learner import ClosedLoopLearner
from src.app.api.data_loader import DataLoader
from src.app.api.schemas import (
    AgentContradictionResponse,
    AgentEmotionResponse,
    AgentHabitResponse,
    AgentJTBDResponse,
    AgentThemeResponse,
    AnalyticsSummaryResponse,
    ArchetypeListResponse,
    BehaviorGraphResponse,
    CategoryAnalyticsResponse,
    ExperimentListResponse,
    HealthResponse,
    HypothesisListResponse,
    InsightListResponse,
    OutcomeSubmissionRequest,
    OutcomeSubmissionResponse,
    PatternListResponse,
    PipelineRunRequest,
    PipelineStatusResponse,
    SentimentAnalyticsResponse,
    ThemeListResponse,
    ValidationReportResponse,
)
from src.app.models.domain import ExperimentOutcomeSubmission
from src.app.services.orchestrator import PipelineOrchestrator

router = APIRouter(prefix="/api/v1", tags=["Blinkit Discovery Engine"])


@router.get("/health", response_model=HealthResponse)
def get_health():
    """Health check endpoint."""
    return HealthResponse(status="healthy")


@router.get("/insights", response_model=InsightListResponse)
def get_insights(
    research_question: Optional[str] = Query(
        None, description="Filter insights by research question ID (e.g. Q1, Q2)"
    )
):
    """Returns list of all validated insights, optionally filtered by research question."""
    loader = DataLoader.get_instance()
    insights = loader.get_insights(research_question=research_question)
    return InsightListResponse(
        total=len(insights),
        insights=insights,
        meta={
            "filter_applied": research_question,
            "north_star_metric": "% MAC purchasing from >=1 new category/month",
        },
    )


@router.get("/insights/{insight_id}")
def get_insight_by_id(insight_id: str):
    """Returns a specific insight by ID with full evidence trail and quotes."""
    loader = DataLoader.get_instance()
    insight = loader.get_insight_by_id(insight_id)
    if not insight:
        raise HTTPException(
            status_code=404, detail=f"Insight with ID '{insight_id}' not found."
        )
    return insight


@router.get("/themes", response_model=ThemeListResponse)
def get_themes(
    source: Optional[str] = Query(
        None, description="Filter themes by source platform (e.g. play_store, app_store, reddit)"
    )
):
    """Returns all extracted themes per source and consolidated mega-themes."""
    loader = DataLoader.get_instance()
    data = loader.get_themes(source=source)
    return ThemeListResponse(
        total_sources=data["total_sources"],
        total_themes=data["total_themes"],
        themes_by_source=data["themes_by_source"],
        consolidated_themes=data["consolidated_themes"],
    )


@router.get("/patterns", response_model=PatternListResponse)
def get_patterns():
    """Returns emerging behavioral patterns detected across streaming feedback."""
    loader = DataLoader.get_instance()
    patterns = loader.get_patterns()
    return PatternListResponse(total=len(patterns), patterns=patterns)


@router.get("/hypotheses", response_model=HypothesisListResponse)
def get_hypotheses():
    """Returns testable PM growth hypotheses."""
    loader = DataLoader.get_instance()
    hypotheses = loader.get_hypotheses()
    return HypothesisListResponse(total=len(hypotheses), hypotheses=hypotheses)


@router.get("/experiments", response_model=ExperimentListResponse)
def get_experiments():
    """Returns recommended PM growth experiment specifications."""
    loader = DataLoader.get_instance()
    experiments = loader.get_experiments()
    return ExperimentListResponse(total=len(experiments), experiments=experiments)


@router.post("/experiments/{experiment_id}/outcome", response_model=OutcomeSubmissionResponse)
def submit_experiment_outcome(experiment_id: str, req: OutcomeSubmissionRequest):
    """Submits an experiment outcome (win/loss/neutral) and triggers closed-loop confidence learning."""
    learner = ClosedLoopLearner()
    submission = ExperimentOutcomeSubmission(
        experiment_id=experiment_id,
        result=req.result,
        observed_primary_metric_lift=req.observed_primary_metric_lift,
        statistical_significance=req.statistical_significance,
        key_learnings=req.key_learnings
    )
    outcome = learner.record_outcome(submission)
    DataLoader.get_instance().reload()
    return OutcomeSubmissionResponse(
        status="success",
        message=f"Experiment outcome logged for '{experiment_id}'. Closed-loop confidence adjusted by {outcome.confidence_score_delta}.",
        outcome=outcome.model_dump()
    )


@router.get("/analytics/summary", response_model=AnalyticsSummaryResponse)
def get_analytics_summary():
    """Returns aggregate data ingestion and review counts across platforms."""
    loader = DataLoader.get_instance()
    return loader.get_analytics_summary()


@router.get("/analytics/categories", response_model=CategoryAnalyticsResponse)
def get_category_analytics():
    """Returns product category mention frequency distribution."""
    loader = DataLoader.get_instance()
    return loader.get_category_analytics()


@router.get("/analytics/sentiment", response_model=SentimentAnalyticsResponse)
def get_sentiment_analytics():
    """Returns sentiment breakdown overall and per feedback source."""
    loader = DataLoader.get_instance()
    return loader.get_sentiment_analytics()


@router.get("/pipeline/status", response_model=PipelineStatusResponse)
def get_pipeline_status():
    """Returns pipeline execution status and data freshness health."""
    loader = DataLoader.get_instance()
    status_data = loader.get_pipeline_status()
    return PipelineStatusResponse(**status_data)


@router.post("/pipeline/run")
def trigger_pipeline_run(req: PipelineRunRequest = PipelineRunRequest()):
    """Triggers end-to-end or stage-specific pipeline execution (scrape, process, analyze, all)."""
    orchestrator = PipelineOrchestrator()
    results = orchestrator.run(stage=req.stage)
    DataLoader.get_instance().reload()
    return {
        "status": "success",
        "stage_executed": req.stage,
        "summary": results,
        "message": f"Pipeline stage '{req.stage}' completed and cache reloaded.",
    }


# ─── Phase 5 Endpoints ───

@router.get("/behavior-graph", response_model=BehaviorGraphResponse)
def get_behavior_graph():
    """Returns directed behavior graph nodes, edges, and density summary."""
    loader = DataLoader.get_instance()
    graph_data = loader.get_behavior_graph()
    return BehaviorGraphResponse(**graph_data)


@router.get("/archetypes", response_model=ArchetypeListResponse)
def get_archetypes():
    """Returns consumer segment archetypes matrix."""
    loader = DataLoader.get_instance()
    arch_data = loader.get_archetypes()
    return ArchetypeListResponse(**arch_data)


@router.get("/agents/theme", response_model=AgentThemeResponse)
def get_agent_theme():
    """Returns Agent 1 theme extractions."""
    loader = DataLoader.get_instance()
    data = loader.get_agent_theme()
    return AgentThemeResponse(**data)


@router.get("/agents/emotion", response_model=AgentEmotionResponse)
def get_agent_emotion():
    """Returns Agent 2 emotion profiles (Risk, Uncertainty, Cognitive Fatigue)."""
    loader = DataLoader.get_instance()
    data = loader.get_agent_emotion()
    return AgentEmotionResponse(**data)


@router.get("/agents/habit", response_model=AgentHabitResponse)
def get_agent_habit():
    """Returns Agent 3 Habit Loops (Trigger -> Action -> Reward)."""
    loader = DataLoader.get_instance()
    data = loader.get_agent_habit()
    return AgentHabitResponse(**data)


@router.get("/agents/jtbd", response_model=AgentJTBDResponse)
def get_agent_jtbd():
    """Returns Agent 4 Jobs-To-Be-Done items."""
    loader = DataLoader.get_instance()
    data = loader.get_agent_jtbd()
    return AgentJTBDResponse(**data)


@router.get("/agents/contradiction", response_model=AgentContradictionResponse)
def get_agent_contradiction():
    """Returns Agent 6 stated vs. actual behavior contradiction patterns."""
    loader = DataLoader.get_instance()
    data = loader.get_agent_contradiction()
    return AgentContradictionResponse(**data)


@router.get("/validation/report", response_model=ValidationReportResponse)
def get_validation_report():
    """Returns Multi-LLM 2/3 consensus pass rates, statistical confidence, and human audit stats."""
    loader = DataLoader.get_instance()
    report = loader.get_validation_report()
    return ValidationReportResponse(**report)
