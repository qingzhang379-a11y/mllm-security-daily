---
layout: page
---

# 数据源说明

本平台所有内容均采集自以下官方信源，严格遵守 robots.txt，仅采集公开官方发布内容。

---

## 📄 学术论文源

| 信源 | 类型 | 采集方式 |
|------|------|----------|
| arXiv (MLLM + Backdoor) | 预印本 | API 关键词检索 |
| arXiv (VLM + Backdoor) | 预印本 | API 关键词检索 |
| arXiv (MLLM + Safety) | 预印本 | API 关键词检索 |
| arXiv (MLLM + Jailbreak) | 预印本 | API 关键词检索 |
| arXiv (VLM + Adversarial) | 预印本 | API 关键词检索 |
| Hugging Face Papers | 论文推荐 | RSS Feed |
| CVPR / ICCV / ECCV | 顶会论文 | Proceedings 页面 |
| NeurIPS / ICML / ICLR | 顶会论文 | Proceedings 页面 |
| ACL / AAAI | 顶会论文 | Proceedings 页面 |

## 🏢 企业官方 Blog

| 信源 | 采集方式 |
|------|----------|
| OpenAI Blog | RSS |
| Google DeepMind Blog | RSS |
| Meta AI Blog | RSS |
| Google AI Blog | RSS |
| Microsoft Research | RSS |
| Anthropic Blog | RSS |
| Meta Research Blog | RSS |

## 📦 开源发布

| 信源 | 采集方式 |
|------|----------|
| Hugging Face Blog | RSS |
| Hugging Face 模型发布 | RSS |

## 🌐 国内源（开发中）

| 信源 | 采集方式 | 状态 |
|------|----------|------|
| BAAI 智源研究院 | 网页爬虫 | 待接入 |
| Qwen 团队 Blog | 网页爬虫 | 待接入 |

---

## ⚙️ 采集规则

- **采集频率**: 每日 UTC 02:00（北京时间 10:00）自动执行
- **去重机制**: 基于原文 URL + 标题的 SHA256 哈希双重去重
- **关键词匹配**: 自动区分普通安全资讯与后门专项资讯
- **机器人协议**: 严格遵守各站点 robots.txt，设置合理请求间隔
- **降级策略**: 海外源不可用时自动切换国内镜像

## ❌ 排除内容

本平台**不收录**以下类型内容：

- 个人博客、个人知乎专栏、个人公众号
- 自媒体转载、汇编解读类文章
- 论坛讨论帖、Reddit、Twitter/X 非官方账号
- 微信非官方公众号

## 📡 RSS 订阅

全站 RSS 订阅链接（即将上线）：

- 全量订阅: `https://<your-domain>/rss.xml`
- 后门专题订阅: `https://<your-domain>/rss-backdoor.xml`
