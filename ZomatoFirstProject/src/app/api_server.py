import sys
import os
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Align python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from src.app.config import settings
from src.app.data.repository import RestaurantRepository
from src.app.services.filter_service import FilterService
from src.app.services.orchestrator import RecommendationOrchestrator
from src.app.models.domain import UserPreferences, RecommendationResponse

app = FastAPI(
    title="Gastro AI Recommendation API Server",
    description="Backend API serving high-fidelity restaurant recommendations leveraging deterministic filtering and LLM synthesis.",
    version="1.0.0"
)

# Allow CORS for development (especially Vite dev server running on localhost:5173)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Instantiate services
# Note: We use parquet storage matching settings.DATA_PATH (Option A) as it is already populated.
repo = RestaurantRepository(storage_type="parquet", file_path=settings.DATA_PATH)
filter_svc = FilterService(repo, settings.MAX_CANDIDATES)
orchestrator = RecommendationOrchestrator(filter_svc)

@app.get("/api/v1/search-options")
def get_search_options():
    """
    Retrieve unique locations and cuisines populated in the underlying Zomato dataset.
    This ensures that select dropdowns match valid dataset parameters perfectly.
    """
    try:
        locations = repo.get_unique_locations()
        cuisines = repo.get_unique_cuisines()
        return {
            "locations": locations,
            "cuisines": cuisines
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to load search parameters from database: {str(e)}"
        )

@app.post("/api/v1/recommendations", response_model=RecommendationResponse)
def get_recommendations(prefs: UserPreferences):
    """
    Generate personalized recommendations based on location, budget, cuisine, rating boundaries, and custom mood.
    """
    try:
        # standardizing fields to lowercase to avoid casing mismatches
        prefs.budget = prefs.budget.lower()
        prefs.cuisine = prefs.cuisine.lower()
        
        response = orchestrator.get_recommendations(prefs)
        return response
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Recommendation engine encountered an exception: {str(e)}"
        )

@app.get("/api/v1/health")
def health_check():
    """
    Standard health check endpoint.
    """
    return {
        "status": "healthy",
        "service": "Gastro AI Recommendation Engine"
    }
