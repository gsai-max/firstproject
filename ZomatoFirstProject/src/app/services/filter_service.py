import pandas as pd
from typing import List
from src.app.models.domain import Restaurant, UserPreferences
from src.app.data.repository import RestaurantRepository

class FilterService:
    def __init__(self, repository: RestaurantRepository, max_candidates: int = 30):
        self.repo = repository
        self.max_candidates = max_candidates

    def filter_candidates(self, prefs: UserPreferences) -> List[Restaurant]:
        df = self.repo.get_all_raw()
        if df is None or df.empty:
            return []
            
        # 1. Location match (case-insensitive)
        loc_mask = df['location'].str.lower() == prefs.location.lower()
        df_filtered = df[loc_mask]
        if df_filtered.empty:
            return []
        
        # 2. Budget band match
        budget_mask = df_filtered['budget_band'].str.lower() == prefs.budget.lower()
        df_filtered = df_filtered[budget_mask]
        if df_filtered.empty:
            return []
        
        # 3. Cuisine match (fuzzy containment array check)
        target_cuisine = prefs.cuisine.lower()
        cuisine_mask = df_filtered['cuisines'].apply(lambda cuisines: target_cuisine in cuisines)
        df_filtered = df_filtered[cuisine_mask]
        if df_filtered.empty:
            return []
        
        # 4. Rating boundaries check
        rating_mask = df_filtered['rating'] >= prefs.min_rating
        df_filtered = df_filtered[rating_mask]
        if df_filtered.empty:
            return []
        
        # 5. Pre-sort and cap
        df_filtered = df_filtered.sort_values(by=['rating', 'estimated_cost'], ascending=[False, True])
        candidates_df = df_filtered.head(self.max_candidates)
        
        return [Restaurant(**row) for _, row in candidates_df.iterrows()]
