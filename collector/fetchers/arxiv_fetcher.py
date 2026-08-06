"""
ArXiv API Fetcher - Query arXiv papers by keywords.
Uses the arXiv API: http://export.arxiv.org/api/query
"""
from __future__ import annotations

import asyncio
from typing import Any, Optional
from urllib.parse import urlencode

import feedparser

from .base_fetcher import BaseFetcher
from ..utils.logger import get_logger

logger = get_logger(__name__)


class ArxivFetcher(BaseFetcher):
    """Fetch papers from arXiv API using keyword queries."""

    MIRROR_DOMAIN_MAP = {
        "export.arxiv.org": "cn.arxiv.org",
        "arxiv.org": "cn.arxiv.org",
    }

    # On GitHub Actions, arxiv.org is reachable; on local CN network, use cn.arxiv.org.
    # sources.yaml already points to cn.arxiv.org, but we keep fallback for GitHub.
    OVERSEAS_DOMAIN_MAP = {
        "cn.arxiv.org": "export.arxiv.org",
    }

    async def fetch(self) -> list[dict[str, Any]]:
        if not self.enabled:
            logger.info(f"Source {self.name} is disabled, skipping")
            return []

        endpoint = self.source_config.get("endpoint", "")
        params = self.source_config.get("params", {})
        query_string = urlencode(params)
        url = f"{endpoint}?{query_string}"

        logger.info(f"Fetching arXiv: {self.name} -> {url}")

        # Try primary URL (should be cn.arxiv.org per config)
        raw_xml = await self.network.aiohttp_get(
            url, source_name=self.name, interval=self.interval
        )

        # Fallback: if primary fails and it's a CN mirror, try overseas (for GitHub Actions)
        if raw_xml is None and "cn.arxiv.org" in url:
            overseas_url = url.replace("cn.arxiv.org", "export.arxiv.org")
            logger.info(f"Trying overseas fallback: {overseas_url}")
            raw_xml = await self.network.aiohttp_get(
                overseas_url, source_name=self.name, interval=self.interval
            )

        # Legacy fallback (for backward compat)
        if raw_xml is None:
            mirror_url = self._get_mirror_url(url)
            if mirror_url:
                logger.info(f"Falling back to mirror: {mirror_url}")
                raw_xml = await self.network.aiohttp_get(
                    mirror_url, source_name=self.name, interval=self.interval
                )

        if raw_xml is None:
            logger.error(f"Failed to fetch arXiv: {self.name}")
            return []

        return self._parse_response(raw_xml)

    def _get_mirror_url(self, url: str) -> Optional[str]:
        """Replace domain with CN mirror for fallback."""
        for orig_domain, mirror_domain in self.MIRROR_DOMAIN_MAP.items():
            if orig_domain in url:
                return url.replace(orig_domain, mirror_domain)
        return None

    def _parse_response(self, xml_data: str) -> list[dict[str, Any]]:
        """Parse arXiv API XML response."""
        feed = feedparser.parse(xml_data)
        items = []

        for entry in feed.entries:
            try:
                item = self._parse_entry(entry)
                if item:
                    items.append(item)
            except Exception as e:
                logger.warning(f"Failed to parse arXiv entry: {e}")
                continue

        logger.info(f"Parsed {len(items)} papers from arXiv: {self.name}")
        return items

    def _parse_entry(self, entry: dict) -> Optional[dict[str, Any]]:
        """Parse a single arXiv entry."""
        title = entry.get("title", "").replace("\n", " ").strip()
        summary = entry.get("summary", "").replace("\n", " ").strip()

        # Extract arXiv ID from the entry ID
        entry_id = entry.get("id", "")
        arxiv_id = ""
        if "arxiv.org/abs/" in entry_id:
            arxiv_id = entry_id.split("arxiv.org/abs/")[-1].split("v")[0]
        elif "arxiv.org/" in entry_id:
            arxiv_id = entry_id.split("arxiv.org/")[-1].split("v")[0]

        # Get PDF link
        pdf_url = ""
        for link in entry.get("links", []):
            href = link.get("href", "")
            if "pdf" in href or link.get("type") == "application/pdf":
                pdf_url = href
                break
        if not pdf_url and arxiv_id:
            pdf_url = f"https://arxiv.org/pdf/{arxiv_id}"

        # Get published date
        published = entry.get("published", "")

        # Get tags/categories
        tags = []
        for tag in entry.get("tags", []):
            tag_term = tag.get("term", "")
            if tag_term:
                tags.append(tag_term)

        origin_url = entry_id if entry_id else f"https://arxiv.org/abs/{arxiv_id}"

        return {
            "title": title,
            "abstract": summary,
            "publish_date": published,
            "origin_url": origin_url,
            "pdf_url": pdf_url,
            "arxiv_id": arxiv_id,
            "tags": tags,
            "is_backdoor": False,  # Will be classified later
        }