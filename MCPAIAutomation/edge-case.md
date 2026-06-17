# Weekly Product Review Pulse — Edge Cases and Failure Modes

This document catalogs the corner cases, failure modes, and mitigation strategies for the automated weekly review pulse system. It acts as a guide for both system developers and operators to ensure the robustness, safety, and reliability of the pipeline.

---

## 1. Data Ingestion & Normalization Layer

This layer interfaces with the external Google Play Store scrapers and filters raw review feeds.

| Category | Edge Case | Description | Severity | Mitigation Strategy |
| :--- | :--- | :--- | :--- | :--- |
| **Scraper** | Play Store Layout Change | The Google Play Store updates its web structure, causing the scraper library to fail or return 0 reviews. | **CRITICAL** | Fail-safe: Detect 0 reviews returned for high-volume apps. Log alert. Fallback to cached reviews if run is a retry, or abort cleanly rather than outputting empty files. |
| **Volume** | Zero Reviews in Window | A quiet week (or a newer product) receives 0 reviews within the rolling 8-12 week window. | **HIGH** | If raw review count is `<20`, trigger the **ML Floor** abort condition immediately. Do not trigger downstream embeddings or LLM APIs. |
| **Volume** | High Review Spike | A major release or incident causes reviews to spike (e.g., 20,000+ reviews). | **MEDIUM** | Enforce a hard configuration cap on raw reviews parsed per run (`max_reviews: 5000`). Paginate and select the most recent reviews up to the cap to avoid out-of-memory errors. |
| **Content** | Multi-lingual / Non-English | Reviews containing Hinglish, regional Indian languages, or emojis (e.g., "Bahut badhiya app 👍"). | **LOW** | Normalization filter strictly enforces `allowed_language: en` and rejects reviews with no English characters. Emoji are stripped during pre-processing. |
| **Content** | Ultra-Short Text | Reviews consisting of only "Good", "Worst app", or rating-only reviews. | **LOW** | Reject review texts shorter than `min_words: 8` words to ensure there is enough semantic context for clustering. |
| **Duplicates** | Spammed / Retried Reviews | Identical review content submitted multiple times by a user, or retrieved across paginated queries. | **LOW** | Deduplicate raw reviews by taking a cryptographic hash of `(text, rating, published_at)` before normalization. |

---

## 2. PII Scrubbing Layer

Before sending any review text to embedding or LLM endpoints, private identifier data must be redacted.

> [!WARNING]
> PII scrubbing failure can lead to severe regulatory and compliance breaches if personal information gets embedded or sent to stakeholders.

### PII Edge Cases and Sanitization
* **Obfuscated Phone Numbers:** Users write phone numbers with spaces, dashes, or custom symbols to bypass standard regex (e.g., `+91 98-76-54-32-10` or `9 8 7 6 5 4 3 2 1 0`).
  * *Mitigation:* Normalize review texts (strip spaces/dashes temporarily to check for 10-digit contiguous numeric patterns) during PII scans.
* **Transaction & Reference Numbers:** Transaction IDs, PAN/Aadhaar cards, or bank account numbers might resemble phone numbers.
  * *Mitigation:* Employ generic redaction tags like `[ID]` or `[NUMERIC]` for any numeric sequence containing 9-16 characters.
* **Names as PII:** Reviewers sometimes sign off with their real names (e.g., "Thanks, Rohan").
  * *Mitigation:* While regex cannot catch all human names without high false-positives, we prioritize redacting contact vectors (emails, phones) and typical ID structures. LLM prompts are instructed to avoid referencing specific names in report outputs.

---

## 3. Reasoning & Clustering Layer

This layer handles vector representations, density clustering, and LLM text generation.

