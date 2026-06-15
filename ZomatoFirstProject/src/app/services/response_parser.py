import json
import re
from typing import List
from src.app.models.domain import Restaurant, UserPreferences, Recommendation, RecommendationResponse

class ResponseParser:
    def parse_response(self, raw_text: str, candidates: List[Restaurant], prefs: UserPreferences) -> RecommendationResponse:
        try:
            # Extract JSON block using regex
            match = re.search(r'\{.*\}', raw_text, re.DOTALL)
            json_str = match.group(0) if match else raw_text
            data = json.loads(json_str)
            
            summary = data.get("summary", "Here are your curated recommendations.")
            recs_raw = data.get("recommendations", [])
            
            candidate_map = {c.id: c for c in candidates}
            recommendations = []
            
            # Enforce Bounded Grounding Assertion
            for r_dict in recs_raw:
                r_id = r_dict.get("id")
                if r_id in candidate_map:
                    recommendations.append(
                        Recommendation(
                            rank=r_dict.get("rank", len(recommendations) + 1),
                            restaurant=candidate_map[r_id],
                            explanation=r_dict.get("explanation", "Perfect fit for search preferences.")
                        )
                    )
            
            # Activate database ranking fallback if zero grounded results return
            if not recommendations:
                return self.generate_fallback(candidates, prefs, "Zero grounded outputs from LLM.")
                
            return RecommendationResponse(
                summary=summary,
                recommendations=recommendations[:prefs.top_k],
                meta={"candidates_considered": len(candidates), "fallback_activated": False}
            )
            
        except Exception as e:
            return self.generate_fallback(candidates, prefs, str(e))

    def generate_fallback(self, candidates: List[Restaurant], prefs: UserPreferences, reason: str) -> RecommendationResponse:
        fallback_recs = []
        items = candidates[:prefs.top_k]
        for rank, c in enumerate(items, start=1):
            explanation = (
                f"Highly rated dining choice in {c.location} with a {c.rating} rating. "
                f"Matches your target cuisine ({', '.join(c.cuisines)}) and fits your budget (costing ₹{c.estimated_cost:.0f})."
            )
            fallback_recs.append(Recommendation(rank=rank, restaurant=c, explanation=explanation))
            
        return RecommendationResponse(
            summary="Here are highly rated dining options matching your criteria (System Fallback Mode).",
            recommendations=fallback_recs,
            meta={
                "candidates_considered": len(candidates),
                "fallback_activated": True,
                "fallback_reason": reason
            }
        )
