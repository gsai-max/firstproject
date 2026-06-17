import json
import os
import sys
from pathlib import Path
from src.config import load_config
from src.pipeline.summarizer import ReviewSummarizer
from src.ingestion.models import Review

# Standard Mock response objects for LLM simulation
class MockMessage:
    def __init__(self, content):
        self.content = content

class MockChoice:
    def __init__(self, content):
        self.message = MockMessage(content)

class MockResponse:
    def __init__(self, content):
        self.choices = [MockChoice(content)]

class MockCompletions:
    def __init__(self):
        self.call_idx = 0
        
    def create(self, *args, **kwargs):
        self.call_idx += 1
        messages = kwargs.get("messages", [])
        prompt = messages[-1]["content"] if messages else ""
        
        # Parse reviews from prompt to extract real verbatim quotes dynamically
        review_lines = []
        for line in prompt.split("\n"):
            if line.strip().startswith("- "):
                review_lines.append(line.strip()[2:])
                
        if review_lines:
            selected = review_lines[0]
            words = selected.split()
            if len(words) > 6:
                quote = " ".join(words[:6])
            else:
                quote = selected
            quotes = [quote]
        else:
            quotes = ["easy to use"]

        # Simulates LLM analysis by checking keywords in reviews block
        if "charge" in prompt or "fee" in prompt or "brokerage" in prompt:
            theme_name = "Brokerage & Transaction Fees"
            summary = "Users complain about high brokerage fee rates and hidden charges on trades."
            actions = [{"title": "Display Brokerage Calculator", "detail": "Add an in-app calculator detailing all charges before purchase."}]
        elif "slow" in prompt or "lag" in prompt or "freeze" in prompt or "crash" in prompt:
            theme_name = "App Performance & Latency"
            summary = "Users report app freezing, slow loading, and delays during peak market hours."
            actions = [{"title": "Scale Peak Server Capacity", "detail": "Increase active server nodes between 9:00 AM and 10:30 AM IST."}]
        else:
            theme_name = "Trading UI & Interface Praise"
            summary = "Users praise the clean, easy-to-use user interface and simple navigation dashboard."
            actions = [{"title": "Maintain Design System Consistency", "detail": "Ensure minimal styling is kept for new features."}]
            
        content = json.dumps({
            "theme_name": theme_name,
            "summary": summary,
            "quotes": quotes,
            "action_ideas": actions
        })
        return MockResponse(content)

class MockChat:
    def __init__(self):
        self.completions = MockCompletions()

class MockLLMClient:
    def __init__(self):
        self.chat = MockChat()


def main():
    print("======================================================================")
    print("Running Phase 2 Analysis Pipeline (PII Scrubbing, Clustering, LLM)")
    print("======================================================================\n")

    config = load_config("groww")

    # Display configured keys (masked)
    groq_key = os.environ.get("GROQ_API_KEY")
    openai_key = os.environ.get("OPENAI_API_KEY")
    hf_token = os.environ.get("HF_TOKEN")

    print(f"Embedding Provider: {config.pipeline.embedding.provider}")
    print(f"LLM Provider: {config.pipeline.summarization.provider}")
    print(f"GROQ_API_KEY: {f'Present ({groq_key[:6]}...)' if groq_key else 'Missing'}")
    print(f"OPENAI_API_KEY: {f'Present ({openai_key[:6]}...)' if openai_key else 'Missing'}")
    print(f"HF_TOKEN: {f'Present ({hf_token[:6]}...)' if hf_token else 'Missing'}\n")

    normalized_path = Path("data/reviews_normalized.json")
    if not normalized_path.exists():
        print(f"Error: Normalized reviews file not found at {normalized_path}.")
        print("Please run Phase 1 (Ingestion) first or ensure data is available.")
        sys.exit(1)

    with open(normalized_path, "r", encoding="utf-8") as f:
        reviews_data = json.load(f)

    print(f"Loaded {len(reviews_data)} reviews from {normalized_path}")

    # Map input review dicts to Review models
    reviews = []
    for r in reviews_data:
        rating = r.get("rating") if "rating" in r else r.get("score")
        reviews.append(Review(text=r["text"], rating=rating))

    # Initialize Summarizer
    mocked_mode = False
    try:
        if not groq_key and config.pipeline.summarization.provider.lower() == "groq":
            print("Notice: GROQ_API_KEY is missing. Initializing ReviewSummarizer in MOCK mode to simulate LLM themes.")
            mock_client = MockLLMClient()
            summarizer = ReviewSummarizer(config=config, client=mock_client)
            mocked_mode = True
        elif not openai_key and config.pipeline.summarization.provider.lower() == "openai":
            print("Notice: OPENAI_API_KEY is missing. Initializing ReviewSummarizer in MOCK mode to simulate LLM themes.")
            mock_client = MockLLMClient()
            summarizer = ReviewSummarizer(config=config, client=mock_client)
            mocked_mode = True
        else:
            summarizer = ReviewSummarizer(config=config)
    except Exception as e:
        print(f"Failed to initialize ReviewSummarizer: {e}")
        sys.exit(1)

    # Run the pipeline
    print("Running clustering and theme extraction (LLM)...")
    try:
        themes = summarizer.run_pipeline(reviews)
        print("\n======================================================================")
        print(f"Pipeline Execution Complete! (Mocked: {mocked_mode})")
        print(f"Generated {len(themes)} Themes:")
        print("======================================================================\n")
        
        for idx, theme in enumerate(themes):
            print(f"Theme {idx + 1}: {theme['theme_name']}")
            print(f"  Score: {theme.get('score', 0.0):.2f}")
            print(f"  Size: {theme.get('size', 0)}")
            print(f"  Avg Rating: {theme.get('avg_rating', 0.0):.2f}")
            print(f"  Summary: {theme['summary']}")
            print("  Verbatim Quotes:")
            for q in theme['quotes']:
                print(f"    - \"{q}\"")
            print("  Action Ideas:")
            for action in theme['action_ideas']:
                print(f"    * {action['title']}: {action['detail']}")
            print("-" * 70)
            
    except Exception as e:
        print(f"\nPipeline execution failed: {e}")

if __name__ == "__main__":
    main()
