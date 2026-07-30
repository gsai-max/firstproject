# Phase-Wise Detailed Implementation Plan: AI-Powered Discovery Engine

This implementation plan outlines the step-by-step engineering roadmap for building the Blinkit AI-Powered Discovery Engine. It translates the core requirements, schemas, data flows, and component designs defined in [context.md](file:///c:/Nextleap%20Projects%20Git/ProductManagerFellowshipGraduationProject/docs/context.md) and [architecture.md](file:///c:/Nextleap%20Projects%20Git/ProductManagerFellowshipGraduationProject/docs/architecture.md) into concrete actionable tasks.

---

### 1. Requirements Traceability

The table below maps requirements from the [Project Context](file:///c:/Nextleap%20Projects%20Git/ProductManagerFellowshipGraduationProject/docs/context.md) and [Architecture Specification](file:///c:/Nextleap%20Projects%20Git/ProductManagerFellowshipGraduationProject/docs/architecture.md) to specific implementation deliverables:

| Req ID | Requirement Description | Component / Phase | Verification Method |
|---|---|---|---|
| **REQ-01** | Scrape Blinkit Android reviews from Google Play Store | Phase 2 (Play Store Scraper) | Record count assertion + spot-check sample reviews |
| **REQ-02** | Scrape Blinkit iOS reviews from Apple App Store | Phase 2 (App Store Scraper) | Record count assertion + spot-check sample reviews |
| **REQ-03** | Scrape Blinkit discussions from Reddit | Phase 2 (Reddit Scraper) | Record count + subreddit distribution check |
| **REQ-04** | Scrape Blinkit tweets & posts from Twitter/X | Phase 2 (Twitter Scraper) | Record count + date range verification |
| **REQ-05** | Crawl forum & blog posts about Q-commerce | Phase 2 (Forum Crawler) | Record count + source URL validation |
| **REQ-06** | Crawl YouTube video review comments | Phase 2 (YouTube Scraper) | Video comment count + API response validation |
| **REQ-07** | Crawl Quora Q&A discussions on Blinkit & competitors | Phase 2 (Quora Crawler) | Record count + topic parsing check |
| **REQ-08** | Ingest Consumer Forum complaint threads | Phase 2 (Consumer Forum Scraper) | Complaint count & sentiment validation |
| **REQ-09** | Scrape competitor reviews (Zepto & Instamart) | Phase 2 (Competitor Scrapers) | Cross-app benchmarking dataset verification |
| **REQ-10** | Save raw ingestion payloads to Local Data Lake (data/raw/) / AWS S3 Fallback | Phase 2 (S3 Data Lake Store) | S3 bucket upload assertion & JSONL validity |
| **REQ-11** | Clean, normalize (≥8 words, no emojis, English only), and deduplicate raw data | Phase 3 (Data Cleaner & Deduplicator) | Dedup stats + schema validation checks |
| **REQ-12** | Vectorize cleaned records (HuggingFace MiniLM) & index in Local Vector DB (ChromaDB) | Phase 3 (Vector Store Service) | Vector query recall & similarity search test |
| **REQ-13** | **Agent 1: Theme Extraction Agent** (Extract operational & product themes) | Phase 4 (Theme Agent) | Theme frequency breakdown validation |
| **REQ-14** | **Agent 2: Emotion Agent** (Extract Risk, Uncertainty, Decision Fatigue) | Phase 4 (Emotion Agent) | Emotion spectrum distribution audit |
| **REQ-15** | **Agent 3: Habit Detection Agent** (Extract Trigger -> Action -> Reward loops) | Phase 4 (Habit Agent) | Habit Loop schema & trigger-action check |
| **REQ-16** | **Agent 4: JTBD Agent** (Identify underlying human needs vs. categories) | Phase 4 (JTBD Agent) | Jobs-To-Be-Done mapping accuracy test |
| **REQ-17** | **Agent 5: Segment Discovery Agent** (Discover consumer archetypes) | Phase 4 (Segment Agent) | Archetype cluster distribution audit |
| **REQ-18** | **Agent 6: Contradiction Agent** (Surface stated preference vs. actual habit gaps) | Phase 4 (Contradiction Agent) | Contradiction pattern detection test |
| **REQ-19** | Build interconnected **Behavior Graph Engine** | Phase 4 (Behavior Graph Builder) | Graph node/edge traversal & JSON schema test |
| **REQ-20** | **Multi-LLM Consensus Validation Engine** (2/3 majority rule across Groq Llama-3.1, HuggingFace Llama-3.2, Free Open Models) | Phase 4.5 (Consensus Validator) | 3-model agreement pass/fail assertion |
| **REQ-21** | **Statistical Confidence & Variance Validation Engine** | Phase 4.5 (Statistical Validator) | Confidence score math & weight assertions |
| **REQ-22** | **Human Audit Sampling Framework** (200 review benchmark target ≥90% agreement) | Phase 4.5 (Human Audit Tool) | Human vs AI annotation agreement score |
| **REQ-23** | **Qualitative User Interview Verification** (20 user interview alignment) | Phase 4.5 (Interview Alignment) | Qualitative finding matrix validation |
| **REQ-24** | Continuous monitoring & emerging pattern detection | Phase 4 (Pattern Detector) | Trend velocity score & spike detection assertions |
| **REQ-25** | Automated growth hypothesis generation | Phase 4 (Hypothesis Generator) | Template compliance & confidence score audit |
| **REQ-26** | Actionable PM experiment recommendation engine | Phase 4 (Experiment Recommender) | A/B test spec validation |
| **REQ-27** | Closed-loop learning from experiment outcomes | Phase 4/5 (Closed-Loop Learner) | Feedback loop confidence score update test |
| **REQ-28** | Expose FastAPI endpoints for Behavior Graphs, Archetypes, 6 Agents, & Consensus | Phase 5 (FastAPI Server) | HTTP integration test assertions |
| **REQ-29** | Build premium interactive React PM Dashboard | Phase 6 (Frontend Dashboard) | Visual rendering + responsive viewport checks |
| **REQ-30** | End-to-end Python workflow pipeline reproducibility via CLI | Phase 7 (E2E Integration) | End-to-end pipeline execution test |

---

## 2. Environment Progression

```
[ Local Development ] ────> [ Staging / E2E Verification ] ────> [ Production / Go-Live ]
  - Cached scrape snapshots     - Live scraping across 10 sources  - Deployed backend + frontend
  - Local Parquet & Vector DB   - Full Python multi-agent pipeline execution      - Pre-computed insights served
  - Mock/dev LLM keys           - Multi-LLM Consensus (3 models)   - Render + Vercel hosting
  - Pytest unit tests            - Integration test suites          - Final demonstration
```

---

## 3. Timeline & Parallelization

* **Total Indicative Duration**: 3–4 weeks.
* **Parallelization Potential**: Frontend development (Phase 6) can run concurrently with Multi-Agent Layer (Phase 4) once the API JSON contract (Phase 5) is established.

---

## 4. Target Project Directory Structure

```
ProductManagerFellowshipGraduationProject/
├── docs/
│   ├── problemstatement.md         # Raw source specification
│   ├── context.md                  # Business & domain context
│   ├── architecture.md             # Technical design blueprint
│   ├── implementation-plan.md      # Phase-wise roadmap (This File)
│   └── deployment-plan.md          # Hosting & CI/CD instructions
├── data/
│   ├── raw/                        # Raw S3 JSONL backups per source
│   │   ├── play_store/
│   │   ├── app_store/
│   │   ├── reddit/
│   │   ├── twitter/
│   │   ├── youtube/
│   │   ├── quora/
│   │   ├── forums/
│   │   ├── blinkit/
│   │   ├── zepto/
│   │   └── instamart/
│   ├── processed/                  # Cleaned Parquet & Vector Store metadata
│   │   ├── all_normalized_reviews.json
│   │   └── processed_records.parquet
│   └── insights/                   # Multi-agent outputs & behavior graph
│       ├── agent_theme_output.json
│       ├── agent_emotion_output.json
│       ├── agent_habit_output.json
│       ├── agent_jtbd_output.json
│       ├── agent_segment_output.json
│       ├── agent_contradiction_output.json
│       ├── behavior_graph.json
│       ├── multi_llm_consensus_report.json
│       └── insights_final.json
├── src/
│   └── app/
│       ├── __init__.py
│       ├── config.py               # Centralized configuration (pydantic-settings)
│       ├── api_server.py           # FastAPI entrypoint
│       ├── models/
│       │   ├── __init__.py
│       │   └── domain.py           # Pydantic domain models (HabitLoop, JTBD, Archetype, Consensus)
│       ├── scrapers/
│       │   ├── __init__.py
│       │   ├── play_store.py       # Google Play Store scraper
│       │   ├── app_store.py        # Apple App Store scraper
│       │   ├── reddit_scraper.py   # Reddit scraper (PRAW)
│       │   ├── twitter_scraper.py  # Twitter/X scraper
│       │   ├── youtube_scraper.py  # YouTube comment crawler
│       │   ├── quora_crawler.py    # Quora Q&A crawler
│       │   ├── forum_crawler.py    # Consumer complaints crawler
│       │   └── competitor_scrapers.py # Zepto & Instamart scraper
│       ├── processing/
│       │   ├── __init__.py
│       │   ├── cleaner.py          # Text cleaning & normalization
│       │   ├── deduplicator.py     # Exact & near-duplicate removal
│       │   └── vector_store.py     # HuggingFace MiniLM vector index (Local ChromaDB)
│       ├── agents/                 # The 6 Multi-Agent Modules
│       │   ├── __init__.py
│       │   ├── theme_agent.py      # Agent 1: Theme Extraction
│       │   ├── emotion_agent.py    # Agent 2: Emotional Spectrum Extraction
│       │   ├── habit_agent.py      # Agent 3: Habit Loop Detector (Trigger -> Action -> Reward)
│       │   ├── jtbd_agent.py       # Agent 4: Jobs-To-Be-Done Analyzer
│       │   ├── segment_agent.py    # Agent 5: Consumer Archetype Finder
│       │   └── contradiction_agent.py # Agent 6: Stated vs. Actual Contradiction Finder
│       ├── analysis/
│       │   ├── __init__.py
│       │   ├── behavior_graph.py   # Behavior Graph builder
│       │   ├── multi_llm_consensus.py # 2/3 Consensus Engine (Groq Llama-3.1 + HF Llama-3.2 + Free Open Models)
│       │   ├── statistical_validator.py # Statistical score & variance calculation
│       │   └── human_audit.py      # Human audit benchmark tool
│       ├── services/
│       │   ├── __init__.py
│       │   ├── llm_client.py       # Multi-LLM client (Groq, HuggingFace Inference API, Free Open Models)
│       │   ├── orchestrator.py # Workflow pipeline orchestrator
│       │   └── prompt_builder.py   # Prompts for all 6 agents
│       └── api/
│           ├── __init__.py
│           ├── routes.py           # FastAPI route definitions
│           └── schemas.py          # API request/response DTOs
├── frontend/                       # React + Vite dashboard
│   ├── src/
│   │   ├── App.jsx
│   │   ├── index.css               # Glassmorphism dark theme
│   │   └── components/
│   │       ├── ExecutiveSummary.jsx
│   │       ├── BehaviorGraphView.jsx
│   │       ├── EmotionSpectrumCard.jsx
│   │       ├── HabitLoopVisualizer.jsx
│   │       ├── JTBDMatrix.jsx
│   │       ├── ArchetypeSegmentGrid.jsx
│   │       ├── ContradictionCard.jsx
│   │       ├── ConsensusReportModal.jsx
│   │       └── PipelineStatus.jsx
│   └── vercel.json
├── scripts/
│   └── analyze_only.py             # CLI for analysis stage only
├── tests/
│   ├── test_scrapers.py
│   ├── test_cleaner.py
│   ├── test_sentiment.py
│   ├── test_tagger.py
│   ├── test_theme_extractor.py
│   ├── test_insight_synthesizer.py
│   ├── test_validator.py
│   └── test_api.py
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md
```

---

## 5. Phase-Wise Implementation

---

### Phase 0: Repository Skeleton, Environment & Testing Setup

* **Objective**: Create the baseline project environment, initialize Python dependencies, define environment variables, and construct the target directory structure.
* **Tasks**:
  1. Initialize Python virtual environment (`.venv`) and create `requirements.txt`:
     ```text
     fastapi>=0.100.0
     uvicorn>=0.22.0
     pandas>=2.0.0
     pyarrow>=12.0.0
     pydantic>=2.0.0
     pydantic-settings>=2.0.0
     groq>=0.9.0
     google-play-scraper>=1.2.4
     app-store-scraper>=0.3.5
     praw>=7.7.0
     snscrape>=0.7.0
     requests>=2.31.0
     beautifulsoup4>=4.12.0
     pytest>=7.4.0
     httpx>=0.24.0
     ```
  2. Create the full source directory structure as defined in §4 above (all `__init__.py` files, empty module stubs).
  3. Create `.env.example`:
     ```bash
     LLM_PROVIDER=groq
     LLM_API_KEY=your_groq_api_key_here
     LLM_MODEL=llama-3.1-8b-instant
     REDDIT_CLIENT_ID=your_reddit_client_id
     REDDIT_CLIENT_SECRET=your_reddit_client_secret
     REDDIT_USER_AGENT=blinkit-discovery-engine/1.0
     ```
  4. Create `.gitignore` excluding `.venv/`, `.env`, `data/raw/`, `data/processed/`, `data/insights/`, `__pycache__/`, `node_modules/`, `frontend/dist/`.
  5. Initialize `pytest` configuration and run a dummy assertion to verify the testing pipeline.
* **Deliverables**: Skeleton directory layout, `requirements.txt`, `.env.example`, `.gitignore`, passing dummy test.
* **Exit Criteria**: `pytest tests/` runs successfully with 0 errors on the skeleton.
* **Risks & Mitigation**: Dependency conflicts on Windows. Mitigated by pinning versions and using `venv` isolation.
* **Dependencies**: None.

---

### Phase 1: Domain Models & Configuration Loader

* **Objective**: Define all Pydantic domain models and the centralized configuration loader used across the entire pipeline.
* **Tasks**:
  1. Implement configuration loader (`src/app/config.py`) using `pydantic-settings`:
     ```python
     from pydantic_settings import BaseSettings
     from pydantic import Field

     class Settings(BaseSettings):
         LLM_PROVIDER: str = Field("groq", env="LLM_PROVIDER")
         LLM_API_KEY: str = Field(..., env="LLM_API_KEY")
         LLM_MODEL: str = Field("llama-3.1-8b-instant", env="LLM_MODEL")

         REDDIT_CLIENT_ID: str = Field("", env="REDDIT_CLIENT_ID")
         REDDIT_CLIENT_SECRET: str = Field("", env="REDDIT_CLIENT_SECRET")
         REDDIT_USER_AGENT: str = Field("blinkit-discovery-engine/1.0", env="REDDIT_USER_AGENT")

         # Data paths
         RAW_DATA_DIR: str = Field("data/raw", env="RAW_DATA_DIR")
         PROCESSED_DATA_DIR: str = Field("data/processed", env="PROCESSED_DATA_DIR")
         INSIGHTS_DIR: str = Field("data/insights", env="INSIGHTS_DIR")

         # Pipeline tuning
         MAX_REVIEWS_PLAY_STORE: int = 5000
         MAX_REVIEWS_APP_STORE: int = 2000
         MAX_POSTS_REDDIT: int = 1000
         MAX_TWEETS: int = 1500
         SENTIMENT_BATCH_SIZE: int = 50
         THEME_BATCH_SIZE: int = 100
         LLM_TIMEOUT_SECONDS: float = 10.0

         class Config:
             env_file = ".env"
             env_file_encoding = "utf-8"

     settings = Settings()
     ```

  2. Define canonical domain models (`src/app/models/domain.py`):
     ```python
     from pydantic import BaseModel, Field
     from typing import List, Optional, Dict
     from datetime import datetime

     class RawFeedbackRecord(BaseModel):
         id: str
         source: str  # play_store | app_store | reddit | twitter | forums
         platform: str
         text: str
         rating: Optional[float] = None
         date: str
         author: str
         metadata: Dict = Field(default_factory=dict)
         scraped_at: str

     class ProcessedFeedbackRecord(BaseModel):
         id: str
         source: str
         text: str
         text_clean: str
         rating: Optional[float] = None
         date: str
         sentiment: str  # positive | neutral | negative
         sentiment_score: float
         categories: List[str] = Field(default_factory=list)
         topics: List[str] = Field(default_factory=list)
         behaviour_signals: List[str] = Field(default_factory=list)
         word_count: int
         source_url: Optional[str] = None
         scraped_at: str

     class RepresentativeQuote(BaseModel):
         record_id: str
         text: str
         source: Optional[str] = None

     class Theme(BaseModel):
         id: str
         name: str
         description: str
         frequency: str  # high | medium | low
         category_relevance: str  # high | medium | low
         source: str
         representative_quotes: List[RepresentativeQuote] = Field(default_factory=list)
         research_question_mapping: List[str] = Field(default_factory=list)

     class Insight(BaseModel):
         id: str
         title: str
         statement: str
         evidence_strength: str  # strong | moderate | weak
         sources_corroborating: List[str] = Field(default_factory=list)
         source_count: int
         supporting_themes: List[str] = Field(default_factory=list)
         representative_quotes: List[RepresentativeQuote] = Field(default_factory=list)
         research_questions_addressed: List[str] = Field(default_factory=list)
         user_segment: str
         recommended_action: str
         impact_potential: str  # high | medium | low
         priority_rank: int

     class InsightReport(BaseModel):
         insights: List[Insight]
         meta: Dict

     class PipelineStatus(BaseModel):
         stage: str
         status: str  # running | completed | failed
         started_at: str
         completed_at: Optional[str] = None
         records_processed: int = 0
         error: Optional[str] = None
     ```

* **Deliverables**: Configuration module, domain model definitions.
* **Exit Criteria**: All models instantiate correctly with sample data; `Settings` loads from `.env.example`.
* **Risks & Mitigation**: Schema changes during development. Mitigated by centralizing all models in `domain.py` for single-source-of-truth updates.
* **Dependencies**: Phase 0.

---

### Phase 2: Data Collection Layer — 10 Multi-Source Scrapers & S3 Data Lake

* **Objective**: Implement 10 scraper/ingestion channels to collect public feedback about Blinkit and quick commerce. Raw data fetching targets are significantly expanded to 157,630 raw records collected across 10 multi-source channels (Play Store, App Store, Reddit, Twitter, YouTube, Quora, Forums, Zepto, Instamart, Tickets) prior to cleaning, emoji/script removal, and deduplication. Save immutable raw JSONL blobs to Local Data Lake (data/raw/) & AWS S3 Fallback (`data/raw/ (with optional s3://blinkit-discovery-engine-raw/ fallback)`).
* **Tasks**:
  1. **Play Store Scraper** (`src/app/scrapers/play_store.py`): Fetch up to **30,000** Android reviews (`com.grofers.customerapp`).
  2. **App Store Scraper** (`src/app/scrapers/app_store.py`): Fetch up to **15,000** iOS reviews.
  3. **Reddit Scraper** (`src/app/scrapers/reddit_scraper.py`): Fetch up to **5,000** posts/comments via PRAW (`r/india`, `r/bangalore`, `r/delhi`, etc.).
  4. **Twitter/X Scraper** (`src/app/scrapers/twitter_scraper.py`): Fetch up to **10,000** tweets on Q-commerce friction and missing categories.
  5. **YouTube Scraper** (`src/app/scrapers/youtube_scraper.py`): Fetch up to **5,000** comments on unboxing & review videos.
  6. **Quora Crawler** (`src/app/scrapers/quora_crawler.py`): Fetch up to **2,500** Q&A discussions comparing Blinkit vs. competitors.
  7. **Consumer Forum Crawler** (`src/app/scrapers/forum_crawler.py`): Fetch up to **2,500** complaint threads (ConsumerComplaints.in, etc.).
  8. **Blinkit On-Platform Scraper** (`src/app/scrapers/play_store.py`): Ingest direct app store reviews.
  9. **Competitor Scrapers** (`src/app/scrapers/competitor_scrapers.py`): Fetch **10,000+** Zepto & Instamart reviews for cross-app behavior benchmarking.
  10. **Local Data Lake (data/raw/) & AWS S3 Fallback Storage**: Persist raw scraped payloads as JSONL blobs (`data/raw/<source>/reviews_YYYYMMDD.jsonl`).

* **Deliverables**: 10 scraper modules, S3 ingestion script, raw JSONL data lake store (157,630 raw records ingested dataset).
* **Exit Criteria**: `python scripts/scrape_only.py` populates `data/raw/` with JSONL files across all 10 sources.


---

### Phase 3: Data Processing & Vectorization Layer — Clean, Deduplicate, Vector Store Indexing

* **Objective**: Transform raw scraped data into clean, enriched, and vectorized records indexed in ChromaDB / FAISS (Local Vector Database).
* **Tasks**:
  1. **Data Cleaner** (`src/app/processing/cleaner.py`):
     * Strip reviews $<8$ words, remove emojis, HTML, and non-English scripts (Devanagari, Tamil, Telugu, etc.).
     * Sanitize PII and non-essential fields.
  2. **Deduplicator** (`src/app/processing/deduplicator.py`):
     * SHA-256 hash exact deduplication + Jaccard similarity near-deduplication ($\ge 85\%$).
  3. **Vector Store Service** (`src/app/processing/vector_store.py`):
     * Vectorize cleaned text using **Sentence-Transformers `sentence-transformers/all-MiniLM-L6-v2`** (Hugging Face / Open Source)**.
     * Index vectors in **ChromaDB / FAISS (Local Vector Database)** vector database with metadata payloads (`source`, `rating`, `date`).
     * Expose semantic RAG search and similarity retrieval methods for downstream multi-agent layer.

* **Deliverables**: Cleaner, deduplicator, vector store module, processed Parquet file.
* **Exit Criteria**: Processed records indexed in vector database; vector similarity recall test passes.

                     result_map = {r["id"]: r for r in results.get("results", [])}
                     for record in batch:
                         if record.id in result_map:
                             record.sentiment = result_map[record.id]["sentiment"]
                             record.sentiment_score = result_map[record.id]["score"]
                 except Exception as e:
                     print(f"Sentiment batch {i} failed: {e}. Using fallback.")
                     for record in batch:
                         record.sentiment, record.sentiment_score = self._fallback_classify(record)
             return records

         def _system_instruction(self) -> str:
             return (
                 "You are a sentiment analysis engine. Classify each review.\n"
                 "Return JSON: {\"results\": [{\"id\": \"...\", \"sentiment\": \"positive|neutral|negative\", \"score\": 0.0-1.0}]}\n"
                 "Score: 0.0 = most negative, 1.0 = most positive."
             )

         def _build_prompt(self, batch: list) -> str:
             return json.dumps({"reviews": batch}, indent=2)

         def _fallback_classify(self, record):
             negative_keywords = ["worst", "terrible", "awful", "hate", "disgusting", "pathetic", "fraud"]
             positive_keywords = ["love", "great", "amazing", "excellent", "best", "awesome", "perfect"]
             text = record.text_clean
             neg = sum(1 for w in negative_keywords if w in text)
             pos = sum(1 for w in positive_keywords if w in text)
             if neg > pos: return "negative", 0.2
             elif pos > neg: return "positive", 0.8
             return "neutral", 0.5
     ```

  4. **Category & Topic Tagger** (`src/app/processing/tagger.py`):
     * LLM-based multi-label classification with a predefined taxonomy.
     * **Category taxonomy**: `groceries`, `snacks`, `beverages`, `personal_care`, `baby_products`, `pet_supplies`, `electronics`, `household`, `pharmacy`, `beauty`, `stationery`, `toys`, `general`.
     * **Topic taxonomy**: `discovery`, `pricing`, `delivery`, `trust`, `habit`, `quality`, `variety`, `ui_navigation`, `recommendation`, `comparison`, `wishlist`, `missing_product`, `customer_support`.
     * **Behaviour signal taxonomy**: `repeat_purchase`, `category_exploration`, `category_switch`, `wishlist_request`, `missing_product_report`, `new_user`, `power_user`.
     * Process in batches; map multi-label results back onto records.

  5. **Processing Orchestrator** (within `src/app/services/orchestrator.py`):
     * Load raw JSONL files from all sources.
     * Run cleaner → deduplicator → sentiment → tagger in sequence.
     * Persist processed records as Parquet files under `data/processed/`.
     * Log processing stats (records in/out, duplicates removed, sentiment distribution).

* **Deliverables**: Cleaner, deduplicator, sentiment classifier, tagger modules, processed Parquet files.
* **Exit Criteria**: Running `python scripts/run_pipeline.py --stage process` produces Parquet files with all enrichment fields populated. Sentiment distribution is reasonable (not 100% one class). Category/topic tags are non-empty for ≥80% of records.
* **Risks & Mitigation**:
  * Groq rate limits during batch classification → Implement exponential backoff + fallback classifiers.
  * Hinglish text confusing sentiment classifier → Include Hinglish examples in few-shot prompts.
* **Dependencies**: Phase 2.

> [!NOTE]
> **Verification Phase 3:** Run `pytest tests/test_cleaner.py tests/test_sentiment.py tests/test_tagger.py`. Verify that processed Parquet files contain valid enrichment columns. Sample 20 records and manually validate sentiment + tag accuracy.

---

### Phase 4: Multi-Agent AI Analysis Layer & Behavior Graph Engine

* **Objective**: Implement the **6 specialized AI Agents** and synthesize their outputs into an interconnected **Behavior Graph** and **Consumer Archetype Matrix**.
* **Tasks**:
  1. **Agent 1: Theme Extraction Agent** (`src/app/agents/theme_agent.py`): Extract operational, product discovery, pricing, and trust themes with percentage breakdowns.
  2. **Agent 2: Emotion Agent** (`src/app/agents/emotion_agent.py`): Extract underlying emotional profiles (**Risk Perception**, **Uncertainty**, **Cognitive Decision Fatigue**).
  3. **Agent 3: Habit Detection Agent** (`src/app/agents/habit_agent.py`): Extract **Habit Loops** (*Trigger* $\rightarrow$ *Action* $\rightarrow$ *Reward* $\rightarrow$ *Exploration Impact*).
  4. **Agent 4: JTBD Agent** (`src/app/agents/jtbd_agent.py`): Identify Jobs-To-Be-Done human needs vs. static categories.
  5. **Agent 5: Segment Discovery Agent** (`src/app/agents/segment_agent.py`): Discover consumer archetypes (*Routine Buyers*, *Explorers*, *Value Seekers*, *Parents*, *Health Focused*, *Convenience Users*).
  6. **Agent 6: Contradiction Agent** (`src/app/agents/contradiction_agent.py`): Surface counter-intuitive gaps between stated desires vs. actual purchasing habits.
  7. **Behavior Graph Engine** (`src/app/analysis/behavior_graph.py`): Merge agent outputs into a directed network graph mapping triggers, habits, emotional barriers, and category expansion opportunities.

* **Deliverables**: 6 agent modules, behavior graph builder, JSON files (`behavior_graph.json`, `agent_*_output.json`).
* **Exit Criteria**: Running `python scripts/analyze_only.py` populates output files for all 6 agents and constructs a valid behavior graph.

---

### Phase 4.5: Quality Validation Layer — Multi-LLM Consensus Engine

* **Objective**: Implement the 4-tier validation engine to guarantee empirical rigor and eliminate AI hallucinations.
* **Tasks**:
  1. **Multi-LLM Consensus Engine** (`src/app/analysis/multi_llm_consensus.py`):
     * Pass candidate insights independently to 3 frontier LLMs: **Groq Llama-3.1**, **HuggingFace Llama-3.2**, and **Free Open Models**.
     * Enforce the **2/3 Majority Rule** (accepted only if $\ge 2$ of 3 models approve).
  2. **Statistical Confidence Validator** (`src/app/analysis/statistical_validator.py`):
     * Compute confidence scores from theme frequency, source diversity, sentiment severity, and variance.
  3. **Human Audit Benchmark Tool** (`src/app/analysis/human_audit.py`):
     * Benchmark AI extractions against 200 manually annotated raw sample reviews (Target: **$\ge 90\%$ agreement**).
  4. **User Interview Verification**: Align AI findings against qualitative insights from 20 user interviews.

* **Deliverables**: Multi-LLM consensus engine, statistical validator, human audit tool, consensus report (`multi_llm_consensus_report.json`).
* **Exit Criteria**: Consensus engine executes 2/3 agreement check across Groq Llama-3.1, HuggingFace Llama-3.2, and Free Open Models.

     * Secondary LLM validation pass to check for hallucinated statistics.
     * Generate `data/insights/validation_report.json` with pass/fail counts and flagged items.

* **Deliverables**: LLM client, prompt builder, theme extractor, insight synthesizer, validator modules, insight JSON files.
* **Exit Criteria**: Running `python scripts/analyze_only.py` generates 10–20 validated insights with research question coverage across all 8 questions. Validation report shows >80% insights passing all checks.
* **Risks & Mitigation**:
  * LLM hallucinating themes not grounded in data → Cross-source validator catches ungrounded quotes; secondary LLM pass validates.
  * Token limits exceeded on large batches → Dynamic batch sizing; truncate long records to 300 chars in prompts.
  * Groq API downtime → Implement retry with exponential backoff; cache intermediate results.
* **Dependencies**: Phase 3.

> [!NOTE]
> **Verification Phase 4:** Run `pytest tests/test_theme_extractor.py tests/test_insight_synthesizer.py tests/test_validator.py`. Verify that `insights_final.json` contains ≥10 insights, each with `evidence_strength` and `research_questions_addressed` populated. Check `validation_report.json` for zero critical failures.

---

### Phase 5: FastAPI Backend & API Layer

* **Objective**: Expose REST API endpoints serving insights, behavior graphs, segment archetypes, agent outputs, and consensus validation metrics to the React dashboard.
* **Tasks**:
  1. **API Endpoints (`src/app/api/routes.py`)**:
     * `GET /api/v1/health` — Health check.
     * `GET /api/v1/insights` — Ranked validated insights with consensus scores.
     * `GET /api/v1/behavior-graph` — Directed behavior graph nodes & edges.
     * `GET /api/v1/archetypes` — Consumer segment archetypes matrix.
     * `GET /api/v1/agents/theme` — Agent 1 theme extractions.
     * `GET /api/v1/agents/emotion` — Agent 2 emotion profiles.
     * `GET /api/v1/agents/habit` — Agent 3 Habit Loops.
     * `GET /api/v1/agents/jtbd` — Agent 4 Jobs-To-Be-Done items.
     * `GET /api/v1/agents/contradiction` — Agent 6 contradiction patterns.
     * `GET /api/v1/validation/report` — Multi-LLM consensus pass rates & audit stats.
     * `POST /api/v1/pipeline/run` — Trigger pipeline execution cascade.

* **Deliverables**: FastAPI server, route definitions, API DTO schemas.
* **Exit Criteria**: `uvicorn src.app.api_server:app --reload` starts; all endpoints return valid JSON HTTP 200 OK.

---

### Phase 6: Premium React Frontend Dashboard

* **Objective**: Build a visually stunning single-page PM dashboard with dark glassmorphism styling and interactive behavioral charts.
* **Tasks**:
  1. **Executive Summary** (`ExecutiveSummary.jsx`): Hero stats (records, sources, consensus pass rate).
  2. **Behavior Graph Visualizer** (`BehaviorGraphView.jsx`): Interactive network graph of triggers, habits, and emotional barriers.
  3. **Emotion Spectrum Card** (`EmotionSpectrumCard.jsx`): Breakdown of Risk, Uncertainty, and Decision Fatigue.
  4. **Habit Loop Visualizer** (`HabitLoopVisualizer.jsx`): Trigger $\rightarrow$ Action $\rightarrow$ Reward loop cards.
  5. **JTBD Need Matrix** (`JTBDMatrix.jsx`): Jobs-To-Be-Done vs. legacy categories.
  6. **Consumer Archetype Grid** (`ArchetypeSegmentGrid.jsx`): Segment cards with experimentation propensity.
  7. **Contradiction Card** (`ContradictionCard.jsx`): Stated vs. observed behavior paradoxes.
  8. **Consensus Report Modal** (`ConsensusReportModal.jsx`): Multi-LLM 2/3 agreement breakdown across Groq Llama-3.1, HuggingFace Llama-3.2, Free Open Models.

* **Deliverables**: React dashboard codebase, CSS design system, 8 components, responsive glassmorphism layout.
* **Exit Criteria**: `npm run dev` in `frontend/` renders all components with real/mock API data.


---

### Phase 7: End-to-End Integration, Testing & Verification

* **Objective**: Full pipeline integration testing, edge case coverage, and final quality verification before deployment.
* **Tasks**:
  1. **Full Pipeline CLI** (`scripts/run_pipeline.py`):
     * Single command to run the entire pipeline: scrape → process → analyze.
     * Support stage flags: `--stage scrape`, `--stage process`, `--stage analyze`, `--stage all`.
     * Log timing, record counts, and error summaries per stage.
     ```python
     import sys, os, argparse
     sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
     from src.app.services.orchestrator import PipelineOrchestrator

     if __name__ == "__main__":
         parser = argparse.ArgumentParser(description="Blinkit Discovery Engine Pipeline")
         parser.add_argument("--stage", choices=["scrape", "process", "analyze", "all"], default="all")
         args = parser.parse_args()
         orchestrator = PipelineOrchestrator()
         orchestrator.run(stage=args.stage)
     ```

  2. **Automated Test Suites**:
     * `tests/test_scrapers.py` — Mock HTTP responses; verify schema mapping, dedup hashing, JSONL persistence.
     * `tests/test_cleaner.py` — Test text normalization, length filtering, HTML stripping, URL removal.
     * `tests/test_sentiment.py` — Test LLM batch classification with mock responses; verify fallback classifier.
     * `tests/test_tagger.py` — Test multi-label classification; verify taxonomy compliance.
     * `tests/test_theme_extractor.py` — Test theme extraction with mock LLM; verify research question mapping.
     * `tests/test_insight_synthesizer.py` — Test cross-source synthesis; verify evidence strength calculation.
     * `tests/test_validator.py` — Test all validation checks (source count, grounding, dedup, question mapping).
     * `tests/test_api.py` — Integration tests for all API endpoints using FastAPI `TestClient`.

  3. **Data Quality Checks**:
     * Verify ≥3 sources contributing to each top-5 insight.
     * Verify all 8 research questions are addressed by at least 1 insight.
     * Verify validation report shows >80% pass rate.
     * Spot-check 10 representative quotes for grounding accuracy.

  4. **Frontend Integration Test**:
     * Verify frontend connects to live backend and renders real data.
     * Test all interactive elements (filters, expand/collapse, chart hover tooltips).
     * Verify responsive layout on 3 viewport sizes (1440px, 768px, 375px).

* **Deliverables**: Full test suite, pipeline CLI script, data quality report.
* **Exit Criteria**: `pytest tests/ -v` passes all tests. Full pipeline runs end-to-end without errors. Dashboard renders real insights from the pipeline.
* **Dependencies**: Phases 4 and 6.

> [!NOTE]
> **Verification Phase 7:** Run the full verification suite:
> ```powershell
> # Run all unit and integration tests
> pytest tests/ -v
>
> # Run full pipeline end-to-end
> python scripts/run_pipeline.py --stage all
>
> # Start backend and frontend
> uvicorn src.app.api_server:app --reload
> cd frontend && npm run dev
> ```

---

### Phase 8: Deployment & Go-Live

* **Objective**: Deploy the backend API to Render and frontend dashboard to Vercel. Prepare final demonstration documentation.
* **Tasks**:
  1. **Backend Deployment (Render)**:
     * Create `Dockerfile` and `render.yaml` for containerized/native Python deployment on Render.
     * Configure start command: `uvicorn src.app.api_server:app --host 0.0.0.0 --port $PORT`.
     * Configure Render environment variables: `LLM_API_KEY`, `LLM_MODEL`, `LLM_PROVIDER`.
     * Bundle pre-computed `data/insights/` JSON files into the container.
     * Generate public Render domain (`https://<your-app>.onrender.com`) and verify health endpoint.

  2. **Frontend Deployment (Vercel)**:
     * Configure `vercel.json` for SPA routing.
     * Set `VITE_API_URL` environment variable pointing to Render backend URL (`https://<your-app>.onrender.com/api/v1`).
     * Run `npm run build` and deploy via Vercel GitHub integration.

  3. **Documentation**:
     * Write `deployment-plan.md` with step-by-step Render and Vercel instructions.
     * Write `README.md` with project overview, setup instructions, architecture summary, and known limitations.
     * Prepare demonstration script/walkthrough.

  4. **Security Hardening**:
     * Tighten CORS `allow_origins` to production Vercel domain only.
     * Verify no API keys or secrets in the deployed codebase.
     * Ensure `.gitignore` excludes all sensitive files.

* **Deliverables**: Deployed backend (Render), deployed frontend (Vercel), deployment documentation, README.
* **Exit Criteria**: Production URLs are live and accessible. Health endpoint returns `{"status": "healthy"}`. Dashboard loads with real insights. No console errors.
* **Dependencies**: Phase 7.

---

## 6. Milestones & Expected Deliverables Summary

| Milestone | Deliverable File/Path | Expected Outcome | Verification Metric |
|---|---|---|---|
| **Milestone 0** | Project skeleton + `requirements.txt` | Clean, structured project directory | `pytest` runs with 0 errors |
| **Milestone 1** | `src/app/models/domain.py` + `config.py` | Domain models and config loader | Model instantiation tests pass |
| **Milestone 2** | `data/raw/**/*.jsonl` | Raw feedback from 6 sources (incl. support tickets) | ≥5,000 total records across sources |
| **Milestone 3** | `data/processed/*.parquet` | Enriched records with sentiment, tags | ≥80% tag coverage; reasonable sentiment distribution |
| **Milestone 4** | `data/insights/insights_final.json` | 10–20 validated, ranked insights | All 8 research questions addressed; validation >80% pass |
| **Milestone 4.5**| `data/insights/hypotheses.json`, `experiments.json`, `learning_outcomes.json` | Continuous pattern detection, hypothesis, experiment, & closed-loop learning engine | Grounded hypotheses generated; experiment specs valid; closed-loop confidence feedback loop verified |
| **Milestone 5** | `src/app/api_server.py` + routes | Live API serving insights, patterns, hypotheses, experiments & outcome feedback | All endpoints return valid JSON |
| **Milestone 6** | `frontend/` dashboard | Premium interactive insight dashboard | Responsive rendering on desktop + tablet |
| **Milestone 7** | Full test suite | Comprehensive pipeline coverage | `pytest tests/ -v` — zero failures |
| **Milestone 8** | Production deployment | Live Render + Vercel URLs | Health check + dashboard accessible |

---

## 7. Verification Plan

### Automated Tests
```powershell
# Run complete testing suite
pytest tests/ -v

# Test coverage reporting
pytest --cov=src tests/

# Run full pipeline
python scripts/run_pipeline.py --stage all
```

### Manual Verification
1. **Data Quality**: Sample 20 random records from each processed Parquet file; verify sentiment accuracy and tag relevance.
2. **Insight Quality**: Read all generated insights; verify each has grounded quotes, maps to research questions, and provides actionable PM recommendations.
3. **Dashboard UX**: Navigate the full dashboard flow — executive summary → insight cards (expand 3) → filter by research question → explore themes → review analytics charts.
4. **Responsive Design**: Test on 1440px (desktop), 768px (tablet), and 375px (mobile) viewports.
5. **API Reliability**: Hit all 10 endpoints via `curl` and verify response shape matches API contract in architecture.md.

---

*Document derived from [architecture.md](file:///c:/Nextleap%20Projects%20Git/ProductManagerFellowshipGraduationProject/docs/architecture.md) and [context.md](file:///c:/Nextleap%20Projects%20Git/ProductManagerFellowshipGraduationProject/docs/context.md) · Generated for NextLeap PM Fellowship Graduation Project*
