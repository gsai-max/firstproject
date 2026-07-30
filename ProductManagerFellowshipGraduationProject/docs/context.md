# Context Document — Blinkit Category Exploration Project

## 1. Role & Ownership

| Field | Detail |
|---|---|
| **Role** | Product Manager, Growth Team |
| **Company** | Blinkit (quick-commerce platform) |
| **Fellowship** | NextLeap Product Manager Fellowship — Graduation Project |

---

## 2. Platform & Domain Context

- **Industry:** Quick commerce (Q-commerce) — ultra-fast delivery of groceries and daily essentials.
- **Platform:** Blinkit — one of India's leading quick-commerce apps delivering in minutes.
- **Current state:** The platform has already achieved strong product-market fit for weekly/recurring purchases. Users treat it as a habitual utility for groceries, snacks & beverages, and household essentials.

---

## 3. Core Problem

> Users' shopping behavior on Blinkit has become **highly repetitive**. They purchase the same set of products from the same categories and **rarely explore new categories** available on the platform.

### Why this matters

- **Revenue ceiling:** Category stickiness limits basket expansion and average revenue per user (ARPU).
- **Under-utilised catalogue:** Blinkit hosts many categories (pet supplies, personal care, baby products, electronics accessories, etc.) that existing users never browse.
- **Growth lever:** Cross-category adoption is a high-impact growth vector — acquiring new category buyers from an existing user base is cheaper than acquiring net-new users.

---

## 4. Strategic Goal (North Star)

> **Increase the percentage of Monthly Active Customers (MAC) who purchase products from at least one new category every month.**

### Illustrative examples

| Current behaviour | Desired expansion |
|---|---|
| Buys groceries | Starts buying **pet supplies** |
| Buys snacks | Starts buying **personal care** products |
| Buys household essentials | Starts buying **baby products** |

---

## 5. Solution Mandate — Multi-Agent AI Discovery Engine

Before proposing any product solution, the project requires building a **Multi-Agent AI Intelligence Engine** that analyzes public user feedback at scale across multiple behavioral, emotional, and psychological dimensions.

### 5.1 Why Multi-Agent Instead of One LLM?

1. **One prompt gives shallow answers:** A single generic prompt collapses complex consumer behavior into generic summaries.
2. **Consumers are complex:** Real purchasing decisions are governed by habits, emotional friction, risk perception, functional needs, and subconscious trade-offs.
3. **Specialized agents study different dimensions:** Delegating discrete analytical tasks to specialized sub-agents extracts deep, structured behavioral science insights from raw unstructured feedback.

### 5.2 10 Ingestion Data Sources

| # | Data Source | Type & Domain |
|---|---|---|
| 1 | **Play Store Reviews** | Android app user feedback (scale & operational issues) |
| 2 | **App Store Reviews** | iOS app user feedback (UX & feature requests) |
| 3 | **Reddit** | Deep community discussions (`r/india`, `r/bangalore`, `r/delhi`, etc.) |
| 4 | **Twitter/X** | Real-time sentiment, public complaints, and organic discourse |
| 5 | **YouTube Comments** | Unfiltered user video reviews and Q-commerce unboxings |
| 6 | **Quora** | Detailed Q&A on quick commerce experiences and alternatives |
| 7 | **Consumer Forums** | In-depth consumer complaint boards and product feedback |
| 8 | **Blinkit Reviews** | Direct app store feedback on Blinkit |
| 9 | **Zepto Reviews** | Competitor review analysis for cross-app behavior comparison |
| 10 | **Instamart Reviews** | Competitor feedback for benchmarking category discovery friction |

---

