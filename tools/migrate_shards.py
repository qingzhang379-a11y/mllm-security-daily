"""
One-time migration: rebuild data into monthly shards + index + latest.
"""
from __future__ import annotations

import json
from pathlib import Path
from datetime import datetime, timezone

DATA_DIR = Path("docs/data")
ARCHIVE_DIR = DATA_DIR / "archive"
ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)

# 1. Load existing all_news.json
with open(DATA_DIR / "all_news.json", "r", encoding="utf-8") as f:
    data = json.load(f)

news = data.get("news", [])
print(f"Total items: {len(news)}")

# 2. Build index + monthly shards
index = {"meta": {}, "ids": [], "items": []}
monthly: dict[str, list] = {}

for item in news:
    item_id = item.get("id", "")
    if not item_id:
        continue
    index["ids"].append(item_id)
    index["items"].append({
        "id": item_id,
        "title": item.get("title", ""),
        "publish_date": item.get("publish_date", ""),
        "category": item.get("category", ""),
        "is_backdoor": item.get("is_backdoor", False),
        "source": item.get("source", ""),
    })

    month = (item.get("publish_date") or "unknown")[:7]
    monthly.setdefault(month, []).append(item)

# 3. Write monthly archives
for month, items in sorted(monthly.items()):
    path = ARCHIVE_DIR / f"{month}.json"
    # Sort by date descending within month
    items.sort(key=lambda x: x.get("publish_date", ""), reverse=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(items, f, ensure_ascii=False, indent=2)
    print(f"  Archive {month}: {len(items)} items")

# 4. Write index.json
index["meta"] = {
    "total_count": len(index["ids"]),
    "last_updated": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
}
index["items"].sort(key=lambda x: x.get("publish_date", ""), reverse=True)
with open(DATA_DIR / "index.json", "w", encoding="utf-8") as f:
    json.dump(index, f, ensure_ascii=False, indent=2)
print(f"  Index: {len(index['ids'])} items")

# 5. Write latest.json (last 30 days)
cutoff = datetime.now(timezone.utc).date()
latest_items = []
seen_ids = set()
for item in news:
    pd = item.get("publish_date", "")
    if pd:
        try:
            d = datetime.strptime(pd[:10], "%Y-%m-%d").date()
            if (cutoff - d).days <= 30 and item.get("id") not in seen_ids:
                latest_items.append(item)
                seen_ids.add(item.get("id"))
        except ValueError:
            pass
latest_items.sort(key=lambda x: x.get("publish_date", ""), reverse=True)
with open(DATA_DIR / "latest.json", "w", encoding="utf-8") as f:
    json.dump({"meta": {"total": len(latest_items), "range": "last 30 days"}, "news": latest_items}, f, ensure_ascii=False, indent=2)
print(f"  Latest: {len(latest_items)} items")

print("Done.")
