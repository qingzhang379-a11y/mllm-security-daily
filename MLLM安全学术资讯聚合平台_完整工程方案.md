# MLLM 多模态大模型安全学术资讯自动聚合平台 — 完整工程方案

> 项目定位：面向 MLLM/VLM 后门攻击与防御方向博士的学术非商用项目  
> 技术栈：Python 采集 + GitHub Actions 定时调度 + JSON 轻量存储 + VitePress 静态网页 + GitHub Pages 部署  
> 版本：v1.0 | 2026-07-27

---

## 目录

1. [板块 1：项目完整需求文档](#板块-1项目完整需求文档)
2. [板块 2：数据源清单](#板块-2数据源清单)
3. [板块 3：页面 UI 布局、组件、样式详细设计文档](#板块-3页面-ui-布局组件样式详细设计文档)
4. [板块 4：完整技术架构说明、模块拆分、依赖库清单](#板块-4完整技术架构说明模块拆分依赖库清单)
5. [板块 5：分步开发计划、部署流程、潜在风险规避方案](#板块-5分步开发计划部署流程潜在风险规避方案)

---

# 板块 1：项目完整需求文档

## 1.1 项目背景与定位

多模态大模型（MLLM/VLM）安全领域正处高速发展期，每日涌现大量新论文、技术报告、开源项目与安全公告。当前缺乏一个**专门面向该领域、自动聚合官方信源、区分后门攻击/防御专题**的学术资讯平台。本项目旨在填补这一空白，为从事 MLLM 后门攻击与防御研究的科研人员提供每日自动推送的学术资讯聚合站。

## 1.2 硬性信源规则

采集内容**只收录官方发布内容，拒绝自媒体二次转述资讯**。

### ✅ 允许信源范围

| 类别 | 具体信源 | 说明 |
|------|----------|------|
| arXiv 预印本 | arxiv.org | 通过 arXiv API / RSS 拉取 MLLM 安全相关论文 |
| 顶会官方论文 | ICML / NeurIPS / ICLR / ACL / CVPR / ECCV / AAAI | 通过 proceedings 官方页面或开放论文库采集 |
| 高校/研究院官方博客 | MIT CSAIL, Stanford AI Lab, Berkeley AI Research (BAIR), Max Planck Institute, Oxford VGG, 中科院自动化所, 清华 AI 研究院 | 官方技术博客 |
| 企业官方公告 | OpenAI, Google DeepMind, Meta AI, 阿里巴巴 (Qwen), 腾讯 (混元), 智源研究院 (BAAI), DeepSeek, 百川, 零一万物, 月之暗面 | 官方 Blog、技术报告、白皮书 |
| Hugging Face 官方 | Hugging Face Blog, 官方模型发布公告, Datasets 发布 | 仅官方账号发布 |
| 国内权威学术平台官方首发 | 机器之心（官方首发标签）、智源社区（官方稿件） | 仅标记为"官方"或"首发"的内容 |

### ❌ 排除清单

- 个人博客、个人知乎专栏、个人公众号
- 自媒体转载、解读类内容（如「量子位」转载、「新智元」汇编）
- 论坛讨论帖、Reddit、Twitter/X 非官方账号
- 微信公众号非官方号

### 内容语言支持

- 同时采集中文、英文资讯
- 不限制语言，按原文展示

### 内容范围覆盖

- MLLM/VLM 全方向安全内容（对抗攻击、越狱、安全对齐、隐私、鲁棒性等）
- **对「后门攻击/后门防御」相关成果强制特殊标注和高亮展示**

## 1.3 资讯分类体系

所有采集资讯自动归类至以下四大类型：

| 类型 | 标签 | 说明 |
|------|------|------|
| 学术论文 | `【学术论文】` | arXiv 预印本、顶会正式论文、技术报告 |
| 官方新闻 | `【官方新闻】` | 企业/实验室官方发布、安全白皮书、技术公告 |
| 开源发布 | `【开源发布】` | 官方开源模型、数据集、安全评测基准、攻防代码仓库 |
| 会议动态 | `【会议动态】` | AI 安全顶会征稿通知、录取论文列表、Workshop 官方通知 |

## 1.4 关键词筛选体系

爬虫自动匹配关键词，区分**普通安全资讯**与**后门专项资讯**。

### （1）高优先级：后门专题标签（核心！命中自动高亮标记）

**英文关键词池：**

```
multimodal LLM, MLLM, VLM, vision-language model,
backdoor attack, backdoor defense, trojan model,
data poisoning, trigger, poisoned sample, multimodal backdoor,
visual backdoor, alignment backdoor, backdoor benchmark,
backdoor detection, backdoor mitigation, backdoor removal,
backdoor injection, backdoor trigger inversion
```

**中文关键词池：**

```
多模态大模型、视觉语言模型、后门攻击、后门防御、
特洛伊模型、数据投毒、后门触发器、视觉后门、
对齐后门、后门评测基准、后门检测、后门去除、
后门注入、触发器反转
```

**规则：** 资讯标题或摘要命中以上任意词汇 → 自动打上红色标签 `【后门专项】`，网页前端卡片高亮展示（红色边框 + 醒目标签）。

### （2）普通 MLLM 安全关键词（无特殊高亮，正常收录）

**英文：**
```
adversarial attack, jailbreak, safety alignment, privacy leakage,
robustness, red teaming, multimodal defense, safety guardrail,
adversarial example, prompt injection, safety evaluation,
hallucination, fairness, bias, model security, secure training
```

**中文：**
```
对抗攻击、越狱、安全对齐、隐私泄露、模型鲁棒性、
红蓝对抗、多模态防御、安全护栏、对抗样本、
提示注入、安全评测、幻觉、公平性、偏见、模型安全
```

### 关键词匹配逻辑

```
IF 标题/摘要 匹配 后门关键词集 → is_backdoor = true, 红色高亮
ELSE IF 标题/摘要 匹配 普通安全关键词集 → is_backdoor = false, 正常展示
ELSE → 不收录（非安全相关内容）
```

匹配算法：不区分大小写的子串匹配 + 正则边界匹配，确保匹配准确率。

## 1.5 爬虫执行规则

### 采集策略

| 项目 | 规则 |
|------|------|
| 采集方式 | 优先抓取官方 RSS 源；RSS 不可用时启用轻量 HTTP 爬虫 |
| robots.txt | 严格遵守，配置每个源的爬取延迟 |
| 请求频率 | 同一域名请求间隔 ≥ 3 秒 |
| 去重机制 | 基于 URL + 标题 SHA256 哈希双重去重 |
| 输出格式 | 结构化 JSON 文件 |

### 单条资讯 JSON Schema

```json
{
  "id": "sha256(title + origin_url)[:12]",
  "title": "标题原文",
  "abstract": "摘要预览（前 300 字符）",
  "source": "来源名称（标注是否官方信源）",
  "source_type": "arxiv | conference | blog | official_news | huggingface | opensource",
  "publish_date": "2026-07-27",
  "category": "学术论文 | 官方新闻 | 开源发布 | 会议动态",
  "is_backdoor": true,
  "tags": ["MLLM", "backdoor attack", "data poisoning"],
  "origin_url": "原文链接",
  "pdf_url": "论文PDF链接（如有）",
  "arxiv_id": "2401.xxxxx（论文类填充）",
  "is_today_new": true,
  "created_at": "2026-07-27T08:00:00Z"
}
```

### 定时调度

- GitHub Actions cron 表达式：`0 2 * * *`（每日 UTC 02:00，北京时间 10:00）
- 每次运行产出：`data/news_{YYYY-MM-DD}.json`（当日新增）+ `data/all_news.json`（全量累积）
- 新增资讯标记 `is_today_new: true`

### 降级策略

- 海外源（如 arXiv）访问异常 → 自动切换国内镜像：
  - arXiv 国内镜像：`https://xxx.cn/arxiv`（cn.arXiv.org）
  - Hugging Face 国内镜像：`https://hf-mirror.com`
- 单一信源连续 3 次采集失败 → 跳过该源，记录告警日志

---

# 板块 2：数据源清单

> 以下清单为可直接接入爬虫的官方 RSS 链接与官网采集入口。

## 2.1 arXiv 论文源

通过 arXiv API 按关键词搜索拉取，无需 RSS：

| 采集端点 | 说明 |
|----------|------|
| `http://export.arxiv.org/api/query?search_query=all:multimodal+AND+all:backdoor&start=0&max_results=100&sortBy=submittedDate&sortOrder=descending` | MLLM+后门专题主查询 |
| `http://export.arxiv.org/api/query?search_query=all:multimodal+AND+all:safety&start=0&max_results=100&sortBy=submittedDate&sortOrder=descending` | MLLM 安全综合查询 |
| `http://export.arxiv.org/api/query?search_query=all:vision-language+AND+all:backdoor&start=0&max_results=100&sortBy=submittedDate&sortOrder=descending` | VLM+后门补充查询 |
| `http://export.arxiv.org/api/query?search_query=all:VLM+AND+all:adversarial&start=0&max_results=100&sortBy=submittedDate&sortOrder=descending` | VLM 对抗安全查询 |
| `http://export.arxiv.org/api/query?search_query=all:multimodal+AND+all:jailbreak&start=0&max_results=100&sortBy=submittedDate&sortOrder=descending` | MLLM 越狱安全查询 |
| arXiv 国内镜像：`https://cn.arxiv.org/api/query?...`（降级用） | |

**arXiv API 说明：**
- 最大每次 100 条，支持分页（`start=0,100,200...`）
- 返回 XML 格式，用 feedparser 解析
- 自动提取：title, summary, published, link, pdf_link, arxiv_id, category

## 2.2 企业/实验室官方 Blog RSS 源

| 来源 | RSS/Feed 地址 | 类型 |
|------|---------------|------|
| **OpenAI Blog** | `https://openai.com/blog/news.xml` | Official News |
| **Google DeepMind Blog** | `https://deepmind.google/blog/rss/` | Official News |
| **Meta AI Blog** | `https://ai.meta.com/blog/rss/` | Official News |
| **Meta Research** | `https://research.facebook.com/blog/rss/` | Official News |
| **Microsoft Research** | `https://www.microsoft.com/en-us/research/feed/` | Official News |
| **Google AI Blog** | `https://ai.googleblog.com/rss/` | Official News |
| **Anthropic Blog** | `https://www.anthropic.com/feed.xml` (需确认) | Official News |
| **Hugging Face Blog** | `https://huggingface.co/blog/feed.xml` | OpenSource |
| **Hugging Face Papers** | `https://huggingface.co/papers/feed` | Academic |
| **BAAI 智源研究院** | `https://www.baai.ac.cn/portal/list/index/id/3.html`（需爬虫） | Official News |
| **DeepSeek Blog** | 需在官方部署后确认 RSS（如无则爬虫采集） | Official News |
| **阿里巴巴 Qwen 团队** | `https://qwenlm.github.io/blog/`（爬虫采集） | Official News |
| **腾讯混元** | 官方技术公告页面（爬虫采集） | Official News |
| **月之暗面 Moonshot** | 官方 Blog（爬虫采集） | Official News |
| **百川智能** | 官方 Blog（爬虫采集） | Official News |

## 2.3 顶会官方论文源

| 会议 | 采集来源 | 备注 |
|------|----------|------|
| **CVPR** | `https://cvpr.thecvf.com/Conferences/20XX/AcceptedPapers` | 每年会议结束后更新 |
| **ICCV** | `https://iccv.thecvf.com/Conferences/20XX/AcceptedPapers` | 同上 |
| **ECCV** | `https://eccv.ecva.net/Conferences/20XX/AcceptedPapers` | 同上 |
| **NeurIPS** | `https://papers.nips.cc/` | proceedings 页面 |
| **ICML** | `https://icml.cc/Conferences/20XX/AcceptedPapers` | proceedings 页面 |
| **ICLR** | `https://openreview.net/group?id=ICLR.cc/20XX/Conference` | OpenReview |
| **ACL** | `https://aclanthology.org/` | ACL Anthology |
| **AAAI** | `https://aaai.org/Conferences/AAAI-20XX/accepted-papers/` | accepted papers 页面 |
| **ACM CCS / S&P / USENIX Security** | 安全四大顶会论文列表 | 安全领域交叉参考 |

顶会论文采集方式：通过 proceedings 页面爬取论文标题 + 作者 + PDF 链接，再通过 arXiv API 补充摘要。

## 2.4 国内权威学术平台官方源

| 平台 | 采集方式 | 说明 |
|------|----------|------|
| **机器之心** | 官方 RSS / 网站爬虫（仅采集标记为"官方首发"或"原创"的内容） | `https://www.jiqizhixin.com/` |
| **智源社区** | 官方页面采集（仅官方稿件） | `https://hub.baai.ac.cn/` |
| **PaperWeekly** | 仅官方发布的论文解读 | `https://www.paperweekly.site/` |

> 注意：国内平台内容需严格甄别是否为官方首发，排除自媒体转载。

## 2.5 安全会议/Workshop 动态

| 事件 | 采集来源 |
|------|----------|
| **NeurIPS Workshop on Security in AI** | 官方 Call for Papers 页面 |
| **ICML Workshop on AI Safety** | 官方 Call for Papers 页面 |
| **CVPR Workshop on Adversarial Machine Learning** | 官方页面 |
| **BlackHat AI Security Track** | 官方公告页面 |
| **IEEE S&P AI Security Workshop** | 官方页面 |

## 2.6 数据源配置化设计

所有信源配置统一存储在 `sources.yaml` 或 `sources.json` 文件中，新增数据源仅需添加配置条目，无需修改爬虫核心代码。

```yaml
sources:
  - name: "arXiv MLLM-Backdoor Query"
    type: "arxiv_api"
    endpoint: "http://export.arxiv.org/api/query"
    params:
      search_query: "all:multimodal+AND+all:backdoor"
      max_results: 100
    interval: 3
    enabled: true
    
  - name: "OpenAI Blog"
    type: "rss"
    feed_url: "https://openai.com/blog/news.xml"
    interval: 5
    enabled: true
    
  - name: "BAAI 智源研究院"
    type: "web_scrape"
    page_url: "https://www.baai.ac.cn/portal/list/index/id/3.html"
    interval: 10
    enabled: true
    selector:
      title: ".article-title a"
      link: ".article-title a@href"
      date: ".article-date"
```

---

# 板块 3：页面 UI 布局、组件、样式详细设计文档

## 3.1 整体设计语言

| 设计维度 | 规范 |
|----------|------|
| 风格 | 简约学术风，低动画干扰，适配科研人员长时间阅读 |
| 主色调 | 深蓝 `#1a365d` + 白色 `#ffffff` |
| 辅色 | 浅蓝 `#ebf4ff`、灰色 `#f7f7f7` |
| 后门高亮色 | 红色边框 `#e53e3e`，红色标签 `【后门专项】` 背景色 `#fff5f5` |
| 字体 | 系统字体栈：`-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Noto Sans SC", sans-serif` |
| 字号基础 | 16px，行高 1.6 |
| 暗色模式 | 支持 Tailwind `dark` class 切换 |
| 响应式 | 移动端自适应（≥320px），桌面端 ≥ 1024px |
| 动画 | 仅 hover 过渡效果（0.2s ease），无侵入性动画 |

## 3.2 导航栏（全局组件）

```
┌──────────────────────────────────────────────────────────────┐
│  🔬 MLLM安全日报    首页 │ 每日日报 │ 月度汇总 │ ⚠️后门专题 │ 检索 🔍 │ 数据源说明 │
│                                                            │
│  最近更新: 2026-07-27 10:00  │  今日资讯 23 条  │  后门专项 7 条  │
└──────────────────────────────────────────────────────────────┘
```

**规范：**
- 固定顶部，滚动时吸顶（sticky header）
- 导航项：首页 | 每日日报 | 月度汇总 | 后门专题 | 数据源说明
- 检索框位于导航右侧，实时搜索过滤
- 状态栏显示：最后更新时间、今日资讯总量、后门专项数量
- 右上角暗色模式切换按钮（🌙/☀️）

## 3.3 首页（页面 1）

### 3.3.1 布局结构

```
┌──────────────────────────────────────────────────────────────┐
│  筛选栏                                                      │
│  [关键词搜索框____________]  [类型▼全选]  [仅后门专项◻]  [排序▼最新] │
├──────────────────────────────────────────────────────────────┤
│  资讯卡片列表                                                │
│  ┌──────────────────────────────────────────────────────────┐│
│  │ [学术论文] 2026-07-27                                    ││
│  │ ⚠️【后门专项】Backdoor Attacks on Multimodal LLMs...    ││
│  │ ── 红色边框 ──                                          ││
│  │ 摘要: This paper investigates...                         ││
│  │ arXiv: 2407.xxxxx  [📄 PDF]  [🔗 原文]                  ││
│  └──────────────────────────────────────────────────────────┘│
│  ┌──────────────────────────────────────────────────────────┐│
│  │ [官方新闻] 2026-07-26                                    ││
│  │ OpenAI发布最新安全对齐技术报告...                         ││
│  │ 摘要: ...                                                ││
│  │ [🔗 原文]                                                ││
│  └──────────────────────────────────────────────────────────┘│
│  ┌──────────────────────────────────────────────────────────┐│
│  │ [开源发布] 2026-07-25                                    ││
│  │ ⚠️【后门专项】SafeUnlearning: 多模态后门防御框架开源     ││
│  │ arXiv: 2407.xxxxx  [📄 PDF]  [🔗 GitHub]                ││
│  └──────────────────────────────────────────────────────────┘│
│                                                              │
│  [← 上一页]  1  2  3  4  5 ...  [下一页 →]                  │
└──────────────────────────────────────────────────────────────┘
```

### 3.3.2 卡片组件设计

**普通资讯卡片：**
```
┌──────────────────────────────────┐
│ [类型标签]  发布日期              │
│ 标题文本（可点击，新标签页打开） │
│ 摘要预览（最多 3 行，hover 展开）│
│ ──────────────────────────────── │
│ 来源名称    [原文链接]           │
│ （论文类额外显示：[arXiv编号] PDF）│
└──────────────────────────────────┘
```

**后门专项资讯卡片（特殊样式）：**
```
┌──── 红色左边框 3px ──────────────┐
│ [类型标签]  ⚠️【后门专项】 发布日期│
│ 标题文本                          │
│ 摘要预览                          │
│ ──────────────────────────────── │
│ 来源名称    [原文链接]           │
│ [arXiv编号]  [PDF]               │
└──────────────────────────────────┘
```

**CSS 规范：**
```css
.card {
  background: #ffffff;
  border-radius: 8px;
  padding: 16px 20px;
  margin-bottom: 12px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.08);
  transition: box-shadow 0.2s ease;
}
.card:hover {
  box-shadow: 0 2px 8px rgba(0,0,0,0.12);
}
.card-backdoor {
  border-left: 3px solid #e53e3e;
  background: #fff5f5;
}
.tag-backdoor {
  display: inline-block;
  background: #e53e3e;
  color: #ffffff;
  font-size: 12px;
  font-weight: 700;
  padding: 2px 8px;
  border-radius: 4px;
}
.tag-category {
  display: inline-block;
  background: #ebf4ff;
  color: #1a365d;
  font-size: 12px;
  padding: 2px 8px;
  border-radius: 4px;
}
```

### 3.3.3 筛选栏交互

| 控件 | 功能 | 交互 |
|------|------|------|
| 关键词搜索框 | 输入关键词实时过滤标题/摘要 | 防抖 300ms，无结果时显示"未找到匹配资讯" |
| 资讯类型下拉 | 全选 / 学术论文 / 官方新闻 / 开源发布 / 会议动态 | 多选 |
| 仅后门专项复选框 | 勾选后只展示 is_backdoor=true 的资讯 | 立即过滤 |
| 排序方式 | 按发布时间倒序（默认）/ 按相关度 | 切换即时刷新 |

### 3.3.4 空状态

- 搜索无结果：显示「未找到匹配的资讯，请尝试其他关键词」
- 某日无资讯：显示「该日期暂无采集记录，可能为周末或节假日」
- 加载中：骨架屏（Skeleton loading）

## 3.4 每日日报归档页（页面 2）

### 3.4.1 布局结构

```
┌──────────────────────────────────────────────────────────────┐
│  每日日报归档                                                │
│  [日期选择器: 2026-07-27 ▼]  [📋 复制日报]                  │
├──────────────────────────────────────────────────────────────┤
│  ┌──────────────────────────────────────────────────────────┐│
│  │  2026年7月27日 星期一  共 23 条资讯                      ││
│  │                                                          ││
│  │  📌 后门专项资讯（7条）                                  ││
│  │  ┌─ 卡片列表 ──────────────────────────────────────────┐│
│  │  │ ...后门高亮卡片...                                    ││
│  │  └──────────────────────────────────────────────────────┘│
│  │                                                          ││
│  │  📋 普通安全资讯（16条）                                 ││
│  │  ┌─ 卡片列表 ──────────────────────────────────────────┐│
│  │  │ ...普通卡片...                                        ││
│  │  └──────────────────────────────────────────────────────┘│
│  └──────────────────────────────────────────────────────────┘│
└──────────────────────────────────────────────────────────────┘
```

### 3.4.2 功能详细设计

- **日期选择器**：日历组件，支持选择任意日期，默认当天
- **分组展示**：当日资讯按「后门专项资讯」「普通安全资讯」分组，每组带计数
- **复制日报**：点击「复制日报」按钮，生成纯文本格式的日报摘要，自动复制到剪贴板

**复制的日报文本格式示例：**
```
MLLM 安全日报 - 2026-07-27
========================
总计 23 条资讯 | 后门专项 7 条

【后门专项】
1. [学术论文] Backdoor Attacks on Multimodal LLMs
   arXiv:2407.xxxxx | https://arxiv.org/abs/2407.xxxxx

2. [开源发布] SafeUnlearning: 多模态后门防御框架
   https://github.com/xxx/safe-unlearning

【普通安全资讯】
1. [官方新闻] OpenAI 发布安全对齐技术报告
   https://openai.com/blog/...

...
```

## 3.5 月度汇总页（页面 3）

### 3.5.1 布局结构

```
┌──────────────────────────────────────────────────────────────┐
│  月度汇总                                                    │
│  [月份选择器: 2026年7月 ▼]                                  │
├──────────────────────────────────────────────────────────────┤
│  统计数据面板                                                │
│  ┌──────┐  ┌──────┐  ┌──────┐  ┌──────┐                    │
│  │ 总资讯 │  │ 论文数 │  │ 开源数 │  │后门文献│               │
│  │  156  │  │  89  │  │  23  │  │  34  │                    │
│  └──────┘  └──────┘  └──────┘  └──────┘                    │
├──────────────────────────────────────────────────────────────┤
│  ┌──────────────────────────────────────────────────────────┐│
│  │  7月1日（3条）                                          ││
│  │  ┌─ 卡片 ─────────────────────────────────────────────┐ ││
│  │  │ ...                                                │ ││
│  │  └────────────────────────────────────────────────────┘ ││
│  │  7月2日（5条）                                         ││
│  │  ...                                                   ││
│  └──────────────────────────────────────────────────────────┘│
└──────────────────────────────────────────────────────────────┘
```

### 3.5.2 统计指标卡

```vue
<StatCard
  title="当月资讯总数"
  value="156"
  icon="📰"
  color="blue"
/>
<StatCard
  title="论文数量"
  value="89"
  icon="📄"
  color="green"
/>
<StatCard
  title="开源项目"
  value="23"
  icon="📦"
  color="purple"
/>
<StatCard
  title="后门相关文献"
  value="34"
  icon="⚠️"
  color="red"
/>
```

## 3.6 后门专题合集页（页面 4 — 核心页面）

### 3.6.1 布局结构

```
┌──────────────────────────────────────────────────────────────┐
│  ⚠️ MLLM 后门攻击与防御专题合集                               │
│                                                              │
│  子筛选: [全部 ▼]  [攻击方向 ▼]  [防御方向 ▼]  [论文 ▼/开源 ▼] │
│                                                              │
│  共收录 127 篇后门专项文献（持续更新中）                      │
├──────────────────────────────────────────────────────────────┤
│  ┌─ 卡片列表（仅展示 is_backdoor=true 的资讯）─────────────┐│
│  │ ...                                                      ││
│  └──────────────────────────────────────────────────────────┘│
└──────────────────────────────────────────────────────────────┘
```

### 3.6.2 子筛选分类体系

**攻击方向标签：**
- 后门注入（Backdoor Injection）
- 数据投毒（Data Poisoning）
- 视觉触发器（Visual Trigger）
- 文本触发器（Text Trigger）
- 对齐后门（Alignment Backdoor）
- 多模态融合后门（Multimodal Fusion Backdoor）

**防御方向标签：**
- 后门检测（Backdoor Detection）
- 后门移除（Backdoor Removal）
- 安全训练（Secure Training）
- 触发器反转（Trigger Inversion）
- 模型净化（Model Purification）

### 3.6.3 专题统计信息

- 后门相关论文总数
- 按年份分布柱状图（ECharts 轻量图）
- 按攻击/防御方向分类统计
- 近 7 天新增后门论文数量

## 3.7 数据源说明页

```
┌──────────────────────────────────────────────────────────────┐
│  数据源说明                                                  │
│                                                              │
│  本平台所有内容均采集自以下官方信源：                        │
│                                                              │
│  📄 学术论文源（5个）                                        │
│  • arXiv API (MLLM+Backdoor 关键词查询)                     │
│  • ...                                                       │
│                                                              │
│  🏢 企业官方 Blog（12个）                                    │
│  • OpenAI Blog, Google DeepMind Blog, ...                   │
│                                                              │
│  📰 国内学术平台（2个）                                      │
│  • 机器之心（官方首发）、智源社区（官方稿件）                │
│                                                              │
│  ⚙️ 采集规则说明                                             │
│  • 采集频率: 每日 UTC 02:00                                  │
│  • 去重机制: URL + 标题双重哈希                              │
│  • 关键词匹配: 自动分类普通安全 / 后门专项                   │
└──────────────────────────────────────────────────────────────┘
```

## 3.8 暗色模式

- 基于 CSS 变量 + `prefers-color-scheme` 自动检测 + 手动切换
- 暗色模式调色板：

| 用途 | 亮色 | 暗色 |
|------|------|------|
| 背景 | `#ffffff` | `#1a202c` |
| 卡片背景 | `#ffffff` | `#2d3748` |
| 主文字 | `#1a202c` | `#e2e8f0` |
| 副文字 | `#718096` | `#a0aec0` |
| 主色调 | `#1a365d` | `#2b6cb0` |
| 卡片阴影 | `rgba(0,0,0,0.08)` | `rgba(0,0,0,0.3)` |
| 后门卡片背景 | `#fff5f5` | `#3d1f1f` |

## 3.9 移动端自适应规则

| 断点 | 布局调整 |
|------|----------|
| ≥ 1024px | 桌面端全宽布局，最大宽度 1200px 居中 |
| 768px - 1023px | 平板，卡片 2 列网格，导航折叠为汉堡菜单 |
| < 768px | 手机，卡片单列，筛选栏折叠可展开，导航底部 Tab |

## 3.10 RSS 订阅链接

- 全站 RSS: `https://<username>.github.io/mllm-security-daily/rss.xml`
- 后门专题 RSS: `https://<username>.github.io/mllm-security-daily/rss-backdoor.xml`
- 由 VitePress 生成或构建脚本生成

---

# 板块 4：完整技术架构说明、模块拆分、依赖库清单

## 4.1 整体技术栈

```
┌─────────────────────────────────────────────────────────────┐
│                      GitHub Pages                           │
│              https://<user>.github.io/mllm-security-daily/   │
├─────────────────────────────────────────────────────────────┤
│                     VitePress 静态网页                        │
│    Vue 3 组件渲染 JSON 数据  │  学术风格 CSS  │  交互筛选    │
├─────────────────────────────────────────────────────────────┤
│                    JSON 数据层                               │
│   data/all_news.json  │  data/news_YYYY-MM-DD.json          │
├─────────────────────────────────────────────────────────────┤
│               GitHub Actions 定时调度                        │
│   cron: 0 2 * * *  │  Python 采集脚本执行                    │
├─────────────────────────────────────────────────────────────┤
│                    Python 采集层                              │
│  RSS Fetcher  │  Web Scraper  │  ArXiv API  │  关键词引擎   │
├─────────────────────────────────────────────────────────────┤
│                   数据源配置层                                │
│   sources.yaml  │  keywords.yaml  │  config.yaml             │
└─────────────────────────────────────────────────────────────┘
```

## 4.2 完整运行链路

```
GitHub Actions Trigger (每日 UTC 02:00)
    │
    ▼
Step 1: Checkout 代码仓库
    │
    ▼
Step 2: 设置 Python 3.10 环境
    │
    ▼
Step 3: pip install -r requirements.txt
    │
    ▼
Step 4: 运行主采集脚本
    ├── arxiv_fetcher.py      → 从 arXiv API 拉取最新论文
    ├── rss_fetcher.py        → 从 RSS 源拉取 Blog 更新
    ├── web_scraper.py        → 从无 RSS 官方页面爬取
    ├── dedup_engine.py       → 基于 URL+标题哈希去重
    ├── keyword_matcher.py    → 关键词分类（普通/后门专项）
    └── json_output.py        → 生成 JSON 数据文件
    │
    ▼
Step 5: git commit + push JSON 数据
    │
    ▼
Step 6: 触发 VitePress 重新构建
    │
    ▼
Step 7: 部署到 gh-pages 分支
    │
    ▼
GitHub Pages 自动更新上线
```

## 4.3 模块拆分详情

### 4.3.1 采集层模块（Python）

```
collector/
├── __init__.py
├── main.py                  # 主入口，编排所有采集流程
├── config/
│   ├── __init__.py
│   ├── sources.yaml          # 数据源配置
│   ├── keywords.yaml         # 关键词配置（后门 + 普通安全）
│   └── config.yaml           # 全局配置（请求延时、输出路径等）
├── fetchers/
│   ├── __init__.py
│   ├── base_fetcher.py       # 采集器基类（请求控制、错误重试）
│   ├── arxiv_fetcher.py      # arXiv API 采集器
│   ├── rss_fetcher.py        # RSS/Atom 源采集器
│   └── web_scraper.py        # 轻量网页爬虫（requests + BeautifulSoup）
├── processors/
│   ├── __init__.py
│   ├── dedup_engine.py       # 去重引擎（基于 URL + 标题哈希）
│   ├── keyword_matcher.py    # 关键词匹配分类器
│   └── json_output.py        # JSON 输出格式化
├── utils/
│   ├── __init__.py
│   ├── network.py            # 网络工具（代理配置、请求重试、国内镜像切换）
│   ├── time_utils.py         # 时间处理工具
│   └── logger.py             # 日志记录
└── requirements.txt          # Python 依赖清单
```

### 4.3.2 前端层模块（VitePress）

```
docs/
├── .vitepress/
│   ├── config.ts             # VitePress 站点配置
│   ├── theme/
│   │   ├── index.ts          # 主题入口
│   │   ├── custom.css        # 全局自定义样式（学术风）
│   │   └── components/
│   │       ├── NewsCard.vue          # 资讯卡片组件
│   │       ├── BackdoorCard.vue      # 后门高亮卡片组件
│   │       ├── FilterBar.vue         # 筛选栏组件
│   │       ├── DatePicker.vue        # 日期选择器
│   │       ├── StatCard.vue          # 统计卡片组件
│   │       ├── Pagination.vue        # 分页组件
│   │       ├── SearchBox.vue         # 搜索框组件
│   │       ├── DarkModeToggle.vue    # 暗色模式切换
│   │       ├── CopyReport.vue        # 复制日报功能
│   │       └── NavBar.vue            # 导航栏组件
│   └── public/
│       └── favicon.ico
├── index.md                  # 首页（读取 all_news.json）
├── daily.md                  # 每日日报归档页
├── monthly.md                # 月度汇总页
├── backdoor.md               # 后门专题合集页
├── sources.md                # 数据源说明页
├── rss.xml                   # RSS 订阅文件（构建时生成）
└── data/                     # JSON 数据目录（由采集脚本生成）
    ├── all_news.json
    └── news_2026-07-27.json
```

### 4.3.3 GitHub Actions 工作流

```
.github/
└── workflows/
    ├── daily_collect.yml     # 每日定时采集 + 部署
    └── manual_collect.yml    # 手动触发采集（可选）
```

## 4.4 全部依赖库清单

### Python 采集端依赖（requirements.txt）

```txt
# HTTP 请求与解析
aiohttp>=3.9.0
requests>=2.31.0
feedparser>=6.0.10
beautifulsoup4>=4.12.0
lxml>=4.9.0

# 轻量浏览器自动化（备用，仅用于少量无 API 站点）
playwright>=1.40.0

# 数据序列化
pyyaml>=6.0
orjson>=3.9.0

# 调试与工具
apscheduler>=3.10.0  # 本地调试用定时任务
pytest>=7.4.0
pytest-asyncio>=0.21.0

# 类型检查
types-requests>=2.31.0
```

### 前端 VitePress 依赖

```json
{
  "devDependencies": {
    "vitepress": "^1.3.0",
    "vue": "^3.4.0",
    "typescript": "^5.3.0"
  },
  "dependencies": {
    "date-fns": "^3.6.0",
    "lodash-es": "^4.17.0"
  }
}
```

## 4.5 工具链版本

| 工具 | 版本要求 | 说明 |
|------|----------|------|
| Python | ≥ 3.10 | 采集脚本运行环境 |
| Node.js | ≥ 18.0 | VitePress 构建环境 |
| GitHub Actions Runner | ubuntu-latest | 云端执行环境 |
| Playwright 浏览器 | chromium | 仅用于无 API 的站点 |

---

# 板块 5：分步开发计划、部署流程、潜在风险规避方案

## 5.1 开发阶段划分（总工期预估：3-4 周）

### Phase 1：本地采集脚本开发（第 1 周）

| 序号 | 任务 | 产出 | 预计工时 |
|------|------|------|----------|
| 1.1 | 项目初始化，创建目录结构 | 仓库骨架 | 0.5天 |
| 1.2 | 实现 `config.yaml` 配置加载、日志模块 | 配置系统 | 0.5天 |
| 1.3 | 实现 `arxiv_fetcher.py`（arXiv API 调用 + 解析） | arXiv 采集器 | 1天 |
| 1.4 | 实现 `rss_fetcher.py`（RSS/Atom 源抓取） | RSS 采集器 | 1天 |
| 1.5 | 实现 `web_scraper.py`（轻量静态爬虫） | Web 采集器 | 1天 |
| 1.6 | 实现 `keyword_matcher.py`（关键词分类引擎） | 分类器 | 0.5天 |
| 1.7 | 实现 `dedup_engine.py`（去重引擎） | 去重器 | 0.5天 |
| 1.8 | 实现 `json_output.py`（JSON 输出格式化） | 输出模块 | 0.5天 |
| 1.9 | 实现 `main.py` 主流程编排 | 完整采集流程 | 1天 |
| 1.10 | 本地调试：运行采集脚本，检查 JSON 输出 | 验证通过 | 1天 |

**检查点 1：** 本地运行 `python collector/main.py` 能成功输出 `data/all_news.json`，包含来自至少 3 个不同源的真实资讯。

### Phase 2：VitePress 前端开发（第 2 周）

| 序号 | 任务 | 产出 | 预计工时 |
|------|------|------|----------|
| 2.1 | 初始化 VitePress 项目，配置主题 | 基础站点 | 0.5天 |
| 2.2 | 实现 `NavBar.vue` 导航栏 + 状态栏 | 导航组件 | 0.5天 |
| 2.3 | 实现 `NewsCard.vue` + `BackdoorCard.vue` 卡片组件 | 卡片组件 | 1天 |
| 2.4 | 实现 `FilterBar.vue` + `SearchBox.vue` 筛选组件 | 筛选组件 | 0.5天 |
| 2.5 | 实现 `Pagination.vue` 分页组件 | 分页组件 | 0.5天 |
| 2.6 | 搭建首页 `index.md`，读取 JSON 渲染卡片列表 | 首页完成 | 0.5天 |
| 2.7 | 搭建每日日报页 `daily.md` + 日期选择器 + 复制日报 | 日报页完成 | 1天 |
| 2.8 | 搭建月度汇总页 `monthly.md` + 统计卡片 | 月报页完成 | 0.5天 |
| 2.9 | 搭建后门专题合集页 `backdoor.md` + 子筛选 | 专题页完成 | 0.5天 |
| 2.10 | 实现暗色模式切换、移动端自适应 | 响应式适配 | 0.5天 |
| 2.11 | 实现数据源说明页 + RSS 生成 | 辅助页面 | 0.5天 |
| 2.12 | 本地集成测试：JSON 数据 → 页面渲染 | 验证通过 | 0.5天 |

**检查点 2：** `npm run docs:dev` 本地启动，所有页面功能正常，筛选/搜索/分页可用，后门高亮正确。

### Phase 3：GitHub Actions 配置与部署（第 3 周初）

| 序号 | 任务 | 产出 | 预计工时 |
|------|------|------|----------|
| 3.1 | 创建 GitHub 仓库，推送全部代码 | 远程仓库 | 0.5天 |
| 3.2 | 配置 GitHub Actions secret（无敏感信息，可跳过） | — | — |
| 3.3 | 编写 `daily_collect.yml` 工作流 | CI 配置 | 1天 |
| 3.4 | 编写 `manual_collect.yml` 手动工作流 | CI 配置 | 0.5天 |
| 3.5 | 配置 GitHub Pages（gh-pages 分支） | Pages 启用 | 0.25天 |
| 3.6 | 首次完整运行测试：Action → 采集 → Build → Deploy | 全链路验证 | 0.5天 |
| 3.7 | 验证国内可访问性（通过 GitHub Pages 域名） | 访问验证 | 0.25天 |

**检查点 3：** 触发一次手动 Action，观察完整链路，确认 `https://<user>.github.io/mllm-security-daily/` 可正常访问。

### Phase 4：数据源扩展与优化（第 3 周后半）

| 序号 | 任务 | 产出 | 预计工时 |
|------|------|------|----------|
| 4.1 | 扩展 arXiv 查询关键词覆盖范围 | 更多论文召回 | 0.5天 |
| 4.2 | 接入更多企业 Blog RSS 源 | 源扩展 | 0.5天 |
| 4.3 | 实现国内源爬虫（机器之心、智源社区） | 国内源接入 | 1天 |
| 4.4 | 优化关键词匹配精度（减少误报） | 匹配优化 | 0.5天 |
| 4.5 | 实现缓存机制，避免重复请求相同页面 | 缓存层 | 0.5天 |

### Phase 5：打磨与上线（第 4 周）

| 序号 | 任务 | 产出 | 预计工时 |
|------|------|------|----------|
| 5.1 | 错误处理与告警日志完善 | 稳定性提升 | 0.5天 |
| 5.2 | 降级策略实现与测试（国内镜像切换） | 降级能力 | 0.5天 |
| 5.3 | 前端交互体验打磨（加载状态、空状态） | UX 优化 | 0.5天 |
| 5.4 | 性能优化（JSON 分片、懒加载） | 性能提升 | 0.5天 |
| 5.5 | 文档完善（数据源说明、配置指南） | 文档 | 0.5天 |
| 5.6 | 全面上线监控运行一周 | 稳定运行 | 持续 |

## 5.2 部署流程

### 首次部署步骤

1. **创建 GitHub 仓库**
   ```bash
   # 在 GitHub 上创建新仓库 mllm-security-daily
   # 本地初始化
   git init
   git add .
   git commit -m "Initial commit: MLLM security daily aggregator"
   git branch -M main
   git remote add origin https://github.com/<username>/mllm-security-daily.git
   git push -u origin main
   ```

2. **配置 GitHub Pages**
   - 仓库 Settings → Pages → Source: Deploy from branch
   - Branch: `gh-pages` / root
   - 第一次部署由 Action 自动推送 gh-pages 分支

3. **配置 GitHub Actions**
   - 推送后 Action 自动识别 `.github/workflows/daily_collect.yml`
   - 手动触发一次验证全链路

4. **验证访问**
   - 打开 `https://<username>.github.io/mllm-security-daily/`
   - 确认样式、数据、交互正常

### 日常维护

- **数据更新**：Actions 每日自动执行，无需人工干预
- **新增数据源**：编辑 `sources.yaml`，添加新 RSS/API 配置，提交即可
- **关键词调整**：编辑 `keywords.yaml`，添加/修改关键词
- **故障排查**：查看 Actions 运行日志 → `collector/utils/logger.py` 日志输出

## 5.3 潜在风险与规避方案

### 风险 1：海外源访问超时/不可达

| 风险场景 | GitHub Actions Runner 可能无法稳定访问 arXiv/OpenAI 等海外源 |
|----------|------------------------------------------------------------|
| 概率 | 中等（取决于 GitHub Runner 网络状况） |
| 影响 | 采集失败或数据不全 |
| **规避方案** | |
| 1 | 实现自动重试机制（最多 3 次，指数退避） |
| 2 | 配置国内镜像降级（cn.arxiv.org, hf-mirror.com） |
| 3 | 在 `config.yaml` 中设置请求超时（connect=15s, read=30s） |
| 4 | 采集部分成功也输出 JSON，不因单个源失败而整体失败 |

### 风险 2：爬虫触发目标网站反爬机制

| 风险场景 | 部分网站可能对 GitHub Runner IP 限制访问 |
|----------|----------------------------------------|
| 概率 | 低 |
| 影响 | 特定源无法采集 |
| **规避方案** | |
| 1 | 严格遵守 robots.txt，设置合理请求间隔（≥ 3s） |
| 2 | 设置 User-Agent 标识为学术项目爬虫（含联系方式） |
| 3 | 优先使用 RSS/API 而非爬虫，减少对目标站的直接请求 |
| 4 | 对频率敏感源降低采集频率至每 2 小时一次 |

### 风险 3：GitHub Actions 运行时长/资源超限

| 风险场景 | 大量爬虫任务可能导致 Action 运行超过限制（免费版 6 小时/月） |
|----------|----------------------------------------------------------|
| 概率 | 低（轻量采集预计单次 5-10 分钟） |
| 影响 | 当月无法自动更新 |
| **规避方案** | |
| 1 | 优化采集效率，避免重复请求和无效请求 |
| 2 | 使用缓存机制（上次采集时间记录，不重复采集） |
| 3 | 设置单次采集最大源数量，或分批轮换执行 |

### 风险 4：JSON 数据文件膨胀

| 风险场景 | 长期累积后 `all_news.json` 过大，影响页面加载速度 |
|----------|--------------------------------------------------|
| 概率 | 高（运行 6 个月后预计千条级别，可承受） |
| 影响 | 首页加载变慢 |
| **规避方案** | |
| 1 | JSON 文件按年/月分片存储 |
| 2 | 前端实行懒加载/虚拟滚动 |
| 3 | 页面只加载当前视图需要的数据 |
| 4 | JSON 文件使用 gzip 压缩传输 |

### 风险 5：关键词误匹配（误报/漏报）

| 风险场景 | 关键词过于宽泛导致误标，或过于严格导致漏标后门论文 |
|----------|--------------------------------------------------|
| 概率 | 中等 |
| 影响 | 后门专题内容不准确 |
| **规避方案** | |
| 1 | 关键词匹配同时检查标题和摘要，提高召回 |
| 2 | 后门关键词采用精确短语匹配（非子串匹配），降低误报 |
| 3 | 增加人工复核界面（可选）：允许手动编辑 is_backdoor 标记 |
| 4 | 提供"反馈"按钮让用户报告分类错误（预留接口） |

### 风险 6：GitHub Pages 国内访问不稳定

| 风险场景 | GitHub Pages 在某些网络环境下被限制访问 |
|----------|---------------------------------------|
| 概率 | 低-中 |
| 影响 | 国内科研人员无法访问 |
| **规避方案** | |
| 1 | 主站使用 GitHub Pages，正常情况国内可访问 |
| 2 | 预留 Cloudflare Pages 镜像（同一代码自动部署）作为备选 |
| 3 | 提供 RSS 订阅输出，即使网页访问受限仍可通过 RSS 阅读器获取 |

### 风险 7：VitePress 构建时 JSON 数据未就位

| 风险场景 | 构建时 data/ 目录 JSON 文件不存在导致构建失败 |
|----------|---------------------------------------------|
| 概率 | 低（首次部署可能遇到） |
| 影响 | 构建失败 |
| **规避方案** | |
| 1 | 在 data/ 目录放置空 JSON 兜底文件（`{"news":[],"total":0}`） |
| 2 | 前端组件添加 `v-if` 检查数据是否存在 |
| 3 | GitHub Actions 工作流中确保采集步骤在构建步骤之前 |

## 5.4 扩展性预留

### 预留接口列表

| 扩展方向 | 预留设计 |
|----------|----------|
| 资讯导出 Markdown | JSON 中已包含完整字段，导出仅需一次转换 |
| BibTeX 引用生成 | 论文类数据已含 arxiv_id，可按 BibTeX 模板生成 |
| 邮件日报推送 | 预留 `email_sender.py` 模块骨架，配置 SMTP 即可接入 |
| Webhook 通知 | 新增资讯时可 POST 到指定 URL |
| 人工审核界面 | JSON 数据加 `reviewed: false` 字段，前端预留审核标记 |
| 多用户订阅 | 预留用户偏好配置接口（关键词定制、源选择） |
| 外部 API | 可提供 `/api/latest.json` 接口供其他工具调用 |

## 5.5 项目目录完整结构

```
mllm-security-daily/
├── .github/
│   └── workflows/
│       ├── daily_collect.yml      # 每日定时采集+部署
│       └── manual_collect.yml     # 手动触发采集
├── collector/
│   ├── __init__.py
│   ├── main.py                    # 主入口脚本
│   ├── config/
│   │   ├── config.yaml            # 全局配置
│   │   ├── sources.yaml           # 数据源配置
│   │   └── keywords.yaml          # 关键词配置
│   ├── fetchers/
│   │   ├── __init__.py
│   │   ├── base_fetcher.py        # 采集基类
│   │   ├── arxiv_fetcher.py       # arXiv API 采集
│   │   ├── rss_fetcher.py         # RSS 采集
│   │   └── web_scraper.py         # 网页爬虫
│   ├── processors/
│   │   ├── __init__.py
│   │   ├── dedup_engine.py        # 去重引擎
│   │   ├── keyword_matcher.py     # 关键词匹配
│   │   └── json_output.py         # JSON 输出
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── network.py             # 网络工具
│   │   ├── time_utils.py          # 时间工具
│   │   └── logger.py              # 日志
│   └── requirements.txt           # Python 依赖
├── docs/
│   ├── .vitepress/
│   │   ├── config.ts              # VitePress 配置
│   │   ├── theme/
│   │   │   ├── index.ts           # 主题入口
│   │   │   ├── custom.css         # 自定义样式
│   │   │   └── components/        # Vue 组件
│   │   │       ├── NewsCard.vue
│   │   │       ├── BackdoorCard.vue
│   │   │       ├── FilterBar.vue
│   │   │       ├── DatePicker.vue
│   │   │       ├── StatCard.vue
│   │   │       ├── Pagination.vue
│   │   │       ├── SearchBox.vue
│   │   │       ├── DarkModeToggle.vue
│   │   │       ├── CopyReport.vue
│   │   │       └── NavBar.vue
│   │   └── public/
│   │       └── favicon.ico
│   ├── index.md                   # 首页
│   ├── daily.md                   # 每日日报
│   ├── monthly.md                 # 月度汇总
│   ├── backdoor.md                # 后门专题
│   ├── sources.md                 # 数据源说明
│   ├── rss.xml                    # RSS 订阅
│   └── data/                      # JSON 数据（由采集生成）
│       ├── all_news.json
│       └── news_2026-07-27.json
├── package.json                   # Node.js 依赖
├── .gitignore
└── README.md
```

---

> **文档版本：** v1.0  
> **更新日期：** 2026-07-27  
> **项目状态：** 方案设计阶段，待进入开发
