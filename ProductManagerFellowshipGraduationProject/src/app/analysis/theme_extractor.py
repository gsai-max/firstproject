import json
import os
from typing import Dict, List, Optional, Set
import pandas as pd

from src.app.config import settings
from src.app.models.domain import ProcessedFeedbackRecord, RepresentativeQuote, Theme
from src.app.services.llm_client import LLMClient
from src.app.services.prompt_builder import PromptBuilder


class ThemeExtractor:
    """Extracts recurring themes per feedback source using LLM analysis with fallback."""

    TOPIC_TO_RQ_MAP: Dict[str, List[str]] = {
        "habit": ["Q1", "Q4"],
        "ui_navigation": ["Q2", "Q3"],
        "discovery": ["Q2", "Q3", "Q5"],
        "variety": ["Q2", "Q8"],
        "missing_product": ["Q2", "Q8"],
        "pricing": ["Q5", "Q6"],
        "trust": ["Q6"],
        "delivery": ["Q4", "Q6"],
        "customer_support": ["Q6"],
        "comparison": ["Q7"],
        "wishlist": ["Q8"],
    }

    def __init__(self, llm_client: Optional[LLMClient] = None):
        self.llm = llm_client
        self.output_dir = settings.INSIGHTS_DIR

    def extract_themes_by_source(
        self, records: Optional[List[ProcessedFeedbackRecord]] = None
    ) -> Dict[str, List[Theme]]:
        """Extracts recurring themes per source from processed feedback records."""
        os.makedirs(self.output_dir, exist_ok=True)

        if records is None:
            records = self._load_processed_records()

        if not records:
            print("ThemeExtractor warning: No processed feedback records available.")
            return {}

        records_by_source: Dict[str, List[ProcessedFeedbackRecord]] = {}
        for r in records:
            records_by_source.setdefault(r.source, []).append(r)

        all_themes_by_source: Dict[str, List[Theme]] = {}
        serializable_output: Dict[str, List[Dict]] = {}

        for source, source_recs in records_by_source.items():
            themes = self._extract_source_themes(source, source_recs)
            all_themes_by_source[source] = themes
            serializable_output[source] = [t.model_dump() for t in themes]

        output_path = os.path.join(self.output_dir, "themes_by_source.json")
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(serializable_output, f, indent=2, ensure_ascii=False)

        print(
            f"ThemeExtractor: Extracted {sum(len(v) for v in all_themes_by_source.values())} themes "
            f"across {len(all_themes_by_source)} sources. Persisted to {output_path}"
        )
        return all_themes_by_source

    def _extract_source_themes(
        self, source: str, records: List[ProcessedFeedbackRecord]
    ) -> List[Theme]:
        """Extracts themes for a single source using LLM or rule-based fallback."""
        if self.llm:
            try:
                return self._extract_with_llm(source, records)
            except Exception as e:
                print(f"LLM Theme extraction warning for source '{source}': {e}. Using fallback extractor.")

        return self._extract_with_fallback(source, records)

    def _extract_with_llm(
        self, source: str, records: List[ProcessedFeedbackRecord]
    ) -> List[Theme]:
        """Uses LLM to extract themes from a source's records."""
        raw_dicts = [r.model_dump() for r in records[:100]]
        user_prompt, system_inst = PromptBuilder.theme_extraction_prompt(source, raw_dicts)

        response_str = self.llm.complete(user_prompt, system_inst)
        data = json.loads(response_str)

        themes: List[Theme] = []
        raw_themes = data.get("themes", [])

        for idx, t_dict in enumerate(raw_themes, 1):
            quotes = [
                RepresentativeQuote(
                    record_id=q.get("record_id", f"{source}_rec_{i}"),
                    text=q.get("text", ""),
                    source=source,
                )
                for i, q in enumerate(t_dict.get("representative_quotes", []))
            ]

            theme = Theme(
                id=t_dict.get("id", f"theme_{source}_{idx:03d}"),
                name=t_dict.get("name", f"Theme {idx} for {source}"),
                description=t_dict.get("description", ""),
                frequency=t_dict.get("frequency", "medium"),
                category_relevance=t_dict.get("category_relevance", "medium"),
                source=source,
                representative_quotes=quotes,
                research_question_mapping=t_dict.get("research_question_mapping", ["Q1", "Q2"]),
            )
            themes.append(theme)

        return themes

    def _extract_with_fallback(
        self, source: str, records: List[ProcessedFeedbackRecord]
    ) -> List[Theme]:
        """Rule-based theme extraction fallback grouped by topic clusters."""
        topic_buckets: Dict[str, List[ProcessedFeedbackRecord]] = {}
        for r in records:
            for top in r.topics:
                topic_buckets.setdefault(top, []).append(r)

        themes: List[Theme] = []
        idx = 1

        # Preset fallback descriptions per topic tailored to Blinkit
        topic_descriptions = {
            "ui_navigation": "Users express difficulty discovering non-grocery items because the app UI strongly prioritizes milk, bread, and daily staples on the home page.",
            "discovery": "Lack of prominent banners or discovery carousels for pet supplies, personal care, and electronics leads users to assume Blinkit only sells groceries.",
            "habit": "Shopping on Blinkit has become a habitual 10-minute task for emergency staples, causing users to bypass browsing secondary product categories.",
            "pricing": "Users perceive non-grocery items on quick-commerce to carry higher handling charges or markups compared to dedicated horizontal e-commerce platforms.",
            "variety": "Feedback indicates limited SKU depth in specialized categories (e.g. pet food brands, stationery options) compared to specialized retailers.",
            "missing_product": "Users report unlisted or out-of-stock items when attempting to search for non-grocery essentials like charger cables or infant care.",
            "delivery": "Fast 10-minute delivery is highly valued for groceries but users doubt speed necessity for non-urgent category purchases.",
            "trust": "Concerns over returns and warranties for electronics accessories bought via quick-commerce.",
            "customer_support": "Frustration with automated support resolution when items are damaged or missing from mixed-category orders.",
            "comparison": "Users compare Blinkit's category breadth with Zepto, Instamart, and Amazon, switching apps for non-grocery purchases.",
            "wishlist": "Users request a wishlist feature to bookmark non-grocery items for later purchase.",
        }

        for topic, topic_recs in sorted(topic_buckets.items(), key=lambda x: len(x[1]), reverse=True):
            if len(topic_recs) < 1:
                continue

            theme_id = f"theme_{source}_{idx:03d}"
            name = f"{topic.replace('_', ' ').title()} Impact on Category Exploration"
            desc = topic_descriptions.get(
                topic,
                f"User feedback related to {topic.replace('_', ' ')} affecting purchasing behavior on {source}."
            )

            freq = "high" if len(topic_recs) > 20 else ("medium" if len(topic_recs) > 5 else "low")
            cat_rel = "high" if topic in ["discovery", "ui_navigation", "variety", "habit"] else "medium"

            quotes = [
                RepresentativeQuote(
                    record_id=r.id,
                    text=r.text_clean[:200],
                    source=source,
                )
                for r in topic_recs[:3]
            ]

            rq_mapping = self.TOPIC_TO_RQ_MAP.get(topic, ["Q1", "Q2"])

            theme = Theme(
                id=theme_id,
                name=name,
                description=desc,
                frequency=freq,
                category_relevance=cat_rel,
                source=source,
                representative_quotes=quotes,
                research_question_mapping=rq_mapping,
            )
            themes.append(theme)
            idx += 1

            if len(themes) >= 10:
                break

        return themes

    def _load_processed_records(self) -> List[ProcessedFeedbackRecord]:
        """Loads normalized processed records from JSON file."""
        json_path = os.path.join(settings.PROCESSED_DATA_DIR, "all_normalized_reviews.json")
        if not os.path.exists(json_path):
            json_path = os.path.join(settings.PROCESSED_DATA_DIR, "all_normalized_reviews.jsonl")

        if not os.path.exists(json_path):
            print(f"ThemeExtractor error: File not found at {json_path}")
            return []

        records = []
        try:
            if json_path.endswith(".json"):
                with open(json_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    for item in data:
                        records.append(ProcessedFeedbackRecord(**item))
            else:
                with open(json_path, "r", encoding="utf-8") as f:
                    for line in f:
                        if line.strip():
                            records.append(ProcessedFeedbackRecord(**json.loads(line)))
        except Exception as e:
            print(f"Error loading processed records: {e}")
        return records
