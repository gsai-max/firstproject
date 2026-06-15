import json
from typing import List
from src.app.models.domain import Restaurant, UserPreferences

class PromptBuilder:
    def get_system_instruction(self) -> str:
        return (
            "You are Zomato's Senior Food Guide and Critic.\n"
            "Your task is to rank and recommend restaurants from the provided candidate list.\n"
            "CRITICAL GROUNDING RULES:\n"
            "1. ONLY select restaurants from the provided candidate list. Never invent or hallucinate a restaurant.\n"
            "2. You MUST respond with a valid JSON object matching this schema:\n"
            "{\n"
            "  \"summary\": \"General summary of the matching restaurants...\",\n"
            "  \"recommendations\": [\n"
            "    {\n"
            "      \"id\": \"restaurant_id\",\n"
            "      \"rank\": 1,\n"
            "      \"explanation\": \"A highly compelling natural language rationale explaining why this spot fits their subjective preference and budget.\"\n"
            "    }\n"
            "  ]\n"
            "}\n"
            "3. Ensure the JSON is properly closed and contains no markdown conversational text."
        )

    def build_user_prompt(self, prefs: UserPreferences, candidates: List[Restaurant]) -> str:
        compact_candidates = []
        for c in candidates:
            compact_candidates.append({
                "id": c.id,
                "name": c.name,
                "rating": c.rating,
                "cost": c.estimated_cost,
                "cuisines": c.cuisines,
                "location": c.location
            })
        
        prompt_dict = {
            "user_preferences": {
                "location": prefs.location,
                "budget": prefs.budget,
                "cuisine": prefs.cuisine,
                "subjective_criteria": prefs.additional_preferences,
                "top_k": prefs.top_k
            },
            "candidate_pool": compact_candidates
        }
        return json.dumps(prompt_dict, indent=2)
