from datetime import datetime, timezone
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    status: str = "healthy"
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    version: str = "1.0.0"


class InsightListResponse(BaseModel):
    total: int
    insights: List[Dict[str, Any]]
    meta: Dict[str, Any] = Field(default_factory=dict)


class ThemeListResponse(BaseModel):
    total_sources: int
    total_themes: int
    themes_by_source: Dict[str, List[Dict[str, Any]]]
    consolidated_themes: List[Dict[str, Any]]


class AnalyticsSummaryResponse(BaseModel):
    total_raw_reviews: int
    total_normalized_reviews: int
    source_breakdown: Dict[str, int]
    last_updated: str


class CategoryAnalyticsResponse(BaseModel):
    categories_distribution: Dict[str, int]
    total_categories_tagged: int


class SentimentAnalyticsResponse(BaseModel):
    overall_sentiment: Dict[str, int]
    source_sentiment_breakdown: Dict[str, Dict[str, int]]


class PipelineStatusResponse(BaseModel):
    status: str
    stage: str
    last_run_timestamp: Optional[str] = None
    records_processed: int = 0
    details: Dict[str, Any] = Field(default_factory=dict)


class PipelineRunRequest(BaseModel):
    stage: str = Field(default="all", description="Pipeline stage to run: scrape, process, analyze, all")


# ─── Closed-Loop API DTOs ───

class PatternListResponse(BaseModel):
    total: int
    patterns: List[Dict[str, Any]]


class HypothesisListResponse(BaseModel):
    total: int
    hypotheses: List[Dict[str, Any]]


class ExperimentListResponse(BaseModel):
    total: int
    experiments: List[Dict[str, Any]]


class OutcomeSubmissionRequest(BaseModel):
    experiment_id: str
    result: str = Field(..., description="Experiment outcome result: win, loss, neutral")
    observed_primary_metric_lift: str = Field(..., description="Observed primary metric lift e.g. '+18.2%'")
    statistical_significance: float = Field(default=0.95, description="Statistical significance (p-value / confidence)")
    key_learnings: str = Field(..., description="PM key learnings from experiment")


class OutcomeSubmissionResponse(BaseModel):
    status: str = "success"
    message: str
    outcome: Dict[str, Any]


# ─── Phase 5 API DTOs ───

class BehaviorGraphResponse(BaseModel):
    summary: Dict[str, Any] = Field(default_factory=dict)
    nodes: List[Dict[str, Any]] = Field(default_factory=list)
    edges: List[Dict[str, Any]] = Field(default_factory=list)


class ArchetypeListResponse(BaseModel):
    agent: str = "SegmentAgent"
    archetype_count: int = 0
    consumer_archetypes: List[Dict[str, Any]] = Field(default_factory=list)


class AgentThemeResponse(BaseModel):
    agent: str = "ThemeAgent"
    theme_count: int = 0
    themes: List[Dict[str, Any]] = Field(default_factory=list)


class AgentEmotionResponse(BaseModel):
    agent: str = "EmotionAgent"
    emotion_count: int = 0
    emotion_profiles: List[Dict[str, Any]] = Field(default_factory=list)


class AgentHabitResponse(BaseModel):
    agent: str = "HabitAgent"
    habit_loop_count: int = 0
    habit_loops: List[Dict[str, Any]] = Field(default_factory=list)


class AgentJTBDResponse(BaseModel):
    agent: str = "JTBDAgent"
    jtbd_count: int = 0
    jtbd_items: List[Dict[str, Any]] = Field(default_factory=list)


class AgentContradictionResponse(BaseModel):
    agent: str = "ContradictionAgent"
    contradiction_count: int = 0
    contradictions: List[Dict[str, Any]] = Field(default_factory=list)


class ValidationReportResponse(BaseModel):
    consensus_report: Dict[str, Any] = Field(default_factory=dict)
    validation_report: Dict[str, Any] = Field(default_factory=dict)
    human_audit_report: Dict[str, Any] = Field(default_factory=dict)
