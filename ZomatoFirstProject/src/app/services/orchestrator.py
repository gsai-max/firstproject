from src.app.models.domain import UserPreferences, RecommendationResponse
from src.app.services.filter_service import FilterService
from src.app.services.prompt_builder import PromptBuilder
from src.app.services.llm_client import GroqClient
from src.app.services.response_parser import ResponseParser

class RecommendationOrchestrator:
    def __init__(self, filter_service: FilterService, llm_client=None):
        self.filter_service = filter_service
        self.prompt_builder = PromptBuilder()
        self.llm_client = llm_client if llm_client is not None else GroqClient()
        self.parser = ResponseParser()

    def get_recommendations(self, prefs: UserPreferences) -> RecommendationResponse:
        # 1. Deterministic DB pre-filtering
        candidates = self.filter_service.filter_candidates(prefs)
        
        # 2. Short-circuit if empty
        if not candidates:
            return RecommendationResponse(
                summary="No restaurants match your search filters. Try updating your limits!",
                recommendations=[],
                meta={"candidates_considered": 0, "fallback_activated": False}
            )
            
        # 3. Framing prompt strings
        system_instruction = self.prompt_builder.get_system_instruction()
        prompt = self.prompt_builder.build_user_prompt(prefs, candidates)
        
        # 4. LLM Completion Call
        try:
            raw_response = self.llm_client.complete(prompt, system_instruction)
        except Exception as e:
            return self.parser.generate_fallback(candidates, prefs, f"LLM client connection failure: {e}")
            
        # 5. Parse, validate grounding and deliver JSON response
        return self.parser.parse_response(raw_response, candidates, prefs)
