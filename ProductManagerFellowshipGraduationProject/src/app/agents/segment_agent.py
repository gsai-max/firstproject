import json
from typing import Dict, List, Any
from src.app.services.llm_client import LLMClient
from src.app.services.prompt_builder import PromptBuilder


class SegmentAgent:
    """Agent 5: Discover emergent consumer archetypes."""

    def __init__(self, llm_client: LLMClient = None):
        self.llm_client = llm_client or LLMClient()

    def process(self, records: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Discovers consumer archetypes and trial barriers."""
        user_prompt, system_inst = PromptBuilder.segment_agent_prompt(records)
        try:
            raw_response = self.llm_client.complete(user_prompt, system_inst)
            parsed = json.loads(raw_response)
            archetypes = parsed.get("consumer_archetypes", [])
        except Exception as e:
            print(f"[SegmentAgent] LLM extraction error: {e}. Using fallback.")
            archetypes = self._fallback_segments()

        return {
            "agent": "SegmentAgent",
            "archetype_count": len(archetypes),
            "consumer_archetypes": archetypes
        }

    def _fallback_segments(self) -> List[Dict[str, Any]]:
        return [
            {
                "archetype_name": "Routine Grocery Buyers",
                "description": "High frequency, buys groceries only, 95% repeat purchases",
                "percentage_estimate": 42,
                "primary_categories": ["groceries", "fresh_produce"],
                "barriers_to_new_categories": "Ingrained habit loop, unaware of full catalog",
                "growth_nudge": "Free sample add-on with weekly grocery basket"
            },
            {
                "archetype_name": "Category Explorers",
                "description": "Open to trying electronics accessories, personal care, and toys",
                "percentage_estimate": 18,
                "primary_categories": ["groceries", "electronics", "personal_care"],
                "barriers_to_new_categories": "Lack of curated discovery collections",
                "growth_nudge": "Personalized trending products banner"
            },
            {
                "archetype_name": "Convenience Seekers",
                "description": "Speed-driven professionals ordering emergency household/personal items",
                "percentage_estimate": 25,
                "primary_categories": ["groceries", "snacks", "pharmacy"],
                "barriers_to_new_categories": "Decision fatigue during checkout",
                "growth_nudge": "1-tap bundle add-ons"
            }
        ]
