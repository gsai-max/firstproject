import pytest
import json
from unittest.mock import patch, MagicMock
from src.delivery.client import generate_markdown_report, generate_email_teaser, append_to_google_doc, send_email_teaser_draft

@pytest.fixture
def sample_themes():
    return [
        {
            "theme_name": "App performance & bugs",
            "summary": "Lag, crashes during trading hours; login/session timeouts.",
            "quotes": [
                "The app freezes exactly when the market opens, very frustrating.",
                "Frequent crashes after update."
            ],
            "action_ideas": [
                {
                    "title": "Stabilize peak-time performance",
                    "detail": "Scale infra during market hours; improve crash visibility."
                }
            ]
        },
        {
            "theme_name": "Customer support friction",
            "summary": "Slow responses; unresolved tickets.",
            "quotes": [
                "Support takes days to reply and doesn't solve the issue."
            ],
            "action_ideas": [
                {
                    "title": "Improve support SLA visibility",
                    "detail": "Expected response time in-app; ticket status tracking."
                }
            ]
        }
    ]

def test_generate_markdown_report_structure(sample_themes):
    display_name = "Groww"
    window_weeks = 10
    generated_date_str = "2026-06-08 IST"
    
    report = generate_markdown_report(
        display_name=display_name,
        window_weeks=window_weeks,
        themes=sample_themes,
        generated_date_str=generated_date_str
    )
    
    # Check Heading 1
    assert f"# {display_name} — Weekly Review Pulse" in report
    
    # Check Metadata Paragraph
    assert f"Period: Last {window_weeks} weeks (rolling) · Source: Google Play Store · Generated: {generated_date_str}" in report
    
    # Check Section Headings
    assert "## Top themes" in report
    assert "## Real user quotes" in report
    assert "## Action ideas" in report
    assert "## Who this helps" in report
    
    # Check Top Themes content
    assert "- App performance & bugs — Lag, crashes during trading hours; login/session timeouts." in report
    assert "- Customer support friction — Slow responses; unresolved tickets." in report
    
    # Check Real User Quotes content
    assert '- "The app freezes exactly when the market opens, very frustrating."' in report
    assert '- "Frequent crashes after update."' in report
    assert '- "Support takes days to reply and doesn\'t solve the issue."' in report
    
    # Check Action Ideas content
    assert "- Stabilize peak-time performance — Scale infra during market hours; improve crash visibility." in report
    assert "- Improve support SLA visibility — Expected response time in-app; ticket status tracking." in report
    
    # Check Who this helps table
    assert "| Audience | Value |" in report
    assert "|---|---|" in report
    assert "| Product | Prioritize roadmap from recurring themes |" in report
    assert "| Support | Spot repeating complaints and quality issues |" in report
    assert "| Leadership | Fast health snapshot tied to customer voice |" in report

def test_generate_markdown_report_default_date(sample_themes):
    display_name = "Groww"
    window_weeks = 10
    
    report = generate_markdown_report(
        display_name=display_name,
        window_weeks=window_weeks,
        themes=sample_themes
    )
    
    # The generated date string should default to today's date in IST format
    assert "IST" in report
    assert "Generated:" in report

def test_generate_email_teaser_no_heading(sample_themes):
    display_name = "Groww"
    iso_week = "2026-W23"
    doc_id = "test_google_doc_id"
    
    teaser = generate_email_teaser(
        display_name=display_name,
        iso_week=iso_week,
        themes=sample_themes,
        doc_id=doc_id
    )
    
    # Check subject
    assert teaser["subject"] == f"{display_name} Weekly Review Pulse — {iso_week}"
    
    # Check HTML body link
    expected_doc_url = f"https://docs.google.com/document/d/{doc_id}"
    assert f'href="{expected_doc_url}"' in teaser["html_body"]
    
    # Check text body link
    assert expected_doc_url in teaser["text_body"]
    
    # Check that themes are included in highlights
    assert "<strong>App performance & bugs</strong>" in teaser["html_body"]
    assert "- App performance & bugs" in teaser["text_body"]

def test_generate_email_teaser_with_heading(sample_themes):
    display_name = "Groww"
    iso_week = "2026-W23"
    doc_id = "test_google_doc_id"
    heading_id = "heading-12345"
    
    teaser = generate_email_teaser(
        display_name=display_name,
        iso_week=iso_week,
        themes=sample_themes,
        doc_id=doc_id,
        heading_id=heading_id
    )
    
    expected_doc_url = f"https://docs.google.com/document/d/{doc_id}#heading={heading_id}"
    assert f'href="{expected_doc_url}"' in teaser["html_body"]
    assert expected_doc_url in teaser["text_body"]

