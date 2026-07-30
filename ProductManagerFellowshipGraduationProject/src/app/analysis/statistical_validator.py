import math
from typing import Dict, List, Any


class StatisticalValidator:
    """Calculates quantitative statistical confidence scores and ranks insights."""

    SOURCE_WEIGHTS = {
        "play_store": 1.0,
        "app_store": 1.0,
        "reddit": 1.2,
        "twitter": 1.1,
        "youtube": 1.1,
        "quora": 1.2,
        "forums": 1.3,
        "support_tickets": 1.3,
        "competitors": 1.1,
    }

    def validate_and_score(self, insights: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Calculates statistical confidence scores (0.0-1.0) and ranks insights."""
        scored_insights = []

        for item in insights:
            insight = item.model_dump() if hasattr(item, "model_dump") else (item.dict() if hasattr(item, "dict") else dict(item))
            sources = insight.get("sources_corroborating", insight.get("contributing_sources", []))
            quotes = insight.get("representative_quotes", [])
            strength = insight.get("evidence_strength", "moderate")

            # 1. Source Diversity Weight (max 0.40)
            weighted_sources = sum(self.SOURCE_WEIGHTS.get(src, 1.0) for src in sources)
            diversity_score = min(0.40, (weighted_sources / 10.0) * 0.40)

            # 2. Quote Grounding Score (max 0.35)
            quote_score = min(0.35, len(quotes) * 0.15)

            # 3. Evidence Strength Base (max 0.25)
            strength_score = 0.25 if strength == "strong" else (0.18 if strength == "moderate" else 0.10)

            # Total Confidence Score
            total_score = round(min(1.0, 0.40 + diversity_score + quote_score + strength_score), 2)
            
            scored_insight = dict(insight)
            scored_insight["confidence_score"] = total_score
            scored_insights.append(scored_insight)

        # Rank insights by confidence score descending
        scored_insights.sort(key=lambda x: x.get("confidence_score", 0.0), reverse=True)
        for idx, item in enumerate(scored_insights):
            item["priority_rank"] = idx + 1

        return scored_insights
