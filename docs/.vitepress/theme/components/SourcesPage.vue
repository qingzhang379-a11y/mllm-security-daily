<template>
  <AppLayout activeNav="sources">
    <!-- Stats Bar -->
    <div class="stats-bar">
      <div class="stat-card">
        <div class="stat-icon blue">📡</div>
        <div class="stat-info">
          <div class="stat-label">官方信源</div>
          <div class="stat-value">{{ sourceStats.totalSources }}</div>
          <div class="stat-sub">RSS + API + 爬虫</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon green">📰</div>
        <div class="stat-info">
          <div class="stat-label">资讯总量</div>
          <div class="stat-value">{{ totalItems }}</div>
          <div class="stat-sub">全部官方采集</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon red">⚠️</div>
        <div class="stat-info">
          <div class="stat-label">后门专项</div>
          <div class="stat-value red">{{ backdoorItems }}</div>
          <div class="stat-sub">攻击 / 防御 / 投毒</div>
        </div>
      </div>
    </div>

    <div class="main-layout">
      <!-- Left Sidebar: rules -->
      <aside class="left-sidebar">
        <div class="filter-group">
          <div class="filter-label">采集规则</div>
          <div style="font-size:13px;color:var(--color-text-secondary);line-height:1.8;">
            <div>• 每日 UTC 02:00 自动采集</div>
            <div>• 严格遵守 robots.txt</div>
            <div>• URL + 标题双重去重</div>
            <div>• 海外源自动切换国内镜像</div>
          </div>
        </div>
        <div class="filter-group">
          <div class="filter-label">排除内容</div>
          <div style="font-size:13px;color:var(--color-text-secondary);line-height:1.8;">
            <div>✗ 个人博客 / 自媒体</div>
            <div>✗ 论坛讨论帖</div>
            <div>✗ 非官方解读文章</div>
          </div>
        </div>
      </aside>

      <!-- Center Content -->
      <main class="center-content">
        <div class="section-header">
          <div class="section-title">官方数据源清单</div>
          <div class="section-count">仅收录官方发布内容</div>
        </div>

        <div class="source-panel">
          <div class="source-group">
            <div class="filter-label" style="font-size:14px;margin-bottom:12px;">📄 学术论文源</div>
            <div v-for="s in paperSources" :key="s.name" class="source-row">
              <span class="source-name">{{ s.name }}</span>
              <span class="source-type">{{ s.type }}</span>
              <span class="source-method">{{ s.method }}</span>
            </div>
          </div>

          <div class="source-group">
            <div class="filter-label" style="font-size:14px;margin-bottom:12px;">🏢 企业官方 Blog</div>
            <div v-for="s in blogSources" :key="s.name" class="source-row">
              <span class="source-name">{{ s.name }}</span>
              <span class="source-type">{{ s.type }}</span>
              <span class="source-method">{{ s.method }}</span>
            </div>
          </div>

          <div class="source-group">
            <div class="filter-label" style="font-size:14px;margin-bottom:12px;">📦 开源发布源</div>
            <div v-for="s in openSources" :key="s.name" class="source-row">
              <span class="source-name">{{ s.name }}</span>
              <span class="source-type">{{ s.type }}</span>
              <span class="source-method">{{ s.method }}</span>
            </div>
          </div>

          <div class="source-group">
            <div class="filter-label" style="font-size:14px;margin-bottom:12px;">🌐 国内平台</div>
            <div v-for="s in cnSources" :key="s.name" class="source-row">
              <span class="source-name">{{ s.name }}</span>
              <span class="source-type">{{ s.type }}</span>
              <span class="source-method">{{ s.method }}</span>
            </div>
          </div>
        </div>
      </main>

      <!-- Right Sidebar: RSS subscription -->
      <aside class="right-sidebar">
        <div class="filter-label">RSS 订阅</div>
        <button class="topic-btn" @click="copyRss">
          <span class="topic-dot" style="background:#e86868;"></span>
          后门专题 RSS
          <span class="topic-count">{{ backdoorItems }}</span>
        </button>
        <button class="topic-btn" @click="copyAllRss">
          <span class="topic-dot" style="background:#5d9fd6;"></span>
          全量 RSS
        </button>
        <div style="font-size:11px;color:var(--color-text-secondary);margin-top:16px;line-height:1.6;">
          RSS 链接点击复制，可导入任意阅读器
        </div>
      </aside>
    </div>
  </AppLayout>
