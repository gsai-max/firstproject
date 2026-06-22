import os
import time
import random
import logging
import json
from datetime import datetime
from pathlib import Path
import requests

logger = logging.getLogger(__name__)

# Standard modern User-Agent to avoid simple user-agent blocking
DEFAULT_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
}

class GrowwScraper:
    def __init__(self, raw_data_dir: Path | str = "data/raw", delay_range: tuple[float, float] = (1.5, 3.5)):
        self.raw_dir = Path(raw_data_dir)
        self.raw_dir.mkdir(parents=True, exist_ok=True)
        self.delay_range = delay_range

    def fetch_page(self, url: str, slug: str, force: bool = False) -> str | None:
        """
        Fetch HTML content from URL and save it along with metadata.
        If force is False, use cached file if it exists.
        """
        html_path = self.raw_dir / f"{slug}.html"
        meta_path = self.raw_dir / f"{slug}.metadata.json"

        if not force and html_path.exists() and meta_path.exists():
            logger.info(f"Using cached HTML for: {slug}")
            with open(html_path, "r", encoding="utf-8") as f:
                return f.read()

        logger.info(f"Fetching URL: {url}")
        
        # Enforce politeness delay
        delay = random.uniform(*self.delay_range)
        logger.debug(f"Sleeping for {delay:.2f} seconds before request...")
        time.sleep(delay)

        try:
            response = requests.get(url, headers=DEFAULT_HEADERS, timeout=15)
            response.raise_for_status()
            html_content = response.text

            # Save raw HTML
            with open(html_path, "w", encoding="utf-8") as f:
                f.write(html_content)

            # Save metadata
            metadata = {
                "url": url,
                "slug": slug,
                "fetched_at": datetime.utcnow().isoformat() + "Z",
                "status_code": response.status_code,
            }
            with open(meta_path, "w", encoding="utf-8") as f:
                json.dump(metadata, f, indent=2, ensure_ascii=False)

            logger.info(f"Successfully fetched and cached: {slug}")
            return html_content

        except Exception as e:
            logger.error(f"Error fetching URL {url}: {e}")
            return None

    def fetch_all(self, schemes: list, force: bool = False) -> dict[str, bool]:
        """
        Fetch all pages in the schemes list.
        Returns a dict mapping slug to success status.
        """
        results = {}
        for scheme in schemes:
            slug = scheme.slug
            url = scheme.source_url
            content = self.fetch_page(url, slug, force=force)
            results[slug] = content is not None
        return results
