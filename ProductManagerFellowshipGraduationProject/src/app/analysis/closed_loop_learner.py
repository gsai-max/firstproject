import json
import os
from datetime import datetime, timezone
from typing import Dict, List, Optional
from src.app.models.domain import ExperimentOutcomeSubmission, LearningOutcome


class ClosedLoopLearner:
    """
    Ingests completed experiment outcome results (win/loss/neutral),
    updates hypothesis confidence scores, and logs closed-loop learnings.
    """

    def __init__(self, output_dir: str = "data/insights"):
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)
        self.outcomes_file = os.path.join(self.output_dir, "learning_outcomes.json")
        self.hypotheses_file = os.path.join(self.output_dir, "hypotheses.json")

    def get_outcomes(self) -> List[LearningOutcome]:
        if not os.path.exists(self.outcomes_file):
            default_outcomes = [
                LearningOutcome(
                    outcome_id="out_001",
                    experiment_id="exp_001",
                    status="completed",
                    result="win",
                    observed_primary_metric_lift="+18.2%",
                    statistical_significance=0.99,
                    key_learnings="Checkout cross-sell prompts successfully convert grocery buyers to pet food when delivery speed is emphasized.",
                    confidence_score_delta="+0.08",
                    updated_at=datetime.now(timezone.utc).isoformat()
                )
            ]
            self._save_outcomes(default_outcomes)
            return default_outcomes

        with open(self.outcomes_file, "r", encoding="utf-8") as f:
            data = json.load(f)
            return [LearningOutcome(**item) for item in data]

    def record_outcome(self, submission: ExperimentOutcomeSubmission) -> LearningOutcome:
        outcomes = self.get_outcomes()
        now_str = datetime.now(timezone.utc).isoformat()

        delta = "+0.05" if submission.result == "win" else ("-0.05" if submission.result == "loss" else "+0.00")

        new_outcome = LearningOutcome(
            outcome_id=f"out_{len(outcomes) + 1:03d}",
            experiment_id=submission.experiment_id,
            status="completed",
            result=submission.result,
            observed_primary_metric_lift=submission.observed_primary_metric_lift,
            statistical_significance=submission.statistical_significance,
            key_learnings=submission.key_learnings,
            confidence_score_delta=delta,
            updated_at=now_str
        )

        outcomes.append(new_outcome)
        self._save_outcomes(outcomes)
        self._update_hypothesis_confidence(submission.experiment_id, submission.result)
        return new_outcome

    def _save_outcomes(self, outcomes: List[LearningOutcome]):
        with open(self.outcomes_file, "w", encoding="utf-8") as f:
            json.dump([o.model_dump() for o in outcomes], f, indent=2)

    def _update_hypothesis_confidence(self, experiment_id: str, result: str):
        if not os.path.exists(self.hypotheses_file):
            return

        try:
            with open(self.hypotheses_file, "r", encoding="utf-8") as f:
                hypotheses = json.load(f)

            for h in hypotheses:
                # Update confidence score based on closed-loop experiment result
                if result == "win":
                    h["confidence_score"] = min(1.0, round(h.get("confidence_score", 0.8) + 0.05, 2))
                    h["status"] = "validated"
                elif result == "loss":
                    h["confidence_score"] = max(0.0, round(h.get("confidence_score", 0.8) - 0.05, 2))
                    h["status"] = "rejected"

            with open(self.hypotheses_file, "w", encoding="utf-8") as f:
                json.dump(hypotheses, f, indent=2)
        except Exception as e:
            print(f"ClosedLoopLearner: Warning updating hypothesis confidence: {e}")
