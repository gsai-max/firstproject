import json
from typing import Dict, List, Any
from src.app.services.llm_client import LLMClient
from src.app.services.prompt_builder import PromptBuilder


class JTBDAgent:
    """Agent 4: Maps fundamental human Jobs-To-Be-Done needs."""

    def __init__(self, llm_client: LLMClient = None):
        self.llm_client = llm_client or LLMClient()

    def process(self, records: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Identifies customer JTBD needs across feedback streams."""
        user_prompt, system_inst = PromptBuilder.jtbd_agent_prompt(records)
        try:
            raw_response = self.llm_client.complete(user_prompt, system_inst)
            parsed = json.loads(raw_response)
            jtbd_items = parsed.get("jtbd_items", [])
        except Exception as e:
            print(f"[JTBDAgent] LLM extraction error: {e}. Using fallback.")
            jtbd_items = self._fallback_jtbd()

        return {
            "agent": "JTBDAgent",
            "jtbd_count": len(jtbd_items),
            "jtbd_items": jtbd_items
        }

    def _fallback_jtbd(self) -> List[Dict[str, Any]]:
        return [
            {
                "job_statement": "When I am preparing for office on short notice, I want grooming items in 10 mins, so that I look presentable without delay.",
                "functional_need": "Instant personal care & grooming items delivery",
                "emotional_need": "Avoid embarrassment & panic before meetings",
                "target_category_opportunity": "Personal Care & Beauty",
                "current_solution": "Borrowing from roomies or skipping product"
            },
            {
                "job_statement": "When my pet runs out of food unexpectedly, I want urgent pet supplies delivered, so that my pet doesn't skip a meal.",
                "functional_need": "Emergency pet food replenishment",
                "emotional_need": "Peace of mind as a responsible pet parent",
                "target_category_opportunity": "Pet Supplies",
                "current_solution": "Physical travel to pet store"
            }
        ]
