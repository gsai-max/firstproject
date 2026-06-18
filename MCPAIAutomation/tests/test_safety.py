import pytest
from src.pipeline.scrubber import scrub_pii


def test_safety_email_scrubbing_complex():
    # Capitalization variations
    assert scrub_pii("Send to USER.NAME@EXAMPLE.COM") == "Send to [EMAIL]"
    
    # Tagged/subaddressed emails
    assert scrub_pii("user+extra-info@domain.co.uk") == "[EMAIL]"
    
    # Weird characters in local-part
    assert scrub_pii("my-email_address.123@sub.domain.org") == "[EMAIL]"
    
    # Multiple emails in a string
    assert scrub_pii("From test1@domain.com to test2@domain.com") == "From [EMAIL] to [EMAIL]"


def test_safety_phone_scrubbing_complex():
    # Standard 10 digits
    assert scrub_pii("my number is 9876543210") == "my number is [PHONE]"
    
    # hyphens
    assert scrub_pii("call 987-654-3210 now") == "call [PHONE] now"
    
    # spaces
    assert scrub_pii("dial 9876 543 210") == "dial [PHONE]"
    
    # +91 prefix with formats
    assert scrub_pii("+919876543210 is active") == "[PHONE] is active"
    assert scrub_pii("+91-9876543210 is active") == "[PHONE] is active"
    assert scrub_pii("+91 98765 43210 is active") == "[PHONE] is active"
    
    # 0 prefix
    assert scrub_pii("09876543210 is my number") == "[PHONE] is my number"


def test_safety_id_scrubbing_complex():
    # Aadhaar format variations
    assert scrub_pii("My Aadhaar is 1234 5678 9012") == "My Aadhaar is [ID]"
    assert scrub_pii("Aadhaar: 1234-5678-9012") == "Aadhaar: [ID]"
    
    # PAN card variations
    assert scrub_pii("My PAN is ABCDE1234F") == "My PAN is [ID]"
    assert scrub_pii("PAN card abcde5678f is verified") == "PAN card [ID] is verified"
    
    # General long numeric sequences (10+ digits)
    assert scrub_pii("Account number 1234567890") == "Account number [ID]"  # 10 digits
    assert scrub_pii("Reference 123456789012345") == "Reference [ID]"  # 15 digits


def test_safety_url_scrubbing_complex():
    # Standard URLs
    assert scrub_pii("Check https://groww.in") == "Check [URL]"
    assert scrub_pii("http://example.com/page?ref=123") == "[URL]"
    
    # Mixed case scheme
    assert scrub_pii("Check HTTPS://GROWW.IN") == "Check [URL]"
    
    # Url with query parameters containing tokens
    assert scrub_pii("Goto https://groww.in/dashboard?token=abcdef12345&phone=9876543210") == "Goto [URL]"


def test_safety_scrubbing_non_pii_intact():
    # Safe short numbers
    assert scrub_pii("Only 5 stars") == "Only 5 stars"
    assert scrub_pii("It is 123 USD") == "It is 123 USD"
    
    # Standard text remains unmodified
    text = "The app has a very nice interface and execution is smooth."
    assert scrub_pii(text) == text
