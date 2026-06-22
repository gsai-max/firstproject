import re

class PIIScrubber:
    """
    Utility class to detect and mask Personally Identifiable Information (PII) 
    from user queries to comply with privacy and safety guidelines.
    """
    # Indian PAN card: 5 uppercase letters, 4 digits, 1 uppercase letter
    PAN_PATTERN = re.compile(r'\b[A-Za-z]{5}\d{4}[A-Za-z]\b')
    
    # Indian Aadhaar card: 12 digits (with optional spaces or hyphens between 4-digit blocks)
    AADHAAR_PATTERN = re.compile(r'\b\d{4}[ -]?\d{4}[ -]?\d{4}\b')
    
    # Email: standard pattern
    EMAIL_PATTERN = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b')
    
    # Phone number: 10 digit number starting with 6-9, optional +91/0 prefix and formatting
    PHONE_PATTERN = re.compile(
        r'\b(?:(?:\+|0{0,2})91[\s-]?)?[6-9]\d{9}\b|\b(?:\d{3}[\s-]?\d{3}[\s-]?\d{4})\b'
    )
    
    # OTP Context Pattern: Matches keywords suggesting an OTP is present in the text
    OTP_CONTEXT_PATTERN = re.compile(r'\b(?:otp|code|pin|password|verification)\b', re.IGNORECASE)

    @classmethod
    def scrub_text(cls, text: str) -> str:
        """
        Scrub sensitive PII from the input string, replacing matches with placeholders.
        """
        if not text:
            return ""
            
        # Scrub PAN
        text = cls.PAN_PATTERN.sub("[MASKED_PAN]", text)
        
        # Scrub Aadhaar
        text = cls.AADHAAR_PATTERN.sub("[MASKED_AADHAAR]", text)
        
        # Scrub Email
        text = cls.EMAIL_PATTERN.sub("[MASKED_EMAIL]", text)
        
        # Scrub Phone
        text = cls.PHONE_PATTERN.sub("[MASKED_PHONE]", text)
        
        # Scrub OTP (only if context keywords like 'otp', 'code', etc. are present)
        if cls.OTP_CONTEXT_PATTERN.search(text):
            def otp_repl(match):
                val = match.group(0)
                # Ignore numbers that look like years (e.g. 1900 to 2100) to avoid false positives
                if len(val) == 4:
                    try:
                        num = int(val)
                        if 1900 <= num <= 2100:
                            return val
                    except ValueError:
                        pass
                return "[MASKED_OTP]"
            
            text = re.sub(r'\b\d{4,6}\b', otp_repl, text)
            
        return text
