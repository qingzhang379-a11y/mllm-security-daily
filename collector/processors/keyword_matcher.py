"""
Keyword Matcher - Classify news items using keyword rules.
Matches titles and abstracts against backdoor-specific and general security keywords.
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
        self._compiled_backdoor_en: list[re.Pattern] = []
        self._compiled_backdoor_zh: list[re.Pattern] = []
        self._compiled_general_en: list[re.Pattern] = []
        self._compiled_general_zh: list[re.Pattern] = []
        self._load_keywords()

    def _load_keywords(self):
        """Load keyword rules from YAML config."""
        kw_path = self.config_dir / "keywords.yaml"
        if not kw_path.exists():
            logger.warning(f"Keywords file not found: {kw_path}")
            return

        with open(kw_path, "r", encoding="utf-8") as f:
            self.keywords = yaml.safe_load(f) or {}

        # Compile backdoor keywords (case-insensitive)
        for kw in self.keywords.get("backdoor", {}).get("en", []):
            self._compiled_backdoor_en.append(
                re.compile(re.escape(kw), re.IGNORECASE)
            )
        for kw in self.keywords.get("backdoor", {}).get("zh", []):
            self._compiled_backdoor_zh.append(
                re.compile(re.escape(kw))
            )

        # Compile general security keywords
        for kw in self.keywords.get("general", {}).get("en", []):
            self._compiled_general_en.append(
                re.compile(re.escape(kw), re.IGNORECASE)
            )
        for kw in self.keywords.get("general", {}).get("zh", []):
            self._compiled_general_zh.append(
                re.compile(re.escape(kw))
            )

        logger.info(
            f"Loaded keywords: {len(self._compiled_backdoor_en)} backdoor EN, "
            f"{len(self._compiled_backdoor_zh)} backdoor ZH, "
            f"{len(self._compiled_general_en)} general EN, "
            f"{len(self._compiled_general_zh)} general ZH"
        )

    def match(self, item: dict[str, Any]) -> dict[str, Any]:
        """
        Match a single item against keyword rules.
        Modifies item in-place with 'is_backdoor' and 'tags' updated.
        Returns the item.
        """
        title = item.get("title", "")
        abstract = item.get("abstract", "")
        text = f"{title} {abstract}"

        tags = item.get("tags", [])
        if not isinstance(tags, list):
            tags = []

        # Check backdoor keywords first (high priority)
        is_backdoor = self._match_patterns(text, self._compiled_backdoor_en) or \
                      self._match_patterns(text, self._compiled_backdoor_zh)

        if is_backdoor:
            item["is_backdoor"] = True
            if "后门专项" not in tags:
                tags.append("后门专项")
            logger.info(f"  [BACKDOOR] {title[:60]}...")
        else:
            # Check general security keywords
            is_security = self._match_patterns(text, self._compiled_general_en) or \
                          self._match_patterns(text, self._compiled_general_zh)
            if not is_security:
                # Not a security-related item at all -> mark as non-security
                item["is_backdoor"] = False
                # We keep the item but it will be filtered or kept
                # Actually, we keep all items that match at least general keywords
                # If it doesn't match anything, it shouldn't have been collected
                pass
            else:
                item["is_backdoor"] = False

        item["tags"] = tags
        return item

    def batch_match(self, items: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Match all items in a list."""
        matched = []
        for item in items:
            matched.append(self.match(item))
        return matched

    def is_backdoor_related(self, item: dict[str, Any]) -> bool:
        """Quick check if an item is backdoor-related."""
        return item.get("is_backdoor", False)

    @staticmethod
    def _match_patterns(text: str, patterns: list[re.Pattern]) -> bool:
        """Check if text matches any of the compiled patterns."""
        for pattern in patterns:
            if pattern.search(text):
                return True
        return False
