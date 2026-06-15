import pandas as pd
import sqlite3
from typing import List, Optional
from src.app.models.domain import Restaurant

class RestaurantRepository:
    def __init__(self, storage_type: str = "parquet", file_path: str = ""):
        self.storage_type = storage_type
        self.file_path = file_path
        self._df: Optional[pd.DataFrame] = None
        self.load()

    def load(self):
        if self.storage_type == "sqlite":
            conn = sqlite3.connect(self.file_path)
            self._df = pd.read_sql("SELECT * FROM restaurants", conn)
            # Parse back comma-joined cuisines list
            self._df['cuisines'] = self._df['cuisines'].apply(lambda x: [i.strip() for i in str(x).split(",") if i.strip()])
            conn.close()
        else:
            self._df = pd.read_parquet(self.file_path)
        print(f"Initialized RestaurantStore Repository with {len(self._df)} cached records.")

    def get_all_raw(self) -> pd.DataFrame:
        return self._df

    def get_unique_locations(self) -> List[str]:
        return sorted(self._df['location'].unique().tolist())

    def get_unique_cuisines(self) -> List[str]:
        flat_list = [c for sublist in self._df['cuisines'].tolist() for c in sublist]
        return sorted(list(set(flat_list)))
