from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Centralized environment configuration loader."""
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Multi-LLM Provider Credentials
    LLM_PROVIDER: str = Field(default="groq")
    LLM_API_KEY: str = Field(default="your_groq_api_key_here")
    LLM_MODEL: str = Field(default="llama-3.1-8b-instant")

    GROQ_API_KEY: str = Field(default="")
    GROQ_MODEL: str = Field(default="llama-3.1-8b-instant")

    HF_TOKEN: str = Field(default="")
    HF_MODEL: str = Field(default="meta-llama/Llama-3.2-3B-Instruct")
    EMBEDDING_MODEL: str = Field(default="sentence-transformers/all-MiniLM-L6-v2")

    OPENAI_API_KEY: str = Field(default="")
    OPENAI_MODEL: str = Field(default="gpt-4o")

    ANTHROPIC_API_KEY: str = Field(default="")
    ANTHROPIC_MODEL: str = Field(default="claude-3-5-sonnet-20241022")

    GEMINI_API_KEY: str = Field(default="")
    GEMINI_MODEL: str = Field(default="gemini-1.5-pro")

    # Data Lake & Vector Database
    AWS_S3_BUCKET: str = Field(default="blinkit-discovery-engine-raw")
    VECTOR_DB_PROVIDER: str = Field(default="chroma")
    CHROMA_PERSIST_DIR: str = Field(default="data/vectorstore")
    PINECONE_API_KEY: str = Field(default="")
    PINECONE_INDEX: str = Field(default="blinkit-discovery-vectors")

    # Reddit API Credentials
    REDDIT_CLIENT_ID: str = Field(default="")
    REDDIT_CLIENT_SECRET: str = Field(default="")
    REDDIT_USER_AGENT: str = Field(default="blinkit-discovery-engine/1.0")

    # Data Storage Paths
    RAW_DATA_DIR: str = Field(default="data/raw")
    PROCESSED_DATA_DIR: str = Field(default="data/processed")
    INSIGHTS_DIR: str = Field(default="data/insights")

    # Scraper & Pipeline Execution Limits (Expanded Raw Data Buckets)
    MAX_REVIEWS_PLAY_STORE: int = 30000
    MAX_REVIEWS_APP_STORE: int = 15000
    MAX_POSTS_REDDIT: int = 5000
    MAX_TWEETS: int = 10000
    MAX_YOUTUBE_COMMENTS: int = 5000
    MAX_QUORA_POSTS: int = 2500
    MAX_FORUM_POSTS: int = 2500
    MAX_COMPETITOR_REVIEWS: int = 10000
    SENTIMENT_BATCH_SIZE: int = 50
    THEME_BATCH_SIZE: int = 100
    LLM_TIMEOUT_SECONDS: float = 10.0


settings = Settings()