```
                  ┌──────────────────────┐
                  │ Normalized Reviews   │
                  └──────────┬───────────┘
                             │
                             ▼
                    [ Count >= 20? ]
                      /          \
                   (No)          (Yes)
                    /              \
         ┌─────────▼────────┐    ┌──▼──────────────────┐
         │ Abort (ML Floor) │    │ OpenAI Embeddings   │
         └──────────────────┘    └─────────┬───────────┘
                                           │
                                           ▼
                                      [ UMAP ]
                                           │
                                           ▼
                                     [ HDBSCAN ]
                                           │
                                           ▼
                                    [ LLM Summary ]
                                           │
                                           ▼
                                  [ Verbatim Quote? ]
                                   /             \
                                (No)            (Yes)
                                /                 \
                     ┌─────────▼────────┐    ┌─────▼─────────────┐
                     │ Omit / Re-prompt │    │ Add to Doc Section│
                     └──────────────────┘    └───────────────────┘
```

### 3.1 OpenAI Embeddings
* **API Timeout / Outage:** The embedding service goes offline.
  * *Mitigation:* Implement exponential backoff (e.g., 3 retries starting at 2s, up to 15s). If it persistently fails, abort the pipeline and mark the run as `failed` in the Ledger.
* **Batch Size Exceeded:** Large review lists exceed token or payload limits for a single HTTP call.
  * *Mitigation:* Batch requests in chunks of 64 (configured via `embedding.batch_size`).

### 3.2 UMAP + HDBSCAN
* **Clustering Failures (No Clusters / All Noise):** HDBSCAN labels every single normalized review as noise (`-1`). This happens when feedback is completely uniform or highly sparse.
  * *Mitigation:* If no clusters satisfy the minimum size (`min_cluster_size=5`), fall back to a simple keyword-based partition or log a descriptive pipeline error and abort.
* **One Massive Cluster:** An single issue dominates (e.g., a systemic outage), grouping 90% of reviews into one cluster.
  * *Mitigation:* The LLM prompt is designed to segment major issues into sub-themes based on sample variance, preventing a single giant wall of text.
* **System Resource Exhaustion:** Running heavy vector operations (UMAP/HDBSCAN) on a low-powered server or runner.
  * *Mitigation:* Keep the maximum review volume strictly capped (`max_reviews: 5000`). If volume rises, down-sample the review pool randomly before embedding.

### 3.3 LLM Summarization (Groq / Llama)
* **Rate Limits (TPM / RPM):** Groq API enforces strict rate limits.
  * *Mitigation:* Execute LLM completion requests sequentially with a `request_interval_seconds: 2` delay between calls.
* **Non-JSON or Malformed LLM Outputs:** LLM outputs conversational prefixes or fails to output syntactically correct JSON despite schema instructions.
  * *Mitigation:* Wrap Groq calls in structured schemas (e.g. using `instructor` or strict JSON parsing blocks). Validate JSON keys immediately upon retrieval and fail early if invalid.
* **Token Cap Overruns:** Massive text dumps exceed the 12,000 token budget per run.
  * *Mitigation:* Strictly limit the number of sample reviews passed to the LLM per cluster (`max_samples_per_cluster: 8`), selecting those closest to the cluster centroid.

### 3.4 Quote Validation
* **Fuzzy Match Failure:** LLM modifies a user quote slightly to fix a typo or grammar (e.g. changing "app crash on login" to "the app crashes on login").
  * *Mitigation:* Normalize both candidate quote and review texts (convert to lowercase, strip non-alphanumeric characters) before checking for a substring match.
* **Ellipsis Match Complexity:** LLM returns an abbreviated quote (e.g., "The app freezes... very frustrating").
  * *Mitigation:* Split the quote on ellipsis (`...` or `…`) and verify each substring independently. Both pieces must match in order within the same source review.
* **Total Quote Loss:** All extracted quotes for a theme fail validation.
  * *Mitigation:* Re-prompt the LLM once, explicitly detailing the mismatch. If the second attempt fails, omit that specific theme from the report to maintain data integrity.

---

## 4. Integration & Delivery Layer

This layer interacts with Google Workspace via MCP servers.

> [!IMPORTANT]
> Since Google Docs and Gmail writes are executed as separate operations, network interrupts can cause the system to enter a partial-delivery state.

