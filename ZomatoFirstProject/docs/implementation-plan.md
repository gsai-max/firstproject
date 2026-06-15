# Phase-Wise Detailed Implementation Plan: AI-Powered Restaurant Recommendation System

This implementation plan outlines the step-by-step engineering roadmap for building the Zomato-inspired recommendation system. It translates the core requirements, schemas, flowcharts, and diagrams defined in [context.md](file:///c:/Nextleap%20Projects%20Git/ZomatoFirstProject/docs/context.md) and [architecture.md](file:///c:/Nextleap%20Projects%20Git/ZomatoFirstProject/docs/architecture.md) into concrete actionable tasks.

To support the architectural technology choices, this plan is divided into two operational execution tracks:
* **Option A: Rapid Milestone Track** (Streamlit Single-Process App with in-memory Parquet storage).
* **Option B: Production-Shaped Track** (FastAPI backend + React frontend + SQLite storage).

---

## 📂 Target Project Directory Structure

```
ZomatoFirstProject/
├── docs/
│   ├── context.md               # Context & business requirements
│   ├── problemstatement.md      # Raw source specification
│   ├── architecture.md          # Technical design blueprint
│   └── implementation-plan.md   # Step-by-step roadmap (This File)
├── data/
│   ├── raw/                     # Raw Hugging Face CSV Cache
│   └── processed/               # Normalized Parquet / SQLite database
├── src/
│   └── app/
│       ├── __init__.py
│       ├── main.py              # Option A Streamlit UI or Option B FastAPI Entry
│       ├── config.py            # Environment Configuration & Env Loader
│       ├── models/
│       │   ├── __init__.py
│       │   └── domain.py        # Pydantic Domain Validation Models
│       ├── ingestion/
│       │   ├── __init__.py
│       │   ├── loader.py        # HF Dataset Downloader (DatasetLoader)
│       │   ├── normalizer.py    # Schema Normalizer & Preprocessor
│       │   └── pipeline.py      # Pipeline Ingestion Coordinator
│       ├── data/
│       │   ├── __init__.py
│       │   └── repository.py    # Data Access (RestaurantRepository)
│       ├── services/
│       │   ├── __init__.py
│       │   ├── filter_service.py# Structured multi-attribute pre-filters
│       │   ├── prompt_builder.py# Dynamic prompt context compiler
│       │   ├── llm_client.py    # Thin wrapper client (LLMClient)
│       │   ├── response_parser.py# Regex JSON extraction & grounding assertion
│       │   └── orchestrator.py  # Central recommendation orchestrator
│       └── api/                 # (Option B Specific)
│           ├── __init__.py
│           ├── routes.py        # FastAPI routes
│           └── schemas.py       # API DTO request/response schemas
├── frontend/                    # (Option B Specific React UI project)
├── scripts/
│   └── ingest.py                # Command-line trigger execution script
├── tests/                       # Unit & integration testing suites
│   ├── __init__.py
│   ├── test_ingestion.py
│   ├── test_filter_service.py
│   └── test_orchestrator.py
├── .env.example                 # Env variables template
└── requirements.txt             # Workspace dependencies
```

---

## 📅 Roadmap Overview

```
┌──────────────────────────────────────────────┐
│ Phase 1: Environment & Data Ingestion        │ ──> Setup config, download dataset, run normalization, store Parquet
└──────────────────────────────────────────────┘
                       │
                       ▼
┌──────────────────────────────────────────────┐
│ Phase 2: Domain Models & Repository Engine   │ ──> Define Pydantic structures, build query engine, add filters
└──────────────────────────────────────────────┘
                       │
                       ▼
┌──────────────────────────────────────────────┐
│ Phase 3: Integration & LLM Orchestrator Layer│ ──> Setup prompts, implement Groq SDK integration, write regex parsers
└──────────────────────────────────────────────┘
                       │
                       ▼
┌──────────────────────────────────────────────┐
│ Phase 4: Presentation Layer Implementation   │ ──> Choose Track A (Streamlit) or Track B (FastAPI + React)
└──────────────────────────────────────────────┘
                       │
                       ▼
┌──────────────────────────────────────────────┐
│ Phase 5: Fault-Tolerance, Fallbacks & Tests  │ ──> Wire timeouts, assert grounded IDs, run full pytest coverage
└──────────────────────────────────────────────┘
```

---

## 🛠️ Step-by-Step Phase Worksheets

---

### Phase 1: Environment Setup & Data Ingestion Pipeline

**Goal:** Configure project settings, fetch the Hugging Face dataset, standardize schemas, clean nulls, and persist normalized outputs locally in Parquet or SQLite.

#### Task 1.1: Project Initial Setup & Configurations
* Create `requirements.txt` containing:
  ```text
  streamlit>=1.35.0
  fastapi>=0.100.0
  uvicorn>=0.22.0
  pandas>=2.0.0
  datasets>=2.12.0
  pydantic>=2.0.0
  pydantic-settings>=2.0.0
  groq>=0.9.0
  pytest>=7.4.0
  pyarrow>=12.0.0
  ```
* Create `src/app/config.py` using `pydantic-settings` to load settings from a local `.env` file:
  ```python
  from pydantic_settings import BaseSettings
  from pydantic import Field

  class Settings(BaseSettings):
      LLM_PROVIDER: str = Field("groq", env="LLM_PROVIDER")
      LLM_API_KEY: str = Field(..., env="LLM_API_KEY")
      LLM_MODEL: str = Field("llama3-8b-8192", env="LLM_MODEL")
      
      # Storage Selection (Option A Parquet, Option B SQLite)
      DATA_PATH: str = Field("data/processed/restaurants.parquet", env="DATA_PATH")
      SQLITE_DB_PATH: str = Field("data/processed/restaurants.db", env="SQLITE_DB_PATH")
      
      # Budget classification thresholds
      LOW_BUDGET_LIMIT: float = Field(500.0, env="LOW_BUDGET_LIMIT")
      MEDIUM_BUDGET_LIMIT: float = Field(1500.0, env="MEDIUM_BUDGET_LIMIT")
      
      # System tuning parameters
      MAX_CANDIDATES: int = 30
      DEFAULT_RECOMMENDATION_COUNT: int = 5

      class Config:
          env_file = ".env"
          env_file_encoding = "utf-8"

  settings = Settings()
  ```
* Create `.env.example` containing:
  ```bash
  LLM_PROVIDER=groq
  LLM_API_KEY=your_groq_api_key_here
  LLM_MODEL=llama3-8b-8192
  DATA_PATH=data/processed/restaurants.parquet
  SQLITE_DB_PATH=data/processed/restaurants.db
  ```

#### Task 1.2: HF Dataset Loader (`src/app/ingestion/loader.py` - `DatasetLoader`)
* Implement the `DatasetLoader` to download and cache the dataset raw files:
  ```python
  import os
  import pandas as pd
  from datasets import load_dataset

  class DatasetLoader:
      def __init__(self, dataset_name: str = "ManikaSaini/zomato-restaurant-recommendation"):
          self.dataset_name = dataset_name
          self.raw_dir = "data/raw"

      def download_dataset(self) -> pd.DataFrame:
          os.makedirs(self.raw_dir, exist_ok=True)
          print(f"Downloading dataset {self.dataset_name} from Hugging Face...")
          # Fetch dataset splits
          dataset = load_dataset(self.dataset_name)
          df = pd.DataFrame(dataset['train'])
          
          # Cache a local copy of the raw dataset
          raw_csv_path = os.path.join(self.raw_dir, "raw_restaurants.csv")
          df.to_csv(raw_csv_path, index=False)
          print(f"Raw dataset cached successfully to {raw_csv_path}")
          return df
  ```

#### Task 1.3: Schema Normalizer & Preprocessor (`src/app/ingestion/normalizer.py`)
* Cleans nulls, standardizes text casing, parses lists of cuisines, and maps estimated costs into budget bands.
  ```python
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
          normalized_df['name'] = df['name'].fillna("Unknown Restaurant").str.strip()
          normalized_df['location'] = df['location'].fillna("Unknown").str.strip()
          
          # Convert cuisine strings into standardized lowercase lists
          normalized_df['cuisines'] = df['cuisines'].fillna("various").apply(
              lambda c: [x.strip().lower() for x in str(c).split(",") if x.strip()]
          )
          
          # Enforce aggregate ratings clean parsing
          normalized_df['rating'] = pd.to_numeric(df['rating'], errors='coerce').fillna(0.0)
          
          # Parse numerical cost for two
          normalized_df['estimated_cost'] = pd.to_numeric(df['cost'], errors='coerce').fillna(0.0)
          
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
  ```

#### Task 1.4: Ingestion Pipeline Coordinator (`src/app/ingestion/pipeline.py` & `scripts/ingest.py`)
* Create `pipeline.py` to compile the loaders, normalizers, and persistence writers:
  ```python
  from src.app.ingestion.loader import DatasetLoader
  from src.app.ingestion.normalizer import SchemaNormalizer
  from src.app.config import settings
  import os
  import sqlite3

  def run_ingestion_pipeline(use_sqlite: bool = False):
      loader = DatasetLoader()
      df_raw = loader.download_dataset()
      
      normalizer = SchemaNormalizer(
          low_limit=settings.LOW_BUDGET_LIMIT,
          medium_limit=settings.MEDIUM_BUDGET_LIMIT
      )
      df_clean = normalizer.normalize(df_raw)
      
      # Persistence Writing Mode
      if use_sqlite:
          # Track Option B Persistence
          os.makedirs(os.path.dirname(settings.SQLITE_DB_PATH), exist_ok=True)
          conn = sqlite3.connect(settings.SQLITE_DB_PATH)
          # Convert list column to string to save in SQL
          df_to_sql = df_clean.copy()
          df_to_sql['cuisines'] = df_to_sql['cuisines'].apply(lambda x: ",".join(x))
          df_to_sql.to_sql("restaurants", conn, if_exists="replace", index=False)
          conn.close()
          print(f"Ingested successfully into SQLite: {settings.SQLITE_DB_PATH}")
      else:
          # Track Option A Persistence
          os.makedirs(os.path.dirname(settings.DATA_PATH), exist_ok=True)
          df_clean.to_parquet(settings.DATA_PATH, index=False)
          print(f"Ingested successfully into Parquet: {settings.DATA_PATH}")
  ```
* Create `scripts/ingest.py` containing:
  ```python
  import sys
  import os
  sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

  from src.app.ingestion.pipeline import run_ingestion_pipeline

  if __name__ == "__main__":
      # Run default Option A pipeline. Flip parameter to True for SQLite Ingestion.
      run_ingestion_pipeline(use_sqlite=False)
  ```

> [!NOTE]
> **Verification Phase 1:** Run `python scripts/ingest.py`. Verify that `data/processed/restaurants.parquet` has been created with all columns populated.

---

### Phase 2: Domain Models & Repository Engine

**Goal:** Formulate Pydantic model contracts, construct database repositories, and build the deterministic pre-filtering service engine.

#### Task 2.1: Canonical Domain Models (`src/app/models/domain.py`)
* Define canonical type models matching the requirements:
  ```python
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
  ```

#### Task 2.2: Data Access Repository (`src/app/data/repository.py` - `RestaurantRepository`)
* Abstract read operations for Parquet (Option A) and SQLite (Option B):
  ```python
  import pandas as pd
  import sqlite3
  from typing import List, Optional
  from src.app.models.domain import Restaurant

  class RestaurantRepository:
      def __init__(self, storage_type: str = "parquet", file_path: str = ""):
          self.storage_type = storage_type
          self.file_path = file_path
          self._df: Optional[pd.DataFrame] = None
          self.load()

      def load(self):
          if self.storage_type == "sqlite":
              conn = sqlite3.connect(self.file_path)
              self._df = pd.read_sql("SELECT * FROM restaurants", conn)
              # Parse back comma-joined cuisines list
              self._df['cuisines'] = self._df['cuisines'].apply(lambda x: [i.strip() for i in str(x).split(",") if i.strip()])
              conn.close()
          else:
              self._df = pd.read_parquet(self.file_path)
          print(f"Initialized RestaurantStore Repository with {len(self._df)} cached records.")

      def get_all_raw(self) -> pd.DataFrame:
          return self._df

      def get_unique_locations(self) -> List[str]:
          return sorted(self._df['location'].unique().tolist())

      def get_unique_cuisines(self) -> List[str]:
          flat_list = [c for sublist in self._df['cuisines'].tolist() for c in sublist]
          return sorted(list(set(flat_list)))
  ```

#### Task 2.3: Structured Filter Service (`src/app/services/filter_service.py`)
* Applies hard, multi-attribute constraints, sorting records by rating descending and capping the candidates at `30` entries.
  ```python
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
          
          # 2. Budget band match
          budget_mask = df_filtered['budget_band'].str.lower() == prefs.budget.lower()
          df_filtered = df_filtered[budget_mask]
          
          # 3. Cuisine match (fuzzy containment array check)
          target_cuisine = prefs.cuisine.lower()
          cuisine_mask = df_filtered['cuisines'].apply(lambda cuisines: target_cuisine in cuisines)
          df_filtered = df_filtered[cuisine_mask]
          
          # 4. Rating boundaries check
          rating_mask = df_filtered['rating'] >= prefs.min_rating
          df_filtered = df_filtered[rating_mask]
          
          # 5. Pre-sort and cap
          df_filtered = df_filtered.sort_values(by=['rating', 'estimated_cost'], ascending=[False, True])
          candidates_df = df_filtered.head(self.max_candidates)
          
          return [Restaurant(**row) for _, row in candidates_df.iterrows()]
  ```

> [!NOTE]
> **Verification Phase 2:** Write unit tests (`tests/test_filter_service.py`) verifying that the Filter Service correctly filters by location, budget band, cuisine, and ratings, and handles zero candidates gracefully.

---

### Phase 3: Integration & LLM Orchestrator Layer

**Goal:** Define system prompt structures, build multi-provider wraps with timeouts, configure regex response parsers, and assemble orchestrator pipelines.

#### Task 3.1: Provider-Agnostic LLM Client (`src/app/services/llm_client.py` - `LLMClient`)
* Establish an interface wrapping provider SDK connections:
  ```python
  import abc
  from groq import Groq
  from src.app.config import settings
  import httpx

  class BaseLLMClient(abc.ABC):
      @abc.abstractmethod
      def complete(self, prompt: str, system_instruction: str) -> str:
          pass

  class GroqClient(BaseLLMClient):
      def __init__(self):
          # Enforce strict 8.0-second timeout boundaries to handle external network latencies
          self.client = Groq(
              api_key=settings.LLM_API_KEY,
              http_client=httpx.Client(timeout=8.0)
          )
          self.model = settings.LLM_MODEL

      def complete(self, prompt: str, system_instruction: str) -> str:
          completion = self.client.chat.completions.create(
              model=self.model,
              messages=[
                  {"role": "system", "content": system_instruction},
                  {"role": "user", "content": prompt}
              ],
              temperature=0.3,
              response_format={"type": "json_object"}
          )
          return completion.choices[0].message.content
  ```

#### Task 3.2: Context Prompt Builder (`src/app/services/prompt_builder.py` - `PromptBuilder`)
* Manage prompt templates, framing instructions, JSON outputs, and strict ID grounding boundaries.
  ```python
  import json
  from typing import List
  from src.app.models.domain import Restaurant, UserPreferences

  class PromptBuilder:
      def get_system_instruction(self) -> str:
          return (
              "You are Zomato's Senior Food Guide and Critic.\n"
              "Your task is to rank and recommend restaurants from the provided candidate list.\n"
              "CRITICAL GROUNDING RULES:\n"
              "1. ONLY select restaurants from the provided candidate list. Never invent or hallucinate a restaurant.\n"
              "2. You MUST respond with a valid JSON object matching this schema:\n"
              "{\n"
              "  \"summary\": \"General summary of the matching restaurants...\",\n"
              "  \"recommendations\": [\n"
              "    {\n"
              "      \"id\": \"restaurant_id\",\n"
              "      \"rank\": 1,\n"
              "      \"explanation\": \"A highly compelling natural language rationale explaining why this spot fits their subjective preference and budget.\"\n"
              "    }\n"
              "  ]\n"
              "}\n"
              "3. Ensure the JSON is properly closed and contains no markdown conversational text."
          )

      def build_user_prompt(self, prefs: UserPreferences, candidates: List[Restaurant]) -> str:
          compact_candidates = []
          for c in candidates:
              compact_candidates.append({
                  "id": c.id,
                  "name": c.name,
                  "rating": c.rating,
                  "cost": c.estimated_cost,
                  "cuisines": c.cuisines,
                  "location": c.location
              })
          
          prompt_dict = {
              "user_preferences": {
                  "location": prefs.location,
                  "budget": prefs.budget,
                  "cuisine": prefs.cuisine,
                  "subjective_criteria": prefs.additional_preferences,
                  "top_k": prefs.top_k
              },
              "candidate_pool": compact_candidates
          }
          return json.dumps(prompt_dict, indent=2)
  ```

#### Task 3.3: Verification Parser & Fallbacks (`src/app/services/response_parser.py` - `ResponseParser`)
* Isolate JSON outputs, enforce Pydantic schema validation, execute grounding ID tests, and build database-driven fallback generators.
  ```python
  import json
  import re
  from typing import List
  from src.app.models.domain import Restaurant, UserPreferences, Recommendation, RecommendationResponse

  class ResponseParser:
      def parse_response(self, raw_text: str, candidates: List[Restaurant], prefs: UserPreferences) -> RecommendationResponse:
          try:
              # Extract JSON block using regex
              match = re.search(r'\{.*\}', raw_text, re.DOTALL)
              json_str = match.group(0) if match else raw_text
              data = json.loads(json_str)
              
              summary = data.get("summary", "Here are your curated recommendations.")
              recs_raw = data.get("recommendations", [])
              
              candidate_map = {c.id: c for c in candidates}
              recommendations = []
              
              # Enforce Bounded Grounding Assertion
              for r_dict in recs_raw:
                  r_id = r_dict.get("id")
                  if r_id in candidate_map:
                      recommendations.append(
                          Recommendation(
                              rank=r_dict.get("rank", len(recommendations) + 1),
                              restaurant=candidate_map[r_id],
                              explanation=r_dict.get("explanation", "Perfect fit for search preferences.")
                          )
                      )
              
              # Activate database ranking fallback if zero grounded results return
              if not recommendations:
                  return self.generate_fallback(candidates, prefs, "Zero grounded outputs from LLM.")
                  
              return RecommendationResponse(
                  summary=summary,
                  recommendations=recommendations[:prefs.top_k],
                  meta={"candidates_considered": len(candidates), "fallback_activated": False}
              )
              
          except Exception as e:
              return self.generate_fallback(candidates, prefs, str(e))

      def generate_fallback(self, candidates: List[Restaurant], prefs: UserPreferences, reason: str) -> RecommendationResponse:
          fallback_recs = []
          items = candidates[:prefs.top_k]
          for rank, c in enumerate(items, start=1):
              explanation = (
                  f"Highly rated dining choice in {c.location} with a {c.rating} rating. "
                  f"Matches your target cuisine ({', '.join(c.cuisines)}) and fits your budget (costing ₹{c.estimated_cost:.0f})."
              )
              fallback_recs.append(Recommendation(rank=rank, restaurant=c, explanation=explanation))
              
          return RecommendationResponse(
              summary="Here are highly rated dining options matching your criteria (System Fallback Mode).",
              recommendations=fallback_recs,
              meta={
                  "candidates_considered": len(candidates),
                  "fallback_activated": True,
                  "fallback_reason": reason
              }
          )
  ```

#### Task 3.4: Recommendation Orchestrator (`src/app/services/orchestrator.py` - `RecommendationOrchestrator`)
* Wires the component flow sequence:
  ```python
  from src.app.models.domain import UserPreferences, RecommendationResponse
  from src.app.services.filter_service import FilterService
  from src.app.services.prompt_builder import PromptBuilder
  from src.app.services.llm_client import GroqClient
  from src.app.services.response_parser import ResponseParser

  class RecommendationOrchestrator:
      def __init__(self, filter_service: FilterService):
          self.filter_service = filter_service
          self.prompt_builder = PromptBuilder()
          self.llm_client = GroqClient()
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
  ```

---

### Phase 4: Presentation Layer Implementation

Choose either **Option A (Rapid Single-Process Streamlit Hub)** or **Option B (FastAPI Backend + React Frontend)** depending on the milestone specifications in [architecture.md](file:///c:/Nextleap%20Projects%20Git/ZomatoFirstProject/docs/architecture.md).

#### Track Option A: Single-Process Streamlit App (`src/app/main.py`)
* Implements page config, sleek dark glassmorphism CSS stylesheets, sidebars, active loading indicators, and cards.
  ```python
  import streamlit as st
  import sys
  import os

  sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

  from src.app.config import settings
  from src.app.data.repository import RestaurantRepository
  from src.app.services.filter_service import FilterService
  from src.app.services.orchestrator import RecommendationOrchestrator
  from src.app.models.domain import UserPreferences

  st.set_page_config(
      page_title="Zomato AI - Gourmet Hub",
      page_icon="🍔",
      layout="wide"
  )

  # Custom styling injections
  st.markdown("""
      <style>
      .main { background-color: #0f1115; color: #e2e8f0; }
      .restaurant-card {
          background: rgba(30, 41, 59, 0.45);
          backdrop-filter: blur(10px);
          border: 1px solid rgba(255, 255, 255, 0.1);
          border-radius: 12px;
          padding: 20px;
          margin-bottom: 20px;
          transition: all 0.3s ease;
      }
      .restaurant-card:hover { transform: translateY(-4px); border-color: #ef4444; }
      .badge-rating { background-color: #22c55e; color: white; padding: 2px 6px; border-radius: 4px; font-weight: bold; }
      .badge-cost { background-color: #3b82f6; color: white; padding: 2px 6px; border-radius: 4px; font-weight: bold; }
      .explanation-box { font-style: italic; color: #94a3b8; border-left: 3px solid #ef4444; padding-left: 10px; margin-top: 10px; }
      </style>
  """, unsafe_allow_html=True)

  @st.cache_resource
  def get_services():
      repo = RestaurantRepository(storage_type="parquet", file_path=settings.DATA_PATH)
      filter_svc = FilterService(repo, settings.MAX_CANDIDATES)
      orch = RecommendationOrchestrator(filter_svc)
      return repo, orch

  repo, orchestrator = get_services()

  st.title("🎯 Zomato AI Recommendation Hub")
  st.markdown("Your custom gourmet matching portal based on real-world eating patterns.")

  with st.sidebar:
      st.header("Search Parameters")
      locations = repo.get_unique_locations()
      cuisines = repo.get_unique_cuisines()
      
      selected_location = st.selectbox("Where to eat?", options=locations)
      selected_cuisine = st.selectbox("What cuisine?", options=cuisines)
      selected_budget = st.radio("Budget Tier", options=["Low", "Medium", "High"], index=1)
      selected_rating = st.slider("Min Rating", 0.0, 5.0, 3.5, 0.1)
      subjective_pref = st.text_area("Subjective mood/preferences", placeholder="e.g. cozy spot for date night with low music")
      top_k = st.number_input("Max recommendations", 1, 10, 5)
      submit = st.button("Generate Suggestions", type="primary", use_container_width=True)

  if submit:
      prefs = UserPreferences(
          location=selected_location,
          budget=selected_budget.lower(),
          cuisine=selected_cuisine.lower(),
          min_rating=selected_rating,
          additional_preferences=subjective_pref,
          top_k=top_k
      )
      
      with st.spinner("⚡ Curating options matching your gourmet palette..."):
          res = orchestrator.get_recommendations(prefs)
          
      if not res.recommendations:
          st.warning("⚠️ No restaurants match these filters.")
      else:
          st.success("Suggestions curated successfully.")
          st.info(res.summary)
          
          for rec in res.recommendations:
              rest = rec.restaurant
              cuisine_tags = " ".join([f"<span style='background:#334155; padding:2px 6px; border-radius:4px; margin-right:4px; font-size:12px;'>{c}</span>" for c in rest.cuisines])
              
              st.markdown(f"""
                  <div class="restaurant-card">
                      <div style="display:flex; justify-content:space-between; align-items:center;">
                          <h3 style="margin:0; color:#ffffff;">#{rec.rank} - {rest.name}</h3>
                          <div>
                              <span class="badge-rating">⭐ {rest.rating:.1f}</span>
                              <span class="badge-cost">💰 ₹{rest.estimated_cost:.0f}</span>
                          </div>
                      </div>
                      <p style="margin-top:6px; font-size:14px; color:#cbd5e1;">📍 {rest.location}</p>
                      <div style="margin-top:8px; margin-bottom:12px;">{cuisine_tags}</div>
                      <div class="explanation-box">
                          <strong>AI Recommendation Rationale:</strong><br>
                          "{rec.explanation}"
                      </div>
                  </div>
              """, unsafe_allow_html=True)
  ```

---

#### Track Option B: FastAPI Backend routes (`src/app/api/routes.py`)
* If setting up a distributed web application, build a robust FastAPI controller interface:
  ```python
  from fastapi import APIRouter, Depends, HTTPException, status
  from src.app.models.domain import UserPreferences, RecommendationResponse
  from src.app.config import settings
  from src.app.data.repository import RestaurantRepository
  from src.app.services.filter_service import FilterService
  from src.app.services.orchestrator import RecommendationOrchestrator

  router = APIRouter(prefix="/api/v1")

  # Setup Dependency Injections
  def get_orchestrator() -> RecommendationOrchestrator:
      repo = RestaurantRepository(storage_type="sqlite", file_path=settings.SQLITE_DB_PATH)
      filter_svc = FilterService(repo, settings.MAX_CANDIDATES)
      return RecommendationOrchestrator(filter_svc)

  @router.post("/recommendations", response_model=RecommendationResponse)
  def create_recommendations(prefs: UserPreferences, orchestrator: RecommendationOrchestrator = Depends(get_orchestrator)):
      try:
          response = orchestrator.get_recommendations(prefs)
          return response
      except Exception as e:
          raise HTTPException(
              status_code=status.HTTP_502_BAD_GATEWAY,
              detail=f"Recommendation engine encountered an exception: {str(e)}"
          )

  @router.get("/health")
  def health_check():
      return {"status": "healthy", "service": "Zomato AI Recommendation Server"}
  ```

---

### Phase 5: Fault-Tolerance & Production Polish

**Goal:** Wrap HTTP calls inside retry blocks, assert strict grounded ID matches to block hallucinations, and run complete Pytest test suites.

#### Task 5.1: Write Unit Test Suites (`tests/test_filter_service.py`)
* Create comprehensive test boundary scripts inside `/tests`:
  ```python
  import pytest
  import pandas as pd
  from src.app.models.domain import UserPreferences, Restaurant
  from src.app.data.repository import RestaurantRepository
  from src.app.services.filter_service import FilterService

  @pytest.fixture
  def mock_repository(tmp_path):
      data = {
          "id": ["r00001", "r00002", "r00003"],
          "name": ["Chili Cafe", "Royal Spice", "Bella Italian"],
          "location": ["Delhi", "Delhi", "Bangalore"],
          "cuisines": [["cafe", "bakery"], ["indian", "spicy"], ["italian", "pasta"]],
          "rating": [4.5, 3.2, 4.8],
          "estimated_cost": [400.0, 600.0, 1200.0],
          "budget_band": ["low", "medium", "medium"]
      }
      df = pd.DataFrame(data)
      file_path = tmp_path / "test_restaurants.parquet"
      df.to_parquet(file_path, index=False)
      return RestaurantRepository(storage_type="parquet", file_path=str(file_path))

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
  ```

#### Task 5.2: Run Validation & Verification Commands
* Run all unit and integration tests inside the PowerShell terminal:
  ```powershell
  # Run complete testing suite
  pytest tests/ -v

  # Test coverage reporting
  pytest --cov=src tests/
  ```

---

## 📅 Milestones & Expected Deliverables Summary

| Milestone | Deliverable File/Path | Expected Outcome | Verification Metric |
| :--- | :--- | :--- | :--- |
| **Milestone 1** | `data/processed/restaurants.parquet` | Clean, standardized dataset store | Schema normalization matching column headers |
| **Milestone 2** | `src/app/services/filter_service.py` | Fast deterministic candidate lists capped at 30 items | Unit tests passing for all filter parameters |
| **Milestone 3** | `src/app/services/orchestrator.py` | Connected inference workflow logic | Integration test verifying parser execution |
| **Milestone 4** | `src/app/main.py` | UI presentation layer | Interactive card layout renders in Streamlit in $< 8.0\text{ s}$ |
| **Milestone 5** | Complete Pytest suite | Full error mitigations and fallback rankings verified | Zero test failures under `pytest tests/` |
