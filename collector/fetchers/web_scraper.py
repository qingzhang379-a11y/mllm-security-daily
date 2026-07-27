"""
Web Scraper - Lightweight HTTP scraper for sites without RSS/API.
Uses requests + BeautifulSoup. Falls back to Playwright if needed.
"""
from __future__ import annotations

from typing import Any, Optional

from bs4 import BeautifulSoup

from .base_fetcher import BaseFetcher
from ..utils.logger import get_logger

logger = get_logger(__name__)


class WebScraper(BaseFetcher):
    """Scrape web pages that don't have RSS feeds."""

    async def fetch(self) -> list[dict[str, Any]]:
        if not self.enabled:
            logger.info(f"Source {self.name} is disabled, skipping")
            return []

        page_url = self.source_config.get("page_url", "")
        selector = self.source_config.get("selector", {})

        if not page_url:
            logger.error(f"No page_url configured for {self.name}")
            return []

        logger.info(f"Scraping: {self.name} -> {page_url}")

        # Use synchronous requests for simplicity (wrapped in async)
        html = await self._fetch_page(page_url)

        if html is None:
            logger.error(f"Failed to scrape: {self.name}")
            return []

        return self._parse_html(html, selector)

    async def _fetch_page(self, url: str) -> Optional[str]:
        """Fetch page content. Returns HTML string or None."""
        return await self.network.aiohttp_get(
            url, source_name=self.name, interval=self.interval
        )

    def _parse_html(self, html: str, selector: dict[str, Any]) -> list[dict[str, Any]]:
        """Parse HTML content using CSS selectors."""
        soup = BeautifulSoup(html, "lxml")
        items = []

        # Try to find article elements
        article_selectors = selector.get("article", "article, .post, .entry, .blog-post, li.item")
        articles = soup.select(article_selectors)

        if not articles:
            # Fallback: treat top-level items as articles
            logger.warning(f"No articles found for {self.name}, trying fallback")
            # Try common listing patterns
            articles = soup.select("ul li, .list-item, .news-item")
            if not articles:
                return []

        for article in articles:
            try:
                item = self._extract_item(article, selector)
                if item and item.get("title"):
                    items.append(item)
            except Exception as e:
                logger.warning(f"Failed to parse item from {self.name}: {e}")
                continue

        logger.info(f"Scraped {len(items)} items from {self.name}")
        return items

    def _extract_item(self, article: Any, selector: dict[str, Any]) -> Optional[dict[str, Any]]:
        """Extract a single item from an HTML element using configured selectors."""
        title_sel = selector.get("title", "h2 a, h3 a, .title a, a[href]")
        link_sel = selector.get("link", "a@href")
        date_sel = selector.get("date", ".date, time, .published, .post-date")
        summary_sel = selector.get("summary", ".summary, .excerpt, p, .description")

        # Extract title
        title_el = article.select_one(title_sel) if title_sel != "a[href]" else article.select_one("a[href]")
        if not title_el:
            return None
        title = title_el.get_text(strip=True)

        # Extract link
        link = ""
        if "@" in str(link_sel):
            css_sel, attr = link_sel.split("@", 1)
            link_el = article.select_one(css_sel) if css_sel else article
            if link_el:
                link = link_el.get(attr, "")
        else:
            link_el = article.select_one(link_sel)
            if link_el:
                link = link_el.get("href", "")

        # Make absolute URL
        base_url = self.source_config.get("page_url", "")
        if link and not link.startswith("http"):
            from urllib.parse import urljoin
            link = urljoin(base_url, link)

        # Extract date
        date = ""
        if date_sel:
            date_el = article.select_one(date_sel)
            if date_el:
                date = date_el.get_text(strip=True)
                # Try to get datetime attribute
                if date_el.has_attr("datetime"):
                    date = date_el["datetime"]

        # Extract summary
        summary = ""
        if summary_sel:
            summary_el = article.select_one(summary_sel)
            if summary_el:
                summary = summary_el.get_text(strip=True)[:300]

        return {
            "title": title,
            "abstract": summary,
            "publish_date": date,
            "origin_url": link,
            "pdf_url": "",
            "arxiv_id": "",
            "tags": [],
            "is_backdoor": False,
        }