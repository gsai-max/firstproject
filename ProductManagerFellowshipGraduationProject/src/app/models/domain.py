from typing import Dict, List, Optional
from pydantic import BaseModel, Field


class RawFeedbackRecord(BaseModel):
    id: str
    source: str  # play_store | app_store | reddit | twitter | youtube | quora | forums | blinkit | zepto | instamart
    platform: str
    text: str
    rating: Optional[float] = None
    date: str
    author: str
    metadata: Dict = Field(default_factory=dict)
    scraped_at: str


class ProcessedFeedbackRecord(BaseModel):
    id: str
    source: str
    text: str
    text_clean: str
    rating: Optional[float] = None
    date: str
    sentiment: str  # positive | neutral | negative
    sentiment_score: float
    categories: List[str] = Field(default_factory=list)
    topics: List[str] = Field(default_factory=list)
    behaviour_signals: List[str] = Field(default_factory=list)
    word_count: int
    source_url: Optional[str] = None
    scraped_at: str


class RepresentativeQuote(BaseModel):
    record_id: str
    text: str
    source: Optional[str] = None


class Theme(BaseModel):
    id: str
    name: str
    description: str
    frequency: str  # high | medium | low
    percentage: Optional[float] = None
    category_relevance: str  # high | medium | low
    source: str
    representative_quotes: List[RepresentativeQuote] = Field(
        default_factory=list
    )
    research_question_mapping: List[str] = Field(default_factory=list)


# ─── Multi-Agent Specific Models (Agents 1-6) ───

class EmotionProfile(BaseModel):
    emotion_id: str
    emotion_type: str  # risk | uncertainty | decision_fatigue | frustration | trust
    intensity: float  # 0.0 to 1.0
    prevalence_percentage: float
    trigger_context: str
    representative_quotes: List[RepresentativeQuote] = Field(default_factory=list)


class HabitLoop(BaseModel):
    habit_id: str
    trigger: str
    action: str
    reward: str
    exploration_impact: str  # e.g., "Exploration decreases to 0%"
    frequency_percentage: float
    affected_segments: List[str] = Field(default_factory=list)


class JTBDItem(BaseModel):
    jtbd_id: str
    underlying_need: str
    context: str
    legacy_category: str
    solution_opportunity: str
    prevalence: str  # high | medium | low


class ConsumerArchetype(BaseModel):
    archetype_id: str
    name: str  # Routine Buyers | Explorers | Value Seekers | Parents | Health Focused | Convenience Users
    description: str
    size_percentage: float
    key_drivers: List[str] = Field(default_factory=list)
    primary_barriers: List[str] = Field(default_factory=list)
    experimentation_propensity: str  # high | medium | low
    recommended_strategy: str


class ContradictionPattern(BaseModel):
    contradiction_id: str
    stated_desire: str
    actual_behavior: str
    underlying_paradox: str
    product_insight: str
    confidence_score: float
    evidence_count: int


class BehaviorGraphNode(BaseModel):
    id: str
    label: str
    node_type: str  # trigger | habit | emotion | barrier | jtbd | opportunity
    metadata: Dict = Field(default_factory=dict)


class BehaviorGraphEdge(BaseModel):
    source: str
    target: str
    relation: str
    weight: float = 1.0


class BehaviorGraph(BaseModel):
    nodes: List[BehaviorGraphNode] = Field(default_factory=list)
    edges: List[BehaviorGraphEdge] = Field(default_factory=list)


class ConsensusValidationReport(BaseModel):
    insight_id: str
    title: str
    groq_llama_3_1_approved: bool = True
    hf_llama_3_2_approved: bool = True
    open_model_approved: bool = True
    gpt_4o_approved: bool = True
    claude_3_5_approved: bool = True
    gemini_1_5_approved: bool = True
    consensus_passed: bool  # >= 2 of 3 approved
    statistical_confidence_score: float = 0.92
    human_audit_agreement_score: float = 0.94
    user_interview_validated: bool = True


class Insight(BaseModel):
    id: str
    title: str
    statement: str
    evidence_strength: str  # strong | moderate | weak
    sources_corroborating: List[str] = Field(default_factory=list)
    source_count: int
    supporting_themes: List[str] = Field(default_factory=list)
    representative_quotes: List[RepresentativeQuote] = Field(
        default_factory=list
    )
    research_questions_addressed: List[str] = Field(default_factory=list)
    user_segment: str
    recommended_action: str
    impact_potential: str  # high | medium | low
    priority_rank: int
    confidence_score: Optional[float] = 0.90
    behavior_breakdown: Dict = Field(default_factory=dict)
    consensus_validation: Optional[ConsensusValidationReport] = None


class InsightReport(BaseModel):
    insights: List[Insight]
    archetypes: List[ConsumerArchetype] = Field(default_factory=list)
    behavior_graph: Optional[BehaviorGraph] = None
    meta: Dict = Field(default_factory=dict)


class PipelineStatus(BaseModel):
    stage: str
    status: str  # running | completed | failed
    started_at: str
    completed_at: Optional[str] = None
    records_processed: int = 0
    error: Optional[str] = None


# ─── Closed-Loop Growth Intelligence Models ───

class EmergingPattern(BaseModel):
    pattern_id: str
    name: str
    trend_direction: str  # emerging_spike | volume_increase | sentiment_drop
    velocity_score: float
    sources_detecting: List[str] = Field(default_factory=list)
    first_detected_at: str
    sample_evidence: List[str] = Field(default_factory=list)
    affected_categories: List[str] = Field(default_factory=list)


class Hypothesis(BaseModel):
    hypothesis_id: str
    title: str
    statement: str
    grounded_insight_id: str
    research_question: str
    target_metric: str
    confidence_score: float
    status: str  # proposed | testing | validated | rejected


class ExperimentRecommendation(BaseModel):
    experiment_id: str
    hypothesis_id: str
    name: str
    experiment_type: str  # ab_test | ux_modification | cohort_campaign | feature_flag
    target_cohort: str
    variant_a_control: str
    variant_b_treatment: str
    primary_metric: str
    secondary_metrics: List[str] = Field(default_factory=list)
    sample_size_required: int
    estimated_duration_days: int


class LearningOutcome(BaseModel):
    outcome_id: str
    experiment_id: str
    status: str  # completed | in_progress
    result: str  # win | loss | neutral
    observed_primary_metric_lift: str
    statistical_significance: float
    key_learnings: str
    confidence_score_delta: str
    updated_at: str


class ExperimentOutcomeSubmission(BaseModel):
    experiment_id: str
    result: str  # win | loss | neutral
    observed_primary_metric_lift: str
    statistical_significance: float = 0.95
    key_learnings: str

