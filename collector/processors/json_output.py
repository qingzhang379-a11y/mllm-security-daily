"""
JSON Output - Write collected data to structured JSON files.
Supports monthly sharding for scalability.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from ..utils.logger import get_logger

logger = get_logger(__name__)


class JsonOutput:
    """Write news items to structured JSON files."""

    def __init__(self, config: dict[str, Any]):
        out_cfg = config.get("output", {})
        self.data_dir = Path(out_cfg.get("data_dir", "docs/data"))
        self.archive_dir = self.data_dir / "archive"
        self.index_file = self.data_dir / "index.json"
        self.latest_file = self.data_dir / "latest.json"
        self.all_news_file = self.data_dir / "all_news.json"
        self.daily_prefix = out_cfg.get("daily_prefix", "news_")
        self.latest_days = 30

        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.archive_dir.mkdir(parents=True, exist_ok=True)

    def write_daily(self, items: list[dict[str, Any]]):
        """Write daily JSON file: data/news_YYYY-MM-DD.json"""
        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        filename = f"{self.daily_prefix}{today}.json"
        filepath = self.data_dir / filename
        self._write_json(filepath, items)
        logger.info(f"Written daily file: {filepath} ({len(items)} items)")

    def _get_month_key(self, date_str: str) -> str:
        """Extract YYYY-MM from a date string."""
        if date_str and len(date_str) >= 7:
            return date_str[:7]
        return datetime.now(timezone.utc).strftime("%Y-%m")

    def merge_all(self, new_items: list[dict[str, Any]]):
        """
        Merge new items with sharding:
        1. Write to monthly archive files
        2. Update index.json (lightweight metadata only)
        3. Update latest.json (last 30 days subset)
        4. Update all_news.json (full archive, for backward compat)
        """
        # Load existing index
        index = self._read_index()
        existing_ids = set(index.get("ids", []))

        # Separate new items
        truly_new = []
        for item in new_items:
            item_id = item.get("id", "")
            if item_id and item_id not in existing_ids:
                truly_new.append(item)
                existing_ids.add(item_id)

        if not truly_new:
            logger.info("No new items to merge")
            return

        logger.info(f"Merging {len(truly_new)} new items")

        # --- Step 1: Write to monthly archives ---
        monthly_buckets: dict[str, list[dict]] = {}
        for item in truly_new:
            month = self._get_month_key(item.get("publish_date", ""))
            monthly_buckets.setdefault(month, []).append(item)

        for month, month_items in monthly_buckets.items():
            archive_path = self.archive_dir / f"{month}.json"
            existing_month = self._read_json(archive_path) or []
            existing_month_ids = {i.get("id") for i in existing_month if i.get("id")}

            for item in month_items:
                if item.get("id") not in existing_month_ids:
                    existing_month.append(item)
                    existing_month_ids.add(item.get("id"))

            logger.info(f"  Monthly archive {month}: {len(existing_month)} items")
            self._write_json(archive_path, existing_month)

        # --- Step 2: Update index.json (lightweight) ---
        for item in truly_new:
            index["ids"].append(item["id"])
            index["items"].append({
                "id": item["id"],
                "title": item.get("title", ""),
                "publish_date": item.get("publish_date", ""),
                "category": item.get("category", ""),
                "is_backdoor": item.get("is_backdoor", False),
                "source": item.get("source", ""),
            })

        index["meta"] = {
            "total_count": len(index["ids"]),
            "last_updated": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "today_new": len(new_items),
            "today_added": len(truly_new),
        }
        # Keep index items sorted by date descending
        index["items"].sort(
            key=lambda x: x.get("publish_date", ""), reverse=True
        )
        self._write_json(self.index_file, index)
        logger.info(f"  Index: {len(index['ids'])} total items")

        # --- Step 3: Update latest.json (last 30 days) ---
        cutoff = datetime.now(timezone.utc).date()
        latest_items = [
            i for i in index["items"]
            if i.get("publish_date") and self._within_days(i["publish_date"], self.latest_days)
        ]
        # Load full content for latest items from archives
        latest_full = []
        seen_ids = set()
        for li in latest_items:
            mid = li["publish_date"][:7]
            archive_data = self._read_json(self.archive_dir / f"{mid}.json") or []
            for item in archive_data:
                if item.get("id") == li["id"] and item["id"] not in seen_ids:
                    latest_full.append(item)
                    seen_ids.add(item["id"])
                    break
        latest_full.sort(key=lambda x: x.get("publish_date", ""), reverse=True)
        self._write_json(self.latest_file, {
            "meta": {
                "total": len(latest_full),
                "range": f"last {self.latest_days} days",
                "last_updated": index["meta"]["last_updated"],
            },
            "news": latest_full,
        })
        logger.info(f"  Latest: {len(latest_full)} items")

        # --- Step 4: Update all_news.json (full archive, backward compat) ---
        all_items = []
        seen_all = set()
        for month_file in sorted(self.archive_dir.glob("*.json"), reverse=True):
            month_data = self._read_json(month_file) or []
            for item in month_data:
                if item.get("id") and item["id"] not in seen_all:
                    all_items.append(item)
                    seen_all.add(item["id"])
        self._write_json(self.all_news_file, {
            "meta": index["meta"],
            "news": all_items,
        })
        logger.info(f"  Full archive: {len(all_items)} items")

    @staticmethod
    def _within_days(date_str: str, days: int) -> bool:
        try:
            d = datetime.strptime(date_str[:10], "%Y-%m-%d").date()
            return (datetime.now(timezone.utc).date() - d).days <= days
        except (ValueError, IndexError):
            return False

    def _read_index(self) -> dict:
        """Read existing index.json or return empty."""
        if self.index_file.exists():
            data = self._read_json(self.index_file)
            if data and "ids" in data:
                return data
        return {"meta": {"total_count": 0, "last_updated": ""}, "ids": [], "items": []}

    @staticmethod
    def _read_json(filepath: Path) -> Any:
        if not filepath.exists():
            return None
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return None

    @staticmethod
    def _write_json(filepath: Path, data: Any):
        filepath.parent.mkdir(parents=True, exist_ok=True)
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def write_today_stats(self, items: list[dict[str, Any]],
                          output_path: str | Path | None = None) -> dict:
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

        path = Path(output_path) if output_path else self.data_dir / "today_stats.json"
        self._write_json(path, stats)
        logger.info(f"Stats: {total} total, {backdoor_count} backdoor")
        return stats
