import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from datetime import datetime, timezone

from src.ingestion.normalizer import clean_and_normalize, is_english, contains_emojis
from src.ingestion.models import RawReview, Review
from src.ingestion.client import PlayStoreMCPClient


def test_contains_emojis():
    assert contains_emojis("Hello 👍 World 🚀!") is True
    assert contains_emojis("No emojis here") is False
    assert contains_emojis("😊🔥✨") is True


def test_is_english():
    assert is_english("This is an English review with standard characters.") is True
    assert is_english("यह ऐप बहुत अच्छा है") is False  # Devanagari
    assert is_english("Great app! 100% works.") is True


def test_clean_and_normalize():
    # Valid review (English, word count >= 8, no emojis)
    text = "The Groww app is very smooth and makes investment extremely simple!"
    cleaned = clean_and_normalize(text, min_words=8)
    assert cleaned == "The Groww app is very smooth and makes investment extremely simple!"

    # Invalid due to containing emojis
    text_with_emoji = "The Groww app is very smooth and makes investment extremely simple! 👍😊"
    assert clean_and_normalize(text_with_emoji, min_words=8) == ""

    # Invalid due to word count
    assert clean_and_normalize("Too short", min_words=8) == ""

    # Invalid due to non-English text
    assert clean_and_normalize("यह ऐप बहुत अच्छा है और मुझे बहुत पसंद आया", min_words=8) == ""



@pytest.fixture
def anyio_backend():
    return "asyncio"


@pytest.mark.anyio
@patch("src.ingestion.client.stdio_client")
@patch("src.ingestion.client.ClientSession")
async def test_fetch_reviews(mock_client_session_cls, mock_stdio_client):
    # Set up mocks for stdio client context manager
    mock_read = MagicMock()
    mock_write = MagicMock()
    
    mock_stdio_context = AsyncMock()
    mock_stdio_context.__aenter__.return_value = (mock_read, mock_write)
    mock_stdio_client.return_value = mock_stdio_context

    # Set up mocks for ClientSession context manager
    mock_session = AsyncMock()
    mock_session_context = AsyncMock()
    mock_session_context.__aenter__.return_value = mock_session
    mock_client_session_cls.return_value = mock_session_context

    # Mock list_tools response
    mock_tool = MagicMock()
    mock_tool.name = "get_play_store_reviews"
    mock_tools_result = MagicMock()
    mock_tools_result.tools = [mock_tool]
    mock_session.list_tools.return_value = mock_tools_result

    # Mock call_tool response for reviews
    now_str = datetime.now(timezone.utc).isoformat()
    mock_call_result = MagicMock()
    mock_call_result.isError = False
    mock_call_result.content = [
        MagicMock(
            text=f"""{{
                "reviews": [
                    {{
                        "id": "1",
                        "userName": "User A",
                        "text": "This is a great review for Groww app!",
                        "score": 5,
                        "date": "{now_str}"
                    }}
                ],
                "nextPaginationToken": null
            }}"""
        )
    ]
    mock_session.call_tool.return_value = mock_call_result

    # Execute fetch_reviews
    client = PlayStoreMCPClient("com.nextbillion.groww")
    reviews = await client.fetch_reviews(window_weeks=10, max_reviews=10)

    # Assertions
    assert len(reviews) == 1
    assert reviews[0].text == "This is a great review for Groww app!"
    assert reviews[0].rating == 5
    
    mock_session.initialize.assert_awaited_once()
    mock_session.list_tools.assert_awaited_once()
    mock_session.call_tool.assert_awaited_once_with(
        "get_play_store_reviews",
        {"appId": "com.nextbillion.groww", "sort": "newest", "num": 100}
    )
