import pytest
from unittest.mock import MagicMock, patch
from typing import List

from src.config import AppConfig, PipelineConfig, ProductConfig, PlayStoreConfig, DeliveryConfig
from src.ingestion.models import Review
from src.pipeline.scrubber import scrub_pii
from src.pipeline.clustering import ClusteringPipeline
from src.pipeline.quote_validator import validate_quote, normalize_text
from src.pipeline.summarizer import ReviewSummarizer

# --- PII Scrubber Tests ---

def test_scrub_pii_emails():
    assert scrub_pii("Contact me at user.name+tag@example.co.in") == "Contact me at [EMAIL]"
    assert scrub_pii("my email is dummy_123@gmail.com") == "my email is [EMAIL]"

def test_scrub_pii_phones():
    assert scrub_pii("My phone number is 9876543210") == "My phone number is [PHONE]"
    assert scrub_pii("reach us at +91 99999 88888.") == "reach us at [PHONE]."
    assert scrub_pii("call 07890-123456 now") == "call [PHONE] now"

def test_scrub_pii_ids():
    assert scrub_pii("Aadhaar: 1234-5678-9012") == "Aadhaar: [ID]"
    assert scrub_pii("My PAN is ABCDE1234F") == "My PAN is [ID]"
    assert scrub_pii("Order ID 12345678901") == "Order ID [ID]"  # 11 digits

def test_scrub_pii_urls():
    assert scrub_pii("Check https://groww.in/charts?token=xyz") == "Check [URL]"
    assert scrub_pii("Check http://localhost:8000/") == "Check [URL]"

# --- Quote Validator Tests ---

def test_normalize_text():
    assert normalize_text("Hello, World! 123...") == "hello world 123"
    assert normalize_text("  App   is   lagging!!  ") == "app is lagging"

def test_validate_quote_simple():
    reviews = [
        "This app is very useful for stock investment.",
        "The interface is clean and execution is fast."
    ]
    assert validate_quote("stock investment", reviews) is True
    assert validate_quote("STOCK INVESTMENT.", reviews) is True
    assert validate_quote("clean and execution", reviews) is True
    assert validate_quote("non-existent text", reviews) is False

def test_validate_quote_ellipsis():
    reviews = [
        "The app freezes exactly when the market opens, which is very frustrating for traders."
    ]
    assert validate_quote("The app freezes... market opens", reviews) is True
    assert validate_quote("freezes... very frustrating... traders", reviews) is True
    # Incorrect order
    assert validate_quote("market opens... app freezes", reviews) is False
    # Leading/trailing ellipsis
    assert validate_quote("...market opens...", reviews) is True

def test_validate_quote_empty():
    assert validate_quote("", ["some review"]) is False
    assert validate_quote("...", ["some review"]) is False

# --- Clustering Pipeline Tests ---

def test_clustering_aborts_below_minimum():
    pipeline = ClusteringPipeline(min_reviews=20)
    reviews = [Review(text=f"Review text {i}", rating=5) for i in range(19)]
    with pytest.raises(ValueError, match="Review count.*below the minimum"):
        pipeline.run(reviews)

def test_clustering_ranking_and_scores():
    pipeline = ClusteringPipeline(min_reviews=5)  # override min for testing
    
    # We will generate reviews that naturally group into two clusters
    # Cluster A reviews (bad ratings, average = 1.0, size = 4)
    # Cluster B reviews (good ratings, average = 5.0, size = 2)
    reviews = [
        Review(text="lagging crash slow freeze bad", rating=1),
        Review(text="lagging crash slow freeze bad", rating=1),
        Review(text="lagging crash slow freeze bad", rating=1),
        Review(text="lagging crash slow freeze bad", rating=1),
        Review(text="excellent smooth clean good", rating=5),
        Review(text="excellent smooth clean good", rating=5),
    ]
    
    clusters = pipeline.run(reviews, num_clusters=2)
    
    assert len(clusters) == 2
    
    # Cluster A (low ratings) should be first because:
    # Score A = 4 * (6 - 1) = 20
    # Score B = 2 * (6 - 5) = 2
    assert clusters[0]["score"] == 20.0
    assert clusters[0]["avg_rating"] == 1.0
    assert clusters[0]["size"] == 4
    
    assert clusters[1]["score"] == 2.0
    assert clusters[1]["avg_rating"] == 5.0
    assert clusters[1]["size"] == 2

