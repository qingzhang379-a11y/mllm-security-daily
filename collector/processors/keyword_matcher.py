"""
Keyword Matcher - Classify and filter news items with a layered keyword system.

分层匹配逻辑（对齐业务方案）:
  层0 准入 (gate):  标题/摘要必须命中第一类 MLLM 限定词（mllm_terms）
  层1 排除 (exclude): 命中排除词 → 直接丢弃（过滤无关噪音）
  层2 标记:
       - 命中第二类后门词 (backdoor)  → is_backdoor=true, 卡片高亮
       - 命中第三/四类通用安全词       → 普通收录, 无后门标签
  结果 is_safe = 通过准入 且 (命中后门 或 通用安全词) 且 未命中排除词

对于 RSS/博客「受信源」(trusted) 放宽准入：因源已手工精选，跳过 MLLM 准入，
仅做排除 + 通用安全匹配。
"""
from __future__ import annotations

import re
from typing import Any, Optional, Union

import yaml
from pathlib import Path

from ..utils.logger import get_logger

logger = get_logger(__name__)


class KeywordMatcher:
    """Match items against layered keyword rules."""

    def __init__(self, config_dir: Union[str, Path]):
        self.config_dir = Path(config_dir)
        self.keywords: dict[str, Any] = {}
        self._compiled: dict[str, list[re.Pattern]] = {}
        self._load_keywords()

    # ---------------------------------------------------------------
    # 加载
    # ---------------------------------------------------------------
    def _compile_list(self, words: list[str], fuzzy: bool) -> list[re.Pattern]:
        """
        编译一组英文+中文关键词。
        fuzzy=True 时英文做模糊匹配（仅小写化，子串即命中），
               反之加单词边界 \b 防子串误匹配。
        中文始终子串匹配。
        """
        pats: list[re.Pattern] = []
        for w in words:
            w = str(w).strip()
            if not w:
                continue
            if w.isascii():
                # 英文词
                if fuzzy:
                    pats.append(re.compile(re.escape(w), re.IGNORECASE))
                else:
                    pats.append(re.compile(rf"\b{re.escape(w)}\b", re.IGNORECASE))
            else:
                # 中文（子串匹配）
                pats.append(re.compile(re.escape(w)))
        return pats

    def _load_keywords(self):
        kw_path = self.config_dir / "keywords.yaml"
        if not kw_path.exists():
            logger.warning(f"Keywords file not found: {kw_path}")
            return

        with open(kw_path, "r", encoding="utf-8") as f:
            self.keywords = yaml.safe_load(f) or {}

        # 五种词表
        self._gate_terms = self._compile_list(
            self.keywords.get("mllm_terms", {}).get("terms", []), fuzzy=True
        )
        self._exclude_terms = self._compile_list(
            self.keywords.get("exclude_terms", {}).get("terms", []), fuzzy=True
        )
        self._backdoor_terms = self._compile_list(
            self.keywords.get("backdoor_terms", {}).get("terms", []), fuzzy=True
        )
        # 通用安全词（攻击/防御/测试/衍生 合并）
        self._general_terms = self._compile_list(
            self.keywords.get("general_terms", {}).get("terms", []), fuzzy=True
        )
        # 兼容旧字段（safety_filter / security / trustworthy / testing / robustness / backdoor）
        legacy = []
        for g in ["safety_filter", "security", "trustworthy", "testing", "robustness"]:
            legacy.extend(self.keywords.get(g, {}).get("en", []))
            legacy.extend(self.keywords.get(g, {}).get("zh", []))
        if legacy:
            self._legacy_general_terms = self._compile_list(legacy, fuzzy=True)
        else:
            self._legacy_general_terms = []
        legacy_backdoor = self.keywords.get("backdoor", {}).get("en", []) + \
            self.keywords.get("backdoor", {}).get("zh", [])
        if legacy_backdoor:
            self._legacy_backdoor_terms = self._compile_list(legacy_backdoor, fuzzy=True)
        else:
            self._legacy_backdoor_terms = []

        logger.info(
            f"Keyword layers: gate={len(self._gate_terms)} "
            f"exclude={len(self._exclude_terms)} "
            f"backdoor={len(self._backdoor_terms)+len(self._legacy_backdoor_terms)} "
            f"general={len(self._general_terms)+len(self._legacy_general_terms)}"
        )

    # ---------------------------------------------------------------
    # 匹配
    # ---------------------------------------------------------------
    def _hit(self, patterns: list[re.Pattern], text: str) -> bool:
        for p in patterns:
            if p.search(text):
                return True
        return False

    def classify(
        self,
        item: dict[str, Any],
        trusted: bool = False,
        need_gate: bool = True,
    ) -> dict[str, Any]:
        """
        分层分类，并附带 item['is_safe']。
        trusted:  受信源（跳过 MLLM 准入）
        need_gate: 是否需要 MLLM 准入限制（普通源需要，受信源可跳过）
        """
        title = str(item.get("title", ""))
        abstract = str(item.get("abstract", ""))
        text = f"{title} {abstract}".lower()

        # 层1 排除：命中任一排除词 → 不安全
        if self._hit(self._exclude_terms, text):
            item["is_safe"] = False
            item["security_tags"] = []
            item["category_tag"] = ""
            item["is_backdoor"] = False
            item["tags"] = list(item.get("tags", []) or [])
            return item

        # ===== 普通源：强制 MLLM 准入 =====
        gate_ok = True
        if need_gate and not trusted:
            gate_ok = self._hit(self._gate_terms, text)

        # ===== 标记层 =====
        backdoor_hit = self._hit(self._backdoor_terms, text) or \
            self._hit(self._legacy_backdoor_terms, text)
        general_hit = self._hit(self._general_terms, text) or \
            self._hit(self._legacy_general_terms, text)

        if not gate_ok:
            # 未过准入，即使有安全词也不收录（除非是受信源）
            item["is_safe"] = False
            item["security_tags"] = []
            item["category_tag"] = ""
            item["is_backdoor"] = False
            item["tags"] = list(item.get("tags", []) or [])
            return item

        # 标签
        tags = list(item.get("tags", []) or [])
        existing = set(tags)
        security_tags = []
        if backdoor_hit:
            security_tags.append("backdoor")
            if "后门专题" not in existing:
                tags.append("后门专题")
                existing.add("后门专题")
        if general_hit:
            security_tags.append("security")
            if "AI安全" not in existing:
                tags.append("AI安全")
                existing.add("AI安全")

        item["tags"] = tags
        item["security_tags"] = security_tags
        item["category_tag"] = security_tags[0] if security_tags else ""
        item["is_backdoor"] = backdoor_hit
        item["is_safe"] = bool(gate_ok and (backdoor_hit or general_hit) and not item.get("is_excluded"))
        return item

    def batch_match(
        self,
        items: list[dict[str, Any]],
        trusted_names: Optional[set[str]] = None,
    ) -> list[dict[str, Any]]:
        """对所有条目分层分类。trusted_names: 受信源名集合（跳过 MLLM 准入）。"""
        matched = []
        for it in items:
            source = it.get("source", "")
            is_trusted = bool(trusted_names) and source in trusted_names
            matched.append(self.classify(it, trusted=is_trusted))
        return matched

    def filter_safe(self, items: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """保留命中安全（且通过准入/排除）的条目。"""
        safe = [i for i in items if i.get("is_safe")]
        dropped = len(items) - len(safe)
        if dropped > 0:
            logger.info(f"Layered safety filter kept {len(safe)}, dropped {dropped}")
        return safe
