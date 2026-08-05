<template>
  <div>
    <!-- Top Navigation -->
    <nav class="top-nav">
      <div class="top-nav-inner">
        <div class="site-title">MLLM 安全日报</div>

        <div class="nav-search">
          <input type="text" placeholder="搜索论文、新闻..." v-model="search" />
        </div>

        <div class="nav-links">
          <a :href="basePath + ''" class="nav-link active">首页</a>
          <a :href="basePath + 'daily'" class="nav-link">每日归档</a>
          <a :href="basePath + 'monthly'" class="nav-link">月度汇总</a>
          <a :href="basePath + 'backdoor'" class="nav-link">后门专题</a>
          <a :href="basePath + 'sources'" class="nav-link">数据源订阅</a>
        </div>

        <button class="theme-toggle" @click="toggleTheme" title="主题切换">
          {{ isDark ? '☀️' : '🌙' }}
        </button>
      </div>
    </nav>

    <!-- Stats Bar -->
    <div class="stats-bar">
      <div class="stat-card">
        <div class="stat-icon green"><i class="fas fa-newspaper"></i></div>
        <div class="stat-info">
          <div class="stat-label">资讯总量</div>
          <div class="stat-value">{{ meta.total_count || items.length }}</div>
          <div class="stat-sub">持续更新中</div>
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-icon red"><i class="fas fa-triangle-exclamation"></i></div>
        <div class="stat-info">
          <div class="stat-label">后门专项</div>
          <div class="stat-value red">{{ backdoorCount }}</div>
          <div class="stat-sub">攻击 / 防御 / 投毒</div>
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-icon blue"><i class="fas fa-clock-rotate-left"></i></div>
        <div class="stat-info">
          <div class="stat-label">上次更新</div>
          <div class="stat-value">{{ lastUpdated }}</div>
          <div class="stat-sub">每日自动采集</div>
        </div>
        <button class="stat-refresh-btn" @click="refresh" title="刷新数据"><i class="fas fa-rotate"></i></button>
      </div>
    </div>

    <!-- Main Layout -->
    <div class="main-layout">
      <FilterSidebar
        v-model:search="search"
        v-model:category="category"
        v-model:backdoorOnly="backdoorOnly"
        v-model:timeRange="timeRange"
        v-model:sort="sort"
      />

      <main class="center-content">
        <div class="section-header">
          <div class="section-title">
            {{ activeTopic ? (hotTopics.find(t => t.key === activeTopic)?.label || '搜索结果') : '全部资讯' }}
          </div>
          <div class="section-count">{{ filteredItems.length }} 条结果</div>
        </div>

        <div v-if="pagedItems.length" class="card-grid">
          <NewsCard v-for="item in pagedItems" :key="item.id || item.origin_url" :item="item" />
        </div>
        <div v-else style="text-align:center;padding:60px 20px;color:var(--color-text-secondary);font-size:14px;">
          暂无匹配资讯
        </div>

        <Pagination v-model:current="currentPage" :total="filteredItems.length" :page-size="PAGE_SIZE" />
      </main>

      <HotTopics :topics="hotTopics" :activeTopic="activeTopic" @select="onTopicSelect" />
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import FilterSidebar from './FilterSidebar.vue'
import HotTopics from './HotTopics.vue'
import Pagination from './Pagination.vue'
import NewsCard from './NewsCard.vue'

const props = defineProps({
  data: { type: Object, default: () => ({ news: [], meta: {} }) }
})

const allItems = computed(() => props.data.news || [])
const meta = computed(() => props.data.meta || {})

const PAGE_SIZE = 10
const items = allItems
const totalCount = computed(() => items.value.length)
const backdoorCount = computed(() => items.value.filter(i => i.is_backdoor).length)
const lastUpdated = computed(() => meta.value.last_updated?.slice(0,10) || '--')

const search = ref('')
const category = ref('')
const backdoorOnly = ref(false)
const timeRange = ref('all')
const sort = ref('date_desc')
const activeTopic = ref('')

