import os
from pathlib import Path
from typing import List, Optional
import yaml
from pydantic import BaseModel, Field

# Root directory of the project
ROOT_DIR = Path(__file__).resolve().parent.parent
CONFIG_DIR = ROOT_DIR / "config"
PRODUCTS_DIR = CONFIG_DIR / "products"


class EmbeddingConfig(BaseModel):
    provider: str = "openai"
    model: str = "text-embedding-3-small"
    batch_size: int = 64


class UMAPConfig(BaseModel):
    n_neighbors: int = 15
    n_components: int = 5
    metric: str = "cosine"


class HDBSCANConfig(BaseModel):
    min_cluster_size: int = 5
    min_samples: int = 3


class ClusteringConfig(BaseModel):
    umap: UMAPConfig = Field(default_factory=UMAPConfig)
    hdbscan: HDBSCANConfig = Field(default_factory=HDBSCANConfig)


class SummarizationConfig(BaseModel):
    provider: str = "groq"
    model: str = "llama-3.3-70b-versatile"
    max_themes: int = 5
    max_tokens_per_run: int = 12000
    max_samples_per_cluster: int = 8
    max_output_tokens_per_theme: int = 800
    request_interval_seconds: float = 2.0


class SafetyConfig(BaseModel):
    scrub_pii: bool = True
    max_review_chars: int = 2000


class PipelineConfig(BaseModel):
    embedding: EmbeddingConfig = Field(default_factory=EmbeddingConfig)
    clustering: ClusteringConfig = Field(default_factory=ClusteringConfig)
    summarization: SummarizationConfig = Field(default_factory=SummarizationConfig)
    safety: SafetyConfig = Field(default_factory=SafetyConfig)


class PlayStoreConfig(BaseModel):
    app_id: str


class IngestionConfig(BaseModel):
    window_weeks: int = 10
    min_reviews: int = 20
    max_reviews: int = 5000
    min_words: int = 8
    allowed_language: str = "en"


class EmailConfig(BaseModel):
    recipients: List[str] = Field(default_factory=list)
    default_mode: str = "draft"


class DeliveryConfig(BaseModel):
    google_doc_id: str
    email: EmailConfig = Field(default_factory=EmailConfig)


class ProductConfig(BaseModel):
    product: str
    display_name: str
    play_store: PlayStoreConfig
    ingestion: IngestionConfig = Field(default_factory=IngestionConfig)
    delivery: DeliveryConfig


class AppConfig(BaseModel):
    pipeline: PipelineConfig
    product: ProductConfig
    openai_api_key: Optional[str] = None
    groq_api_key: Optional[str] = None
    hf_token: Optional[str] = None


def load_yaml(file_path: Path) -> dict:
    if not file_path.exists():
        raise FileNotFoundError(f"Configuration file not found: {file_path}")
    with open(file_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def get_product_config(product_name: str) -> ProductConfig:
    product_file = PRODUCTS_DIR / f"{product_name}.yaml"
    if not product_file.exists():
        # Case insensitive check
        yaml_files = list(PRODUCTS_DIR.glob("*.yaml"))
        for f in yaml_files:
            if f.stem.lower() == product_name.lower():
                product_file = f
                break
        else:
            raise ValueError(f"Product '{product_name}' configuration not found in {PRODUCTS_DIR}")
    
    data = load_yaml(product_file)
    return ProductConfig.model_validate(data)


def load_config(product_name: str) -> AppConfig:
    pipeline_file = CONFIG_DIR / "pipeline.yaml"
    pipeline_data = load_yaml(pipeline_file)
    pipeline_config = PipelineConfig.model_validate(pipeline_data)
    
    product_config = get_product_config(product_name)
    
    # Load environment variables from .env if present
    env_file = ROOT_DIR / ".env"
    if env_file.exists():
        with open(env_file, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    parts = line.split("=", 1)
                    k = parts[0].strip()
                    v = parts[1].strip()
                    # Strip quotes if present
                    if (v.startswith('"') and v.endswith('"')) or (v.startswith("'") and v.endswith("'")):
                        v = v[1:-1]
                    if k not in os.environ:
                        os.environ[k] = v
    
    # Extract keys from environment
    openai_api_key = os.environ.get("OPENAI_API_KEY")
    groq_api_key = os.environ.get("GROQ_API_KEY")
    hf_token = os.environ.get("HF_TOKEN")
    
    # Override Google Doc ID from environment if specified
    env_doc_id = os.environ.get("GOOGLE_DOC_ID")
    if env_doc_id:
        product_config.delivery.google_doc_id = env_doc_id
        
    # Override email recipients if specified
    env_email_to = os.environ.get("PULSE_EMAIL_TO")
    if env_email_to:
        product_config.delivery.email.recipients = [
            email.strip() for email in env_email_to.split(",") if email.strip()
        ]
        
    # Override email delivery mode if specified
    env_email_mode = os.environ.get("PULSE_EMAIL_MODE")
    if env_email_mode:
        product_config.delivery.email.default_mode = env_email_mode
    
    return AppConfig(
        pipeline=pipeline_config,
        product=product_config,
        openai_api_key=openai_api_key,
        groq_api_key=groq_api_key,
        hf_token=hf_token
    )
