import json
import os
import sys
import datetime
from pathlib import Path
from src.config import load_config
from src.pipeline.summarizer import ReviewSummarizer
from src.ingestion.models import Review
from src.delivery.client import generate_markdown_report, append_to_google_doc

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
    print("Running Phase 4 Delivery Pipeline (Clustering -> Google Doc Delivery)")
    print("======================================================================\n")

    config = load_config("groww")

    # Display configured keys (masked)
    groq_key = os.environ.get("GROQ_API_KEY")
    openai_key = os.environ.get("OPENAI_API_KEY")

    print(f"Embedding Provider: {config.pipeline.embedding.provider}")
    print(f"LLM Provider: {config.pipeline.summarization.provider}")
    print(f"GROQ_API_KEY: {f'Present ({groq_key[:6]}...)' if groq_key else 'Missing'}")
    print(f"OPENAI_API_KEY: {f'Present ({openai_key[:6]}...)' if openai_key else 'Missing'}\n")

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
        print(f"Generated {len(themes)} Themes.")
        
        # Determine ISO week
        today = datetime.date.today()
        iso_year, iso_week_num, _ = today.isocalendar()
        iso_week = f"{iso_year}-W{iso_week_num:02d}"
        
        # Generate Markdown Report
        print("\nGenerating Markdown Report...")
        utc_now = datetime.datetime.now(datetime.timezone.utc)
        ist_now = utc_now + datetime.timedelta(hours=5, minutes=30)
        generated_date_str = f"{ist_now.strftime('%Y-%m-%d')} IST"
        
        markdown_report = generate_markdown_report(
            display_name="Groww",
            window_weeks=config.product.ingestion.window_weeks,
            themes=themes,
            generated_date_str=generated_date_str
        )
        
        # Append to Google Doc
        doc_id = config.product.delivery.google_doc_id
        print(f"\nAttempting Google Doc Delivery (Doc ID: {doc_id})...")
        delivery_res = append_to_google_doc(
            doc_id=doc_id,
            content=markdown_report,
            iso_week=iso_week
        )
        
        print("\n======================================================================")
        print("Delivery Result:")
        print("======================================================================\n")
        print(json.dumps(delivery_res, indent=2))
        print("======================================================================")
        
    except Exception as e:
        print(f"\nPipeline execution failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
