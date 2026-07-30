import json
import httpx
from typing import Optional, Dict, Any
from src.app.config import settings

try:
    from groq import Groq
except ImportError:
    Groq = None


class LLMClient:
    """Multi-provider LLM client wrapper supporting Groq & Hugging Face open models."""

    def __init__(
        self,
        provider: Optional[str] = None,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
    ):
        self.provider = (provider or settings.LLM_PROVIDER).lower()
        self.api_key = api_key or (settings.GROQ_API_KEY or settings.LLM_API_KEY)
        self.model = model or (settings.GROQ_MODEL if self.provider == "groq" else settings.HF_MODEL)
        self.client = None

        if self.provider == "groq":
            if Groq and self.api_key and self.api_key != "your_groq_api_key_here":
                try:
                    self.client = Groq(
                        api_key=self.api_key,
                        http_client=httpx.Client(timeout=settings.LLM_TIMEOUT_SECONDS),
                    )
                except Exception as e:
                    print(f"LLMClient warning: failed to initialize Groq client ({e}). Running in fallback mode.")
        elif self.provider == "huggingface":
            self.hf_token = settings.HF_TOKEN
            self.hf_model = settings.HF_MODEL

    def complete(self, prompt: str, system_instruction: str) -> str:
        """Sends chat completion request to Groq or Hugging Face LLM."""
        if self.provider == "groq":
            if not self.client:
                raise RuntimeError("Groq LLMClient is unconfigured or missing a valid API key.")

            completion = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_instruction},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.3,
                response_format={"type": "json_object"},
            )
            return completion.choices[0].message.content

        elif self.provider == "huggingface":
            headers = {"Authorization": f"Bearer {self.hf_token}"} if self.hf_token else {}
            url = f"https://api-inference.huggingface.co/models/{self.hf_model}"
            payload = {
                "inputs": f"System: {system_instruction}\nUser: {prompt}\nAssistant:",
                "parameters": {"max_new_tokens": 1024, "temperature": 0.3, "return_full_text": False},
            }
            with httpx.Client(timeout=settings.LLM_TIMEOUT_SECONDS * 2) as client:
                response = client.post(url, headers=headers, json=payload)
                response.raise_for_status()
                res = response.json()
                if isinstance(res, list) and len(res) > 0:
                    return res[0].get("generated_text", json.dumps(res[0]))
                return json.dumps(res)

        else:
            raise ValueError(f"Unsupported LLM provider: {self.provider}")

