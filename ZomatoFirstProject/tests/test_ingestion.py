import pytest
import pandas as pd
import numpy as np
from src.app.ingestion.normalizer import SchemaNormalizer

def test_schema_normalizer_success_case():
    # Setup mock raw data that contains all columns as per standard Hugging Face dataset
    raw_data = {
        "name": ["  Toscano  ", "Empire Restaurant", None],
        "location": ["UB City", "Jayanagar", None],
        "cuisines": ["Italian, Pizza, Cafe", "North Indian, South Indian", None],
        "rate": ["4.3/5", "3.8 /5", "NEW"],
        "approx_cost(for two people)": ["1,500", "600", None]
    }
    df_raw = pd.DataFrame(raw_data)
    
    normalizer = SchemaNormalizer(low_limit=500.0, medium_limit=1500.0)
    df_clean = normalizer.normalize(df_raw)
    
    # Assertions
    assert len(df_clean) == 3
    
    # Row 0
    assert df_clean.loc[0, "name"] == "Toscano"
    assert df_clean.loc[0, "location"] == "UB City"
    assert df_clean.loc[0, "cuisines"] == ["italian", "pizza", "cafe"]
    assert df_clean.loc[0, "rating"] == 4.3
    assert df_clean.loc[0, "estimated_cost"] == 1500.0
    assert df_clean.loc[0, "budget_band"] == "medium"
    
    # Row 1
    assert df_clean.loc[1, "name"] == "Empire Restaurant"
    assert df_clean.loc[1, "location"] == "Jayanagar"
    assert df_clean.loc[1, "cuisines"] == ["north indian", "south indian"]
    assert df_clean.loc[1, "rating"] == 3.8
    assert df_clean.loc[1, "estimated_cost"] == 600.0
    assert df_clean.loc[1, "budget_band"] == "medium"
    
    # Row 2 (Null/Edge cases)
    assert df_clean.loc[2, "name"] == "Unknown Restaurant"
    assert df_clean.loc[2, "location"] == "Unknown"
    assert df_clean.loc[2, "cuisines"] == ["various"]
    assert df_clean.loc[2, "rating"] == 0.0
    assert df_clean.loc[2, "estimated_cost"] == 0.0
    assert df_clean.loc[2, "budget_band"] == "low"

def test_schema_normalizer_budget_boundaries():
    raw_data = {
        "name": ["Cheap Eats", "Mid Range", "Fine Dining"],
        "location": ["Indiranagar", "Indiranagar", "Indiranagar"],
        "cuisines": ["Fast Food", "Chinese", "Continental"],
        "rate": ["3.5", "4.0", "4.5"],
        "approx_cost(for two people)": ["499", "1500", "1501"]
    }
    df_raw = pd.DataFrame(raw_data)
    
    normalizer = SchemaNormalizer(low_limit=500.0, medium_limit=1500.0)
    df_clean = normalizer.normalize(df_raw)
    
    assert df_clean.loc[0, "budget_band"] == "low"      # 499 <= 500
    assert df_clean.loc[1, "budget_band"] == "medium"   # 1500 <= 1500
    assert df_clean.loc[2, "budget_band"] == "high"     # 1501 > 1500
