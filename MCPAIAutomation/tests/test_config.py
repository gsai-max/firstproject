import os
from src.config import load_config


def test_load_config_groww(monkeypatch):
    # Set dummy env vars for test coverage cleanly using monkeypatch
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test-openai-key")
    monkeypatch.setenv("GROQ_API_KEY", "gsk-test-groq-key")
    monkeypatch.delenv("GOOGLE_DOC_ID", raising=False)
    monkeypatch.delenv("PULSE_EMAIL_TO", raising=False)
    monkeypatch.delenv("PULSE_EMAIL_MODE", raising=False)

    # Prevent loading the real .env file in tests
    from pathlib import Path
    orig_exists = Path.exists
    def mock_exists(self):
        if self.name == ".env":
            return False
        return orig_exists(self)
    monkeypatch.setattr(Path, "exists", mock_exists)

    config = load_config("groww")

    # Validate product configuration details
    assert config.product.product == "groww"
    assert config.product.display_name == "Groww"
    assert config.product.play_store.app_id == "com.nextbillion.groww"
    assert config.product.ingestion.window_weeks == 10
    assert config.product.ingestion.min_reviews == 20
    assert config.product.ingestion.max_reviews == 5000
    assert config.product.ingestion.min_words == 8
    assert config.product.ingestion.allowed_language == "en"
    assert config.product.delivery.google_doc_id == "groww_shared_doc_id"
    assert "product-leads@example.com" in config.product.delivery.email.recipients
    assert config.product.delivery.email.default_mode == "draft"

    # Validate pipeline settings
    assert config.pipeline.embedding.provider == "openai"
    assert config.pipeline.embedding.model == "text-embedding-3-small"
    assert config.pipeline.embedding.batch_size == 64
    assert config.pipeline.clustering.umap.n_neighbors == 15
    assert config.pipeline.clustering.hdbscan.min_cluster_size == 5
    assert config.pipeline.summarization.provider == "groq"
    assert config.pipeline.summarization.model == "llama-3.3-70b-versatile"
    assert config.pipeline.safety.scrub_pii is True

    # Validate environment variable propagation
    assert config.openai_api_key == "sk-test-openai-key"
    assert config.groq_api_key == "gsk-test-groq-key"
