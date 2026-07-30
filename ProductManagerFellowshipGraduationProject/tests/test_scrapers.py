"""
Phase 2 Unit Tests — Multi-Source Scrapers

Validates scraper execution, domain model mapping, JSONL file persistence,
and non-empty output collection across all 5 feedback sources.
"""
import glob
import os
import shutil
import pytest

from src.app.config import settings
from src.app.models.domain import RawFeedbackRecord
from src.app.scrapers.app_store import AppStoreScraper
from src.app.scrapers.competitor_scrapers import CompetitorScraper
from src.app.scrapers.forum_crawler import ForumCrawler
from src.app.scrapers.play_store import PlayStoreScraper
from src.app.scrapers.quora_crawler import QuoraCrawler
from src.app.scrapers.reddit_scraper import RedditScraper
from src.app.scrapers.twitter_scraper import TwitterScraper
from src.app.scrapers.youtube_scraper import YouTubeScraper
from src.app.services.s3_store import S3DataLakeStore


class TestScrapers:
    """Test suite for Phase 2 data collection scrapers."""

    @pytest.fixture(autouse=True)
    def setup_test_dir(self, tmp_path):
        """Overrides raw data dir to temporary folder during tests."""
        self.original_dir = settings.RAW_DATA_DIR
        settings.RAW_DATA_DIR = str(tmp_path)
        yield
        settings.RAW_DATA_DIR = self.original_dir

    def test_play_store_scraper(self):
        scraper = PlayStoreScraper()
        records = scraper.scrape()
        assert len(records) > 0
        assert all(isinstance(r, RawFeedbackRecord) for r in records)
        assert records[0].source == "play_store"
        assert os.path.exists(os.path.join(settings.RAW_DATA_DIR, "play_store"))

    def test_app_store_scraper(self):
        scraper = AppStoreScraper()
        records = scraper.scrape()
        assert len(records) > 0
        assert all(isinstance(r, RawFeedbackRecord) for r in records)
        assert records[0].source == "app_store"
        assert os.path.exists(os.path.join(settings.RAW_DATA_DIR, "app_store"))

    def test_reddit_scraper(self):
        scraper = RedditScraper()
        records = scraper.scrape()
        assert len(records) > 0
        assert all(isinstance(r, RawFeedbackRecord) for r in records)
        assert records[0].source == "reddit"
        assert os.path.exists(os.path.join(settings.RAW_DATA_DIR, "reddit"))

    def test_twitter_scraper(self):
        scraper = TwitterScraper()
        records = scraper.scrape()
        assert len(records) > 0
        assert all(isinstance(r, RawFeedbackRecord) for r in records)
        assert records[0].source == "twitter"
        assert os.path.exists(os.path.join(settings.RAW_DATA_DIR, "twitter"))

    def test_forum_crawler(self):
        crawler = ForumCrawler()
        records = crawler.scrape()
        assert len(records) > 0
        assert all(isinstance(r, RawFeedbackRecord) for r in records)
        assert records[0].source == "forums"
        assert os.path.exists(os.path.join(settings.RAW_DATA_DIR, "forums"))

    def test_youtube_scraper(self):
        scraper = YouTubeScraper()
        records = scraper.scrape()
        assert len(records) > 0
        assert all(isinstance(r, RawFeedbackRecord) for r in records)
        assert records[0].source == "youtube"
        assert os.path.exists(os.path.join(settings.RAW_DATA_DIR, "youtube"))

    def test_quora_crawler(self):
        crawler = QuoraCrawler()
        records = crawler.scrape()
        assert len(records) > 0
        assert all(isinstance(r, RawFeedbackRecord) for r in records)
        assert records[0].source == "quora"
        assert os.path.exists(os.path.join(settings.RAW_DATA_DIR, "quora"))

    def test_competitor_scraper(self):
        scraper = CompetitorScraper()
        records = scraper.scrape()
        assert len(records) > 0
        assert all(isinstance(r, RawFeedbackRecord) for r in records)
        assert os.path.exists(os.path.join(settings.RAW_DATA_DIR, "zepto"))
        assert os.path.exists(os.path.join(settings.RAW_DATA_DIR, "instamart"))

    def test_s3_data_lake_store(self):
        store = S3DataLakeStore()
        record = RawFeedbackRecord(
            id="s3_test_01",
            source="play_store",
            platform="Google Play Store",
            text="Test record for S3 persistence",
            rating=5.0,
            date="2026-07-29",
            author="Tester",
            metadata={},
            scraped_at="2026-07-29T00:00:00",
        )
        path = store.persist_raw_records("play_store", [record])
        assert "s3://" in path
        assert os.path.exists(os.path.join(settings.RAW_DATA_DIR, "play_store"))