# --- Summarizer Integration & Retry Tests ---

@pytest.fixture
def dummy_config():
    pipeline_conf = PipelineConfig()
    pipeline_conf.summarization.provider = "openai"
    pipeline_conf.summarization.model = "gpt-4o"
    pipeline_conf.summarization.max_themes = 2
    pipeline_conf.summarization.request_interval_seconds = 0.0  # speed up tests
    
    prod_conf = ProductConfig(
        product="groww",
        display_name="Groww",
        play_store=PlayStoreConfig(app_id="com.nextbillion.groww"),
        delivery=DeliveryConfig(google_doc_id="doc-id")
    )
    prod_conf.ingestion.min_reviews = 5  # override for testing
    
    return AppConfig(
        pipeline=pipeline_conf,
        product=prod_conf,
        openai_api_key="mock-key",
        groq_api_key="mock-key"
    )

def test_summarizer_orchestration_success(dummy_config):
    # Mock LLM Client
    mock_client = MagicMock()
    
    mock_response_1 = MagicMock()
    mock_response_1.choices = [MagicMock()]
    mock_response_1.choices[0].message.content = """{
        "theme_name": "Performance",
        "summary": "App lags and freezes.",
        "quotes": ["app freezes... very frustrating"],
        "action_ideas": [{"title": "Stabilize performance", "detail": "Fix lag issues"}]
    }"""
    
    mock_response_2 = MagicMock()
    mock_response_2.choices = [MagicMock()]
    mock_response_2.choices[0].message.content = """{
        "theme_name": "Trading UX",
        "summary": "App makes trading easy.",
        "quotes": ["simple and clean"],
        "action_ideas": [{"title": "Maintain UX", "detail": "Keep UI clean"}]
    }"""
    
    mock_client.chat.completions.create.side_effect = [mock_response_1, mock_response_2]

    summarizer = ReviewSummarizer(config=dummy_config, client=mock_client)

    reviews = [
        Review(text="The app freezes when I open it, which is very frustrating.", rating=1),
        Review(text="The app freezes when I open it, which is very frustrating.", rating=1),
        Review(text="The app freezes when I open it, which is very frustrating.", rating=1),
        Review(text="The app freezes when I open it, which is very frustrating.", rating=1),
        Review(text="This app makes trading simple and clean.", rating=5),
        Review(text="This app makes trading simple and clean.", rating=5),
    ]

    result = summarizer.run_pipeline(reviews)
    assert len(result) == 2
    assert result[0]["theme_name"] == "Performance"
    assert result[0]["quotes"] == ["app freezes... very frustrating"]
    # Verify PII was scrubbed if any (e.g. if we add a phone to review, it would be scrubbed)
    # Check that average ratings are computed
    assert result[0]["avg_rating"] == 1.0

def test_summarizer_retry_on_invalid_quotes(dummy_config):
    mock_client = MagicMock()
    
    # Mocking first call to return invalid quote
    mock_response_1 = MagicMock()
    mock_response_1.choices = [MagicMock()]
    mock_response_1.choices[0].message.content = """{
        "theme_name": "Performance",
        "summary": "App lags and freezes.",
        "quotes": ["This quote does not exist"],
        "action_ideas": []
    }"""
    
    # Mocking second call (retry) to return valid quote
    mock_response_2 = MagicMock()
    mock_response_2.choices = [MagicMock()]
    mock_response_2.choices[0].message.content = """{
        "theme_name": "Performance",
        "summary": "App lags.",
        "quotes": ["app freezes"],
        "action_ideas": []
    }"""
    
    mock_client.chat.completions.create.side_effect = [mock_response_1, mock_response_2, mock_response_2, mock_response_2]

    summarizer = ReviewSummarizer(config=dummy_config, client=mock_client)

    reviews = [
        Review(text="The app freezes when I open it.", rating=1),
        Review(text="The app freezes when I open it.", rating=1),
        Review(text="The app freezes when I open it.", rating=1),
        Review(text="The app freezes when I open it.", rating=1),
        Review(text="This app makes trading simple.", rating=5),
        Review(text="This app makes trading simple.", rating=5),
    ]

    result = summarizer.run_pipeline(reviews)
    
    # The first cluster succeeded after retry
    assert len(result) >= 1
    assert result[0]["theme_name"] == "Performance"
    assert result[0]["quotes"] == ["app freezes"]
    # Confirm chat.completions.create was called multiple times due to retry
    assert mock_client.chat.completions.create.call_count >= 2

