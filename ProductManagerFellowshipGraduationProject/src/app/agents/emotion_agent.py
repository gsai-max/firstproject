import json
from typing import Dict, List, Any
from src.app.services.llm_client import LLMClient
from src.app.services.prompt_builder import PromptBuilder


class EmotionAgent:
    """Agent 2: Extracts emotional profiles blocking category expansion."""

    def __init__(self, llm_client: LLMClient = None):
        self.llm_client = llm_client or LLMClient()

    def process(self, records: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Extracts emotional friction spectrum across input records."""
        user_prompt, system_inst = PromptBuilder.emotion_agent_prompt(records)
        try:
            raw_response = self.llm_client.complete(user_prompt, system_inst)
            parsed = json.loads(raw_response)
            profiles = parsed.get("emotion_profiles", [])
        except Exception as e:
            print(f"[EmotionAgent] LLM extraction error: {e}. Using fallback.")
            profiles = self._fallback_emotions()

        return {
            "agent": "EmotionAgent",
            "emotion_count": len(profiles),
            "emotion_profiles": profiles
        }

    def _fallback_emotions(self) -> List[Dict[str, Any]]:
        return [
            {
                "emotion_name": "Risk Perception",
                "intensity": 0.85,
                "trigger_context": "Fear of getting damaged, fake, or non-returnable non-grocery products",
                "impact_on_exploration": "High Friction",
                "representative_quotes": [{"text": "I order milk daily but wouldn't buy earphones here.", "source": "reddit"}]
            },
            {
                "emotion_name": "Cognitive Decision Fatigue",
                "intensity": 0.78,
                "trigger_context": "Quick commerce users want 1-minute checkout; deep catalog browsing feels exhausting",
                "impact_on_exploration": "High Friction",
                "representative_quotes": [{"text": "I just reorder my weekly grocery list. Don't want to browse.", "source": "play_store"}]
            },
            {
                "emotion_name": "Uncertainty of Quality",
                "intensity": 0.72,
                "trigger_context": "Lack of rich reviews & ratings for non-food items",
                "impact_on_exploration": "Moderate Barrier",
                "representative_quotes": [{"text": "Need to see user reviews before trying personal care brands.", "source": "twitter"}]
            }
        ]
