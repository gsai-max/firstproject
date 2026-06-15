import os
import sqlite3
from src.app.ingestion.loader import DatasetLoader
from src.app.ingestion.normalizer import SchemaNormalizer
from src.app.config import settings

def run_ingestion_pipeline(use_sqlite: bool = False):
    loader = DatasetLoader()
    df_raw = loader.download_dataset()
    
    normalizer = SchemaNormalizer(
        low_limit=settings.LOW_BUDGET_LIMIT,
        medium_limit=settings.MEDIUM_BUDGET_LIMIT
    )
    df_clean = normalizer.normalize(df_raw)
    
    # Persistence Writing Mode
    if use_sqlite:
        os.makedirs(os.path.dirname(settings.SQLITE_DB_PATH), exist_ok=True)
        conn = sqlite3.connect(settings.SQLITE_DB_PATH)
        # Convert list column to string to save in SQL
        df_to_sql = df_clean.copy()
        df_to_sql['cuisines'] = df_to_sql['cuisines'].apply(lambda x: ",".join(x))
        df_to_sql.to_sql("restaurants", conn, if_exists="replace", index=False)
        conn.close()
        print(f"Ingested successfully into SQLite: {settings.SQLITE_DB_PATH}")
    else:
        os.makedirs(os.path.dirname(settings.DATA_PATH), exist_ok=True)
        df_clean.to_parquet(settings.DATA_PATH, index=False)
        print(f"Ingested successfully into Parquet: {settings.DATA_PATH}")
