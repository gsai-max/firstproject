import re
from typing import List

def normalize_text(text: str) -> str:
    """
    Converts to lowercase, removes punctuation (keeps only alphanumeric and whitespace),
    and normalizes whitespace sequences to a single space.
    """
    if not text:
        return ""
    text_lower = text.lower()
    # Remove punctuation: replace non-alphanumeric and non-space characters with empty string.
    no_punc = re.sub(r'[^\w\s]', '', text_lower)
    # Normalize whitespaces
    cleaned = " ".join(no_punc.split())
    return cleaned

def check_pieces_in_order(pieces: List[str], target: str) -> bool:
    """
    Checks if all non-empty pieces appear in target in the correct order.
    """
    current_pos = 0
    for piece in pieces:
        if not piece:
            continue
        pos = target.find(piece, current_pos)
        if pos == -1:
            return False
        current_pos = pos + len(piece)
    return True

def validate_quote(quote: str, reviews: List[str]) -> bool:
    """
    Checks if a quote is a verbatim substring of at least one review in the list.
    Supports ellipsis '...' truncation/omission.
    """
    if not quote or not reviews:
        return False
    
    # Split the quote by ellipsis and normalize each piece
    raw_pieces = quote.split("...")
    normalized_pieces = [normalize_text(p) for p in raw_pieces]
    # Filter out empty pieces
    normalized_pieces = [p for p in normalized_pieces if p]
    
    # If the quote has no text contents (only dots/punctuation), it's invalid
    if not normalized_pieces:
        return False
        
    for review in reviews:
        normalized_review = normalize_text(review)
        if check_pieces_in_order(normalized_pieces, normalized_review):
            return True
            
    return False
