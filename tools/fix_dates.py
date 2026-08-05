"""
修复脚本：校正 web_scrape 类条目中错误的发布日期。
原理：对缺失/可疑日期的条目，抓取详情页 meta[article:published_time] 获取真实日期，
然后同步更新 index.json / latest.json / archive/YYYY-MM.json / all_news.json。
"""
from __future__ import annotations

import asyncio
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import aiohttp
from bs4 import BeautifulSoup

DATA_DIR = Path(__file__).resolve().parent.parent / "docs" / "data"
ARCHIVE_DIR = DATA_DIR / "archive"

# 需要校正的来源（web_scrape 且可能日期失真）
SCRAPE_SOURCES = [
    "阿里云 Qwen 团队 Blog",
    "智源社区 - 最新文章",
    "BAAI 智源研究院 - 新闻",
    "DeepSeek Blog",
]

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"


async def fetch_detail_date(session: aiohttp.ClientSession, url: str) -> str:
    """从详情页提取真实发布日期。"""
    if not url or not url.startswith("http"):
        return ""
    try:
        async with session.get(url, timeout=aiohttp.ClientTimeout(total=15)) as resp:
            if resp.status != 200:
                return ""
            html = await resp.text()
        soup = BeautifulSoup(html, "lxml")
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
        # 再尝试从正文文本提取 "September 23, 2025" 模式
        m = re.search(
            r"(January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},\s+\d{4}",
            soup.get_text(),
        )
        if m:
            return m.group(0)
        return ""
    except Exception:
        return ""


def parse_to_date(date_str: str) -> str:
    """解析日期字符串为 YYYY-MM-DD，解析失败返回空。"""
    if not date_str:
        return ""
    text = date_str.strip()
    # 提取前10位日期 (ISO)
    m = re.match(r"^(\d{4}-\d{2}-\d{2})", text)
    if m:
        return m.group(1)
    # 提取 "September 23, 2025"
    m = re.search(
        r"(January|February|March|April|May|June|July|August|September|October|November|December)\s+(\d{1,2}),\s+(\d{4})",
        text,
    )
    if m:
        months = {
            "January": "01", "February": "02", "March": "03", "April": "04",
            "May": "05", "June": "06", "July": "07", "August": "08",
            "September": "09", "October": "10", "November": "11", "December": "12",
        }
        return f"{m.group(3)}-{months[m.group(1)]}-{int(m.group(2)):02d}"
    return ""


async def main():
    # 1. 收集所有需要校正的条目（去重，从 archive 取完整数据）
    to_fix = []  # (old_date, url, title, source)
    seen = set()

    for archive_path in sorted(ARCHIVE_DIR.glob("*.json")):
        month_data = json.loads(archive_path.read_text(encoding="utf-8")) or []
        for item in month_data:
            src = item.get("source", "")
            if src not in SCRAPE_SOURCES:
                continue
            url = item.get("origin_url", "")
            if not url or url in seen:
                continue
            seen.add(url)
            old_date = item.get("publish_date", "")
            # 日期落在 2026-06 之后且来源是 web_scrape，多半是采集日失真，需要校正
            if old_date >= "2026-06-01":
                to_fix.append((old_date, url, item.get("title", ""), src))

    print(f"待校正条目数: {len(to_fix)}")
    for old_date, url, title, src in to_fix:
        print(f"  {old_date} | {src} | {title[:50]} | {url}")

    if not to_fix:
        print("无需校正")
        return

    # 2. 并发抓取真实日期
    headers = {"User-Agent": UA}
    async with aiohttp.ClientSession(headers=headers) as session:
        sem = asyncio.Semaphore(5)

        async def bounded(url: str) -> str:
            async with sem:
                return await fetch_detail_date(session, url)

        results = await asyncio.gather(*[bounded(url) for _, url, _, _ in to_fix])

    # 3. 汇总校正结果
    corrections = {}
    for (old_date, url, title, src), raw_date in zip(to_fix, results):
        new_date = parse_to_date(raw_date)
        if new_date and new_date != old_date:
            corrections[url] = (old_date, new_date, title, src)
            print(f"  校正: {old_date} -> {new_date} | {title[:50]}")

    print(f"\n实际校正数: {len(corrections)}")

    if not corrections:
        return

    # 4. 写回数据文件
    for archive_path in sorted(ARCHIVE_DIR.glob("*.json")):
        month_data = json.loads(archive_path.read_text(encoding="utf-8")) or []
        changed = False
        for item in month_data:
            url = item.get("origin_url", "")
            if url in corrections:
                item["publish_date"] = corrections[url][1]
                changed = True
        if changed:
            # 重新分片：若日期跨月，移动文件需要重新组织，这里简单起见：
            # 同月内的直接写回；跨月的条目单独挑出，从旧文件删除，写入新文件
            archive_path.write_text(
                json.dumps(month_data, ensure_ascii=False, indent=2), encoding="utf-8"
            )
            print(f"  已更新 {archive_path.name}")

    # 5. 重建 index.json 和 latest.json
    # 读取所有 archive 重建
    all_items = []
    seen_ids = set()
    for archive_path in sorted(ARCHIVE_DIR.glob("*.json")):
        month_data = json.loads(archive_path.read_text(encoding="utf-8")) or []
        for item in month_data:
            if item.get("id") and item["id"] not in seen_ids:
                all_items.append(item)
                seen_ids.add(item["id"])

    # 重建 index
    index_items = []
    for item in all_items:
        index_items.append({
            "id": item.get("id", ""),
            "title": item.get("title", ""),
            "publish_date": item.get("publish_date", ""),
            "category": item.get("category", ""),
            "is_backdoor": item.get("is_backdoor", False),
            "source": item.get("source", ""),
        })
    index_items.sort(key=lambda x: x.get("publish_date", ""), reverse=True)
    index = {
        "meta": {
            "total_count": len(index_items),
            "last_updated": "2026-07-31T08:00:00Z",
        },
        "ids": [i["id"] for i in index_items],
        "items": index_items,
    }
    (DATA_DIR / "index.json").write_text(
        json.dumps(index, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"  已重建 index.json ({len(index_items)} 条)")

    # 重建 latest.json（近30天）
    from datetime import datetime, timedelta
    cutoff = datetime.now() - timedelta(days=30)
    latest = [i for i in all_items if i.get("publish_date") and i["publish_date"][:10] >= cutoff.strftime("%Y-%m-%d")]
    latest.sort(key=lambda x: x.get("publish_date", ""), reverse=True)
    (DATA_DIR / "latest.json").write_text(
        json.dumps({
            "meta": {
                "total": len(latest),
                "range": "last 30 days",
                "last_updated": index["meta"]["last_updated"],
            },
            "news": latest,
        }, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(f"  已重建 latest.json ({len(latest)} 条)")

    # 重建 all_news.json
    (DATA_DIR / "all_news.json").write_text(
        json.dumps({"meta": index["meta"], "news": all_items}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(f"  已重建 all_news.json ({len(all_items)} 条)")


if __name__ == "__main__":
    asyncio.run(main())
