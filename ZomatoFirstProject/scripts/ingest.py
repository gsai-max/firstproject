import sys
import os

# Align python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.app.ingestion.pipeline import run_ingestion_pipeline

if __name__ == "__main__":
    # Defaulting to False (Option A Parquet storage). Change to True if SQLite is preferred.
    run_ingestion_pipeline(use_sqlite=False)