### 5.3 The 6-Agent AI Intelligence Ar```
                 Raw Feedback (157,630 Raw Reviews / 5,320 Filtered)
                                      │
                                      ▼
                        Python Pipeline Cleaning & Deduplication
                                      │
                                      ▼
             Embeddings (MiniLM-L6-v2) + Vector DB (Local ChromaDB)
                                      │
    ┌─────────────────┬───────────────┼───────────────┬─────────────────┬─────────────────┐
    │                 │               │               │                 │                 │
    ▼                 ▼               ▼               ▼                 ▼                 ▼
Agent 1           Agent 2         Agent 3         Agent 4           Agent 5           Agent 6
Theme Extractor   Emotion         Habit           JTBD              Segment           Contradiction
Agent             Agent           Agent           Agent             Agent             Agent
    │                 │               │               │                 │                 │
    └─────────────────┴───────────────┼───────────────┴─────────────────┴─────────────────┘
                                      │
                                      ▼
                              Behavior Graph
                                      │
                                      ▼
                            Quality Validation
       (Groq Llama-3.1 + HF Llama-3.2 + Multi-LLM Consensus 2/3 Rule)
                                      │
                                      ▼
                         Insights & PM Dashboard
```�
                                      ▼
                              Behavior Graph
                                      │
                                      ▼
                            Quality Validation
                 (Human Audit + Multi-LLM Consensus 2/3 Rule)
                                      │
                                      ▼
                         Insights & PM Dashboard
```

#### Agent 1 — Theme Extraction Agent
* **Purpose:** Find repeating operational and product themes across raw feedback streams.
* **Sample Output:** Late Delivery $\rightarrow$ 14%, Product Discovery Issues $\rightarrow$ 21%, Search Problems $\rightarrow$ 9%, Trust Issues $\rightarrow$ 6%, Habit Purchases $\rightarrow$ 18%, Price Sensitivity $\rightarrow$ 12%.

#### Agent 2 — Emotion Agent
* **Purpose:** Uncover *how* users feel rather than just *what* they say.
* **Example:** Review: *"I always order the same things because trying new products feels risky."* $\rightarrow$ Emotion: **Risk, Uncertainty, Decision Fatigue**.
* **Rationale:** Commerce is inherently emotional; unaddressed risk blocks cross-category trial.

#### Agent 3 — Habit Detection Agent (Secret Weapon)
* **Purpose:** Convert raw text into behavioral science by extracting Habit Loops:
  - **Trigger:** Sunday Grocery Need
  - **Action:** Repeat Previous Order
  - **Reward:** Fast 10-Minute Checkout
  - **Result:** Category exploration decreases to near zero.

#### Agent 4 — Jobs-To-Be-Done (JTBD) Agent
* **Purpose:** Identify the fundamental underlying human problems customers are trying to solve.
* **Example:**
  - Instead of *Personal Care* category $\rightarrow$ Need: **"Look presentable for office on short notice."**
  - Instead of *Snacks* category $\rightarrow$ Need: **"Quick stress relief during work breaks."**
* **Rationale:** Allows optimizing the product experience for human needs rather than static taxonomy categories.

#### Agent 5 — Segment Discovery Agent
* **Purpose:** Discover emergent consumer archetypes (Explorers, Routine Buyers, Value Seekers, Parents, Health Focused, Convenience Users) and identify who experiments most, who needs incentives, and who requires trust building.

#### Agent 6 — Contradiction Agent
* **Purpose:** Surface counter-intuitive gaps between what users say vs. how they actually behave.
* **Example:** Users say *"I want more product discovery,"* but behavior shows **95% repeat purchases**.
* **Insight:** Users want discovery **without added cognitive effort or trial risk**.

---

### 5.4 The 4-Layer Discovery Framework

All analyzed data passes through a 4-layer transformation:

```
[ WHAT ]      --> Users repeat purchases from the same 1-2 categories.
[ WHY ]       --> Deeply ingrained habits + lack of trust in non-grocery quality.
[ EMOTION ]   --> Fear of financial/product risk + cognitive decision fatigue.
[ OPPORTUNITY]--> Reduce uncertainty via social proof, risk-free trial, and context-aware bundles.
```