</template>

<script setup>
import { ref, computed } from 'vue'
import AppLayout from './AppLayout.vue'

const props = defineProps({
  data: { type: Object, default: () => ({ items: [] }) }
})

const indexItems = computed(() => {
  if (props.data && props.data.items) return props.data.items
  return []
})

const totalItems = computed(() => indexItems.value.length)
const backdoorItems = computed(() => indexItems.value.filter(i => i.is_backdoor).length)

const sourceStats = computed(() => ({
  totalSources: paperSources.value.length + blogSources.value.length + openSources.value.length + cnSources.value.length,
}))

const paperSources = computed(() => [
  { name: 'arXiv API (MLLM+Backdoor)', type: '预印本', method: 'API 检索' },
  { name: 'arXiv API (VLM+Backdoor)', type: '预印本', method: 'API 检索' },
  { name: 'arXiv API (MLLM+Safety)', type: '预印本', method: 'API 检索' },
  { name: 'arXiv API (MLLM+Jailbreak)', type: '预印本', method: 'API 检索' },
  { name: 'CVPR / ICCV / ECCV', type: '顶会', method: 'Proceeding 页面' },
  { name: 'NeurIPS / ICML / ICLR', type: '顶会', method: 'Proceeding 页面' },
  { name: 'ACL / AAAI', type: '顶会', method: 'Proceeding 页面' },
])

const blogSources = computed(() => [
  { name: 'OpenAI Blog', type: '官方', method: 'RSS' },
  { name: 'Google DeepMind Blog', type: '官方', method: 'RSS' },
  { name: 'Meta AI Blog', type: '官方', method: 'RSS' },
  { name: 'Microsoft Research', type: '官方', method: 'RSS' },
  { name: 'Anthropic Blog', type: '官方', method: 'RSS' },
])

const openSources = computed(() => [
  { name: 'Hugging Face Blog', type: '官方', method: 'RSS' },
  { name: 'Hugging Face Papers', type: '官方', method: 'RSS' },
])

const cnSources = computed(() => [
  { name: '机器之心 (官方首发)', type: '学术媒体', method: 'RSS / 爬虫' },
  { name: '智源社区 (官方稿件)', type: '学术社区', method: '爬虫' },
  { name: 'BAAI 智源研究院', type: '研究院', method: '爬虫' },
  { name: 'Qwen 团队 Blog', type: '企业', method: '爬虫' },
])

function copyRss() {
  navigator.clipboard.writeText('https://your-domain/rss-backdoor.xml')
  alert('后门专题 RSS 链接已复制')
}
function copyAllRss() {
  navigator.clipboard.writeText('https://your-domain/rss.xml')
  alert('全量 RSS 链接已复制')
}
</script>

<style scoped>
.source-panel {
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  padding: 24px;
}

.source-group {
  margin-bottom: 28px;
}

.source-group:last-child {
  margin-bottom: 0;
}

.source-row {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px 12px;
  border-bottom: 1px solid var(--color-border);
  font-size: 13px;
}

.source-row:last-child {
  border-bottom: none;
}

.source-name {
  flex: 1;
  color: var(--color-text);
  font-weight: 500;
}

.source-type {
  padding: 2px 8px;
  border-radius: 4px;
  background: var(--color-primary-glow);
  color: var(--color-primary-light);
  font-size: 11px;
  white-space: nowrap;
}

.source-method {
  font-size: 11px;
  color: var(--color-text-secondary);
  white-space: nowrap;
  width: 90px;
  text-align: right;
}
</style>
