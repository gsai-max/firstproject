import datetime
import urllib.request
import json
import os
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

def generate_markdown_report(
    display_name: str,
    window_weeks: int,
    themes: List[Dict[str, Any]],
    generated_date_str: str = ""
) -> str:
    """
    Renders the weekly pulse report in standard markdown format.
    
    Args:
        display_name: The product display name (e.g., "Groww")
        window_weeks: Number of weeks in the rolling window
        themes: List of theme dicts, each with keys 'theme_name', 'summary', 'quotes', and 'action_ideas'
        generated_date_str: Optional date string. Defaults to today's date in 'YYYY-MM-DD IST'
    
    Returns:
        A markdown string containing the formatted report.
    """
    if not generated_date_str:
        # Generate current time in IST (standardized UTC+5:30)
        # For simplicity, we can get UTC time and add 5:30
        utc_now = datetime.datetime.now(datetime.timezone.utc)
        ist_now = utc_now + datetime.timedelta(hours=5, minutes=30)
        generated_date_str = f"{ist_now.strftime('%Y-%m-%d')} IST"
        
    lines = []
    
    # We don't include the iso_week in Heading 1 of the markdown report itself if we want it to be clean,
    # but wait: Docs section structure says Heading 1: "{display_name} — Weekly Review Pulse — {iso_week}"
    # Wait, the markdown report generated might be appended to the Doc.
    # Let's make sure the heading is dynamically constructed. Let's pass iso_week or make sure we handle it.
    # Let's add iso_week as an optional argument to allow including it.
    return build_markdown_content(display_name, window_weeks, themes, generated_date_str)

def build_markdown_content(
    display_name: str,
    window_weeks: int,
    themes: List[Dict[str, Any]],
    generated_date_str: str,
    iso_week: str = ""
) -> str:
    title_suffix = f" — {iso_week}" if iso_week else ""
    lines = [
        f"# {display_name} — Weekly Review Pulse{title_suffix}",
        "",
        f"Period: Last {window_weeks} weeks (rolling) · Source: Google Play Store · Generated: {generated_date_str}",
        "",
        "## Top themes"
    ]
    
    for theme in themes:
        theme_name = theme.get("theme_name", "Unknown Theme")
        summary = theme.get("summary", "")
        lines.append(f"- {theme_name} — {summary}")
        
    lines.append("")
    lines.append("## Real user quotes")
    
    for theme in themes:
        quotes = theme.get("quotes", [])
        for quote in quotes:
            lines.append(f'- "{quote}"')
            
    lines.append("")
    lines.append("## Action ideas")
    
    for theme in themes:
        action_ideas = theme.get("action_ideas", [])
        for action in action_ideas:
            title = action.get("title", "")
            detail = action.get("detail", "")
            lines.append(f"- {title} — {detail}")
            
    lines.append("")
    lines.append("## Who this helps")
    lines.append("| Audience | Value |")
    lines.append("|---|---|")
    lines.append("| Product | Prioritize roadmap from recurring themes |")
    lines.append("| Support | Spot repeating complaints and quality issues |")
    lines.append("| Leadership | Fast health snapshot tied to customer voice |")
    lines.append("") # trailing newline
    
    return "\n".join(lines)


def generate_email_teaser(
    display_name: str,
    iso_week: str,
    themes: List[Dict[str, Any]],
    doc_id: str,
    heading_id: str = ""
) -> Dict[str, str]:
    """
    Generates the subject, HTML body, and plain text body for the stakeholder email teaser.
    
    Args:
        display_name: The product display name (e.g., "Groww")
        iso_week: ISO 8601 week (e.g., "2026-W23")
        themes: List of theme dicts (top 3-5 will be listed)
        doc_id: Google Doc ID containing the full report
        heading_id: Optional Google Doc heading ID for deep-linking
        
    Returns:
        A dict with 'subject', 'html_body', and 'text_body' keys.
    """
    subject = f"{display_name} Weekly Review Pulse — {iso_week}"
    
    doc_url = f"https://docs.google.com/document/d/{doc_id}"
    if heading_id:
        doc_url = f"{doc_url}#heading={heading_id}"
        
    # Pick top themes (up to 5)
    teaser_themes = themes[:5]
    
    # HTML Body
    html_bullets = []
    for theme in teaser_themes:
        theme_name = theme.get("theme_name", "Unknown Theme")
        summary = theme.get("summary", "")
        html_bullets.append(f"  <li><strong>{theme_name}</strong>: {summary}</li>")
        
    html_body = (
        f"<p>Hello team,</p>\n"
        f"<p>The {display_name} Weekly Review Pulse report for <strong>{iso_week}</strong> is now available.</p>\n"
        f"<p>Key highlights (top themes):</p>\n"
        f"<ul>\n"
        + "\n".join(html_bullets) + "\n"
        f"</ul>\n"
        f"<p>You can read the full report including real user quotes and action ideas in the Google Doc:</p>\n"
        f"<p><a href=\"{doc_url}\">Read Full Report</a></p>\n"
        f"<p>Best regards,<br>\n"
        f"Pulse Agent</p>"
    )
    
    # Text Body
    text_bullets = []
    for theme in teaser_themes:
        theme_name = theme.get("theme_name", "Unknown Theme")
        summary = theme.get("summary", "")
        text_bullets.append(f"- {theme_name}: {summary}")
        
    text_body = (
        f"Hello team,\n\n"
        f"The {display_name} Weekly Review Pulse report for {iso_week} is now available.\n\n"
        f"Key highlights (top themes):\n"
        + "\n".join(text_bullets) + "\n\n"
        f"You can read the full report including real user quotes and action ideas in the Google Doc:\n"
        f"{doc_url}\n\n"
        f"Best regards,\n"
        f"Pulse Agent"
    )
    
    return {
        "subject": subject,
        "html_body": html_body,
        "text_body": text_body
    }


