# Deployment Guide — Weekly Product Review Pulse

This document outlines the deployment plan, environment setup, and operational runbook for deploying the Groww Weekly Review Pulse system to staging and production environments.

---

## 1. System Architecture Summary

The pulse agent runs as a batch CLI utility (typically triggered weekly via a scheduler). It orchestrates:
1. **Ingestion**: Spawns a local Node.js scraper process (`mcp_servers/playstore_mcp/index.js`) using stdio-based Model Context Protocol (MCP) to scrape reviews.
2. **Analysis**: Uses OpenAI or Hugging Face embeddings, performs local UMAP/HDBSCAN clustering (with K-Means fallbacks), and summarizes low-star complaints using Groq's Llama-3 model.
3. **Ledger Audit**: Records run attempts, statuses (completed, failed), and delivery IDs in a local SQLite database (`db.sqlite`).
4. **Delivery**: Appends reports to the Google Doc and creates Gmail stakeholder drafts via the Railway-hosted external MCP server (`chay-mcp-server-production.up.railway.app`).

---

## 2. Prerequisites & Dependencies

Before deploying, ensure the target runner environment meets the following specifications:
- **Operating System**: Linux (Ubuntu 20.04+ / Debian) or Windows Server.
- **Python**: 3.10 or higher.
- **Node.js**: 18.x or higher (required to run the stdio Play Store scraper subprocess).
- **Network Access**:
  - Outbound HTTPS to `https://api.groq.com` (Groq completion API).
  - Outbound HTTPS to `https://api.openai.com` (OpenAI embeddings API).
  - Outbound HTTPS to `https://play.google.com` (Play Store scraping).
  - Outbound HTTPS/SSE to `https://chay-mcp-server-production.up.railway.app` (Railway-hosted Google Workspace MCP server).

---

## 3. Environment Installation

Run the following commands in the runner environment to bootstrap the project:

### Step 1: Clone the Repository
```bash
git clone <repository_url> MCPAIAutomation
cd MCPAIAutomation
```

### Step 2: Set Up Python Virtual Environment
```bash
# Create virtual environment
python -m venv .venv

# Activate virtual environment
# On Linux/macOS:
source .venv/bin/activate
# On Windows:
.venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Step 3: Install Node.js Scraper Dependencies
```bash
cd mcp_servers/playstore_mcp
npm install
cd ../..
```

### Step 4: Configure Environment Variables
Copy `.env.example` to `.env` and configure key values:
```bash
cp .env.example .env
```

Ensure `.env` contains the required keys:
```env
# Groq API Key for completion reasoning
GROQ_API_KEY=gsk_...

# OpenAI API Key (or HF_TOKEN) for embeddings
OPENAI_API_KEY=sk-proj-...

# Auth bypass key for chay-mcp-server
BYPASS_APPROVAL_KEY=your_mcp_secret_token

# Google Doc ID to append reviews
GOOGLE_DOC_ID=1WEU3Wi1StN0SBq-ICEw0g-...

# Email targets for Gmail drafts (comma separated)
PULSE_EMAIL_TO=product-leads@example.com,support-leads@example.com

# Email mode: draft (safe default) or send
PULSE_EMAIL_MODE=draft
```

---

## 4. Operational Verification

Always run local validation checks to verify API credentials and scraper integrity before scheduling live runs.

### 1. Run Automated Test Suite
Ensure all unit and integration tests are passing in the target environment:
```bash
.venv/bin/pytest
```

### 2. Manual Dry-Run Execution
Execute a dry-run to verify the Play Store scraper, embeddings API, and Groq reasoning work end-to-end without writing to Google Workspace:
```bash
.venv/bin/python -m src.main dry-run --product groww
```
Verify that:
- Clean summaries are outputted in the console.
- Output files are generated under `data/reports/` and `data/emails/`.
- Run ledger records are written to `db.sqlite` with status `COMPLETED`.

---

## 5. Deployment & Scheduling Options

The pulse agent runs as a cron schedule. Here are the two recommended deployment channels:

### Option A: GitHub Actions (Cloud-Hosted runner)
Create a workflow file `.github/workflows/pulse-weekly.yml`:

```yaml
name: Weekly Product Review Pulse

on:
  schedule:
    # Trigger every Monday at 09:00 AM IST (03:30 AM UTC)
    - cron: '30 3 * * 1'
  workflow_dispatch: # Enable manual run trigger

jobs:
  run-pulse:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout Code
        uses: actions/checkout@v4

      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
          cache: 'pip'

      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '20'

      - name: Install Python Dependencies
        run: pip install -r requirements.txt

      - name: Install Node.js Scraper Dependencies
        run: |
          cd mcp_servers/playstore_mcp
          npm install

      - name: Run Pulse Agent
        env:
          GROQ_API_KEY: ${{ secrets.GROQ_API_KEY }}
          OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
          BYPASS_APPROVAL_KEY: ${{ secrets.BYPASS_APPROVAL_KEY }}
          GOOGLE_DOC_ID: ${{ secrets.GOOGLE_DOC_ID }}
          PULSE_EMAIL_TO: ${{ secrets.PULSE_EMAIL_TO }}
          PULSE_EMAIL_MODE: "draft"
        run: |
          python -m src.main run --product groww
```

### Option B: Linux Crontab (Server-Hosted runner)
Configure a crontab entry on a local Linux deployment runner:
```bash
# Open crontab editor
crontab -e
```

Add the following cron entry (Runs every Monday at 9:00 AM IST):
```cron
30 9 * * 1 cd /path/to/MCPAIAutomation && .venv/bin/python -m src.main run --product groww >> /var/log/pulse-weekly.log 2>&1
```

---

## 6. Runbook & Troubleshooting

### Q1: How do I query the status of a specific week?
Run the `status` command:
```bash
python -m src.main status --product groww --iso-week 2026-W25
```
It returns the execution log timestamps, number of reviews, error messages, and URL links to the generated Google Doc section and Gmail draft.

### Q2: What happens if a run fails mid-way?
The run is marked as `FAILED` in the database.
- Correct the environment problem (e.g. invalid API key, network timeout).
- Re-run the command:
  ```bash
  python -m src.main run --product groww --iso-week 2026-W25
  ```
  The orchestrator will see the previous run failed and will **re-trigger** a fresh run for that week.

### Q3: How do I backfill historical weeks?
Use the `backfill` command to run a sequential series of weeks. The orchestrator skips any week that has already completed successfully (idempotent):
```bash
python -m src.main backfill --product groww --from 2026-W20 --to 2026-W25
```
Use `--dry-run` flag to test backfilling without modifying Google Docs/Gmail.
