import pytest
from unittest.mock import MagicMock, patch
from src.app.services.llm_client import GroqClient

@patch("src.app.services.llm_client.Groq")
@patch("src.app.services.llm_client.time.sleep") # mock sleep so tests run instantly
def test_groq_client_retry_success(mock_sleep, mock_groq_class):
    # Setup mock Groq client and create response
    mock_client = MagicMock()
    mock_groq_class.return_value = mock_client
    
    # Mock completion object returned by chat.completions.create
    mock_completion = MagicMock()
    mock_completion.choices = [MagicMock(message=MagicMock(content='{"status": "success"}'))]
    
    # Configure side effect: raise exceptions twice, then succeed
    mock_client.chat.completions.create.side_effect = [
        Exception("Temporary Server Error"),
        Exception("Connection Timeout"),
        mock_completion
    ]
    
    client = GroqClient()
    response = client.complete("test prompt", "system instruction")
    
    assert response == '{"status": "success"}'
    assert mock_client.chat.completions.create.call_count == 3
    assert mock_sleep.call_count == 2

@patch("src.app.services.llm_client.Groq")
@patch("src.app.services.llm_client.time.sleep")
def test_groq_client_retry_exhausted(mock_sleep, mock_groq_class):
    mock_client = MagicMock()
    mock_groq_class.return_value = mock_client
    
    # Configure side effect to always fail
    mock_client.chat.completions.create.side_effect = Exception("Persistent API Error")
    
    client = GroqClient()
    
    with pytest.raises(Exception, match="Persistent API Error"):
        client.complete("test prompt", "system instruction")
        
    # Should call 1 original attempt + 3 retries = 4 times total
    assert mock_client.chat.completions.create.call_count == 4
    assert mock_sleep.call_count == 3