def append_to_google_doc(
    doc_id: str,
    content: str,
    bypass_key: Optional[str] = None,
    iso_week: Optional[str] = None
) -> Dict[str, Any]:
    """
    Appends the report content to the canonical Google Doc via the remote MCP server.
    Falls back to writing a local markdown file under data/reports/ if offline or errors occur.
    """
    url = "https://chay-mcp-server-production.up.railway.app/append_to_doc"
    payload = {
        "doc_id": doc_id,
        "content": content
    }
    data = json.dumps(payload).encode("utf-8")
    headers = {
        "Content-Type": "application/json"
    }
    # Retrieve bypass key from environment if not passed explicitly
    if not bypass_key:
        bypass_key = os.environ.get("BYPASS_APPROVAL_KEY")
    if bypass_key:
        headers["x-approval-key"] = bypass_key

    req = urllib.request.Request(url, data=data, headers=headers, method="POST")
    
    try:
        logger.info(f"Attempting to append report to Google Doc {doc_id} via remote server...")
        with urllib.request.urlopen(req, timeout=30) as response:
            res_data = json.loads(response.read().decode("utf-8"))
            logger.info("Successfully appended report to Google Doc via remote server.")
            return res_data
    except Exception as e:
        logger.warning(f"Failed to append to Google Doc via remote server: {e}. Triggering local fallback...")
        
        # Determine ISO week for fallback file naming
        if not iso_week:
            today = datetime.date.today()
            iso_year, iso_week_num, _ = today.isocalendar()
            iso_week = f"{iso_year}-W{iso_week_num:02d}"
            
        reports_dir = Path("data/reports")
        reports_dir.mkdir(parents=True, exist_ok=True)
        fallback_path = reports_dir / f"weekly_report_groww_{iso_week}.md"
        
        try:
            with open(fallback_path, "w", encoding="utf-8") as f:
                f.write(content)
            logger.info(f"Fallback report successfully saved to {fallback_path}")
            return {
                "status": "fallback",
                "path": str(fallback_path),
                "error": str(e)
            }
        except Exception as file_err:
            logger.critical(f"Failed to save fallback report locally: {file_err}")
            raise file_err


def send_email_teaser_draft(
    to: str,
    subject: str,
    body: str,
    bypass_key: Optional[str] = None,
    iso_week: Optional[str] = None
) -> Dict[str, Any]:
    """
    Creates an email draft via the remote Gmail MCP server.
    Falls back to writing a local JSON file under data/emails/ if offline or errors occur.
    """
    url = "https://chay-mcp-server-production.up.railway.app/create_email_draft"
    payload = {
        "to": to,
        "subject": subject,
        "body": body
    }
    data = json.dumps(payload).encode("utf-8")
    headers = {
        "Content-Type": "application/json"
    }
    if not bypass_key:
        bypass_key = os.environ.get("BYPASS_APPROVAL_KEY")
    if bypass_key:
        headers["x-approval-key"] = bypass_key

    req = urllib.request.Request(url, data=data, headers=headers, method="POST")
    
    try:
        logger.info(f"Attempting to create email draft to {to} via remote server...")
        with urllib.request.urlopen(req, timeout=30) as response:
            res_data = json.loads(response.read().decode("utf-8"))
            logger.info("Successfully created email draft via remote server.")
            return res_data
    except Exception as e:
        logger.warning(f"Failed to create email draft via remote server: {e}. Triggering local fallback...")
        
        # Determine ISO week for fallback file naming
        if not iso_week:
            today = datetime.date.today()
            iso_year, iso_week_num, _ = today.isocalendar()
            iso_week = f"{iso_year}-W{iso_week_num:02d}"
            
        emails_dir = Path("data/emails")
        emails_dir.mkdir(parents=True, exist_ok=True)
        fallback_path = emails_dir / f"email_teaser_groww_{iso_week}.json"
        
        try:
            with open(fallback_path, "w", encoding="utf-8") as f:
                json.dump(payload, f, indent=2)
            logger.info(f"Fallback email draft successfully saved to {fallback_path}")
            return {
                "status": "fallback",
                "path": str(fallback_path),
                "error": str(e)
            }
        except Exception as file_err:
            logger.critical(f"Failed to save fallback email draft locally: {file_err}")
            raise file_err


