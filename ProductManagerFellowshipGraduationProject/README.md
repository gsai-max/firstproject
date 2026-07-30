# Blinkit AI Discovery Engine — Category Exploration

[![Python Version](https://img.shields.io/badge/python-3.12-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-1.0.0-emerald.svg)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-18.2-cyan.svg)](https://reactjs.org/)
[![Test Suite](https://img.shields.io/badge/tests-76%20passed-brightgreen.svg)]()
[![Deployment](https://img.shields.io/badge/Render%20%2B%20Vercel-live-purple.svg)](https://render.com/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)]()

> **NextLeap Product Manager Fellowship — Graduation Project**  
> An AI-native customer intelligence engine that ingests, cleans, normalizes, and analyzes multi-channel user feedback at scale across 10 channels to discover why quick-commerce users exhibit repetitive purchasing habits and how to unlock cross-category exploration.

---

## Executive Overview & North Star Metric

Shopping behavior on quick-commerce platforms like **Blinkit** has become highly repetitive — users purchase the same 3 to 5 grocery staples habitually and rarely explore non-grocery categories (pet supplies, personal care, baby products, electronics, etc.).

### North Star Metric
> **Increase the percentage of Monthly Active Customers (MAC) who purchase products from at least one new category every month.**

The **Blinkit AI Discovery Engine** automates customer research by ingesting public reviews and discussions from 10 channels (157,630 raw feedback corpus), normalizing raw data, running **6 specialized AI Agents**, building an interconnected **Behavior Graph**, and validating evidence via a **Multi-LLM Consensus Engine (2/3 Majority Rule)** to guide PM product strategy.

---

## System Architecture

```
                                    AI DISCOVERY ENGINE PIPELINE
┌─────────────────────────┐     ┌────────────────────────────┐     ┌────────────────────────────┐
│   Data Collection (10)  │     │    Data Processing Layer   │     │    6-Agent AI Analysis     │
│ • Google Play Store     │ ──► │ • Length Filter (≥8 words) │ ──► │ • Agent 1: Theme Extractor │
│ • Apple App Store       │     │ • Emoji / Script Filter    │     │ • Agent 2: Emotion Agent   │
│ • Reddit Discussions    │     │ • SHA-256 & Jaccard Dedup  │     │ • Agent 3: Habit Loop      │
│ • Twitter / X           │     │ • MiniLM Vector Embedding  │     │ • Agent 4: JTBD Need       │
│ • YouTube Comments      │     │ • ChromaDB Vector Indexing │     │ • Agent 5: Segment Archetype│
│ • Quora Q&A Threads     │     │ • Parquet / JSON Storage   │     │ • Agent 6: Contradiction   │
│ • Consumer Forums       │     └────────────────────────────┘     └────────────────────────────┘
│ • Support Tickets       │                                                  │
│ • Zepto Reviews (Comp)  │                                                  │
│ • Instamart Reviews     │                                                  ▼
└─────────────────────────┘                                    ┌────────────────────────────┐
                                                               │  Behavior Graph Engine     │
                                                               └────────────────────────────┘
                                                                             │
                                                                             ▼
                                                               ┌────────────────────────────┐
                                                               │ Multi-LLM Consensus (2/3)  │
                                                               │ (Groq + HF Llama + Open)   │
                                                               └────────────────────────────┘
                                                                             │
┌─────────────────────────┐     ┌────────────────────────────┐               │
│ Premium React Dashboard │ ◄── │  FastAPI Backend & API     │ ◄─────────────┘
│ • Executive Summary     │     │ • REST Endpoints (/api/v1) │
│ • Behavior Graph View   │     │ • In-Memory Data Loader    │
│ • Emotion & Habit Cards │     │ • Render Web Service       │
│ • Consensus Modal       │     │ • Pipeline Trigger Endpoint│
└─────────────────────────┘     └────────────────────────────┘
```

---

## Key Features

* **10-Source Data Ingestion Pipeline**: Scrapes and consolidates feedback across Play Store, App Store, Reddit, Twitter/X, YouTube, Quora, Consumer Forums, Support Tickets, Zepto, and Instamart.
* **Strict Quality & PII Filtering**: Enforces an 8-word minimum, strips emojis and non-English scripts (Devanagari, Tamil, etc.), removes PII, and deduplicates via exact SHA-256 and Jaccard similarity ($\ge 85\%$).
* **Vector Database Indexing**: Generates 384-dimensional dense vector embeddings using **Sentence-Transformers `all-MiniLM-L6-v2`** indexed in a local **ChromaDB** vector database.
* **6 Specialized AI Agents**:
  1. **Theme Extraction Agent**: Categorizes operational, product, pricing, and trust friction.
  2. **Emotion Agent**: Surfaces underlying Risk Perception, Uncertainty, and Cognitive Decision Fatigue.
  3. **Habit Loop Agent**: Extracts Trigger $\rightarrow$ Action $\rightarrow$ Reward loops.
  4. **JTBD Agent**: Identifies underlying functional needs vs. static catalog categories.
  5. **Segment Discovery Agent**: Maps consumer archetypes (Explorers, Routine Buyers, Value Seekers, etc.).
  6. **Contradiction Agent**: Surfaces stated desire vs. observed purchasing behavior gaps.
* **Behavior Graph Engine**: Merges multi-agent outputs into an interconnected network graph (30 nodes, 20 edges).
* **4-Tier Quality Validation Layer**: Enforces a **2/3 Multi-LLM Consensus rule** (Groq Llama-3.1, HuggingFace Llama-3.2, Free Open Models), statistical confidence scoring, 200-review human audit benchmark, and 20 user interviews.
* **Closed-Loop Growth Engine**: Automatically generates emerging patterns, growth hypotheses, PM experiment specs, and closed-loop confidence feedback.
* **Render & Vercel Deployment**: Deployed as a containerized/native Python FastAPI service on Render paired with a Vercel React SPA.

---

## Quick Start Guide

### Prerequisites
* Python 3.12+
* Node.js 18+ (for React dashboard)

### 1. Environment Setup & Installation
```powershell
# Clone workspace
cd ProductManagerFellowshipGraduationProject

# Create and activate Python virtual environment
python -m venv .venv
.venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Environment Variables
Copy `.env.example` to `.env` and fill in your API keys:
```bash
LLM_PROVIDER=groq
LLM_API_KEY=your_groq_api_key_here
LLM_MODEL=llama-3.1-8b-instant
```

### 3. Run Automated Test Suite
```powershell
pytest tests/ -v
# Output: 76 passed in 10.01s
```

### 4. Run Full Pipeline CLI
```powershell
# Run full discovery pipeline end-to-end (scrape → process → analyze)
python scripts/run_pipeline.py --stage all
```

### 5. Launch FastAPI Backend Server
```powershell
python -m uvicorn src.app.api_server:app --port 8000 --reload
# Interactive OpenAPI Docs available at http://localhost:8000/docs
```

### 6. Launch React Frontend Dashboard
```powershell
cd frontend
npm install
npm run dev
# Dashboard available at http://localhost:3000
```

---

## REST API Specification (`/api/v1`)

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/v1/health` | Service health check |
| `GET` | `/api/v1/insights` | Validated multi-agent insights with consensus scores (`?research_question=Q1`) |
| `GET` | `/api/v1/behavior-graph` | Interconnected Behavior Graph nodes and edges |
| `GET` | `/api/v1/archetypes` | Consumer segment archetypes matrix |
| `GET` | `/api/v1/agents/theme` | Agent 1 Theme extractions |
| `GET` | `/api/v1/agents/emotion` | Agent 2 Emotion profiles |
| `GET` | `/api/v1/agents/habit` | Agent 3 Habit loops |
| `GET` | `/api/v1/agents/jtbd` | Agent 4 Jobs-To-Be-Done extractions |
| `GET` | `/api/v1/agents/contradiction` | Agent 6 Contradiction patterns |
| `GET` | `/api/v1/validation/report` | Multi-LLM consensus pass rates & human audit stats |
| `GET` | `/api/v1/analytics/summary` | Aggregate review volume and sentiment distribution |
| `GET` | `/api/v1/pipeline/status` | Pipeline execution status and health metadata |
| `POST` | `/api/v1/pipeline/run` | Trigger end-to-end pipeline execution and refresh cache |

---

## Production Deployment (Render + Vercel)

### Backend Deployment on Render
1. Create a new **Web Service** on [Render.com](https://render.com).
2. Connect this GitHub repository. Render reads [render.yaml](file:///c:/Nextleap%20Projects%20Git/ProductManagerFellowshipGraduationProject/render.yaml) automatically.
3. Set environment variables: `LLM_PROVIDER`, `LLM_API_KEY`, `LLM_MODEL`.
4. Deploy. Render assigns a live public URL: `https://<your-backend-app>.onrender.com`.

### Frontend Deployment on Vercel
1. Import `frontend/` folder into [Vercel.com](https://vercel.com).
2. Set Environment Variable: `VITE_API_URL=https://<your-backend-app>.onrender.com/api/v1`.
3. Deploy. Vercel issues live URL: `https://<your-dashboard-app>.vercel.app`.

---

## Project Structure

```
├── data/
│   ├── raw/                        # Raw JSONL payloads (Play Store, App Store, Reddit, Twitter, YouTube, Quora, Forums, Support Tickets, Competitors)
│   ├── processed/                  # Normalized reviews (all_normalized_reviews.json, Parquet, Vector Store)
│   └── insights/                   # Validated Agent outputs, Behavior Graph, Consensus report, Hypotheses
├── docs/                           # Architecture, Context, Implementation Plan, Deployment Plan, Edge Cases
├── frontend/                       # Vite + React Glassmorphism Dashboard codebase
├── render.yaml                      # Render Blueprint Infrastructure specification
├── Dockerfile                      # Container build definition for Render/Docker
├── Procfile                        # Uvicorn start process command
├── scripts/
│   ├── run_pipeline.py             # CLI pipeline runner
│   └── run_quality_audit.py        # Automated data quality audit script
├── src/
│   └── app/
│       ├── agents/                 # 6 Specialized AI Agents (Theme, Emotion, Habit, JTBD, Segment, Contradiction)
│       ├── analysis/               # BehaviorGraph, MultiLLMConsensus, StatisticalValidator, HumanAudit, ClosedLoop
│       ├── api/                    # FastAPI routes, schemas, data_loader cache
│       ├── models/                 # Pydantic domain models
│       ├── processing/             # Cleaner, Deduplicator, Sentiment, Tagger, VectorStore
│       ├── scrapers/               # Scrapers for 10 multi-source channels
│       └── api_server.py           # FastAPI application entrypoint
└── tests/                          # 76 Unit and Integration test cases
```

---

## License

MIT License · Project developed for **NextLeap Product Manager Fellowship Graduation Project**.
