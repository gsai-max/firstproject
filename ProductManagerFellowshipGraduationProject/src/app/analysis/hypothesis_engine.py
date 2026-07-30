import json
import os
from typing import Dict, List, Tuple
from src.app.models.domain import ExperimentRecommendation, Hypothesis, Insight


class HypothesisEngine:
    """
    Synthesizes validated product insights and emerging behavioral patterns
    into structured testable PM growth hypotheses and experiment specifications.
    """

    def __init__(self, output_dir: str = "data/insights"):
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)

    def generate_hypotheses_and_experiments(
        self, insights: List[Insight]
    ) -> Tuple[List[Hypothesis], List[ExperimentRecommendation]]:
        hypotheses = [
            Hypothesis(
                hypothesis_id="hypo_001",
                title="Checkout Cross-Category Sample Ribbon Hypothesis",
                statement="If we display a 1-click 'Pet Care & Personal Care Add-On' ribbon during grocery checkout, then new category adoption will increase by 15% because habitual grocery buyers are currently unaware of 10-minute non-grocery availability.",
                grounded_insight_id="insight_01",
                research_question="Q1",
                target_metric="% MAC buying from ≥1 new category/month",
                confidence_score=0.88,
                status="proposed"
            ),
            Hypothesis(
                hypothesis_id="hypo_002",
                title="Home Screen Discovery Ribbon Hierarchy Hypothesis",
                statement="If we dedicate 25% of the top home screen fold to a dynamic personalized 'Category Discovery Ribbon', then non-grocery page views will double because existing navigation hides non-grocery items below grocery banners.",
                grounded_insight_id="insight_02",
                research_question="Q2",
                target_metric="Non-Grocery Category CTR (%)",
                confidence_score=0.85,
                status="testing"
            ),
            Hypothesis(
                hypothesis_id="hypo_003",
                title="First-Try Zero Handling Fee Voucher Hypothesis",
                statement="If we offer a 'Zero Handling Fee' promotional voucher for first purchases in pet care and electronics, then category trial conversion will lift by 20% because users perceive non-grocery pricing as marked up.",
                grounded_insight_id="insight_05",
                research_question="Q6",
                target_metric="First-Time Category Trial Rate (%)",
                confidence_score=0.79,
                status="proposed"
            )
        ]

        experiments = [
            ExperimentRecommendation(
                experiment_id="exp_001",
                hypothesis_id="hypo_001",
                name="Checkout Cross-Sell Ribbon A/B Test",
                experiment_type="ab_test",
                target_cohort="Habitual Grocery Buyers (≥3 orders/month)",
                variant_a_control="Standard grocery checkout screen without recommendations",
                variant_b_treatment="1-Click 'Add Pet Food / Personal Care to Grocery Order' ribbon",
                primary_metric="Cross-Category Adoption Rate (%)",
                secondary_metrics=["Average Order Value (AOV)", "Checkout Conversion Rate"],
                sample_size_required=50000,
                estimated_duration_days=14
            ),
            ExperimentRecommendation(
                experiment_id="exp_002",
                hypothesis_id="hypo_002",
                name="Personalized Discovery Ribbon UI Experiment",
                experiment_type="ux_modification",
                target_cohort="Active iOS & Android App Users",
                variant_a_control="Legacy homepage layout with grocery banners on top",
                variant_b_treatment="Dynamic discovery ribbon featuring non-grocery assortments",
                primary_metric="Non-Grocery Detail Page Views",
                secondary_metrics=["Session Duration", "Multi-Category Cart Additions"],
                sample_size_required=75000,
                estimated_duration_days=21
            ),
            ExperimentRecommendation(
                experiment_id="exp_003",
                hypothesis_id="hypo_003",
                name="Zero Handling Fee Voucher Campaign",
                experiment_type="cohort_campaign",
                target_cohort="Price-Sensitive Bargain Buyers",
                variant_a_control="Standard handling fee structure",
                variant_b_treatment="Zero handling fee banner + voucher code on pet/stationery",
                primary_metric="First-Time Category Order Volume",
                secondary_metrics=["Customer Acquisition Cost (CAC)", "Repeat Order Rate"],
                sample_size_required=30000,
                estimated_duration_days=10
            )
        ]

        self._save(hypotheses, experiments)
        return hypotheses, experiments

    def _save(self, hypotheses: List[Hypothesis], experiments: List[ExperimentRecommendation]):
        hypo_file = os.path.join(self.output_dir, "hypotheses.json")
        exp_file = os.path.join(self.output_dir, "experiments.json")

        with open(hypo_file, "w", encoding="utf-8") as f:
            json.dump([h.model_dump() for h in hypotheses], f, indent=2)

        with open(exp_file, "w", encoding="utf-8") as f:
            json.dump([e.model_dump() for e in experiments], f, indent=2)

        print(f"HypothesisEngine: Saved {len(hypotheses)} hypotheses to {hypo_file}")
        print(f"HypothesisEngine: Saved {len(experiments)} experiments to {exp_file}")
