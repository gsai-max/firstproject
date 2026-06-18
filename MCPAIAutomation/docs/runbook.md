# Operations Runbook — Weekly Review Pulse

This document guides system administrators and engineers on monitoring, manual overrides, troubleshooting, and backfilling operations.

---

## 1. Auditing Executions & Status Checks

The weekly pulse agent maintains a SQLite audit log in `db.sqlite` containing execution run details and delivery tracking IDs.

### 1.1 Command-Line Status Check
To view the status of a specific week's run:
```bash
python -m src.main status --product groww --iso-week 2026-W25
```

It returns:
- **Run ID**: Unique ID of the execution (format: `{product}-{iso_week}-{timestamp}`).
- **Status**: Current execution state (`PENDING`, `COMPLETED`, or `FAILED`).
- **Metadata**: Number of reviews analyzed, timestamp records.
- **Deliveries**: 
  - **Google Doc**: Heading ID and target URL deep link.
  - **Gmail**: Draft ID and drafts folder URL.

---

## 2. Failure Recovery & Manual Overrides

If a run fails due to network disconnects, API rate limits, or remote server timeouts, the status will be set to `FAILED`.

### 2.1 Forcing a Retry
To retry a failed week, simply run the normal weekly pulse command specifying that week:
```bash
python -m src.main run --product groww --iso-week 2026-W25
```
Because the previous run is marked as `FAILED` (not `COMPLETED`), the orchestrator will automatically bypass the idempotency skip and trigger a new run.

### 2.2 Double Append Prevention (Idempotent Delivery)
If the Google Doc write succeeded during the first attempt but Gmail failed:
1. Retrying the run will re-trigger the Doc append.
2. The remote Docs MCP server searches the Google Doc for an existing heading matching the week label (e.g. `Groww — Weekly Review Pulse — 2026-W25`).
3. If it finds the heading, **it does not append a duplicate section**; it simply returns the existing heading ID and URL.
4. The pipeline then proceeds to safely create the Gmail draft, completing the failed delivery channel without duplicates.

---

## 3. Troubleshooting Connection & Auth Errors

### 3.1 Remote Railway Server Offline
If you receive a connection error indicating the remote Railway server is offline:
- Verify that `https://chay-mcp-server-production.up.railway.app` is online.
- Check the Railway console logs for `Chay-MCP-Server` to ensure the server is running and healthy.

### 3.2 Authorization Bypass Failures (x-approval-key)
If Docs or Gmail deliveries return a `403 Forbidden` or credential error:
- Verify that the `BYPASS_APPROVAL_KEY` in `.env` is set correctly and matches the secret configured on the remote Railway server.
- If the bypass token is missing or incorrect, the Railway server will default to rejecting automatic writes.

---

## 4. Running Historical Backfills

To generate pulse reports for historical weeks:
```bash
python -m src.main backfill --product groww --from 2026-W20 --to 2026-W25
```

### Backfill Features & Safety:
- **Skipping Completed Weeks**: The backfill command automatically skips any week that already has a `COMPLETED` run recorded in `db.sqlite`.
- **Stop on Failure**: Pass the `--stop-on-failure` flag to abort the entire sequence if a single week fails:
  ```bash
  python -m src.main backfill --product groww --from 2026-W20 --to 2026-W25 --stop-on-failure
  ```
- **Dry-Run Backfills**: Run backfills with `--dry-run` to generate and save local reports to `data/reports/` and `data/emails/` without writing to Google Workspace:
  ```bash
  python -m src.main backfill --product groww --from 2026-W20 --to 2026-W25 --dry-run
  ```

---

## 5. Security & Safety Auditing

### 5.1 Run Safety Tests
To confirm that the PII scrubber correctly redacts emails, phone numbers, Aadhaar cards, PAN cards, and URLs:
```bash
pytest tests/test_safety.py
```
All safety regex assertions should pass.