def test_generate_email_teaser_max_themes_cap():
    display_name = "Groww"
    iso_week = "2026-W23"
    doc_id = "test_google_doc_id"
    
    # Generate 7 themes to test cap of 5
    many_themes = [
        {"theme_name": f"Theme {i}", "summary": f"Summary {i}"} for i in range(1, 8)
    ]
    
    teaser = generate_email_teaser(
        display_name=display_name,
        iso_week=iso_week,
        themes=many_themes,
        doc_id=doc_id
    )
    
    # HTML bullets count should be 5
    assert teaser["html_body"].count("<li>") == 5
    assert "Theme 5" in teaser["html_body"]
    assert "Theme 6" not in teaser["html_body"]
    
    # Text bullets count should be 5
    assert teaser["text_body"].count("\n- Theme") == 5
    assert "Theme 5" in teaser["text_body"]
    assert "Theme 6" not in teaser["text_body"]


def test_append_to_google_doc_success():
    doc_id = "test_doc_id"
    content = "Hello, world!"
    
    mock_res = MagicMock()
    mock_res.read.return_value = b'{"status": "success", "response": {"documentId": "test_doc_id"}}'
    
    mock_context = MagicMock()
    mock_context.__enter__.return_value = mock_res
    
    with patch("urllib.request.urlopen", return_value=mock_context) as mock_urlopen:
        res = append_to_google_doc(doc_id=doc_id, content=content, bypass_key="mock_key")
        
        assert res["status"] == "success"
        assert res["response"]["documentId"] == "test_doc_id"
        mock_urlopen.assert_called_once()
        # Ensure the request URL was correct and header was passed
        called_req = mock_urlopen.call_args[0][0]
        assert called_req.full_url == "https://chay-mcp-server-production.up.railway.app/append_to_doc"
        assert called_req.headers.get("X-approval-key") == "mock_key"


def test_append_to_google_doc_fallback():
    import shutil
    doc_id = "test_doc_id"
    content = "Fallback test content"
    iso_week = "2026-W99"
    
    # Mock urlopen to raise an exception
    with patch("urllib.request.urlopen", side_effect=Exception("Connection refused")) as mock_urlopen:
        res = append_to_google_doc(
            doc_id=doc_id,
            content=content,
            bypass_key="mock_key",
            iso_week=iso_week
        )
        
        assert res["status"] == "fallback"
        assert "weekly_report_groww_2026-W99.md" in res["path"]
        assert "Connection refused" in res["error"]
        mock_urlopen.assert_called_once()
        
        # Verify file was written
        from pathlib import Path
        filepath = Path(res["path"])
        assert filepath.exists()
        with open(filepath, "r", encoding="utf-8") as f:
            written_content = f.read()
        assert written_content == content
        
        # Clean up the created fallback file
        if filepath.exists():
            filepath.unlink()


def test_send_email_teaser_draft_success():
    to = "leads@example.com"
    subject = "Groww Review Pulse"
    body = "Draft email content"
    
    mock_res = MagicMock()
    mock_res.read.return_value = b'{"status": "success", "response": {"id": "mock_draft_id"}}'
    
    mock_context = MagicMock()
    mock_context.__enter__.return_value = mock_res
    
    with patch("urllib.request.urlopen", return_value=mock_context) as mock_urlopen:
        res = send_email_teaser_draft(to=to, subject=subject, body=body, bypass_key="mock_key")
        
        assert res["status"] == "success"
        assert res["response"]["id"] == "mock_draft_id"
        mock_urlopen.assert_called_once()
        called_req = mock_urlopen.call_args[0][0]
        assert called_req.full_url == "https://chay-mcp-server-production.up.railway.app/create_email_draft"
        assert called_req.headers.get("X-approval-key") == "mock_key"


def test_send_email_teaser_draft_fallback():
    to = "leads@example.com"
    subject = "Groww Review Pulse"
    body = "Draft email content"
    iso_week = "2026-W99"
    
    with patch("urllib.request.urlopen", side_effect=Exception("Connection refused")) as mock_urlopen:
        res = send_email_teaser_draft(
            to=to,
            subject=subject,
            body=body,
            bypass_key="mock_key",
            iso_week=iso_week
        )
        
        assert res["status"] == "fallback"
        assert "email_teaser_groww_2026-W99.json" in res["path"]
        assert "Connection refused" in res["error"]
        mock_urlopen.assert_called_once()
        
        from pathlib import Path
        filepath = Path(res["path"])
        assert filepath.exists()
        with open(filepath, "r", encoding="utf-8") as f:
            written_payload = json.load(f)
        assert written_payload["to"] == to
        assert written_payload["subject"] == subject
        assert written_payload["body"] == body
        
        if filepath.exists():
            filepath.unlink()


