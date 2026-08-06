"""
Web Scraper - Lightweight HTTP scraper for sites without RSS/API.
Uses requests + BeautifulSoup. Supports site-specific parser rules.
"""
from __future__ import annotations

import asyncio
from typing import Any, Optional
from urllib.parse import urljoin

from bs4 import BeautifulSoup

from .base_fetcher import BaseFetcher
from ..utils.logger import get_logger

logger = get_logger(__name__)

# Site-specific parser configurations
SITE_PARSERS = {
    "BAAI 智源研究院": {
        "article": "div.news-list > div.item, .news-item, .article-item, li.news-li, .list-item",
        "title": "a, h3 a, h4 a, .title a",
        "link": "a@href",
        "date": "span.date, .time, .post-time, .news-date",
        "summary": "p.desc, .summary, .abstract, .brief",
    },
    "智源社区": {
        "article": "article, .post-card, .feed-item, .content-list > div, .article-item",
        "title": "h2 a, h3 a, .title a, .post-title a",
        "link": "a@href",
        "date": "time, .date, .time, .post-meta time, .publish-date",
        "summary": "p, .summary, .excerpt, .description, .post-summary",
    },
    "阿里云 Qwen": {
        "article": "article, .post, .blog-post, .entry, .post-item",
        "title": "h1 a, h2 a, .post-title a, .entry-title a",
        "link": "a@href",
        "date": "time, .date, .post-date, .entry-date, .published",
        "summary": "p, .summary, .excerpt, .post-summary, .entry-summary",
    },
    "DeepSeek": {
        "article": "article, .blog-card, .post-item, .blog-item, .card-item",
        "title": "h2 a, h3 a, .card-title a, .blog-title a",
        "link": "a@href",
        "date": "time, .date, .blog-date, .meta-date",
        "summary": "p, .summary, .card-desc, .blog-desc",
    },
}


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

        html = await self._fetch_page(page_url)

        if html is None:
            logger.error(f"Failed to scrape: {self.name}")
            return []

        return await self._parse_html(html, selector)

    async def _fetch_page(self, url: str) -> Optional[str]:
        """Fetch page content. Returns HTML string or None."""
        return await self.network.aiohttp_get(
            url, source_name=self.name, interval=self.interval
        )

    def _get_site_selectors(self) -> dict[str, str]:
        """Get site-specific selectors or use defaults."""
        # Match by source name prefix
        for site_key, site_sel in SITE_PARSERS.items():
            if site_key in self.name:
                return site_sel
        return {}

    async def _parse_html(self, html: str, selector: dict[str, Any]) -> list[dict[str, Any]]:
        """Parse HTML content using CSS selectors."""
        soup = BeautifulSoup(html, "lxml")
        items = []

        # Merge site-specific selectors with user-configured ones
        site_sel = self._get_site_selectors()
        merged_sel = {**site_sel, **selector}

        # Article container selector (try site-specific first, then general)
        article_sel = merged_sel.get(
            "article",
            "article, .post, .entry, .blog-post, li.item, .news-item, "
            ".post-card, .card-item, .content-item, .list-item, "
            "div[class*='post'], div[class*='article'], div[class*='news']"
        )
        articles = soup.select(article_sel)

        if not articles:
            logger.warning(f"No articles found for {self.name}, trying fallback patterns")
            # Broader fallback patterns for Chinese sites
            fallback_patterns = [
                "ul li a[href*='blog'], ul li a[href*='post'], ul li a[href*='news']",
                "div.item, li.item, div.list-item",
                "a[href*='blog']:not([href*='#']):not([href*='tag'])",
            ]
            for pattern in fallback_patterns:
                articles = soup.select(pattern)
                if articles:
                    logger.info(f"Found {len(articles)} items with fallback: {pattern}")
                    break

        if not articles:
            return []

        for article in articles:
            try:
                item = self._extract_item(article, merged_sel)
                if item and item.get("title"):
                    items.append(item)
            except Exception as e:
                logger.warning(f"Failed to parse item from {self.name}: {e}")
                continue

        # If too few items, try broader article extraction
        if len(items) < 3:
            more_items = self._extract_broad(soup)
            existing_urls = {i.get("origin_url") for i in items if i.get("origin_url")}
            for mi in more_items:
                if mi.get("origin_url") not in existing_urls and mi.get("title"):
                    items.append(mi)
                    existing_urls.add(mi.get("origin_url", ""))

        # Enrich missing publish dates by fetching detail pages (bounded concurrency)
        missing_date = [i for i in items if not i.get("publish_date")]
        if missing_date:
            logger.info(f"Fetching detail pages for {len(missing_date)} items missing dates")
            sem = asyncio.Semaphore(5)
            tasks = [self._fetch_detail_date(i.get("origin_url", ""), sem) for i in missing_date]
            dates = await asyncio.gather(*tasks, return_exceptions=True)
            for item, date in zip(missing_date, dates):
                if isinstance(date, str) and date:
                    item["publish_date"] = date

        logger.info(f"Scraped {len(items)} items from {self.name}")
        return items

    async def _fetch_detail_date(self, url: str, sem: asyncio.Semaphore) -> str:
        """Fetch a detail page and extract its real publish date from meta tags."""
        if not url or not url.startswith("http"):
            return ""
        try:
            async with sem:
                html = await self.network.aiohttp_get(
                    url, source_name=self.name, interval=self.interval, timeout=15
                )
            if not html:
                return ""
            soup = BeautifulSoup(html, "lxml")
            # Priority: meta[property=article:published_time] > og:published_time > time[datetime]
            for sel in [
                'meta[property="article:published_time"]',
                'meta[property="og:published_time"]',
                'meta[name="date"]',
                'meta[itemprop="datePublished"]',
                'time[datetime]',
            ]:
                el = soup.select_one(sel)
                if not el:
                    continue
                value = el.get("content") or el.get("datetime")
                if value:
                    return value.strip()
            return ""
        except Exception as e:
            logger.debug(f"Failed to fetch detail date for {url}: {e}")
            return ""

    def _extract_broad(self, soup: BeautifulSoup) -> list[dict[str, Any]]:
        """Broader extraction: find all links with meaningful titles."""
        items = []
        seen_urls = set()
        for a_tag in soup.find_all("a", href=True):
            href = a_tag.get("href", "")
            title = a_tag.get_text(strip=True)
            # Filter out short/noise links
            if len(title) < 8 or not href.startswith(("http", "/")):
                continue
            if any(kw in href.lower() for kw in ["#", "javascript", "tag", "login", "register"]):
                continue
            key = href if href.startswith("http") else None
            if key and key in seen_urls:
                continue
            if key:
                seen_urls.add(key)

            base_url = self.source_config.get("page_url", "")
            full_url = urljoin(base_url, href) if not href.startswith("http") else href

            items.append({
                "title": title,
                "abstract": "",
                "publish_date": "",
                "origin_url": full_url,
                "pdf_url": "",
                "arxiv_id": "",
                "tags": [],
                "is_backdoor": False,
            })
        return items

    def _extract_item(self, article: Any, selector: dict[str, str]) -> Optional[dict[str, Any]]:
        """Extract a single item from an HTML element using configured selectors."""
        title_sel = selector.get("title", "h2 a, h3 a, .title a, a[href]")
        link_sel = selector.get("link", "a@href")
        date_sel = selector.get("date", ".date, time, .published, .post-date, .time")
        summary_sel = selector.get("summary", ".summary, .excerpt, p, .description, .abstract")

        # Extract title
        title_el = article.select_one(title_sel) if title_sel != "a[href]" else article.select_one("a[href]")
        if not title_el:
            # Try direct text
            direct_text = article.get_text(strip=True)[:80]
            if direct_text and len(direct_text) > 8:
                title = direct_text
            else:
                return None
        else:
            title = title_el.get_text(strip=True)

        # Extract link
        link = ""
        if "@" in str(link_sel):
            css_sel, attr = link_sel.split("@", 1)
            # If css_sel is empty, use the article itself
            if css_sel:
                link_el = article.select_one(css_sel)
            else:
                link_el = article.select_one("a[href]") or article
            if link_el:
                link = link_el.get(attr, "")
                if not link:
                    link = link_el.get("href", "")
        else:
            link_el = article.select_one(link_sel)
            if link_el:
                link = link_el.get("href", "")

        # If no link, try finding any link in the article
        if not link:
            any_link = article.find("a", href=True)
            if any_link:
                link = any_link.get("href", "")

        # Make absolute URL
        base_url = self.source_config.get("page_url", "")
        if link and not link.startswith("http"):
            if link.startswith("/"):
                from urllib.parse import urlparse
                parsed = urlparse(base_url)
                link = f"{parsed.scheme}://{parsed.netloc}{link}"
            else:
                link = urljoin(base_url, link)

        # Extract date
        date = ""
        if date_sel:
            date_el = article.select_one(date_sel)
            if date_el:
                date = date_el.get_text(strip=True)
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