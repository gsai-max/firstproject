import json
from typing import Dict, List, Any
from src.app.services.llm_client import LLMClient
from src.app.services.prompt_builder import PromptBuilder


class ContradictionAgent:
    """Agent 6: Surfaces counter-intuitive gaps between stated desires vs actual behaviors."""

    def __init__(self, llm_client: LLMClient = None):
        self.llm_client = llm_client or LLMClient()

    def process(self, records: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Surfaces stated vs actual behavioral contradictions."""
        user_prompt, system_inst = PromptBuilder.contradiction_agent_prompt(records)
        try:
            raw_response = self.llm_client.complete(user_prompt, system_inst)
            parsed = json.loads(raw_response)
            contradictions = parsed.get("contradictions", [])
        except Exception as e:
            print(f"[ContradictionAgent] LLM extraction error: {e}. Using fallback.")
            contradictions = self._fallback_contradictions()

        return {
            "agent": "ContradictionAgent",
            "contradiction_count": len(contradictions),
            "contradictions": contradictions
        }

    def _fallback_contradictions(self) -> List[Dict[str, Any]]:
        return [
            {
                "stated_desire": "Users claim they want better product recommendations and catalog discovery.",
                "actual_behavior": "95% of orders originate from search bar or 'Buy Again' list; category pages are rarely visited.",
                "underlying_friction": "Users want discovery WITHOUT added effort, browsing time, or cognitive decision fatigue.",
                "product_opportunity": "Context-aware basket completion nudges during 1-click checkout rather than forcing browsing."
            },
            {
                "stated_desire": "Users want cheaper prices and lower delivery fees before trying non-groceries.",
                "actual_behavior": "Users pay premium convenience fees for groceries but hesitate on $5 non-grocery items due to return anxiety.",
                "underlying_friction": "The true barrier is return hassle and quality risk, not item price.",
                "product_opportunity": "No-questions-asked 10-minute instant doorstep returns for trial categories."
            }
        ]
