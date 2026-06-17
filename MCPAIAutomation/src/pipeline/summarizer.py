import time
import logging
from typing import List, Dict, Any, Optional
import json
import re

from src.config import AppConfig
from src.ingestion.models import Review
from src.pipeline.scrubber import scrub_pii
from src.pipeline.clustering import ClusteringPipeline
from src.pipeline.quote_validator import validate_quote

logger = logging.getLogger(__name__)

class ReviewSummarizer:
    def __init__(self, config: AppConfig, client: Optional[Any] = None):
        self.config = config
        self.client = client
        self.clustering_pipeline = ClusteringPipeline(
            min_reviews=config.product.ingestion.min_reviews,
            openai_api_key=config.openai_api_key,
            hf_token=config.hf_token,
            config=config
        )
        self._init_llm_client()

    def _init_llm_client(self):
        """Initializes LLM client if not already provided."""
        if self.client is not None:
            return
            
        provider = self.config.pipeline.summarization.provider.lower()
        if provider == "groq":
            from groq import Groq
            api_key = self.config.groq_api_key
            if not api_key:
                logger.warning("GROQ_API_KEY is not set in configuration.")
            self.client = Groq(api_key=api_key)
        elif provider == "openai":
            from openai import OpenAI
            api_key = self.config.openai_api_key
            if not api_key:
                logger.warning("OPENAI_API_KEY is not set in configuration.")
            self.client = OpenAI(api_key=api_key)
        else:
            raise ValueError(f"Unsupported LLM provider: {provider}")

    def _call_llm(self, prompt: str, system_prompt: str = "") -> str:
        """Helper to invoke the configured LLM client."""
        provider = self.config.pipeline.summarization.provider.lower()
        model = self.config.pipeline.summarization.model
        max_tokens = self.config.pipeline.summarization.max_output_tokens_per_theme
        
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        if provider == "groq":
            response = self.client.chat.completions.create(
                model=model,
                messages=messages,
                max_tokens=max_tokens,
                temperature=0.1,
                response_format={"type": "json_object"}
            )
            return response.choices[0].message.content
        elif provider == "openai":
            response = self.client.chat.completions.create(
                model=model,
                messages=messages,
                max_tokens=max_tokens,
                temperature=0.1,
                response_format={"type": "json_object"}
            )
            return response.choices[0].message.content
        else:
            raise ValueError(f"Unsupported LLM provider: {provider}")

    def _parse_and_validate(
        self, 
        content: str, 
        review_texts: List[str], 
        is_retry: bool = False
    ) -> Optional[Dict[str, Any]]:
        """Parses LLM output and validates quotes verbatim."""
        try:
            data = self._parse_json(content)
        except Exception as e:
            logger.warning(f"JSON parsing failed: {e}. Content: {content}")
            return None

        # Verify fields exist
        theme_name = data.get("theme_name")
        summary = data.get("summary")
        quotes = data.get("quotes", [])
        action_ideas = data.get("action_ideas", [])

        if not theme_name or not summary:
            logger.warning("Missing required fields in LLM response.")
            return None

        # Validate each quote verbatim
        valid_quotes = []
        for q in quotes:
            if validate_quote(q, review_texts):
                valid_quotes.append(q)
            else:
                logger.warning(f"Quote failed verbatim validation: '{q}'")

        if not valid_quotes:
            if not is_retry:
                # Signal that retry is needed because we have 0 valid quotes
                return None
            else:
                # Omit theme completely if second attempt also has 0 valid quotes
                logger.warning(f"Theme '{theme_name}' omitted: 0 valid quotes after retry.")
                return None

        return {
            "theme_name": theme_name,
            "summary": summary,
            "quotes": valid_quotes,
            "action_ideas": action_ideas
        }

    def _parse_json(self, content: str) -> Dict[str, Any]:
        """Robust parser for JSON content."""
        content = content.strip()
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            pass

        # Try to find a JSON object in markdown blocks
        match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', content, re.DOTALL)
        if match:
            return json.loads(match.group(1))

        # Try matching any curly braces
        match = re.search(r'(\{.*\})', content, re.DOTALL)
        if match:
            return json.loads(match.group(1))

        raise ValueError("No JSON object could be extracted from content.")

    def run_pipeline(self, raw_reviews: List[Any]) -> List[Dict[str, Any]]:
        """
        Runs the full Phase 2 pipeline:
        1. Scrubs PII from reviews.
        2. Clusters reviews using the clustering pipeline.
        3. Invokes LLM sequentially for each top cluster.
        4. Validates quotes and handles re-prompts/retry logic.
        """
        # 1. Scrub PII
        scrubbed_reviews = []
        for r in raw_reviews:
            if isinstance(r, dict):
                text = r.get("text", "")
                rating = r.get("rating") if "rating" in r else r.get("score")
            else:
                text = getattr(r, "text", "")
                rating = getattr(r, "rating", None)
                if rating is None:
                    rating = getattr(r, "score", None)
                    
            scrubbed_text = scrub_pii(str(text))
            scrubbed_reviews.append(Review(
                text=scrubbed_text,
                rating=int(rating) if rating is not None else 3
            ))

        # 2. Cluster reviews
        max_themes = self.config.pipeline.summarization.max_themes
        ranked_clusters = self.clustering_pipeline.run(
            scrubbed_reviews,
            num_clusters=max_themes
        )

        summarized_themes = []
        total_tokens_estimated = 0
        max_tokens_budget = self.config.pipeline.summarization.max_tokens_per_run
        
        # 3. Iterate through top clusters (up to max_themes)
        for idx, cluster in enumerate(ranked_clusters[:max_themes]):
            cluster_reviews = cluster["reviews"]
            cluster_review_texts = [r.text for r in cluster_reviews]

            # Select sample reviews for prompt
            max_samples = self.config.pipeline.summarization.max_samples_per_cluster
            sorted_samples = sorted(
                cluster_reviews,
                key=lambda r: (r.rating, -len(r.text))
            )
            sample_reviews = sorted_samples[:max_samples]
            sample_texts = [r.text for r in sample_reviews]

            reviews_input_str = "\n".join(f"- {text}" for text in sample_texts)

            system_prompt = (
                "You are an expert product analyst. You must analyze customer reviews for the Groww app, "
                "identify the primary feedback theme, and output a valid JSON object matching the requested schema."
            )

            prompt = (
                "Identify the main feedback theme in the customer reviews below.\n\n"
                f"Reviews:\n{reviews_input_str}\n\n"
                "Provide the output strictly as a JSON object with this schema:\n"
                "{\n"
                '  "theme_name": "Short name for the feedback category",\n'
                '  "summary": "1-2 sentence description of the feedback",\n'
                '  "quotes": ["1-3 exact verbatim quotes from the reviews above, or truncated with \'...\'"],\n'
                '  "action_ideas": [\n'
                "    {\n"
                '      "title": "Actionable task title",\n'
                '      "detail": "Actionable detail"\n'
                "    }\n"
                "  ]\n"
                "}\n\n"
                "Rules for quotes:\n"
                "1. Quotes must be verbatim substrings of the provided reviews.\n"
                "2. Keep spelling, spacing, and casing of the reviews where possible. You may use '...' to skip words, but do not paraphrase."
            )

            # Check token budget before LLM call
            estimated_call_tokens = (len(prompt) + len(system_prompt)) // 4
            if total_tokens_estimated + estimated_call_tokens > max_tokens_budget:
                logger.warning("Token budget exceeded. Stopping summarization pipeline.")
                break

            # Sequential rate limit sleep
            if idx > 0:
                time.sleep(self.config.pipeline.summarization.request_interval_seconds)

            logger.info(f"Summarizing cluster {idx+1}/{len(ranked_clusters[:max_themes])}...")
            
            # First attempt
            try:
                response_content = self._call_llm(prompt, system_prompt)
                total_tokens_estimated += estimated_call_tokens + (len(response_content) // 4)
            except Exception as e:
                logger.error(f"LLM call failed for cluster {idx}: {e}")
                continue

            theme_data = self._parse_and_validate(response_content, cluster_review_texts, is_retry=False)

            # Retry logic if validation fails (returns None due to 0 quotes)
            if theme_data is None:
                logger.info(f"0 valid quotes for cluster {idx+1}. Retrying with stricter instructions...")
                
                retry_prompt = (
                    "Your previous response had quotes that were not found verbatim in the review texts.\n"
                    "Select 1-3 quotes that are EXACT, character-for-character substrings of the reviews below.\n"
                    "Do NOT rewrite, fix typos, or edit punctuation. You may use '...' for truncation.\n\n"
                    f"Reviews:\n{reviews_input_str}\n\n"
                    "Output a single valid JSON matching the same schema."
                )

                if total_tokens_estimated + (len(retry_prompt) // 4) > max_tokens_budget:
                    logger.warning("Token budget exceeded for retry. Skipping retry.")
                    continue

                # Sequential rate limit sleep
                time.sleep(self.config.pipeline.summarization.request_interval_seconds)

                try:
                    response_content = self._call_llm(retry_prompt, system_prompt)
                    total_tokens_estimated += (len(retry_prompt) // 4) + (len(response_content) // 4)
                    theme_data = self._parse_and_validate(response_content, cluster_review_texts, is_retry=True)
                except Exception as e:
                    logger.error(f"LLM retry call failed for cluster {idx}: {e}")
                    continue

            if theme_data:
                # Add cluster metadata for reporting
                theme_data["score"] = cluster["score"]
                theme_data["avg_rating"] = cluster["avg_rating"]
                theme_data["size"] = cluster["size"]
                summarized_themes.append(theme_data)

        return summarized_themes
