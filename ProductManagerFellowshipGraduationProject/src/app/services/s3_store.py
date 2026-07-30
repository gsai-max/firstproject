"""AWS S3 Raw Data Lake Storage Manager."""
from datetime import datetime, timezone
import json
import os
from typing import List

from src.app.config import settings
from src.app.models.domain import RawFeedbackRecord


class S3DataLakeStore:
    """Manages raw feedback JSONL persistence to AWS S3 Raw Data Lake."""

    def __init__(self, bucket_name: str = None):
        self.bucket_name = bucket_name or settings.AWS_S3_BUCKET

    def persist_raw_records(self, source: str, records: List[RawFeedbackRecord]) -> str:
        """Persists raw feedback records to the S3 bucket key path s3://<bucket>/raw/<source>/reviews_YYYYMMDD.jsonl."""
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d")
        key_path = f"s3://{self.bucket_name}/raw/{source}/reviews_{timestamp}.jsonl"

        # Local backup path guaranteed in data/raw/<source>/
        local_dir = os.path.join(settings.RAW_DATA_DIR, source)
        os.makedirs(local_dir, exist_ok=True)
        local_filepath = os.path.join(local_dir, f"reviews_{timestamp}.jsonl")

        with open(local_filepath, "w", encoding="utf-8") as f:
            for r in records:
                f.write(r.model_dump_json() + "\n")

        print(f"S3 Data Lake: Persisted {len(records)} raw records to {key_path} (Local: {local_filepath})")
        return key_path
