import json
from typing import Dict, List, Any
from src.app.services.llm_client import LLMClient
from src.app.services.prompt_builder import PromptBuilder


class HabitAgent:
    """Agent 3: Extracts behavioral Habit Loops (Trigger -> Action -> Reward)."""

    def __init__(self, llm_client: LLMClient = None):
        self.llm_client = llm_client or LLMClient()

    def process(self, records: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Extracts customer habit loops preventing cross-category trial."""
        user_prompt, system_inst = PromptBuilder.habit_agent_prompt(records)
        try:
            raw_response = self.llm_client.complete(user_prompt, system_inst)
            parsed = json.loads(raw_response)
            loops = parsed.get("habit_loops", [])
        except Exception as e:
            print(f"[HabitAgent] LLM extraction error: {e}. Using fallback.")
            loops = self._fallback_habits()

        return {
            "agent": "HabitAgent",
            "habit_loop_count": len(loops),
            "habit_loops": loops
        }

    def _fallback_habits(self) -> List[Dict[str, Any]]:
        return [
            {
                "trigger": "Sunday Morning Grocery Need",
                "action": "Open App -> Repeat Previous Basket in 1-Click",
                "reward": "10-Minute Checkout + Instant Relief",
                "exploration_barrier": "Zero screen time allocated to category browsing",
                "interruption_opportunity": "Contextual cart cross-sell before 1-click checkout"
            },
            {
                "trigger": "Late Night Snack Craving",
                "action": "Search Chips/Beverages directly",
                "reward": "Instant Craving Satisfaction",
                "exploration_barrier": "Direct search bypasses category landing pages",
                "interruption_opportunity": "Pairing recommendations (e.g., Board Games / Party Supplies with Snacks)"
            }
        ]
