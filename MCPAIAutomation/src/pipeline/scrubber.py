import re

# Regex for emails
EMAIL_RE = re.compile(
    r'\b[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}\b',
    re.IGNORECASE
)

# Regex for phone numbers (focusing on Indian formats and standard 10-digit formats)
# Supports optional country code +91, 91, 0, or just the number, with optional spaces/dashes.
# Digit sequences like 9876543210, +91 98765 43210, 07890-123456, etc.
PHONE_RE = re.compile(
    r'(?<!\d)(?:\+91[\s.-]?|91[\s.-]?|0[\s.-]?)?[6-9](?:[\s.-]?\d){9}\b'
)

# Regex for Aadhaar card (12 digits, optional spaces/dashes)
AADHAAR_RE = re.compile(
    r'\b\d{4}[\s.-]?\d{4}[\s.-]?\d{4}\b'
)

# Regex for PAN card (5 letters, 4 digits, 1 letter)
PAN_RE = re.compile(
    r'\b[a-zA-Z]{5}\d{4}[a-zA-Z]\b'
)

# Regex for any general long numeric sequences (10+ digits) to protect IDs/Account numbers
GENERIC_ID_RE = re.compile(
    r'\b\d{10,}\b'
)

# Regex for URLs. We will match any URL and redact it to [URL]
URL_RE = re.compile(
    r'https?://\S+',
    re.IGNORECASE
)

def scrub_pii(text: str) -> str:
    """
    Scrubs PII from the review text.
    Redacts:
    - Emails to [EMAIL]
    - Phone numbers to [PHONE]
    - PAN, Aadhaar, and general long numeric sequences (10+ digits) to [ID]
    - URLs to [URL]
    """
    if not text:
        return ""
        
    # Order of execution: Emails, then URLs, then Phones, then PAN/Aadhaar/IDs.
    # We redact URLs early to prevent URL components (like phone numbers/IDs in query strings)
    # from being double-redacted incorrectly.
    # We redact Phones before Aadhaar/generic IDs to prevent 12-digit formatted numbers 
    # (like +919876543210) from being classified as Aadhaar/IDs.
    
    text = EMAIL_RE.sub("[EMAIL]", text)
    text = URL_RE.sub("[URL]", text)
    text = PHONE_RE.sub("[PHONE]", text)
    text = PAN_RE.sub("[ID]", text)
    text = AADHAAR_RE.sub("[ID]", text)
    text = GENERIC_ID_RE.sub("[ID]", text)
    
    return text
