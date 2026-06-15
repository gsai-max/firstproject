from pydantic import BaseModel, Field
from typing import List, Optional, Dict

class Restaurant(BaseModel):
    id: str
    name: str
    location: str
    cuisines: List[str]
    rating: float
    estimated_cost: float
    budget_band: str

class UserPreferences(BaseModel):
    location: str = Field(..., description="Target locality exact string")
    budget: str = Field("medium", description="Budget tier: 'low', 'medium', or 'high'")
    cuisine: str = Field(..., description="Cuisine classification keyword")
    min_rating: float = Field(0.0, ge=0.0, le=5.0, description="Minimum star rating boundary")
    additional_preferences: str = Field("", max_length=500, description="Free-text criteria")
    top_k: int = Field(5, ge=1, le=10, description="Result size")

class Recommendation(BaseModel):
    rank: int
    restaurant: Restaurant
    explanation: str

class RecommendationResponse(BaseModel):
    summary: str
    recommendations: List[Recommendation]
    meta: Dict
