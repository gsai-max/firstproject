import pandas as pd
import numpy as np

class SchemaNormalizer:
    def __init__(self, low_limit: float = 500.0, medium_limit: float = 1500.0):
        self.low_limit = low_limit
        self.medium_limit = medium_limit

    def normalize(self, df: pd.DataFrame) -> pd.DataFrame:
        normalized_df = pd.DataFrame()
        
        # Enforce type-safe internal schema mapping
        normalized_df['id'] = df.index.map(lambda x: f"r{x:05d}")
        normalized_df['name'] = df['name'].fillna("Unknown Restaurant").astype(str).str.strip()
        normalized_df['location'] = df['location'].fillna("Unknown").astype(str).str.strip()
        
        # Convert cuisine strings into standardized lowercase lists
        normalized_df['cuisines'] = df['cuisines'].fillna("various").apply(
            lambda c: [x.strip().lower() for x in str(c).split(",") if x.strip()]
        )
        
        # Enforce aggregate ratings clean parsing: '4.1/5' -> 4.1, 'NEW' -> 0.0
        rate_series = df['rate'].astype(str).str.split('/').str[0].str.strip()
        normalized_df['rating'] = pd.to_numeric(rate_series, errors='coerce').fillna(0.0)
        
        # Parse numerical cost for two: '1,200' -> 1200.0
        cost_series = df['approx_cost(for two people)'].astype(str).str.replace(',', '').str.strip()
        normalized_df['estimated_cost'] = pd.to_numeric(cost_series, errors='coerce').fillna(0.0)
        
        # Map cost to budget band Low/Medium/High
        normalized_df['budget_band'] = normalized_df['estimated_cost'].apply(self._classify_budget)
        
        return normalized_df

    def _classify_budget(self, cost: float) -> str:
        if cost <= self.low_limit:
            return "low"
        elif cost <= self.medium_limit:
            return "medium"
        else:
            return "high"
