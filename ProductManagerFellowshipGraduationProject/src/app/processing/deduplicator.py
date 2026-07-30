import hashlib
import re
from typing import Dict, List, Set

from src.app.models.domain import ProcessedFeedbackRecord


class Deduplicator:
    """Removes exact and near-duplicate feedback records per source without wiping out source distribution."""

    SIMILARITY_THRESHOLD = 0.85

    def deduplicate(self, records: List[ProcessedFeedbackRecord]) -> List[ProcessedFeedbackRecord]:
        """Deduplicates a list of ProcessedFeedbackRecord objects cleanly across all sources."""
        seen_hashes: Set[str] = set()
        seen_source_word_sets: Dict[str, List[Set[str]]] = {}
        unique_records: List[ProcessedFeedbackRecord] = []
        exact_dups = 0
        near_dups = 0

        for record in records:
            # 1. Strip superficial trailing IDs/number tags for hash comparison
            base_text = re.sub(
                r"\s*[\(\[\{]?(?:Order|Review|Post|Tweet|Comment|Thread|ID)?\s*#?\d+[\)\]\}]?",
                "",
                record.text_clean,
                flags=re.IGNORECASE,
            ).strip()

            text_hash = hashlib.sha256(f"{record.source}:{base_text}".encode("utf-8")).hexdigest()

            if text_hash in seen_hashes:
                exact_dups += 1
                continue

            # 2. Near-duplicate check per source for non-trivial texts (>8 words)
            # Use alphanumeric word tokens to ensure punctuation variations are deduplicated
            words = set(re.findall(r"\w+", base_text.lower()))
            if len(words) > 8:
                src_word_sets = seen_source_word_sets.setdefault(record.source, [])
                is_near_dup = False
                # Limit check window to last 50 entries per source to prevent artificial cluster collapse
                for existing_words in src_word_sets[-50:]:
                    intersection = len(words.intersection(existing_words))
                    union = len(words.union(existing_words))
                    if union > 0 and (intersection / union) >= self.SIMILARITY_THRESHOLD:
                        is_near_dup = True
                        break
                if is_near_dup:
                    near_dups += 1
                    continue
                src_word_sets.append(words)

            seen_hashes.add(text_hash)
            unique_records.append(record)

        print(
            f"Deduplicator: Removed {exact_dups} exact dups and {near_dups} near dups. "
            f"Retained {len(unique_records)}/{len(records)} records."
        )
        return unique_records
