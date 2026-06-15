import pytest
import pandas as pd
from src.app.models.domain import UserPreferences, Restaurant
from src.app.data.repository import RestaurantRepository
from src.app.services.filter_service import FilterService
from src.app.services.orchestrator import RecommendationOrchestrator

@pytest.fixture
def mock_repository(tmp_path):
    data = {
        "id": ["r00001", "r00002"],
        "name": ["Chili Cafe", "Royal Spice"],
        "location": ["Delhi", "Delhi"],
        "cuisines": [["cafe"], ["indian"]],
        "rating": [4.5, 3.2],
        "estimated_cost": [400.0, 600.0],
        "budget_band": ["low", "medium"]
    }
    df = pd.DataFrame(data)
    file_path = tmp_path / "test_restaurants.parquet"
    df.to_parquet(file_path, index=False)
    return RestaurantRepository(storage_type="parquet", file_path=str(file_path))

class MockLLMClient:
    def __init__(self, response_text: str, raise_exception: bool = False):
        self.response_text = response_text
        self.raise_exception = raise_exception

    def complete(self, prompt: str, system_instruction: str) -> str:
        if self.raise_exception:
            raise Exception("Mock Connection Timeout")
        return self.response_text

def test_orchestrator_success_flow(mock_repository):
    filter_svc = FilterService(mock_repository)
    
    # Mock normal successful LLM output
    llm_output = """
    {
      "summary": "Best spots in Delhi.",
      "recommendations": [
        {
          "id": "r00001",
          "rank": 1,
          "explanation": "Compelling cafe rationale"
        }
      ]
    }
    """
    mock_llm = MockLLMClient(llm_output)
    orchestrator = RecommendationOrchestrator(filter_svc, llm_client=mock_llm)
    
    prefs = UserPreferences(
        location="Delhi",
        budget="low",
        cuisine="cafe",
        min_rating=4.0,
        additional_preferences="quiet place",
        top_k=2
    )
    
    res = orchestrator.get_recommendations(prefs)
    assert res.meta["fallback_activated"] is False
    assert len(res.recommendations) == 1
    assert res.recommendations[0].restaurant.name == "Chili Cafe"
    assert res.recommendations[0].explanation == "Compelling cafe rationale"

def test_orchestrator_mismatched_id_grounding(mock_repository):
    filter_svc = FilterService(mock_repository)
    
    # Mock output returning a hallucinated ID (r99999) along with a valid one
    llm_output = """
    {
      "summary": "Best spots in Delhi.",
      "recommendations": [
        {
          "id": "r99999",
          "rank": 1,
          "explanation": "Hallucinated restaurant description"
        },
        {
          "id": "r00001",
          "rank": 2,
          "explanation": "Valid restaurant description"
        }
      ]
    }
    """
    mock_llm = MockLLMClient(llm_output)
    orchestrator = RecommendationOrchestrator(filter_svc, llm_client=mock_llm)
    
    prefs = UserPreferences(
        location="Delhi",
        budget="low",
        cuisine="cafe",
        min_rating=4.0,
        additional_preferences="quiet place",
        top_k=2
    )
    
    res = orchestrator.get_recommendations(prefs)
    assert res.meta["fallback_activated"] is False
    # Hallucinated ID must be filtered out, leaving only r00001
    assert len(res.recommendations) == 1
    assert res.recommendations[0].restaurant.id == "r00001"

def test_orchestrator_malformed_json_fallback(mock_repository):
    filter_svc = FilterService(mock_repository)
    
    # Mock completely malformed raw text instead of JSON
    llm_output = "Sorry, I encountered an issue. Here is Chili Cafe, a great place!"
    mock_llm = MockLLMClient(llm_output)
    orchestrator = RecommendationOrchestrator(filter_svc, llm_client=mock_llm)
    
    prefs = UserPreferences(
        location="Delhi",
        budget="low",
        cuisine="cafe",
        min_rating=4.0,
        additional_preferences="quiet place",
        top_k=2
    )
    
    res = orchestrator.get_recommendations(prefs)
    # Parser should catch malformed JSON and fall back to DB ranking
    assert res.meta["fallback_activated"] is True
    assert len(res.recommendations) == 1
    assert res.recommendations[0].restaurant.name == "Chili Cafe"
    assert "System Fallback Mode" in res.summary

def test_orchestrator_connection_failure_fallback(mock_repository):
    filter_svc = FilterService(mock_repository)
    
    # Mock client raising network exceptions
    mock_llm = MockLLMClient("", raise_exception=True)
    orchestrator = RecommendationOrchestrator(filter_svc, llm_client=mock_llm)
    
    prefs = UserPreferences(
        location="Delhi",
        budget="low",
        cuisine="cafe",
        min_rating=4.0,
        additional_preferences="quiet place",
        top_k=2
    )
    
    res = orchestrator.get_recommendations(prefs)
    # Connection failure must trigger database ranking fallback
    assert res.meta["fallback_activated"] is True
    assert len(res.recommendations) == 1
    assert res.recommendations[0].restaurant.name == "Chili Cafe"
    assert "System Fallback Mode" in res.summary
