"""
Base fetcher class with common interface for all data source types.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from ..utils.logger import get_logger
from ..utils.network import NetworkUtils


class BaseFetcher(ABC):
    """Abstract base class for all fetchers."""

    def __init__(self, source_config: dict[str, Any], global_config: dict[str, Any]):
        self.source_config = source_config
        self.global_config = global_config
        self.name: str = source_config.get("name", "unknown")
        self.interval: float = float(source_config.get("interval", 3.0))
        self.category: str = source_config.get("category", "学术论文")
        self.enabled: bool = source_config.get("enabled", True)
        self.network = NetworkUtils(global_config)
        self.logger = get_logger(__name__)

    @abstractmethod
    async def fetch(self) -> list[dict[str, Any]]:
        """Fetch and parse items from this source. Returns list of raw item dicts."""
        ...

    def get_source_meta(self) -> dict[str, Any]:
        """Return source metadata for each item."""
        return {
            "source": self.name,
            "category": self.category,
            "source_type": self.source_config.get("type", "unknown"),
        }

    def to_standard_item(self, raw: dict[str, Any]) -> dict[str, Any]:
        """Convert a raw fetched item to the standardized schema."""
        import hashlib
        from ..utils.time_utils import TimeUtils

        title = raw.get("title", "").strip()
        origin_url = raw.get("origin_url", "").strip()
        unique_str = f"{title}|{origin_url}"
        item_id = hashlib.sha256(unique_str.encode("utf-8")).hexdigest()[:12]

        publish_date = raw.get("publish_date", "")
        parsed_date = TimeUtils.parse_date(publish_date)

        return {
            "id": item_id,
            "title": title,
            "abstract": raw.get("abstract", "").strip()[:300],
            "source": self.name,
            "source_type": self.source_config.get("type", "unknown"),
            "publish_date": TimeUtils.format_date(parsed_date) if parsed_date else TimeUtils.today_str(),
            "category": self.category,
            "is_backdoor": raw.get("is_backdoor", False),
            "tags": raw.get("tags", []),
            "origin_url": origin_url,
            "pdf_url": raw.get("pdf_url", ""),
            "arxiv_id": raw.get("arxiv_id", ""),
            "is_today_new": True,
            "created_at": TimeUtils.today_str(),
        }