---

## 6. Key Research Questions

The discovery engine answers the following 8 core research questions:

1. **Why do users repeatedly buy from the same categories?**
2. **What prevents users from exploring new categories?**
3. **How do users discover products today?**
4. **What role do habits play in shopping behavior?**
5. **What information do users need before trying a new category?**
6. **What frustrations emerge repeatedly?**
7. **Which user segments are more likely to experiment?**
8. **What unmet needs emerge consistently across discussions?**

---

## 7. Quality Validation Layer

To eliminate AI hallucinations and ensure empirical rigor, all generated insights pass through a 4-stage validation process:

1. **Human Audit:** Manual audit of 200 raw sample reviews comparing AI theme extractions against human annotators (target: **$\ge$ 90% agreement**).
2. **Multi-LLM Consensus:** Every insight is passed through three independent frontier models (**Groq Llama-3.1**, **HuggingFace Llama-3.2**, **Free Open Models**). Insights are accepted **only if $\ge$ 2 of 3 models agree**.
3. **Statistical Validation:** Every insight is assigned a quantitative confidence score calculated from theme frequency, sentiment distribution, source diversity, and variance.
4. **User Interviews:** 20 structured user interviews conducted to empirically validate AI-detected behavioral habits and friction points.

---

## 8. Deliverables & Demonstration Requirements

| # | Deliverable | Description |
|---|---|---|
| 1 | **Multi-Source Data Pipeline** | Ingestion from 10 feedback channels (App Store, Play Store, Reddit, Twitter, YouTube, Quora, Forums, etc.) |
| 2 | **6-Agent AI Architecture** | Multi-agent execution (Theme, Emotion, Habit, JTBD, Segment, Contradiction) |
| 3 | **Behavior Graph Engine** | Interconnected graph mapping user triggers, emotions, habits, and category exploration barriers |
| 4 | **4-Tier Quality Validation** | Human audit, Multi-LLM consensus (Groq Llama-3.1 + HF Llama-3.2 + Free Open Models), statistical scoring, and user interview alignment |
| 5 | **Continuous Monitoring** | Background listening and trend detection across streaming feedback |
| 6 | **Hypothesis & Experiment Engine** | Automated PM-ready growth hypotheses and A/B test specs |
| 7 | **PM Interactive Dashboard** | Premium dashboard displaying behavior graphs, consumer archetypes, and actionable product opportunities |

---

## 9. Success Criteria

- Produces **validated behavioral insights** backed by a 90%+ confidence score and multi-source evidence.
- Directly informs a growth strategy to increase the North Star metric (**% MAC purchasing from $\ge$ 1 new category/month**).
- Implements a **reproducible multi-agent pipeline** using modern orchestrators (n8n, Python, Vector DBs).
- Replaces shallow single-prompt analysis with **depth-first behavioral science**.

---

## 10. The Winning Narrative

> **Traditional Review Analysis:** Reviews $\rightarrow$ Keywords $\rightarrow$ Basic Themes
>
> **Blinkit AI Discovery Engine:** Conversations $\rightarrow$ Emotions $\rightarrow$ Habits $\rightarrow$ Jobs-To-Be-Done $\rightarrow$ Consumer Archetypes $\rightarrow$ Behavior Graph $\rightarrow$ **High-Impact Product Opportunities**

---

## 11. Constraints & Assumptions

| Type | Detail |
|---|---|
| **No direct data access** | Relies on public feedback and scrapers; no internal database access |
| **Data Cleaning** | Filter out reviews < 8 words, containing emojis, or written in non-English scripts |
| **Sanitization** | Strip PII and non-essential metadata (`userName`, `userImage`, `reviewId`, etc.) |
| **Geography** | India quick-commerce market (Blinkit, Zepto, Instamart ecosystem) |

---

*Document updated for NextLeap Product Manager Fellowship — Graduation Project*

