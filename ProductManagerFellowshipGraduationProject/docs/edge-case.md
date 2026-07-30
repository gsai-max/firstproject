# Blinkit Discovery Engine — Edge Cases and Failure Modes

This document catalogs the corner cases, failure modes, and mitigation strategies across every layer of the AI-Powered Discovery Engine for the Blinkit Category Exploration project. It is organized by system layer as defined in [architecture.md](file:///c:/Nextleap%20Projects%20Git/ProductManagerFellowshipGraduationProject/docs/architecture.md).

---

## 1. Data Collection Layer — Scrapers

This offline layer scrapes public reviews, discussions, and social media posts from 5 platforms. Each scraper faces platform-specific failure modes.

### 1.1 Play Store Scraper

| Category | Edge Case | Description | Severity | Mitigation Strategy |
|:---|:---|:---|:---|:---|
| **API Limits** | Rate Limiting / IP Blocking | Fetching 5,000–10,000 reviews in rapid succession triggers Google's anti-scraping defences, returning `429 Too Many Requests` or empty payloads. | **HIGH** | **Throttled Batching:** Fetch reviews in batches of 200 with a randomized sleep delay (2–5 seconds) between batches. Cache partially scraped results to JSONL after each batch so progress isn't lost on failure. |
| **Data Quality** | Empty or Null Review Bodies | Some Play Store reviews contain only star ratings with blank text fields (users tap stars without writing). | **MEDIUM** | **Minimum Content Filter:** Skip records with `text == None` or `len(text.strip()) < 5` during scraping. Log skip count for data quality tracking. |
| **Encoding** | Non-UTF-8 / Emoji-Heavy Reviews | Indian users frequently write in Devanagari script, use Hinglish, or embed heavy emoji sequences that corrupt text processing. | **MEDIUM** | **Encoding Normalization:** Force UTF-8 encoding on all text fields. Preserve emojis during scraping (they carry sentiment signal) but strip them during the cleaning stage if they interfere with LLM tokenization. |
| **Schema** | Library Version Breaking Changes | `google-play-scraper` library updates its response schema (renamed fields, removed attributes), causing `KeyError` crashes. | **LOW** | **Defensive Field Access:** Use `.get()` with fallback defaults for all field mappings. Pin the library version in `requirements.txt`. |
| **Duplication** | Cross-Sort Overlap | Fetching reviews sorted by `NEWEST` and `MOST_RELEVANT` produces overlapping records. | **MEDIUM** | **Dedup at Scrape Time:** Hash `text + date` using SHA-256; skip records with already-seen hashes within the same scraping session. |

### 1.2 App Store Scraper

| Category | Edge Case | Description | Severity | Mitigation Strategy |
|:---|:---|:---|:---|:---|
| **Availability** | App Store API Region Restrictions | Apple restricts review access by country code. Reviews from `country='in'` may return fewer results than expected or timeout. | **HIGH** | **Multi-Country Fallback:** If India (`in`) returns < 500 reviews, also query `us` and `gb` stores. Tag records with `country` metadata for later filtering. |
| **Volume** | Low Review Count | Blinkit's iOS user base is smaller than Android. The App Store may yield only 500–1,000 reviews vs. the 2,000–5,000 target. | **MEDIUM** | **Graceful Degradation:** Accept whatever volume is available. Log a warning if count < 500 but don't fail the pipeline. App Store becomes a supplementary source rather than primary. |
| **Library** | `app-store-scraper` Instability | The library is community-maintained and may fail silently or return malformed data on Apple API changes. | **MEDIUM** | **Retry with Backoff:** Wrap scraper calls in a retry loop (max 3 attempts, exponential backoff). If all retries fail, log error and skip App Store for this run — pipeline continues with other sources. |

### 1.3 Reddit Scraper

| Category | Edge Case | Description | Severity | Mitigation Strategy |
|:---|:---|:---|:---|:---|
| **Auth** | OAuth Credential Expiry | Reddit API OAuth tokens expire after 1 hour. Long-running scrapes across multiple subreddits may hit `401 Unauthorized` mid-session. | **HIGH** | **Auto-Refresh Token:** Use `praw`'s built-in OAuth refresh mechanism. Validate token before each subreddit query batch. |
| **Rate Limits** | 60 Requests/Minute Cap | Reddit API enforces strict rate limits. Querying 7 subreddits × 7 search terms = 49 queries can exhaust the budget quickly. | **HIGH** | **Batched Queries with Sleep:** Insert 1.5-second delays between API calls. Prioritize subreddits by expected relevance (e.g., `r/india` first, city-specific subs last). |
| **Relevance** | Irrelevant Noise in Results | Searching "blinkit" on `r/india` returns posts about Blinkit delivery issues, rider complaints, and unrelated e-commerce threads that don't discuss category exploration. | **HIGH** | **Post-Scrape Relevance Filter:** After collection, run a lightweight LLM classification pass to score each post's relevance to "category exploration / product discovery / shopping behaviour" (0.0–1.0). Discard posts scoring < 0.3. |
| **Depth** | Comments vs. Posts | Top-level comments often contain richer behavioural insights than the original post. Ignoring comments loses valuable signal. | **MEDIUM** | **Thread Expansion:** For each post, fetch up to 20 top-level comments (sorted by score). Store each comment as a separate `RawFeedbackRecord` with `metadata.parent_post_id` for traceability. |
| **Historical** | Pushshift API Deprecation | Pushshift (used for historical Reddit data) has been intermittently unavailable since 2023. | **MEDIUM** | **Fallback to PRAW Search:** Use `praw`'s native `subreddit.search()` with `time_filter='year'`. Accept that historical coverage may be limited to what Reddit's search API returns (typically 6–12 months). |

### 1.4 Twitter/X Scraper

| Category | Edge Case | Description | Severity | Mitigation Strategy |
|:---|:---|:---|:---|:---|
| **Access** | Twitter/X API Paywall | Twitter/X has restricted free API access. `snscrape` may be blocked, and API v2 Basic tier has severe rate limits (10,000 tweets/month). | **CRITICAL** | **Multi-Fallback Strategy:** (1) Try `snscrape` first. (2) If blocked, use Twitter API v2 Basic tier with strict query budgeting. (3) If both fail, create a **curated manual dataset** by extracting publicly visible tweets from web browser screenshots and text copies. Tag these records with `metadata.collection_method = "manual"`. |
| **Noise** | Brand Mentions ≠ User Feedback | Many tweets mentioning "blinkit" are promotional, competitor comparisons, or memes — not genuine user feedback about categories. | **HIGH** | **Tweet Quality Filter:** Exclude retweets (RT), tweets from verified brand accounts, and tweets with < 5 words. Apply the same relevance classifier used for Reddit. |
| **Language** | Hinglish Dominance | Indian Twitter is heavily Hinglish (e.g., "blinkit pe pet food milta hai kya?" = "does Blinkit have pet food?"). Pure English NLP pipelines may misclassify sentiment or topics. | **HIGH** | **Hinglish-Aware Prompts:** Include Hinglish examples in few-shot prompts for sentiment and topic classification. Use LLM-based classification (which handles code-switching natively) instead of rule-based approaches for Hindi-English mixed text. |

### 1.5 Forum & Blog Crawler

| Category | Edge Case | Description | Severity | Mitigation Strategy |
|:---|:---|:---|:---|:---|
| **Robots.txt** | Crawling Blocked by robots.txt | Target sites (Quora, Medium, ConsumerComplaints.in) may block automated crawling via `robots.txt` directives. | **HIGH** | **Ethical Compliance:** Always check `robots.txt` before crawling. If a domain blocks crawling, skip it and log a warning. Do not circumvent `robots.txt`. Use publicly available API endpoints where available (e.g., Quora's public answer pages). |
| **Layout** | Heterogeneous HTML Structures | Each forum/blog platform has a completely different DOM structure. A single generic parser will fail. | **MEDIUM** | **Domain-Specific Parsers:** Implement separate parsing functions per target domain (e.g., `_parse_quora()`, `_parse_consumercomplaints()`, `_parse_medium()`). Each function uses domain-specific CSS selectors. |
| **Volume** | Thin Content | Forums may yield very few Blinkit-specific posts (< 50). | **LOW** | **Graceful Degradation:** Accept thin sources. Even 20–50 quality forum posts provide valuable triangulation signal for cross-source validation. Log volume warnings but don't fail. |
| **Anti-Bot** | CAPTCHA / JavaScript-Rendered Pages | Some forums require JavaScript rendering or present CAPTCHAs to automated requests. | **MEDIUM** | **Static HTML First:** Attempt plain `requests.get()`. If the response is empty or contains CAPTCHA markers, skip the page. Do not attempt to bypass CAPTCHAs (ethical compliance). Consider using cached Google search results as an alternative data source. |

---

## 2. Data Processing Layer — Clean, Deduplicate, Enrich

This layer transforms raw scraped data into analysis-ready records.

### 2.1 Text Cleaning & Normalization

| Category | Edge Case | Description | Severity | Mitigation Strategy |
|:---|:---|:---|:---|:---|
| **Encoding** | Mixed Script Reviews | A single review may contain English, Hindi (Devanagari), emojis, and special characters (₹, ★). Aggressive cleaning may strip meaningful content. | **HIGH** | **Selective Stripping:** Remove HTML tags and URLs but preserve currency symbols (₹), star ratings (★), and transliterated Hindi words. Only strip emojis during the LLM prompt stage, not during storage. |
| **Length** | Ultra-Short Reviews | Reviews like "good app" or "worst" (< 10 words) contain minimal analysis signal but dominate volume (often 40–60% of app store reviews). | **MEDIUM** | **Two-Tier Filtering:** Discard reviews < 5 words entirely. Keep 5–10 word reviews but tag them as `low_signal = true` so the analysis layer can optionally exclude them from theme extraction batches. |
| **Spam** | Fake / Incentivized Reviews | App stores contain fake 5-star reviews (e.g., "Great app! Best app! Download now!") that skew sentiment and theme analysis. | **HIGH** | **Spam Detector:** Flag reviews matching spam patterns: (1) excessive exclamation marks (>3), (2) generic praise without specifics, (3) duplicate text across multiple authors. Tag as `is_spam = true` and exclude from analysis. |
| **Context Loss** | URL Stripping Removes Product References | Some reviews contain Blinkit deep links or product URLs that carry category context (e.g., "blinkit.com/pet-food"). Stripping URLs loses this signal. | **LOW** | **URL Category Extraction:** Before stripping URLs, parse any Blinkit deep links to extract category slugs (e.g., `/pet-food` → `pet_supplies`). Store extracted categories in `metadata.url_categories` before removing the URL from text. |

### 2.2 Deduplication

| Category | Edge Case | Description | Severity | Mitigation Strategy |
|:---|:---|:---|:---|:---|
| **Cross-Source** | Same User Posts on Multiple Platforms | A user posts the same complaint on both Play Store and Reddit. Exact dedup (same source hash) won't catch this. | **MEDIUM** | **Near-Duplicate Detection:** After exact dedup, run Jaccard similarity (word-level) across all records. Flag pairs with >85% similarity. Keep the record with richer metadata (more fields populated) and discard the other. |
| **Paraphrased Duplicates** | Same Complaint, Different Words | Users express the same frustration in different words (e.g., "Blinkit only shows groceries" vs. "I can only find grocery items on Blinkit"). These are semantically duplicate but lexically different. | **LOW** | **Accept as Separate Records:** Do not attempt semantic dedup at the processing stage — this risks removing genuinely different perspectives. Let the LLM theme extractor naturally consolidate these into themes during Phase 4. |
| **Temporal** | Same User, Updated Review | Play Store allows users to update their reviews. Both the old and new version may be scraped. | **MEDIUM** | **Timestamp-Based Dedup:** For records with the same `author` + same `source`, keep only the most recent version (latest `date`). |

### 2.3 Sentiment Classification

| Category | Edge Case | Description | Severity | Mitigation Strategy |
|:---|:---|:---|:---|:---|
| **Sarcasm** | Sarcastic Positive Language | Users write sarcastic reviews like "Oh great, Blinkit delivered my order to the wrong address again. Amazing service!" — lexically positive but semantically negative. | **HIGH** | **LLM-Based Classification:** Rule-based sentiment classifiers fail on sarcasm. The LLM-based classifier (Groq) handles sarcasm better with the instruction: "Consider sarcasm and irony when classifying sentiment. A review like 'great service, only 3 hours late' should be classified as negative." |
| **Mixed Sentiment** | Split Sentiment in Single Review | A review contains both positive and negative sentiments: "Love the grocery delivery speed but the personal care section is terrible." | **MEDIUM** | **Overall Sentiment with Signal Preservation:** Classify the overall dominant sentiment but add an `is_mixed = true` flag. During theme extraction, the LLM can reference both positive and negative aspects from mixed reviews. |
| **Rating-Sentiment Mismatch** | 5-Star Rating with Negative Text | Users give 5 stars but write negative feedback (e.g., "5 stars but please add more categories"). Or 1 star with positive text (accidental tap). | **MEDIUM** | **Text-First Sentiment:** Always use text-based LLM sentiment as the primary signal. Use star rating as a secondary validation signal. Flag records where `rating >= 4 AND sentiment == "negative"` (or vice versa) for manual review sampling. |
| **Rate Limits** | Groq API Rate Limit During Batch Classification | Processing 8,000+ records in batches of 50 generates 160+ LLM API calls, potentially exceeding Groq's free tier rate limits. | **HIGH** | **Exponential Backoff + Fallback:** Implement retry with exponential backoff (1s, 2s, 4s, 8s) on `429` responses. If rate limit persists after 3 retries, switch to the rule-based keyword fallback classifier for the remaining batch. Log which records used fallback for quality tracking. |

### 2.4 Category & Topic Tagging

| Category | Edge Case | Description | Severity | Mitigation Strategy |
|:---|:---|:---|:---|:---|
| **Implicit Categories** | Category Mentioned Without Name | Users reference categories without naming them: "I wish they had stuff for my dog" (= pet supplies), "need something for the baby" (= baby products). | **HIGH** | **Semantic Category Inference:** Include implicit category examples in the LLM tagger's few-shot prompt: `"stuff for my dog" → pet_supplies`, `"something for the baby" → baby_products`, `"face wash and shampoo" → personal_care`. The LLM handles contextual inference better than keyword matching. |
| **Multi-Category** | Single Review Mentions Multiple Categories | A review discusses 3+ categories: "I buy groceries, snacks, and sometimes medicines on Blinkit." | **LOW** | **Multi-Label Tagging:** The tagger is already multi-label. Ensure the LLM prompt explicitly states: "A single review can belong to multiple categories. Return ALL applicable categories as a JSON array." |
| **Unknown Categories** | User Mentions a Category Not in Taxonomy | A user mentions "stationery" or "gym supplements" which aren't in the predefined taxonomy. | **MEDIUM** | **Open Taxonomy Extension:** Include a `general` / `other` catch-all category. After the full pipeline run, review records tagged `general` to identify new categories worth adding to the taxonomy for future runs. |
| **Competitor Bleed** | Competitor Product Mentions | Users compare Blinkit to Zepto/Instamart: "Zepto has better personal care options." This contains category signal but is about a competitor. | **MEDIUM** | **Tag + Flag:** Tag the mentioned category (`personal_care`) but also add a behaviour signal `competitor_comparison`. During insight synthesis, these records provide valuable "what competitors offer that Blinkit doesn't" evidence. |

---

## 3. LLM Analysis Layer — Theme Extraction & Insight Synthesis

This is the core intelligence layer. LLM failure modes here directly impact insight quality.

### 3.1 Theme Extraction

| Category | Edge Case | Description | Severity | Mitigation Strategy |
|:---|:---|:---|:---|:---|
| **Hallucination** | Fabricated Themes | The LLM generates a theme that doesn't exist in the input batch (e.g., inventing "users want crypto payment options" when no record mentions crypto). | **CRITICAL** | **Quote Grounding Assertion:** Every theme must include `representative_quotes` with `record_id` references. The validator checks that each `record_id` exists in the processed data and the quoted text appears in that record. Themes with zero valid quotes are discarded. |
| **Theme Granularity** | Too Broad or Too Narrow Themes | The LLM outputs overly broad themes ("Users don't like the app") or extremely narrow ones ("One user wants organic turmeric powder"). | **HIGH** | **Granularity Guidelines in Prompt:** System prompt explicitly states: "Each theme should describe a pattern shared by at least 3 reviews. Avoid themes so broad they could apply to any app, and avoid themes so specific they apply to only 1 review." |
| **Batch Inconsistency** | Same Theme Named Differently Across Batches | When processing records in batches of 100, the LLM may name the same theme differently: "Grocery Lock-In" in batch 1 vs. "Category Tunnel Vision" in batch 2. | **HIGH** | **Post-Batch Theme Dedup:** After extracting themes from all batches, run a secondary LLM pass to merge themes with >70% description overlap. Use the most descriptive name from the merged set. |
| **Research Question Drift** | Themes Not Mapped to Any Research Question | The LLM extracts valid themes but forgets to map them to Q1–Q8, or maps them incorrectly. | **MEDIUM** | **Explicit Mapping Prompt:** Include all 8 research questions verbatim in the system prompt. Instruct: "For each theme, list which research questions (Q1–Q8) it directly addresses. A theme must map to at least 1 question." Validator flags themes with empty mappings. |
| **Token Overflow** | Batch Too Large for Context Window | A batch of 100 records × 300 chars = 30,000 chars may exceed the LLM's effective context window, causing truncated or degraded output. | **MEDIUM** | **Dynamic Batch Sizing:** Calculate token count per batch before sending. If estimated tokens > 6,000 (conservative for 8K context), reduce batch size to 50 or 25. Log adjusted batch sizes. |

### 3.2 Insight Synthesis

| Category | Edge Case | Description | Severity | Mitigation Strategy |
|:---|:---|:---|:---|:---|
| **Single-Source Insights** | Insight Backed by Only 1 Source | An insight is generated from themes found in only Play Store reviews, with no corroboration from Reddit, Twitter, or forums. | **HIGH** | **Evidence Strength Downgrade:** If `source_count < 2`, automatically set `evidence_strength = "weak"`. The dashboard displays weak insights with a warning badge. Prioritize multi-source insights in ranking. |
| **Confirmation Bias** | LLM Over-Indexes on Frequent Topics | Delivery complaints dominate review volume (70%+ of negative reviews). The LLM may generate insights primarily about delivery rather than category exploration. | **HIGH** | **Topic-Filtered Batching:** Before sending records to the theme extractor, pre-filter batches by topic relevance. Create separate batches for `discovery`, `variety`, `habit`, and `wishlist` topics. This ensures category-exploration insights aren't drowned out by delivery noise. |
| **Actionability Gap** | Vague Recommended Actions | The LLM generates generic actions like "Improve the app" instead of specific PM recommendations. | **MEDIUM** | **Action Quality Prompt:** System prompt explicitly states: "Each recommended_action must be specific enough for a PM to write a JIRA ticket. BAD: 'Improve discovery.' GOOD: 'Add a "New on Blinkit" category carousel on the homepage showing products from categories the user hasn't explored.'" |
| **Impact Ranking Subjectivity** | LLM Ranks Insights by Frequency Instead of Impact | The LLM may rank insights purely by how often a theme appears, not by potential impact on the North Star metric. | **MEDIUM** | **Explicit Ranking Criteria:** Prompt includes: "Rank insights by potential impact on the North Star metric (% MAC buying from ≥1 new category/month), not just by frequency. A rare insight about a high-leverage behaviour change should rank higher than a common complaint about delivery speed." |
| **Circular Insights** | Insight Restates the Problem Statement | The LLM generates insights like "Users buy from the same categories repeatedly" — which is the problem definition, not an insight. | **MEDIUM** | **Insight Novelty Check:** Validator compares each insight statement against the problem statement text. If cosine similarity > 0.8, flag as "restating problem" and either discard or require the LLM to regenerate with the instruction: "This insight restates the known problem. Generate a deeper insight about WHY this happens or WHAT specifically prevents change." |

### 3.3 Cross-Source Validation

| Category | Edge Case | Description | Severity | Mitigation Strategy |
|:---|:---|:---|:---|:---|
| **Ungrounded Quotes** | Quote Text Doesn't Match Record | The LLM fabricates or paraphrases a quote instead of copying verbatim from the input. | **HIGH** | **Exact Substring Match:** Validator checks that each `representative_quote.text` appears as an exact or near-exact substring (≥90% character overlap) within the referenced `record_id`'s `text_clean` field. Non-matching quotes are stripped from the insight. |
| **Duplicate Insights** | Semantically Identical Insights | Two insights say essentially the same thing in different words: "Users don't discover new categories because the homepage is grocery-focused" vs. "The grocery-heavy homepage prevents category exploration." | **MEDIUM** | **Semantic Dedup:** Compute pairwise cosine similarity on insight statements (using LLM embeddings or simple word overlap). Merge pairs with >80% similarity, keeping the higher-ranked version. |
| **Missing Research Question Coverage** | Some Q1–Q8 Questions Have No Insights | After synthesis, questions like Q7 ("Which user segments are more likely to experiment?") may have zero addressing insights. | **HIGH** | **Coverage Gap Report:** Validator generates a research question coverage matrix. If any question has 0 insights, trigger a targeted re-extraction: filter processed records by that question's relevant topics and run an additional theme extraction + synthesis pass specifically for the gap. |

---

## 4. FastAPI Backend & API Layer

### API Edge Cases

| Category | Edge Case | Description | Severity | Mitigation Strategy |
|:---|:---|:---|:---|:---|
| **Data Loading** | Missing Insight Files on Startup | Server starts before the pipeline has generated `insights_final.json`, causing `FileNotFoundError` on data load. | **HIGH** | **Graceful Empty State:** If insight files don't exist, serve empty arrays `{"insights": [], "meta": {"total": 0}}` with a `"pipeline_status": "not_run"` flag. Dashboard renders a "Run Pipeline First" prompt. |
| **Concurrency** | Pipeline Triggered While API Serves Reads | A `POST /api/v1/pipeline/run` request triggers a long-running pipeline while `GET /api/v1/insights` is serving stale data. | **MEDIUM** | **Async Pipeline with Lock:** Run pipeline in a background thread/process. Set a `pipeline_running = true` flag. API serves existing data during pipeline execution. After completion, reload in-memory cache atomically. Reject concurrent pipeline triggers with `409 Conflict`. |
| **Payload Size** | Large Theme/Insight JSON Responses | With 50+ themes and 20 insights (each with multiple quotes), the JSON response may exceed 1MB, causing slow frontend rendering. | **LOW** | **Pagination + Summarization:** Add `?limit=10&offset=0` pagination to `/api/v1/themes`. For insights, return a summarized view by default; full evidence trail only on `/api/v1/insights/{id}`. |
| **CORS** | Frontend Fetch Blocked by CORS | Vercel frontend domain not matching the Render backend's `allow_origins` list. | **MEDIUM** | **Wildcard in Dev, Strict in Prod:** Use `allow_origins=["*"]` during development. Before production deployment, update to the specific Vercel domain (e.g., `["https://blinkit-discovery.vercel.app"]`). |
| **Environment** | Missing LLM_API_KEY on Startup | Server starts without the `LLM_API_KEY` environment variable, causing crashes when the pipeline is triggered. | **HIGH** | **Startup Validation:** In `config.py`, use `pydantic-settings` with `Field(...)` (required) for `LLM_API_KEY`. The server fails fast on startup with a clear error message: `"LLM_API_KEY is required. Set it in .env or as an environment variable."` |

---

## 5. React Frontend Dashboard

### UI Edge Cases

| Category | Edge Case | Description | Severity | Mitigation Strategy |
|:---|:---|:---|:---|:---|
| **Empty State** | No Insights Available | Dashboard loads before any pipeline has run. All data endpoints return empty arrays. | **HIGH** | **Designed Empty State:** Render a premium empty state component with: "No insights generated yet. Run the discovery pipeline to analyze user feedback." Include a visual illustration (not a blank page). |
| **Loading State** | Slow Backend / Network Timeout | Backend takes > 5 seconds to respond (e.g., Render cold start), causing the dashboard to hang with no feedback. | **HIGH** | **Skeleton Shimmer Loading:** Show animated skeleton placeholders for all components on mount. Set a 10-second fetch timeout. On timeout, show a retry button with "Backend may be waking up. Try again in a few seconds." |
| **Error State** | Backend Unreachable | Render deployment is down or `VITE_API_URL` is misconfigured. All fetches return network errors. | **HIGH** | **Fallback to Sample Data:** Bundle a `sample_insights.json` file in the frontend build. If all API calls fail after 2 retries, render the dashboard with sample data and display a banner: "Showing sample data. Live backend is unreachable." |
| **Overflow** | Long Insight Text Truncation | An insight statement or representative quote exceeds the card width, breaking the layout. | **MEDIUM** | **CSS Text Clamping:** Use `overflow: hidden; text-overflow: ellipsis; display: -webkit-box; -webkit-line-clamp: 3;` on text containers. Expanded view shows full text. |
| **Filter Combinations** | Filtering Results in Zero Items | User selects Research Question Q7 but no insights address it, resulting in an empty filtered view. | **MEDIUM** | **Empty Filter State:** Display "No insights found for this research question" with a suggestion to select a different question. Highlight questions that have ≥1 insight with a count badge. |
| **Chart Rendering** | Zero-Value Chart Segments | If one source (e.g., Forums) has 0 records, chart rendering may produce NaN percentages or invisible segments. | **LOW** | **Zero-Guard in Chart Data:** Filter out sources with 0 records before passing data to Recharts/Chart.js. Display "No data" label for missing sources in the legend. |
| **Responsive** | Mobile Viewport (< 768px) | Sidebar navigation and multi-column insight cards break on small screens. | **MEDIUM** | **Responsive Breakpoints:** At < 768px, collapse sidebar into a top hamburger menu. Stack insight cards vertically. Hide analytics charts behind a "View Analytics" toggle to reduce initial render weight. |

### Build & Deployment Edge Cases

| Category | Edge Case | Description | Severity | Mitigation Strategy |
|:---|:---|:---|:---|:---|
| **Windows** | PowerShell Execution Policy Blocks npm | Running `npm install` on Windows PowerShell throws `SecurityError` because it invokes `npm.ps1` which is blocked by the execution policy. | **HIGH** | **Use npm.cmd:** Directly invoke `npm.cmd install` and `npm.cmd run dev` to bypass PowerShell script execution restrictions. Document this in the README for Windows developers. |
| **Vercel** | `VITE_API_URL` Not Set During Build | Forgetting to set the `VITE_API_URL` environment variable on Vercel causes all API calls to go to `undefined/api/v1/...`, resulting in network errors. | **HIGH** | **Build-Time Validation:** Add a check in `App.jsx` on mount: if `import.meta.env.VITE_API_URL` is falsy, display a prominent error banner: "API URL not configured. Set VITE_API_URL in environment variables." |
| **Vercel** | Browserslist Regex Corruption | Vercel's `@vercel/nft` file tracing utility may corrupt regex patterns in `browserslist` dependency, causing `SyntaxError: Invalid regular expression` at build time. | **MEDIUM** | **Inline PostCSS Config:** If using any PostCSS plugins, configure them inline in `vite.config.js` instead of a separate `postcss.config.js`. Remove `autoprefixer` and `postcss` from devDependencies. This bypasses the `@vercel/nft` tracing bug entirely (same fix applied in the RAGMF project). |

---

## 6. Pipeline Orchestration & Execution

### End-to-End Pipeline Edge Cases

| Category | Edge Case | Description | Severity | Mitigation Strategy |
|:---|:---|:---|:---|:---|
| **Partial Failure** | Scraper Fails Mid-Pipeline | The Reddit scraper fails due to API auth errors, but Play Store and App Store scrapers succeed. The pipeline should not abort entirely. | **CRITICAL** | **Graceful Partial Execution:** Each scraper runs independently inside a try/except block. Failed scrapers log errors and return empty record lists. The pipeline continues with available data. The final insight report includes a `sources_available` field listing which sources contributed. |
| **Empty Pipeline** | All Scrapers Fail | Every scraper fails (network down, all APIs blocked). Processing and analysis stages have no input. | **HIGH** | **Minimum Source Threshold:** If total scraped records < 100 across all sources, abort the pipeline with a clear error: "Insufficient data collected. Minimum 100 records required." Don't generate insights from extremely thin data — it produces unreliable results. |
| **Stale Re-Run** | Pipeline Re-Run Without New Data | User triggers a pipeline re-run, but raw data hasn't changed since the last run. The analysis layer regenerates identical insights, wasting LLM API credits. | **LOW** | **Data Freshness Check:** Before processing, compare the hash of raw data files with the last run's hash (stored in `data/insights/pipeline_meta.json`). If unchanged, skip processing and analysis; serve cached insights. Log: "No new data since last run. Serving cached insights." |
| **Disk Space** | Large Raw Data Accumulation | Multiple pipeline runs accumulate raw JSONL files, potentially consuming significant disk space (especially on Render's limited storage). | **LOW** | **Retention Policy:** Keep only the 2 most recent raw data snapshots per source. On each new scrape, delete JSONL files older than the current + previous run. |
| **Timeout** | LLM Analysis Stage Takes Too Long | Processing 8,000+ records through sentiment, tagging, theme extraction, and synthesis requires 100+ LLM API calls. The full pipeline may take > 20 minutes. | **MEDIUM** | **Progress Logging & Checkpointing:** Log progress after each sub-stage (e.g., "Sentiment: 3000/8000 records processed"). Save intermediate results to disk after each stage so a crashed pipeline can resume from the last checkpoint instead of restarting from scratch. |

---

## 7. LLM Provider & External API Dependencies

| Category | Edge Case | Description | Severity | Mitigation Strategy |
|:---|:---|:---|:---|:---|
| **Groq Downtime** | Groq API Returns 500/503 Errors | Groq's inference service experiences downtime during a pipeline run. | **HIGH** | **Retry + Provider Fallback:** Retry with exponential backoff (1s, 2s, 4s) up to 3 times. If Groq remains unavailable, log the failure and skip the LLM-dependent stage. Do not silently produce empty results — mark affected records with `llm_processed = false`. |
| **Model Deprecation** | `llama-3.1-8b-instant` Removed from Groq | Groq may deprecate or rename the model, causing `ModelNotFoundError`. | **MEDIUM** | **Config-Driven Model Selection:** Model name is stored in `.env` (`LLM_MODEL`), not hardcoded. To switch models, update the env var without code changes. Keep a list of tested fallback models in documentation (e.g., `llama-3.3-70b-versatile`). |
| **JSON Parse Failure** | LLM Returns Malformed JSON | Despite `response_format: json_object`, the LLM occasionally returns truncated or invalid JSON (especially under token pressure). | **HIGH** | **Regex JSON Extraction + Fallback:** Use `re.search(r'\{.*\}', response, re.DOTALL)` to extract JSON blocks. If `json.loads()` still fails, log the raw response and skip that batch. Never crash the pipeline on a single LLM parse failure. |
| **Token Budget** | Free Tier Token Limits Exceeded | Groq's free tier has daily/monthly token limits. A full pipeline run consuming 200K+ tokens may exceed the budget. | **HIGH** | **Token Budgeting:** Estimate total tokens per pipeline run upfront (records × avg chars / 4). If estimated usage exceeds 80% of daily budget, reduce batch sizes or truncate record text to 200 chars. Log token usage per stage for monitoring. |
| **Inconsistent Output** | LLM Produces Different Results on Re-Run | Running the same theme extraction prompt twice produces different themes (inherent LLM non-determinism). | **LOW** | **Temperature 0.3 + Seed Pinning:** Use `temperature=0.3` for more deterministic outputs. If the Groq API supports a `seed` parameter, pin it to a constant value for reproducibility. Accept that minor variations across runs are normal for LLM-generated analysis. |

---

## 8. Data Quality & Bias Concerns

These are not technical bugs but analytical edge cases that affect insight quality.

| Category | Edge Case | Description | Severity | Mitigation Strategy |
|:---|:---|:---|:---|:---|
| **Self-Selection Bias** | Reviewers ≠ All Users | People who write reviews are a vocal minority (typically dissatisfied users). Insights skew negative and may not represent the silent majority. | **HIGH** | **Bias Disclaimer:** Include a prominent note in the dashboard and insight report: "Insights are derived from self-reported public feedback and may over-represent dissatisfied users. Treat as directional signals, not statistically representative findings." |
| **Recency Bias** | Recent Events Dominate | A recent Blinkit outage or viral complaint may temporarily dominate reviews, skewing themes toward a transient issue rather than structural patterns. | **MEDIUM** | **Temporal Windowing:** Tag records with `date` and allow the analysis layer to weight recent reviews lower if a spike is detected. Alternatively, split analysis into "last 30 days" vs. "last 12 months" windows to separate acute issues from chronic patterns. |
| **Competitor Contamination** | Insights About Competitors, Not Blinkit | Users discussing Zepto or Instamart in the context of "which is better" generate themes about competitors that get attributed to Blinkit. | **MEDIUM** | **Blinkit Attribution Filter:** During theme extraction, instruct the LLM: "Generate themes only about Blinkit user behaviour. If a review primarily discusses a competitor, extract insights about what users wish Blinkit offered, not about the competitor's features." |
| **Category Mismatch** | User's Notion of "Category" ≠ Blinkit's Taxonomy | Users may reference products (e.g., "protein powder") without mapping to Blinkit's internal category taxonomy. The tagger may mis-categorize. | **LOW** | **Product-to-Category Mapping:** Maintain a lookup table mapping common product names to Blinkit categories (e.g., `protein powder → health_supplements`, `diapers → baby_products`). Use this mapping in the tagger prompt's few-shot examples. |

---

## 9. Security & Compliance

| Category | Edge Case | Description | Severity | Mitigation Strategy |
|:---|:---|:---|:---|:---|
| **API Key Leak** | Secrets Committed to Git | Developer accidentally commits `.env` file containing Groq API key or Reddit credentials to the repository. | **CRITICAL** | **Multi-Layer Prevention:** (1) `.gitignore` excludes `.env`. (2) Pre-commit hook scans for API key patterns. (3) Use `.env.example` with placeholder values only. (4) If leaked, rotate keys immediately via provider dashboards. |
| **Scraping Legality** | Terms of Service Violations | Aggressive scraping may violate platform ToS (Google Play, Reddit, Twitter). | **HIGH** | **Compliance Checklist:** (1) Respect `robots.txt`. (2) Use official APIs where available (Reddit, Twitter). (3) Rate-limit all scrapers. (4) Don't store or republish PII from reviews. (5) Use data only for research/analysis, not redistribution. |
| **PII in Reviews** | User Reviews Contain Personal Information | Reviews may contain the user's name, phone number, address, or order ID (e.g., "My order #BL123456 was late to 123 MG Road"). | **MEDIUM** | **PII Scrubber in Processing:** Before storing processed records, run regex patterns to redact: phone numbers (`[PHONE REDACTED]`), email addresses (`[EMAIL REDACTED]`), and order IDs matching Blinkit patterns (`[ORDER_ID REDACTED]`). Never send raw PII to the LLM. |
| **No User Tracking** | Dashboard Must Be Stateless | The dashboard should not track who views it, store cookies, or collect analytics. | **LOW** | **Static SPA:** Build as a purely static React app. No authentication, no cookies, no analytics scripts. Serve pre-computed insights via read-only API endpoints. |

---

*Document derived from [architecture.md](file:///c:/Nextleap%20Projects%20Git/ProductManagerFellowshipGraduationProject/docs/architecture.md) and [implementation-plan.md](file:///c:/Nextleap%20Projects%20Git/ProductManagerFellowshipGraduationProject/docs/implementation-plan.md) · Generated for NextLeap PM Fellowship Graduation Project*
