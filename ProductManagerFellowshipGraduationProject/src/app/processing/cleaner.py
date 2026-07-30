import html
import re
import unicodedata
from typing import Optional

from src.app.models.domain import ProcessedFeedbackRecord, RawFeedbackRecord


class DataCleaner:
    """Cleans, normalizes, and filters raw feedback records."""

    MIN_WORD_COUNT = 8

    NON_ENGLISH_SCRIPTS = {
        "DEVANAGARI", "BENGALI", "TAMIL", "TELUGU", "KANNADA", "MALAYALAM",
        "GUJARATI", "GURMUKHI", "ORIYA", "ARABIC", "CYRILLIC", "GREEK",
        "HEBREW", "THAI", "HANGUL", "HIRAGANA", "KATAKANA", "CJK", "HAN"
    }

    def has_emoji(self, text: str) -> bool:
        """Checks if text contains emoji characters or symbols."""
        if not text:
            return False
        for ch in text:
            cat = unicodedata.category(ch)
            if cat == "So":
                return True
            cp = ord(ch)
            if (
                0x1F600 <= cp <= 0x1F64F
                or 0x1F300 <= cp <= 0x1F5FF
                or 0x1F680 <= cp <= 0x1F6FF
                or 0x1F1E0 <= cp <= 0x1F1FF
                or 0x2600 <= cp <= 0x27BF
                or 0xFE00 <= cp <= 0xFE0F
                or 0x1F900 <= cp <= 0x1F9FF
                or 0x1FA70 <= cp <= 0x1FAFF
                or 0x2300 <= cp <= 0x23FF
                or cp in (0x2B50, 0x200D, 0x20E3)
            ):
                return True
        return False

    def is_other_language(self, text: str) -> bool:
        """Checks if text contains non-English / non-Latin script characters."""
        if not text:
            return False
        for ch in text:
            cat = unicodedata.category(ch)
            name = unicodedata.name(ch, "")
            words = set(name.replace("-", " ").split())
            if words.intersection(self.NON_ENGLISH_SCRIPTS):
                return True
            if cat.startswith("L") and "LATIN" not in name:
                return True
        return False

    def clean(self, record: RawFeedbackRecord) -> Optional[ProcessedFeedbackRecord]:
        """Cleans text and converts RawFeedbackRecord to ProcessedFeedbackRecord."""
        if not record.text:
            return None

        # Filter reviews containing emojis or in another language
        if self.has_emoji(record.text) or self.is_other_language(record.text):
            return None

        text_clean = self._normalize_text(record.text)
        word_count = len(text_clean.split())

        # Filter reviews with less than 8 words
        if word_count < self.MIN_WORD_COUNT:
            return None

        # Double-check cleaned text for emojis or non-English scripts
        if self.has_emoji(text_clean) or self.is_other_language(text_clean):
            return None

        source_url = record.metadata.get("source_url") or record.metadata.get("permalink")

        return ProcessedFeedbackRecord(
            id=record.id,
            source=record.source,
            text=record.text,
            text_clean=text_clean,
            rating=record.rating,
            date=record.date,
            sentiment="",
            sentiment_score=0.5,
            categories=[],
            topics=[],
            behaviour_signals=[],
            word_count=word_count,
            source_url=source_url,
            scraped_at=record.scraped_at,
        )

    def _normalize_text(self, text: str) -> str:
        """Applies normalization steps to raw feedback text."""
        if not text:
            return ""
        # Unescape HTML entities
        cleaned = html.unescape(text)
        # Remove URLs
        cleaned = re.sub(r"http\S+|www\.\S+", "", cleaned)
        # Remove HTML tags
        cleaned = re.sub(r"<[^>]+>", "", cleaned)
        # Normalize whitespace
        cleaned = re.sub(r"\s+", " ", cleaned).strip()
        return cleaned.lower()

