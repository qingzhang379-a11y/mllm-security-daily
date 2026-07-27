"""
RSS/Atom Feed Fetcher - Fetch items from RSS/Atom feeds.
"""
from __future__ import annotations

from typing import Any, Optional

import feedparser

from .base_fetcher import BaseFetcher
from ..utils.logger import get_logger

logger = get_logger(__name__)


class RssFetcher(BaseFetcher):
    """Fetch items from standard RSS/Atom feeds."""

    async def fetch(self) -> list[dict[str, Any]]:
        if not self.enabled:
            logger.info(f"Source {self.name} is disabled, skipping")
            return []

        feed_url = self.source_config.get("feed_url", "")
        if not feed_url:
            logger.error(f"No feed_url configured for {self.name}")
            return []

        logger.info(f"Fetching RSS: {self.name} -> {feed_url}")

        raw_xml = await self.network.aiohttp_get(
            feed_url, source_name=self.name, interval=self.interval
        )

        if raw_xml is None:
            logger.error(f"Failed to fetch RSS: {self.name}")
            return []

        return self._parse_feed(raw_xml)

    def _parse_feed(self, xml_data: str) -> list[dict[str, Any]]:
        """Parse RSS/Atom feed XML."""
        feed = feedparser.parse(xml_data)
        items = []

        for entry in feed.entries:
            try:
                item = self._parse_entry(entry)
                if item:
                    items.append(item)
            except Exception as e:
                logger.warning(f"Failed to parse RSS entry from {self.name}: {e}")
                continue

        logger.info(f"Parsed {len(items)} items from RSS: {self.name}")
        return items

    def _parse_entry(self, entry: dict) -> Optional[dict[str, Any]]:
        """Parse a single RSS/Atom entry."""
        title = entry.get("title", "").strip()
        if not title:
            return None

        # Get link (prefer 'link' field, fallback to 'id')
        link = ""
        entry_link = entry.get("link", "")
        if isinstance(entry_link, str):
            link = entry_link
        elif isinstance(entry_link, dict):
            link = entry_link.get("href", "")
        if not link:
            link = entry.get("id", "")

        # Get summary/description
        summary = ""
        for field in ["summary", "description", "content", "subtitle"]:
            val = entry.get(field, "")
            if val:
                if isinstance(val, str):
                    summary = val
                elif isinstance(val, list) and len(val) > 0:
                    summary = val[0].get("value", "") if isinstance(val[0], dict) else str(val[0])
                elif isinstance(val, dict):
                    summary = val.get("value", "")
                break

        # Clean HTML tags from summary
        if summary:
            import re
            summary = re.sub(r"<[^>]+>", "", summary).strip()

        # Get published date
        published = entry.get("published", "") or entry.get("updated", "") or ""

        # Get tags/categories
        tags = []
        for tag in entry.get("tags", []):
            tag_term = ""
            if isinstance(tag, dict):
                tag_term = tag.get("term", "") or tag.get("label", "")
            elif isinstance(tag, str):
                tag_term = tag
            if tag_term:
                tags.append(tag_term)

        return {
            "title": title,
            "abstract": summary[:300],
            "publish_date": published,
            "origin_url": link,
            "pdf_url": "",
            "arxiv_id": "",
            "tags": tags,
            "is_backdoor": False,
        }