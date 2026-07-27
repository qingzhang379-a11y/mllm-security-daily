"""
Dedup Engine - Remove duplicate news items based on URL + title hash.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Optional, Union

from ..utils.logger import get_logger

logger = get_logger(__name__)


class DedupEngine:
    """Deduplicate news items using SHA256 hashing."""

    def __init__(self, data_dir: Union[str, Path], config: Optional[dict[str, Any]] = None):
        self.data_dir = Path(data_dir)
        self.config = config or {}
        self._existing_hashes: set[str] = set()
        self._load_existing()

    def _load_existing(self):
        """Load existing item hashes from the all_news.json file."""
        all_news_path = self.data_dir / "all_news.json"
        if all_news_path.exists():
            try:
                with open(all_news_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                items = data.get("news", []) if isinstance(data, dict) else data
                for item in items:
                    item_hash = self._compute_hash(item)
                    if item_hash:
                        self._existing_hashes.add(item_hash)
                logger.info(f"Loaded {len(self._existing_hashes)} existing hashes")
            except (json.JSONDecodeError, IOError) as e:
                logger.warning(f"Could not load existing data: {e}")

    @staticmethod
    def _compute_hash(item: dict[str, Any]) -> Optional[str]:
        """Compute SHA256 hash from origin_url and title."""
        origin_url = item.get("origin_url", "").strip()
        title = item.get("title", "").strip()
        if not origin_url and not title:
            return None
        unique_str = f"{origin_url}|{title}".lower().strip()
        return hashlib.sha256(unique_str.encode("utf-8")).hexdigest()[:16]

    def is_duplicate(self, item: dict[str, Any]) -> bool:
        """Check if an item is a duplicate."""
        item_hash = self._compute_hash(item)
        if item_hash is None:
            return False
        return item_hash in self._existing_hashes

    def mark_as_seen(self, item: dict[str, Any]):
        """Add an item's hash to the seen set."""
        item_hash = self._compute_hash(item)
        if item_hash:
            self._existing_hashes.add(item_hash)

    def dedup(self, items: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """
        Remove duplicates from a list of items.
        Returns only new (non-duplicate) items.
        """
        new_items = []
        dup_count = 0
        for item in items:
            if self.is_duplicate(item):
                dup_count += 1
                continue
            self.mark_as_seen(item)
            new_items.append(item)

        if dup_count > 0:
            logger.info(f"Dedup: removed {dup_count} duplicates, "
                        f"{len(new_items)} new items remaining")
        return new_items
