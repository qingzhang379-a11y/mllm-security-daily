"""根据前端编辑的关键词 JSON，写回 collector/config/keywords.yaml"""
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import yaml

ROOT = Path(__file__).resolve().parents[2]
KW_PATH = ROOT / "collector" / "config" / "keywords.yaml"

GROUPS = ["safety_filter", "backdoor", "security",
          "trustworthy", "testing", "robustness"]


def main():
    raw = os.environ.get("KEYWORDS_JSON", "")
    if not raw:
        print("ERROR: KEYWORDS_JSON env var is empty", file=sys.stderr)
        sys.exit(1)

    try:
        data = json.loads(raw)
    except json.JSONDecodeError as e:
        print(f"ERROR: invalid keywords JSON: {e}", file=sys.stderr)
        sys.exit(1)

    # 只保留我们认识的组，并确保每组有 en/zh 列表
    out = {}
    for g in GROUPS:
        group = data.get(g, {})
        out[g] = {
            "en": [str(w) for w in group.get("en", []) if str(w).strip()],
            "zh": [str(w) for w in group.get("zh", []) if str(w).strip()],
        }

    import datetime
    header = (
        "# ===== 采集关键词（由前端数据源订阅页编辑，经 update_keywords workflow 写回）=====\n"
        f"# 更新时间: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} (UTC)\n"
        "# 每次采集时 KeywordMatcher 按这些词过滤/分类资讯\n\n"
    )

    body = yaml.safe_dump(out, allow_unicode=True, sort_keys=True, default_flow_style=False)

    KW_PATH.write_text(header + body, encoding="utf-8")
    print(f"keywords.yaml written: {KW_PATH}")


if __name__ == "__main__":
    main()
