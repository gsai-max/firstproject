from pydantic_settings import BaseSettings
from pydantic import Field

class Settings(BaseSettings):
    LLM_PROVIDER: str = Field("groq", env="LLM_PROVIDER")
    LLM_API_KEY: str = Field("gsk_dummykeyhere", env="LLM_API_KEY")
    LLM_MODEL: str = Field("llama-3.1-8b-instant", env="LLM_MODEL")
    
    # Storage Selection (Option A Parquet, Option B SQLite)
    DATA_PATH: str = Field("data/processed/restaurants.parquet", env="DATA_PATH")
    SQLITE_DB_PATH: str = Field("data/processed/restaurants.db", env="SQLITE_DB_PATH")
    
    # Budget classification thresholds
    LOW_BUDGET_LIMIT: float = Field(500.0, env="LOW_BUDGET_LIMIT")
    MEDIUM_BUDGET_LIMIT: float = Field(1500.0, env="MEDIUM_BUDGET_LIMIT")
    
    # System tuning parameters
    MAX_CANDIDATES: int = 30
    DEFAULT_RECOMMENDATION_COUNT: int = 5

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"

settings = Settings()
