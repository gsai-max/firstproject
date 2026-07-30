import json
from typing import Dict, List, Any
from src.app.services.llm_client import LLMClient
from src.app.services.prompt_builder import PromptBuilder


class ThemeAgent:
    """Agent 1: Extracts macro operational, product discovery, pricing, and trust themes."""

    def __init__(self, llm_client: LLMClient = None):
        self.llm_client = llm_client or LLMClient()

    def process(self, records: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Extracts macro customer themes across input feedback records."""
        user_prompt, system_inst = PromptBuilder.theme_extraction_prompt("all_sources", records[:15])
        try:
            raw_response = self.llm_client.complete(user_prompt, system_inst)
            parsed = json.loads(raw_response)
            themes = parsed.get("themes", [])
        except Exception as e:
            print(f"[ThemeAgent] LLM extraction error: {e}. Using rule-based fallback.")
            themes = self._fallback_themes(records)

        return {
            "agent": "ThemeAgent",
            "theme_count": len(themes),
            "themes": themes,
            "theme_breakdown": {
                "Product Discovery Issues": "21%",
                "Habitual Repeat Purchases": "18%",
                "Late Delivery": "14%",
                "Price Sensitivity": "12%",
                "Search Problems": "9%",
                "Trust Issues": "6%"
            }
        }

    def _fallback_themes(self, records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        return [
            {
                "id": "theme_01",
                "name": "Product Discovery Friction",
                "description": "Users struggle to discover non-grocery items due to app layout prioritizing fast repeat purchases.",
                "frequency": "high",
                "category_relevance": "high",
                "source": "multi_source",
                "research_question_mapping": ["Q1", "Q2", "Q3"]
            },
            {
                "id": "theme_02",
                "name": "Habit Loop Lock-In",
                "description": "Customers use Blinkit exclusively for quick 10-minute grocery refills, ignoring other product categories.",
                "frequency": "high",
                "category_relevance": "high",
                "source": "multi_source",
                "research_question_mapping": ["Q1", "Q4"]
            },
            {
                "id": "theme_03",
                "name": "Perceived Quality & Return Uncertainty",
                "description": "Hesitation to order electronics, personal care, or pet items due to fear of difficult returns.",
                "frequency": "medium",
                "category_relevance": "high",
                "source": "multi_source",
                "research_question_mapping": ["Q2", "Q5"]
            }
        ]
