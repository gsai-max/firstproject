"""CLI entrypoint for running the scraping stage across all 10 feedback sources.

Usage:
    python scripts/scrape_only.py
"""
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.app.scrapers.app_store import AppStoreScraper
from src.app.scrapers.competitor_scrapers import CompetitorScraper
from src.app.scrapers.forum_crawler import ForumCrawler
from src.app.scrapers.play_store import PlayStoreScraper
from src.app.scrapers.quora_crawler import QuoraCrawler
from src.app.scrapers.reddit_scraper import RedditScraper
from src.app.scrapers.twitter_scraper import TwitterScraper
from src.app.scrapers.youtube_scraper import YouTubeScraper
from src.app.services.s3_store import S3DataLakeStore


def run_scraping():
    print("==================================================")
    print("  Blinkit Discovery Engine — 10-Channel Scraper  ")
    print("==================================================")

    scrapers = [
        ("Play Store", PlayStoreScraper(), "play_store"),
        ("App Store", AppStoreScraper(), "app_store"),
        ("Reddit", RedditScraper(), "reddit"),
        ("Twitter/X", TwitterScraper(), "twitter"),
        ("YouTube", YouTubeScraper(), "youtube"),
        ("Quora", QuoraCrawler(), "quora"),
        ("Forums", ForumCrawler(), "forums"),
        ("Competitors", CompetitorScraper(), "competitors"),
    ]

    s3_store = S3DataLakeStore()
    total_records = 0
    summary = {}

    for name, scraper, source_tag in scrapers:
        print(f"\n[+] Running {name} Scraper...")
        try:
            records = scraper.scrape()
            count = len(records)
            summary[name] = count
            total_records += count
            s3_store.persist_raw_records(source_tag, records)
            print(f"    --> Successfully collected {count} raw records.")
        except Exception as e:
            print(f"    --> Error running {name} scraper: {e}")
            summary[name] = 0

    print("\n==================================================")
    print("  Scraping Summary (10-Channel Data Lake)")
    print("==================================================")
    for name, count in summary.items():
        print(f"  - {name:<12}: {count:>6} raw records")
    print(f"  TOTAL RAW    : {total_records:>6} records")
    print("==================================================")
    return summary


if __name__ == "__main__":
    run_scraping()