// Auto-extract hot topics from data: count keyword occurrences across all items
const TOPIC_KEYWORDS = {
  'backdoor attack': { label: '后门攻击', color: '#e86868', kws: ['backdoor attack', '后门攻击', 'trojan attack'] },
  'backdoor defense': { label: '后门防御', color: '#5cb884', kws: ['backdoor defense', '后门防御', 'backdoor detection', 'backdoor removal', 'backdoor mitigation'] },
  'data poisoning': { label: '数据投毒', color: '#d4a050', kws: ['data poisoning', '投毒', 'poisoned', 'dirty label', 'poisoning attack'] },
  'visual trigger': { label: '视觉触发器', color: '#8b7fc7', kws: ['visual trigger', '触发器', 'trigger pattern', 'patch trigger', 'trigger inversion'] },
  'safety alignment': { label: '安全对齐', color: '#5d9fd6', kws: ['safety alignment', '安全对齐', 'alignment', 'rlhf', 'dpo', 'constitutional'] },
  'jailbreak': { label: '越狱攻击', color: '#e86868', kws: ['jailbreak', '越狱', 'prompt injection', '提示注入'] },
  'adversarial': { label: '对抗攻击', color: '#c49a6a', kws: ['adversarial attack', 'adversarial example', '对抗攻击', '对抗样本'] },
  'privacy': { label: '隐私安全', color: '#6aab8e', kws: ['privacy leakage', 'privacy', '隐私泄露', '隐私'] },
  'robustness': { label: '鲁棒性', color: '#7ba3c4', kws: ['robustness', '鲁棒性', 'robust'] },
  'red teaming': { label: '红队测试', color: '#e86868', kws: ['red teaming', '红蓝对抗', '红队', 'red team'] },
}

const hotTopics = computed(() => {
  const result = []
  for (const [key, cfg] of Object.entries(TOPIC_KEYWORDS)) {
    const count = items.value.filter(i => {
      const text = (i.title + ' ' + (i.abstract || '')).toLowerCase()
      return cfg.kws.some(kw => text.includes(kw))
    }).length
    if (count > 0) {
      result.push({ key, label: cfg.label, color: cfg.color, count })
    }
  }
  // Sort by count descending, take top 8
  result.sort((a, b) => b.count - a.count)
  return result.slice(0, 8)
})

function onTopicSelect(key) {
  activeTopic.value = activeTopic.value === key ? '' : key
}

const filteredItems = computed(() => {
  let arr = items.value
  if (search.value) {
    const q = search.value.toLowerCase()
    arr = arr.filter(i => (i.title||'').toLowerCase().includes(q) || (i.abstract||'').toLowerCase().includes(q))
  }
  if (category.value) arr = arr.filter(i => i.category === category.value)
  if (backdoorOnly.value) arr = arr.filter(i => i.is_backdoor)
  if (timeRange.value !== 'all') {
    const days = parseInt(timeRange.value); const cutoff = new Date(); cutoff.setDate(cutoff.getDate() - days)
    arr = arr.filter(i => i.publish_date && new Date(i.publish_date) >= cutoff)
  }
  if (activeTopic.value) {
    const cfg = TOPIC_KEYWORDS[activeTopic.value]
    const kws = cfg ? cfg.kws : []
    arr = arr.filter(i => { const t = (i.title+' '+(i.abstract||'')).toLowerCase(); return kws.some(k => t.includes(k)) })
  }
  arr = [...arr]
  arr.sort((a, b) => sort.value === 'date_desc'
    ? (b.publish_date||'').localeCompare(a.publish_date||'')
    : (a.publish_date||'').localeCompare(b.publish_date||''))
  return arr
})

const currentPage = ref(1)
const pagedItems = computed(() => { const s = (currentPage.value-1)*PAGE_SIZE; return filteredItems.value.slice(s, s+PAGE_SIZE) })
watch(filteredItems, () => { currentPage.value = 1 })

function refresh() { window.location.reload() }

const basePath = import.meta.env.BASE_URL || '/'

const isDark = ref(true)
function toggleTheme() {
  isDark.value = !isDark.value
  document.documentElement.classList.toggle('dark', isDark.value)
  localStorage.setItem('mllm-dark-mode', String(isDark.value))
}
onMounted(() => {
  const stored = localStorage.getItem('mllm-dark-mode')
  isDark.value = stored === null ? true : stored === 'true'
  document.documentElement.classList.toggle('dark', isDark.value)
})
</script>
