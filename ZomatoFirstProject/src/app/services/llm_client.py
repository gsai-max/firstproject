import abc
import time
import logging
from groq import Groq
from src.app.config import settings
import httpx

logger = logging.getLogger(__name__)

class BaseLLMClient(abc.ABC):
    @abc.abstractmethod
    def complete(self, prompt: str, system_instruction: str) -> str:
        pass

class GroqClient(BaseLLMClient):
    def __init__(self):
        # Enforce strict 8.0-second timeout boundaries to handle external network latencies
        self.client = Groq(
            api_key=settings.LLM_API_KEY,
            http_client=httpx.Client(timeout=8.0)
        )
        self.model = settings.LLM_MODEL

    def complete(self, prompt: str, system_instruction: str) -> str:
        max_retries = 3
        backoff_factor = 2.0
        initial_delay = 1.0

        for attempt in range(max_retries + 1):
            try:
                completion = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": system_instruction},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.3,
                    response_format={"type": "json_object"}
                )
                return completion.choices[0].message.content
            except Exception as e:
                if attempt == max_retries:
                    logger.error(f"Groq API call failed after {max_retries} retries: {e}")
                    raise e
                delay = initial_delay * (backoff_factor ** attempt)
                logger.warning(
                    f"Groq API call failed (attempt {attempt + 1}/{max_retries + 1}) due to: {e}. "
                    f"Retrying in {delay:.1f}s..."
                )
                time.sleep(delay)