def test_summarizer_omits_theme_on_double_failure(dummy_config):
    mock_client = MagicMock()
    
    # Both calls return invalid quotes
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = """{
        "theme_name": "Performance",
        "summary": "App lags.",
        "quotes": ["This quote does not exist"],
        "action_ideas": []
    }"""
    
    mock_client.chat.completions.create.return_value = mock_response

    summarizer = ReviewSummarizer(config=dummy_config, client=mock_client)

    reviews = [
        Review(text="The app freezes when I open it.", rating=1),
        Review(text="The app freezes when I open it.", rating=1),
        Review(text="The app freezes when I open it.", rating=1),
        Review(text="The app freezes when I open it.", rating=1),
        Review(text="This app makes trading simple.", rating=5),
        Review(text="This app makes trading simple.", rating=5),
    ]

    result = summarizer.run_pipeline(reviews)
    
    # Since quote validation failed twice for both clusters (because mock returns same invalid quotes),
    # both themes are omitted.
    assert len(result) == 0


# --- Additional Refactoring Tests ---

def test_contains_hinglish():
    from src.ingestion.normalizer import contains_hinglish
    assert contains_hinglish("This is a clean English review.") is False
    assert contains_hinglish("brokerage charge ka samjh nhi aata hai") is True
    assert contains_hinglish("Bhai groww app mera paisa kha rh h") is True
    assert contains_hinglish("bahut ghatiya aapp h hang marta h") is True

def test_star_emoji_filtering():
    from src.ingestion.normalizer import clean_and_normalize
    # Star emoji should trigger clean_and_normalize to return empty string
    assert clean_and_normalize("I recommend it to anyone who is new to investing. \u2b50\u2b50\u2b50") == ""


def test_clustering_supports_dict_shape():
    pipeline = ClusteringPipeline(min_reviews=5)
    reviews = [
        {"text": "lagging crash slow freeze bad", "score": 1},
        {"text": "lagging crash slow freeze bad", "score": 1},
        {"text": "lagging crash slow freeze bad", "score": 1},
        {"text": "lagging crash slow freeze bad", "score": 1},
        {"text": "excellent smooth clean good", "score": 5},
        {"text": "excellent smooth clean good", "score": 5},
    ]
    clusters = pipeline.run(reviews, num_clusters=2)
    assert len(clusters) == 2
    assert clusters[0]["avg_rating"] == 1.0


def test_hf_bge_embeddings():
    import json
    mock_res = MagicMock()
    mock_res.read.return_value = json.dumps([[0.1]*384] * 6).encode("utf-8")
    
    mock_context = MagicMock()
    mock_context.__enter__.return_value = mock_res
    
    with patch("urllib.request.urlopen", return_value=mock_context):
        pipeline = ClusteringPipeline(min_reviews=5, hf_token="mock-hf-token")
        reviews = [
            {"text": "lagging crash slow freeze bad", "score": 1},
            {"text": "lagging crash slow freeze bad", "score": 1},
            {"text": "lagging crash slow freeze bad", "score": 1},
            {"text": "lagging crash slow freeze bad", "score": 1},
            {"text": "excellent smooth clean good", "score": 5},
            {"text": "excellent smooth clean good", "score": 5},
        ]
        clusters = pipeline.run(reviews, num_clusters=2)
        assert len(clusters) == 2


