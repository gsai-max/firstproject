import json
import logging
from datetime import datetime, timedelta, timezone
from typing import List
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from src.config import ROOT_DIR
from src.ingestion.models import RawReview

logger = logging.getLogger(__name__)

SERVER_DIR = ROOT_DIR / "mcp_servers" / "playstore_mcp"
SERVER_JS = SERVER_DIR / "index.js"


class PlayStoreMCPClient:
    """
    Python client that spawns and communicates with the Node.js Play Store MCP Server.
    """
    def __init__(self, app_id: str):
        self.app_id = app_id
        # Define stdio subprocess transport configuration
        self.server_params = StdioServerParameters(
            command="node",
            args=[str(SERVER_JS)],
            cwd=str(SERVER_DIR)
        )

    async def fetch_reviews(self, window_weeks: int, max_reviews: int = 5000) -> List[RawReview]:
        """
        Fetches reviews for the configured app.
        Paginates until reviews are older than window_weeks or max_reviews limit is reached.
        """
        start_date = datetime.now(timezone.utc) - timedelta(weeks=window_weeks)
        all_reviews: List[RawReview] = []
        next_token = None
        
        logger.info(f"Connecting to Play Store MCP server at {SERVER_JS}...")
        
        async with stdio_client(self.server_params) as (read_stream, write_stream):
            async with ClientSession(read_stream, write_stream) as session:
                await session.initialize()
                
                # Check for get_play_store_reviews tool availability
                tools_result = await session.list_tools()
                tool_names = [t.name for t in tools_result.tools]
                if "get_play_store_reviews" not in tool_names:
                    raise RuntimeError("Required tool 'get_play_store_reviews' not exposed by Play Store MCP server.")
                
                while len(all_reviews) < max_reviews:
                    args = {
                        "appId": self.app_id,
                        "sort": "newest",
                        "num": 100
                    }
                    if next_token:
                        args["nextPaginationToken"] = next_token
                        
                    logger.info(f"Calling get_play_store_reviews (fetched {len(all_reviews)} so far)...")
                    result = await session.call_tool("get_play_store_reviews", args)
                    
                    if result.isError:
                        error_msg = result.content[0].text if result.content else "Unknown error"
                        raise RuntimeError(f"MCP server error: {error_msg}")
                        
                    response_text = result.content[0].text if result.content else "{}"
                    data = json.loads(response_text)
                    
                    reviews_data = data.get("reviews", [])
                    next_token = data.get("nextPaginationToken")
                    
                    if not reviews_data:
                        logger.info("No more reviews returned by scraper.")
                        break
                        
                    page_reviews: List[RawReview] = []
                    stop_paging = False
                    
                    for r in reviews_data:
                        try:
                            raw_review = RawReview.model_validate(r)
                            
                            # If review is older than the window, stop paging
                            if raw_review.published_at < start_date:
                                stop_paging = True
                                break
                                
                            page_reviews.append(raw_review)
                        except Exception as e:
                            logger.warning(f"Failed to parse review data: {r}. Error: {e}")
                            
                    all_reviews.extend(page_reviews)
                    
                    if stop_paging or not next_token:
                        break
                        
        return all_reviews[:max_reviews]


def save_reviews_to_files(raw_reviews: List[RawReview], product_name: str) -> None:
    from src.ingestion.normalizer import clean_and_normalize
    
    data_dir = ROOT_DIR / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    
    raw_path = data_dir / "reviews_raw.json"
    normalized_path = data_dir / "reviews_normalized.json"
    
    # Deduplicate raw reviews by hash of (text, rating, published_at) before saving/normalization
    seen_raw = set()
    deduped_raw = []
    for r in raw_reviews:
        published_dt = r.published_at.isoformat() if hasattr(r.published_at, "isoformat") else str(r.published_at)
        key = (" ".join(r.text.split()).lower(), r.rating, published_dt)
        if key not in seen_raw:
            seen_raw.add(key)
            deduped_raw.append(r)
            
    # 1. Save all raw reviews
    raw_list = [r.model_dump(mode="json") for r in deduped_raw]
    with open(raw_path, "w", encoding="utf-8") as f:
        json.dump(raw_list, f, indent=2, ensure_ascii=False)
    logger.info(f"Saved {len(raw_list)} raw reviews to {raw_path}")
    
    # 2. Clean and normalize
    normalized_list = []
    for r in deduped_raw:
        cleaned_text = clean_and_normalize(r.text)
        if cleaned_text:
            normalized_list.append({
                "text": cleaned_text,
                "rating": r.rating
            })
            
    with open(normalized_path, "w", encoding="utf-8") as f:
        json.dump(normalized_list, f, indent=2, ensure_ascii=False)
    logger.info(f"Saved {len(normalized_list)} normalized reviews to {normalized_path}")


if __name__ == "__main__":
    import asyncio
    from src.config import load_config
    
    logging.basicConfig(level=logging.INFO)
    
    async def run():
        # Load configuration for groww
        config = load_config("groww")
        client = PlayStoreMCPClient(app_id=config.product.play_store.app_id)
        
        # Fetch reviews
        raw_reviews = await client.fetch_reviews(
            window_weeks=config.product.ingestion.window_weeks,
            max_reviews=config.product.ingestion.max_reviews
        )
        
        # Save reviews to files
        save_reviews_to_files(raw_reviews, "groww")
        
    asyncio.run(run())

