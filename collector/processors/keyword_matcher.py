"""
Keyword Matcher - Classify news items using keyword rules.
Matches titles and abstracts against safety-oriented keyword groups.

重构：以安全领域为核心。
- is_safe: 是否命中 safety_filter（准入门槛，用于过滤 RSS/爬虫源）
- category_tag: 命中的安全分类标签（backdoor/security/trustworthy/testing/robustness）
- is_backdoor: 是否后门专题（红色高亮，取自 backdoor 分类）
"""
from __future__ import annotations

import re
from typing import Any, Union

import yaml
from pathlib import Path

from ..utils.logger import get_logger

logger = get_logger(__name__)


class KeywordMatcher:
    """Match items against keyword rules to set category and backdoor flag."""

    def __init__(self, config_dir: Union[str, Path]):
        self.config_dir = Path(config_dir)
        self.keywords: dict[str, Any] = {}
        self._compiled: dict[str, list[re.Pattern]] = {}
        self._load_keywords()

    def _load_keywords(self):
        """Load keyword rules from YAML config."""
        kw_path = self.config_dir / "keywords.yaml"
        if not kw_path.exists():
            logger.warning(f"Keywords file not found: {kw_path}")
            return

        with open(kw_path, "r", encoding="utf-8") as f:
            self.keywords = yaml.safe_load(f) or {}

        # 编译每一类关键词（按语言），全部忽略大小写
        for group_name in ["safety_filter", "backdoor", "security",
                           "trustworthy", "testing", "robustness"]:
            group = self.keywords.get(group_name, {})
            pats: list[re.Pattern] = []
            for kw in group.get("en", []):
                pats.append(re.compile(re.escape(kw), re.IGNORECASE))
            for kw in group.get("zh", []):
                pats.append(re.compile(re.escape(kw)))
            self._compiled[group_name] = pats

        logger.info(
            "Loaded keyword groups: "
            + ", ".join(f"{k}:{len(v)}" for k, v in self._compiled.items())
        )

    def classify(self, item: dict[str, Any]) -> dict[str, Any]:
        """
        对单条 item 进行安全分类（不改变是否入库）。
        设置:
          item['is_safe']       - 是否命中 safety_filter
          item['security_tags'] - 命中的安全分类标签列表
          item['category_tag']  - 主分类标签（优先 backdoor）
          item['is_backdoor']   - 是否后门专题
        """
        title = item.get("title", "")
        abstract = item.get("abstract", "")
        text = f"{title} {abstract}".lower()

        safety_groups = [
            "backdoor", "security", "trustworthy", "testing", "robustness",
        ]

        # 逐类匹配
        hits = []
        for group in safety_groups:
            if self._match_patterns(text, self._compiled.get(group, [])):
                hits.append(group)

        # is_safe = 命中任一具体安全分类（不再由宽泛的 safety_filter 兜底，避免误收录）
        is_safe = bool(hits)

        tags = list(item.get("tags", []) or [])
        # 添加分类标签（去重）
        existing_tags = set(tags)
        for group in hits:
            tag_label = {
                "backdoor": "后门专题",
                "security": "AI安全",
                "trustworthy": "可信性",
                "testing": "AI测试",
                "robustness": "鲁棒性",
            }.get(group)
            if tag_label and tag_label not in existing_tags:
                tags.append(tag_label)
                existing_tags.add(tag_label)

        item["tags"] = tags
        item["is_safe"] = bool(is_safe)
        item["security_tags"] = hits
        item["category_tag"] = hits[0] if hits else ""
        item["is_backdoor"] = "backdoor" in hits
        return item

    def batch_match(self, items: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """对所有条目做安全分类（不改变数量）。"""
        matched = []
        for item in items:
            matched.append(self.classify(item))
        return matched

    def filter_safe(self, items: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """保留命中安全关键词的条目（用于 RSS/爬虫源收窄范围）。"""
        safe = [i for i in items if i.get("is_safe")]
        dropped = len(items) - len(safe)
        if dropped > 0:
            logger.info(f"Safety filter dropped {dropped} unrelated items")
        return safe

    @staticmethod
    def _match_patterns(text: str, patterns: list[re.Pattern]) -> bool:
        """Check if text matches any of the compiled patterns."""
        for pattern in patterns:
            if pattern.search(text):
                return True
        return False
