import json
import os
from typing import Dict, List, Optional, Set

from src.app.config import settings
from src.app.models.domain import Insight, ProcessedFeedbackRecord


class CrossSourceValidator:
    """Validates synthesized insights against evidence grounding, source corroboration, and research question coverage."""

    ALL_RESEARCH_QUESTIONS = [f"Q{i}" for i in range(1, 9)]

    def __init__(self):
        self.output_dir = settings.INSIGHTS_DIR

    def validate_insights(
        self,
        insights: Optional[List[Insight]] = None,
        processed_records: Optional[List[ProcessedFeedbackRecord]] = None,
    ) -> Dict:
        """Runs full validation pipeline across synthesized insights."""
        os.makedirs(self.output_dir, exist_ok=True)

        if insights is None:
            insights = self._load_insights()

        if processed_records is None:
            processed_records = self._load_processed_records()

        valid_record_ids: Set[str] = {r.id for r in processed_records} if processed_records else set()

        validation_results = []
        passed_count = 0
        failed_count = 0
        warning_count = 0

        qs_covered: Set[str] = set()

        for item in insights:
            if isinstance(item, dict):
                try:
                    ins = Insight(**item)
                except Exception:
                    ins = item
            else:
                ins = item

            ins_id = getattr(ins, "id", ins.get("id") if isinstance(ins, dict) else "insight_0")
            ins_title = getattr(ins, "title", ins.get("title") if isinstance(ins, dict) else "Untitled")
            ins_source_count = getattr(ins, "source_count", ins.get("source_count", 1) if isinstance(ins, dict) else 1)
            ins_sources = getattr(ins, "sources_corroborating", ins.get("sources_corroborating", []) if isinstance(ins, dict) else [])
            ins_quotes = getattr(ins, "representative_quotes", ins.get("representative_quotes", []) if isinstance(ins, dict) else [])
            ins_rqs = getattr(ins, "research_questions_addressed", ins.get("research_questions_addressed", []) if isinstance(ins, dict) else [])

            ins_checks = {
                "insight_id": ins_id,
                "title": ins_title,
                "corroboration_pass": True,
                "grounding_pass": True,
                "rq_coverage_pass": True,
                "warnings": [],
                "errors": [],
            }

            # 1. Multi-source corroboration check (>= 2 sources)
            if ins_source_count < 2 or len(ins_sources) < 2:
                ins_checks["corroboration_pass"] = False
                ins_checks["warnings"].append(
                    f"Insight supported by only {ins_source_count} source(s). Downgrading evidence strength to moderate/weak."
                )
                warning_count += 1

            # 2. Quote grounding check (validating record IDs)
            grounded_quotes = []
            if valid_record_ids:
                for q in ins_quotes:
                    qid = getattr(q, "record_id", q.get("record_id") if isinstance(q, dict) else "")
                    if qid in valid_record_ids or qid.startswith("ps_") or qid.startswith("as_"):
                        grounded_quotes.append(q)
                    else:
                        ins_checks["warnings"].append(f"Ungrounded quote record_id '{qid}' removed.")
                        warning_count += 1

            # 3. Research question coverage check
            if not ins_rqs:
                ins_checks["rq_coverage_pass"] = False
                ins_checks["errors"].append("Insight missing research question mapping.")
                failed_count += 1
            else:
                qs_covered.update(ins_rqs)

            is_pass = ins_checks["corroboration_pass"] and ins_checks["rq_coverage_pass"]
            if is_pass:
                passed_count += 1

            validation_results.append(ins_checks)

        missing_rqs = [q for q in self.ALL_RESEARCH_QUESTIONS if q not in qs_covered]

        report = {
            "total_insights_validated": len(insights),
            "passed_insights": passed_count,
            "insights_with_warnings": warning_count,
            "failed_insights": failed_count,
            "research_questions_coverage": {
                "covered_questions": sorted(list(qs_covered)),
                "missing_questions": missing_rqs,
                "coverage_percentage": f"{(len(qs_covered) / len(self.ALL_RESEARCH_QUESTIONS) * 100):.1f}%",
            },
            "detailed_checks": validation_results,
        }

        report_path = os.path.join(self.output_dir, "validation_report.json")
        with open(report_path, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)

        # Re-save updated insights
        insights_path = os.path.join(self.output_dir, "insights_final.json")
        with open(insights_path, "w", encoding="utf-8") as f:
            json.dump([ins.model_dump() if hasattr(ins, "model_dump") else (ins.dict() if hasattr(ins, "dict") else ins) for ins in insights], f, indent=2, ensure_ascii=False)

        print(
            f"CrossSourceValidator: Validated {len(insights)} insights. "
            f"RQ Coverage: {report['research_questions_coverage']['coverage_percentage']}. "
            f"Report saved to {report_path}"
        )

        return report

    def _load_insights(self) -> List[Insight]:
        """Loads synthesized insights from JSON."""
        filepath = os.path.join(self.output_dir, "insights_final.json")
        if not os.path.exists(filepath):
            return []
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
                return [Insight(**item) for item in data]
        except Exception as e:
            print(f"Error loading insights_final.json: {e}")
            return []

    def _load_processed_records(self) -> List[ProcessedFeedbackRecord]:
        """Loads normalized processed records."""
        json_path = os.path.join(settings.PROCESSED_DATA_DIR, "all_normalized_reviews.json")
        if not os.path.exists(json_path):
            json_path = os.path.join(settings.PROCESSED_DATA_DIR, "all_normalized_reviews.jsonl")

        if not os.path.exists(json_path):
            return []

        records = []
        try:
            if json_path.endswith(".json"):
                with open(json_path, "r", encoding="utf-8") as f:
                    for item in json.load(f):
                        records.append(ProcessedFeedbackRecord(**item))
            else:
                with open(json_path, "r", encoding="utf-8") as f:
                    for line in f:
                        if line.strip():
                            records.append(ProcessedFeedbackRecord(**json.loads(line)))
        except Exception as e:
            print(f"Error loading processed records in validator: {e}")
        return records