### 4.1 Google Docs MCP
* **Document Lock / Deletion:** The target Google Doc ID is deleted, has permissions changed, or is locked due to concurrent editing.
  * *Mitigation:* Verify write permissions before executing the append. If the Doc write fails, do not proceed to Gmail. Mark run as `failed` in the Ledger.
* **Partial Write / Interruption:** Connection drops mid-write, leaving a corrupt or half-written section.
  * *Mitigation:* Docs MCP writes should bundle structural updates in a single batch request to the Google Docs API (all-or-nothing write transaction).

### 4.2 Gmail MCP
* **Invalid Recipients:** Configured email addresses do not exist or bounce back.
  * *Mitigation:* Catch API errors returned by Gmail MCP. If an address fails, send to a configured fallback admin address instead.
* **OAuth Scope Expiry:** Gmail write permissions are revoked, but Docs permissions remain active.
  * *Mitigation:* The system halts immediately when a Workspace delivery tool returns a `401 Unauthorized` or scope error, prompting operators to refresh server configurations.

### 4.3 Workspace Dry-Runs & Offline Fallbacks
* **Offline Mock Mode:** Dev and staging environments running without Workspace API access.
  * *Mitigation:* When `--dry-run` or mock mode is active, the orchestrator redirects output templates to:
    * Google Doc Section $\rightarrow$ saved as raw Markdown to `data/reports/groww-YYYY-Www.md`
    * Gmail Teaser $\rightarrow$ saved as HTML/Text drafts to `data/emails/groww-YYYY-Www.html`

---

## 5. Ledger & Orchestration Layer

Tracks run status, protects against duplicate execution, and enforces idempotency.

```
       ┌────────────────────────┐
       │ CLI Trigger: run/retry │
       └───────────┬────────────┘
                   │
                   ▼
         [ Check Run Ledger ]
          /              \
    (Exists & Done)   (New or Failed)
        /                  \
 ┌─────▼─────────────┐   ┌──▼───────────────────┐
 │ Skip: Success Log │   │ Start Execution      │
 └───────────────────┘   └──────────┬───────────┘
                                    │
                                    ▼
                          [ Write Google Doc ]
                                    │
                                    ▼
                           [ Send Gmail Email ]
                                    │
                                    ▼
                         [ Commit Ledger 'Done' ]
```

### 5.1 Idempotency & Partial Failure Recoveries

* **Scenario A: Docs succeeds, Gmail fails, Ledger is not marked 'completed'.**
  * *Resolution on Retry:*
    1. Orchestrator reads the Ledger and sees the run failed at the Gmail stage.
    2. Docs MCP checks for the stable section anchor (`{product}-{iso_week}`). Finding it already present, it skips editing and returns the existing heading URL.
    3. Gmail MCP checks the idempotency key (`{product}-{iso_week}-email`). If Gmail previously sent it, it skips sending. If not, it delivers the email.
    4. Ledger is updated to `completed`.
* **Scenario B: Docs and Gmail succeed, but Ledger write fails (disk full / db locked).**
  * *Resolution:*
    * Logs generate a high-priority alert.
    * On the next automated run, the idempotency checks on Docs and Gmail MCP level (using the stable heading anchor and message headers) prevent double delivery even without local database records.

### 5.2 Concurrency & Timezones

* **Race Conditions:** Two instances of the CLI run simultaneously (e.g. manual backfill overlaps with a cron schedule).
  * *Mitigation:* The SQLite database uses brief write-locks. Run orchestrator checks for a `pending` status in the `runs` ledger. If a run is already marked `pending`, subsequent processes block or terminate immediately.
* **ISO Week Boundaries:** Differences in server timezones (e.g., UTC vs IST) resulting in calculations pointing to incorrect ISO weeks.
  * *Mitigation:* Enforce IST (Indian Standard Time) timezone globally inside the CLI orchestrator when defining ISO week boundaries for Indian products like Groww.
