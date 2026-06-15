import pytest
import pandas as pd
from src.app.models.domain import UserPreferences, Restaurant
from src.app.data.repository import RestaurantRepository
from src.app.services.filter_service import FilterService

@pytest.fixture
def mock_repository(tmp_path):
    data = {
        "id": ["r00001", "r00002", "r00003", "r00004"],
        "name": ["Chili Cafe", "Royal Spice", "Bella Italian", "Venezia Pizzeria"],
        "location": ["Delhi", "Delhi", "Bangalore", "Bangalore"],
        "cuisines": [["cafe", "bakery"], ["indian", "spicy"], ["italian", "pasta"], ["italian", "pizza"]],
        "rating": [4.5, 3.2, 4.8, 4.2],
        "estimated_cost": [400.0, 600.0, 1200.0, 800.0],
        "budget_band": ["low", "medium", "medium", "medium"]
    }
    df = pd.DataFrame(data)
    file_path = tmp_path / "test_restaurants.parquet"
    df.to_parquet(file_path, index=False)
    return RestaurantRepository(storage_type="parquet", file_path=str(file_path))

def test_filter_service_filtering_logic(mock_repository):
    filter_svc = FilterService(mock_repository)
    
    # Check Bangalore Italian Medium Budget
    prefs = UserPreferences(
        location="Bangalore",
        budget="medium",
        cuisine="italian",
        min_rating=4.0,
        additional_preferences="",
        top_k=5
    )
    
    candidates = filter_svc.filter_candidates(prefs)
    assert len(candidates) == 2
    # Verify sorting (rating descending): Bella Italian (4.8) should be first, Venezia (4.2) second
    assert candidates[0].name == "Bella Italian"
    assert candidates[0].rating == 4.8
    assert candidates[1].name == "Venezia Pizzeria"
    assert candidates[1].rating == 4.2

def test_filter_service_caps_candidates(mock_repository):
    # Capping limit at 1 element
    filter_svc = FilterService(mock_repository, max_candidates=1)
    
    prefs = UserPreferences(
        location="Delhi",
        budget="low",
        cuisine="cafe",
        min_rating=4.0,
        additional_preferences="",
        top_k=2
    )
    
    candidates = filter_svc.filter_candidates(prefs)
    assert len(candidates) == 1
    assert candidates[0].name == "Chili Cafe"

def test_filter_service_zero_candidates(mock_repository):
    filter_svc = FilterService(mock_repository)
    
    # Query with no matches
    prefs = UserPreferences(
        location="Delhi",
        budget="high", # None are high budget
        cuisine="italian",
        min_rating=4.0,
        additional_preferences="",
        top_k=5
    )
    
    candidates = filter_svc.filter_candidates(prefs)
    assert len(candidates) == 0
