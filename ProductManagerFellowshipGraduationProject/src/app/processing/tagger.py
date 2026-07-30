import json
from typing import Dict, List, Optional

from src.app.models.domain import ProcessedFeedbackRecord
from src.app.services.llm_client import LLMClient


class CategoryTopicTagger:
    """Tags feedback records with categories, topics, and behaviour signals."""

    CATEGORIES = [
        "groceries", "snacks", "beverages", "personal_care", "baby_products",
        "pet_supplies", "electronics", "household", "pharmacy", "beauty",
        "stationery", "toys", "general"
    ]
    TOPICS = [
        "discovery", "pricing", "delivery", "trust", "habit", "quality",
        "variety", "ui_navigation", "recommendation", "comparison", "wishlist",
        "missing_product", "customer_support"
    ]
    BEHAVIOUR_SIGNALS = [
        "repeat_purchase", "category_exploration", "category_switch",
        "wishlist_request", "missing_product_report", "new_user", "power_user"
    ]

    CATEGORY_KEYWORDS: Dict[str, List[str]] = {
        "groceries": ["milk", "bread", "veggie", "vegetable", "fruit", "grocery", "dall", "atta", "rice", "kirana"],
        "snacks": ["chip", "snack", "biscuit", "chocolate", "munch", "namkeen", "popcorn"],
        "beverages": ["drink", "soda", "juice", "water", "coke", "pepsi", "cold drink", "tea", "coffee"],
        "personal_care": ["shampoo", "soap", "toothpaste", "skincare", "lip balm", "lotion", "deodorant"],
        "baby_products": ["baby", "diaper", "wipes", "infant", "cerelac"],
        "pet_supplies": ["pet", "dog", "cat", "pedigree", "whiskas", "litter", "kibble"],
        "electronics": ["electronic", "charger", "cable", "earphone", "headphone", "battery", "appliance"],
        "household": ["cleaner", "detergent", "tissue", "mop", "kitchen", "decor", "home"],
        "pharmacy": ["medicine", "doctor", "tablet", "pharma", "first aid", "bandage", "health"],
        "beauty": ["makeup", "lipstick", "cosmetic", "beauty", "face wash"],
        "stationery": ["office", "stationary", "paper", "pen", "notebook", "printer paper"],
        "toys": ["toy", "game", "puzzle", "kids"],
    }

    TOPIC_KEYWORDS: Dict[str, List[str]] = {
        "discovery": ["find", "explore", "discover", "search", "visible", "banner", "section", "hidden"],
        "pricing": ["price", "cost", "charge", "expensive", "mony", "rs", "handling fee", "discount", "off"],
        "delivery": ["fast", "quick", "delivery", "late", "time", "10 min", "mins", "minute", "speed"],
        "trust": ["scam", "cheat", "refund", "fake", "defective", "return", "expired", "fraud"],
        "habit": ["habit", "always", "usual", "routine", "emergency", "kirana", "perception"],
        "quality": ["quality", "fresh", "damaged", "good quality", "worst quality"],
        "variety": ["variety", "option", "selection", "assortment", "range", "limited"],
        "ui_navigation": ["ui", "app", "crash", "interface", "navigation", "checkout", "search bar"],
        "comparison": ["zepto", "instamart", "amazon", "flipkart", "blinkit vs"],
        "wishlist": ["wishlist", "wish", "hope", "please add"],
        "missing_product": ["missing", "not available", "unlisted", "hard to find", "request"],
        "customer_support": ["customer", "support", "representative", "service", "help"],
    }

    BEHAVIOUR_KEYWORDS: Dict[str, List[str]] = {
        "category_exploration": ["explore", "tried buying", "discovered", "new categories", "browse"],
        "category_switch": ["switch", "amazon", "flipkart", "zepto", "instead"],
        "missing_product_report": ["missing", "add more", "not visible", "hard to find"],
        "wishlist_request": ["please add", "wish", "request"],
        "repeat_purchase": ["always buy", "only buy", "same 3 items", "every time"],
    }

    def __init__(self, llm_client: Optional[LLMClient] = None, batch_size: int = 50):
        self.llm = llm_client
        self.batch_size = batch_size

    def tag_batch(self, records: List[ProcessedFeedbackRecord]) -> List[ProcessedFeedbackRecord]:
        """Tags a batch of ProcessedFeedbackRecord objects with categories, topics, and signals."""
        for i in range(0, len(records), self.batch_size):
            batch = records[i:i + self.batch_size]

            if self.llm:
                try:
                    self._tag_with_llm(batch)
                    continue
                except Exception as e:
                    print(f"LLM Tagger batch {i} warning: {e}. Using rule-based fallback tagger.")

            for record in batch:
                self._fallback_tag(record)

        return records

    def _tag_with_llm(self, batch: List[ProcessedFeedbackRecord]):
        """LLM-based multi-label tagging."""
        batch_input = [{"id": r.id, "text": r.text_clean[:300]} for r in batch]
        prompt = json.dumps({"reviews": batch_input}, indent=2)
        system_instruction = (
            f"You are a product feedback tagger for Blinkit.\n"
            f"Categories taxonomy: {self.CATEGORIES}\n"
            f"Topics taxonomy: {self.TOPICS}\n"
            f"Behaviour signals taxonomy: {self.BEHAVIOUR_SIGNALS}\n"
            f"Return JSON: {{\"results\": [{{\"id\": \"...\", \"categories\": [...], \"topics\": [...], \"behaviour_signals\": [...]}}]}}"
        )
        response = self.llm.complete(prompt, system_instruction)
        results = json.loads(response)
        result_map = {r["id"]: r for r in results.get("results", [])}

        for record in batch:
            if record.id in result_map:
                res = result_map[record.id]
                record.categories = [c for c in res.get("categories", []) if c in self.CATEGORIES] or ["general"]
                record.topics = [t for t in res.get("topics", []) if t in self.TOPICS] or ["discovery"]
                record.behaviour_signals = [b for b in res.get("behaviour_signals", []) if b in self.BEHAVIOUR_SIGNALS]
            else:
                self._fallback_tag(record)

    def _fallback_tag(self, record: ProcessedFeedbackRecord):
        """Rule-based fallback keyword tagger."""
        text = record.text_clean
        categories = set()
        topics = set()
        signals = set()

        for cat, kw_list in self.CATEGORY_KEYWORDS.items():
            if any(kw in text for kw in kw_list):
                categories.add(cat)

        for top, kw_list in self.TOPIC_KEYWORDS.items():
            if any(kw in text for kw in kw_list):
                topics.add(top)

        for sig, kw_list in self.BEHAVIOUR_KEYWORDS.items():
            if any(kw in text for kw in kw_list):
                signals.add(sig)

        record.categories = list(categories) if categories else ["groceries" if "milk" in text or "grocery" in text else "general"]
        record.topics = list(topics) if topics else ["delivery" if "fast" in text or "time" in text else "discovery"]
        record.behaviour_signals = list(signals)
