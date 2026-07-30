import json
from typing import List, Optional

from src.app.models.domain import ProcessedFeedbackRecord
from src.app.services.llm_client import LLMClient


class SentimentClassifier:
    """Classifies sentiment (positive, neutral, negative) and assigns sentiment score."""

    NEGATIVE_KEYWORDS = [
        "worst", "terrible", "awful", "hate", "disgusting", "pathetic",
        "fraud", "scam", "bad", "slow", "late", "expired", "defective",
        "useless", "horrible", "refund", "cheated", "charging extra"
    ]
    POSITIVE_KEYWORDS = [
        "love", "great", "amazing", "excellent", "best", "awesome",
        "perfect", "fast", "good", "helpful", "super", "happy", "smooth",
        "convenient", "nice", "delighted"
    ]

    def __init__(self, llm_client: Optional[LLMClient] = None, batch_size: int = 50):
        self.llm = llm_client
        self.batch_size = batch_size

    def classify_batch(self, records: List[ProcessedFeedbackRecord]) -> List[ProcessedFeedbackRecord]:
        """Classifies sentiment across all records in batches."""
        for i in range(0, len(records), self.batch_size):
            batch = records[i:i + self.batch_size]

            if self.llm:
                try:
                    self._classify_with_llm(batch)
                    continue
                except Exception as e:
                    print(f"LLM Sentiment classification batch {i} warning: {e}. Using fallback classifier.")

            # Fallback heuristic classification
            for record in batch:
                record.sentiment, record.sentiment_score = self._fallback_classify(record)

        return records

    def _classify_with_llm(self, batch: List[ProcessedFeedbackRecord]):
        """Uses LLM to classify sentiment for a batch."""
        batch_input = [{"id": r.id, "text": r.text_clean[:300]} for r in batch]
        prompt = json.dumps({"reviews": batch_input}, indent=2)
        system_instruction = (
            "You are a sentiment analysis engine. Classify each review.\n"
            "Return JSON: {\"results\": [{\"id\": \"...\", \"sentiment\": \"positive|neutral|negative\", \"score\": 0.0-1.0}]}\n"
            "Score: 0.0 = most negative, 0.5 = neutral, 1.0 = most positive."
        )
        response = self.llm.complete(prompt, system_instruction)
        results = json.loads(response)
        result_map = {r["id"]: r for r in results.get("results", [])}

        for record in batch:
            if record.id in result_map:
                record.sentiment = result_map[record.id].get("sentiment", "neutral")
                record.sentiment_score = float(result_map[record.id].get("score", 0.5))
            else:
                record.sentiment, record.sentiment_score = self._fallback_classify(record)

    def _fallback_classify(self, record: ProcessedFeedbackRecord):
        """Rule-based fallback sentiment classifier."""
        # Use star rating if available
        if record.rating is not None:
            if record.rating >= 4.0:
                return "positive", min(0.7 + (record.rating - 4.0) * 0.3, 1.0)
            elif record.rating <= 2.0:
                return "negative", max(0.3 - (2.0 - record.rating) * 0.15, 0.0)

        text = record.text_clean
        neg_count = sum(1 for w in self.NEGATIVE_KEYWORDS if w in text)
        pos_count = sum(1 for w in self.POSITIVE_KEYWORDS if w in text)

        if neg_count > pos_count:
            return "negative", max(0.5 - (neg_count * 0.15), 0.1)
        elif pos_count > neg_count:
            return "positive", min(0.5 + (pos_count * 0.15), 0.9)
        else:
            return "neutral", 0.5
