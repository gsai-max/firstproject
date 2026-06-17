import asyncio
import json
import os
from pathlib import Path
from datetime import datetime

from src.config import load_config
from src.ingestion.client import PlayStoreMCPClient
from src.ingestion.normalizer import clean_and_normalize

# Setup directories
DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)

# Custom encoder to serialize datetime objects to ISO strings
class DateTimeEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)

async def main():
    print("Loading configuration for product 'groww'...")
    config = load_config("groww")
    
    app_id = config.product.play_store.app_id
    window_weeks = config.product.ingestion.window_weeks
    max_reviews = config.product.ingestion.max_reviews
    min_words = config.product.ingestion.min_words
    
    print(f"App ID: {app_id}")
    print(f"Window: {window_weeks} weeks")
    print(f"Max Reviews to fetch: {max_reviews}")
    print(f"Min Words: {min_words}")

    print("Connecting to Play Store MCP Server and fetching reviews...")
    client = PlayStoreMCPClient(app_id)
    
    try:
        raw_reviews_models = await client.fetch_reviews(
            window_weeks=window_weeks,
            max_reviews=max_reviews
        )
    except Exception as e:
        print(f"Failed to fetch reviews: {e}")
        return

    print(f"Fetched {len(raw_reviews_models)} raw reviews within the {window_weeks}-week window.")

    # Deduplicate raw reviews by hash of (text, rating, published_at) before normalization/saving
    seen_raw = set()
    deduped_raw_reviews = []
    for r in raw_reviews_models:
        published_dt = r.published_at.isoformat() if hasattr(r.published_at, "isoformat") else str(r.published_at)
        key = (" ".join(r.text.split()).lower(), r.rating, published_dt)
        if key not in seen_raw:
            seen_raw.add(key)
            deduped_raw_reviews.append(r)

    print(f"Deduplicated to {len(deduped_raw_reviews)} unique raw reviews.")

    # 1. actual reviews: remove reviewId, userName, userImage, reviewCreatedVersion, at, replyContent, repliedAt
    # RawReview has text, rating, published_at.
    # We save them containing only these fields, which automatically excludes userName, userImage, etc.
    actual_reviews = []
    for r in deduped_raw_reviews:
        actual_reviews.append({
            "text": r.text,
            "score": r.rating,
            "date": r.published_at
        })

    # Save to data/reviews_raw.json
    raw_file = DATA_DIR / "reviews_raw.json"
    with open(raw_file, "w", encoding="utf-8") as f:
        json.dump(actual_reviews, f, indent=2, cls=DateTimeEncoder)
    print(f"Saved all actual reviews to {raw_file}")

    # 2. normalized reviews: apply normalizer logic (min_words, no emoji, english only)
    normalized_reviews = []
    for r in deduped_raw_reviews:
        cleaned_text = clean_and_normalize(r.text, min_words=min_words)
        if cleaned_text:
            normalized_reviews.append({
                "text": cleaned_text,
                "rating": r.rating
            })

    # Save to data/reviews_normalized.json
    norm_file = DATA_DIR / "reviews_normalized.json"
    with open(norm_file, "w", encoding="utf-8") as f:
        json.dump(normalized_reviews, f, indent=2)
    print(f"Saved {len(normalized_reviews)} normalized reviews to {norm_file}")

if __name__ == "__main__":
    asyncio.run(main())
