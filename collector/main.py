"""
MLLM Security Daily - Main Collector Entry Point

Orchestrates the full collection pipeline:
1. Load config & sources
2. Fetch from all enabled sources
3. Match keywords (backdoor / general security)
4. Deduplicate
5. Output structured JSON
6. Log summary stats
"""
from __future__ import annotations

import asyncio
import os
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Union

import yaml

# Add project root to sys.path if running as script
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

# Disable Playwright default download (avoids unnecessary downloads)
os.environ["PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD"] = "1"

from collector.fetchers import ArxivFetcher, RssFetcher, WebScraper
from collector.processors import KeywordMatcher, DedupEngine, JsonOutput
from collector.utils.logger import setup_logger, get_logger

setup_logger(
    name="mllm_collector",
    level="INFO",
    log_file=str(project_root / "collector" / "logs" / "collector.log")
)
logger = get_logger(__name__)


class CollectorOrchestrator:
    """Orchestrates the full daily collection pipeline."""

    def __init__(self, config_dir: Union[str, Path], data_dir: Union[str, Path]):
        self.config_dir = Path(config_dir)
        self.data_dir = Path(data_dir)

        # Load configs
        self.global_config = self._load_yaml("config.yaml")
        self.sources_config = self._load_yaml("sources.yaml")

        # Init processors
        self.keyword_matcher = KeywordMatcher(self.config_dir)
        self.dedup_engine = DedupEngine(self.data_dir, self.global_config)
        self.json_output = JsonOutput(self.global_config)

        # All collected raw items before dedup
        self.all_raw_items: list[dict] = []

    def _load_yaml(self, filename: str) -> dict:
        """Load a YAML config file."""
        path = self.config_dir / filename
        if not path.exists():
            logger.error(f"Config file not found: {path}")
            return {}
        with open(path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f) or {}

    def _export_keywords_snapshot(self):
        """将当前 keywords.yaml 镜像为 docs/data/keywords.json，供前端数据源页展示。
        每次采集前刷新，保证前端看到的词与后端采集一致。"""
        try:
            kw = self.keyword_matcher.keywords

            def _flat(group_name: str) -> list[str]:
                g = kw.get(group_name, {})
                if isinstance(g, dict) and "terms" in g:
                    return list(g.get("terms", []))
                return []

            snapshot = {
                "mllm_terms": {"en": "", "zh": "", "terms": _flat("mllm_terms"),
                               "group": "gist", "label": "MLLM 限定词（准入）"},
                "backdoor_terms": {"en": "", "zh": "", "terms": _flat("backdoor_terms"),
                                   "group": "mark", "label": "后门专项（标记 is_backdoor）"},
                "general_terms": {"en": "", "zh": "", "terms": _flat("general_terms"),
                                  "group": "mark", "label": "通用 MLLM 安全词（普通收录）"},
                "exclude_terms": {"en": "", "zh": "", "terms": _flat("exclude_terms"),
                                  "group": "filter", "label": "排除过滤词"},
                # 旧分组，向前端兼容展示
                "safety_filter": {"en": kw.get("safety_filter", {}).get("en", []),
                                  "zh": kw.get("safety_filter", {}).get("zh", []),
                                  "terms": [], "group": "legacy", "label": "Safety（旧，兼容）"},
            }
            out = {
                "updated_at": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
                "groups": snapshot,
            }
            target = self.data_dir / "keywords.json"
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(
                json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8"
            )
            logger.info("Exported keywords snapshot -> docs/data/keywords.json")
        except Exception as e:
            logger.warning(f"Failed to export keywords snapshot: {e}")

    async def run(self):
        """Execute the full collection pipeline."""
        logger.info("=" * 60)
        logger.info("MLLM Security Daily - Starting collection")
        logger.info("=" * 60)

        # 导出关键词快照供前端展示
        self._export_keywords_snapshot()

        sources = self.sources_config.get("sources", [])
        if not sources:
            logger.error("No sources configured")
            return

        all_items = []

        # Phase 1: Fetch from all sources concurrently
        logger.info(f"\n--- Phase 1: Fetching from {len(sources)} sources ---")
        fetch_tasks = []
        for src in sources:
            fetcher = self._create_fetcher(src)
            if fetcher:
                fetch_tasks.append(self._safe_fetch(fetcher))

        results = await asyncio.gather(*fetch_tasks, return_exceptions=True)

        for result in results:
            if isinstance(result, Exception):
                logger.error(f"Fetch task failed: {result}")
            elif isinstance(result, list):
                all_items.extend(result)

        logger.info(f"Phase 1 complete: {len(all_items)} raw items collected")

        # Apply date filter: only keep items from lookback_days to today
        lookback = self.global_config.get("date_filter", {}).get("lookback_days", 400)
        cutoff_date = (datetime.now(timezone.utc) - timedelta(days=lookback)).strftime("%Y-%m-%d")
        before = len(all_items)
        all_items = [
            i for i in all_items
            if i.get("publish_date", "") and i["publish_date"][:10] >= cutoff_date
        ]
        filtered = before - len(all_items)
        if filtered:
            logger.info(f"Date filter (lookback={lookback}d): dropped {filtered} items older than {cutoff_date}")

        # Phase 2: Keyword matching (classify security / backdoor) + safety filter
        logger.info(f"\n--- Phase 2: Keyword matching ---")
        # 受信源（trusted:true，手工精选的 RSS/博客）跳过 MLLM 准入，
        # 但仍走排除 + 通用安全匹配；arXiv 等全量源需完整分层（准入+排除+安全词）
        trusted_names = {
            s["name"] for s in sources if s.get("trusted")
        }
        matched_items = self.keyword_matcher.batch_match(all_items, trusted_names=trusted_names)

        # 安全过滤：所有源统一走 is_safe（AI 安全/可信主题门槛），
        # 避免无关的通用 AI 内容（agent 框架、普通研究等）混入
        safe_items = [
            item for item in matched_items if item.get("is_safe")
        ]

        backdoor_count = sum(1 for i in safe_items if i.get("is_backdoor"))
        logger.info(f"Phase 2 complete: {len(safe_items)} safe items kept, "
                    f"{backdoor_count} backdoor-related")

        # Phase 3: Deduplication
        logger.info(f"\n--- Phase 3: Deduplication ---")
        new_items = self.dedup_engine.dedup(safe_items)
        logger.info(f"Phase 3 complete: {len(new_items)} new items after dedup")

        if not new_items:
            logger.info("No new items to publish")
            self.json_output.write_today_stats([])
            return

        # Phase 4: Output structured JSON
        logger.info(f"\n--- Phase 4: JSON Output ---")
        self.json_output.write_daily(new_items)
        self.json_output.merge_all(new_items)
        stats = self.json_output.write_today_stats(new_items)

        logger.info(f"\n{'=' * 60}")
        logger.info("Collection complete!")
        logger.info(f"  Total new items: {stats['total_items']}")
        logger.info(f"  Backdoor items:  {stats['backdoor_items']}")
        logger.info(f"  Categories:      {stats['category_breakdown']}")
        logger.info(f"{'=' * 60}")

    def _create_fetcher(self, src_config: dict):
        """Create the appropriate fetcher instance for a source config."""
        src_type = src_config.get("type", "")
        try:
            if src_type == "arxiv_api":
                return ArxivFetcher(src_config, self.global_config)
            elif src_type == "rss":
                return RssFetcher(src_config, self.global_config)
            elif src_type == "web_scrape":
                return WebScraper(src_config, self.global_config)
            else:
                logger.warning(f"Unknown source type: {src_type} for {src_config.get('name')}")
                return None
        except Exception as e:
            logger.error(f"Failed to create fetcher for {src_config.get('name')}: {e}")
            return None

    async def _safe_fetch(self, fetcher) -> list[dict]:
        """Safely fetch from a single fetcher with error handling."""
        try:
            items = await fetcher.fetch()
            # Add source metadata and standardize
            meta = fetcher.get_source_meta()
            standardized = []
            for item in items:
                item.update(meta)
                standardized.append(fetcher.to_standard_item(item))
            return standardized
        except Exception as e:
            logger.error(f"Error fetching from {fetcher.name}: {e}")
            return []


async def main():
    """Entry point."""
    # Determine paths relative to project root
    proj_root = Path(__file__).resolve().parent.parent
    config_dir = proj_root / "collector" / "config"
    data_dir = proj_root / "docs" / "data"

    orchestrator = CollectorOrchestrator(config_dir, data_dir)
    await orchestrator.run()


if __name__ == "__main__":
    asyncio.run(main())
