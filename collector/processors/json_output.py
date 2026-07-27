"""
JSON Output - Write collected data to structured JSON files.
"""
from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional, Union

from ..utils.logger import get_logger

logger = get_logger(__name__)


class JsonOutput:
    """Write news items to structured JSON files."""

    def __init__(self, config: dict[str, Any]):
        out_cfg = config.get("output", {})
        self.data_dir = Path(out_cfg.get("data_dir", "docs/data"))
        self.all_news_file = out_cfg.get("all_news_file", "all_news.json")
        self.daily_prefix = out_cfg.get("daily_prefix", "news_")
        self.data_dir.mkdir(parents=True, exist_ok=True)

    def write_daily(self, items: list[dict[str, Any]]):
        """Write daily JSON file: data/news_YYYY-MM-DD.json"""
        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        filename = f"{self.daily_prefix}{today}.json"
        filepath = self.data_dir / filename
        self._write_json(filepath, items)
        logger.info(f"Written daily file: {filepath} ({len(items)} items)")

    def merge_all(self, new_items: list[dict[str, Any]]):
        """
        Merge new items into all_news.json.
        Reads existing file, appends new items, sorts by date descending.
        """
        filepath = self.data_dir / self.all_news_file
        existing = self._read_existing(filepath)

        # Create lookup for existing IDs
        existing_ids = {item["id"] for item in existing if "id" in item}

        # Add only truly new items
        added = 0
        for item in new_items:
            item_id = item.get("id", "")
            if item_id and item_id not in existing_ids:
                existing.append(item)
                existing_ids.add(item_id)
                added += 1

        # Sort by publish_date descending
        existing.sort(
            key=lambda x: x.get("publish_date", ""),
            reverse=True
        )

        # Write deduplicated merged data
        output_data = {
            "meta": {
                "total_count": len(existing),
                "last_updated": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
                "today_new": len(new_items),
                "today_added": added,
            },
            "news": existing,
        }
        self._write_json(filepath, output_data)
        logger.info(f"Merged into {filepath}: +{added} new, "
                    f"{len(existing)} total")

    def write_today_stats(self, items: list[dict[str, Any]], output_path: Optional[Union[str, Path]] = None):
        """Write a stats summary for today's collection run."""
        total = len(items)
        backdoor_count = sum(1 for i in items if i.get("is_backdoor"))
        categories = {}
        for item in items:
            cat = item.get("category", "unknown")
            categories[cat] = categories.get(cat, 0) + 1

        stats = {
            "date": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
            "total_items": total,
            "backdoor_items": backdoor_count,
            "category_breakdown": categories,
            "sources": list({item.get("source", "") for item in items if item.get("source")}),
        }

        if output_path:
            path = Path(output_path)
        else:
            path = self.data_dir / "today_stats.json"

        self._write_json(path, stats)
        logger.info(f"Stats: {total} total, {backdoor_count} backdoor")
        return stats

    @staticmethod
    def _read_existing(filepath: Path) -> list[dict[str, Any]]:
        """Read existing all_news.json."""
        if not filepath.exists():
            return []
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
            if isinstance(data, dict) and "news" in data:
                return data["news"]
            if isinstance(data, list):
                return data
            return []
        except (json.JSONDecodeError, IOError) as e:
            logger.warning(f"Could not read existing data: {e}")
            return []

    @staticmethod
    def _write_json(filepath: Path, data: Any):
        """Write JSON with pretty formatting."""
        filepath.parent.mkdir(parents=True, exist_ok=True)
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
