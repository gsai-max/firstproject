import os
import time
import pandas as pd
from datasets import load_dataset

class DatasetLoader:
    def __init__(self, dataset_name: str = "ManikaSaini/zomato-restaurant-recommendation"):
        self.dataset_name = dataset_name
        self.raw_dir = "data/raw"

    def download_dataset(self) -> pd.DataFrame:
        os.makedirs(self.raw_dir, exist_ok=True)
        print(f"Downloading dataset {self.dataset_name} from Hugging Face...")
        
        max_retries = 3
        backoff_factor = 2.0
        initial_delay = 1.0
        dataset = None
        
        for attempt in range(max_retries + 1):
            try:
                dataset = load_dataset(self.dataset_name)
                break
            except Exception as e:
                if attempt == max_retries:
                    print(f"Failed to download dataset from HF after {max_retries} retries: {e}")
                    raise e
                delay = initial_delay * (backoff_factor ** attempt)
                print(f"Download failed (attempt {attempt + 1}/{max_retries + 1}): {e}. Retrying in {delay:.1f}s...")
                time.sleep(delay)
                
        df = pd.DataFrame(dataset['train'])
        
        # Cache a local copy of the raw dataset
        raw_csv_path = os.path.join(self.raw_dir, "raw_restaurants.csv")
        df.to_csv(raw_csv_path, index=False)
        print(f"Raw dataset cached successfully to {raw_csv_path}")
        return df
