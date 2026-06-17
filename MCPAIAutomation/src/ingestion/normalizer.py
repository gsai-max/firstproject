import re

# Regex matching standard emoji ranges, symbols, dingbats, and star ranges
EMOJI_RE = re.compile(
    "["
    "\U00010000-\U0010ffff"  # Most emojis
    "\u2600-\u27bf"          # Dingbats & misc symbols
    "\u2b00-\u2bff"          # Miscellaneous Symbols and Arrows (includes stars like \u2b50)
    "\u200d"                 # Zero-width joiner
    "]+",
    flags=re.UNICODE
)

# Common Romanized Hindi / Hinglish functional words
HINGLISH_INDICATORS = {
    "hai", "hain", "bhi", "kabhi", "nhi", "nahi", "ko", "ka", "ke", "aur", "mera", 
    "meri", "mere", "paisa", "paise", "bekar", "ghatiya", "karta", "karo", 
    "raha", "rha", "hota", "hoti", "ye", "wo", "sabse", "bhai", "samjh", 
    "aata", "kat", "krta", "bahut", "pehle", "thik", "baad", "rh", "tha", "se"
}

def contains_emojis(text: str) -> bool:
    """Checks if the text contains any emojis or symbols."""
    return bool(EMOJI_RE.search(text))


def contains_hinglish(text: str) -> bool:
    """Checks if the text contains common Romanized Hindi/Hinglish words."""
    if not text:
        return False
    # Normalize punctuation/spacing to split into words cleanly
    cleaned = re.sub(r'[^\w\s]', ' ', text.lower())
    words = set(cleaned.split())
    return not words.isdisjoint(HINGLISH_INDICATORS)


def is_english(text: str, threshold: float = 0.9) -> bool:
    """
    Checks if the text is primarily English/ASCII.
    Returns True if the ratio of ASCII characters to total characters is above the threshold.
    """
    if not text:
        return False
    ascii_count = sum(1 for c in text if c.isascii())
    return (ascii_count / len(text)) >= threshold


def clean_and_normalize(text: str, min_words: int = 8) -> str:
    """
    Cleans and checks if text meets word count, emoji-free, and language filters.
    Returns the cleaned string if valid, otherwise empty string.
    """
    if not text:
        return ""
    
    # Discard if it contains emojis
    if contains_emojis(text):
        return ""
        
    # Discard if it contains Romanized Hindi/Hinglish words
    if contains_hinglish(text):
        return ""
    
    # Normalize whitespaces
    cleaned = " ".join(text.split())
    
    # Check word count
    words = cleaned.split()
    if len(words) < min_words:
        return ""
        
    # Check English language requirement
    if not is_english(cleaned):
        return ""
        
    return cleaned


