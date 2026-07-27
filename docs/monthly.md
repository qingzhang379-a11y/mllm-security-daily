---
layout: page
---

<script setup>
import { ref, computed, onMounted } from 'vue'
import NewsCard from '../.vitepress/theme/components/NewsCard.vue'
import StatCard from '../.vitepress/theme/components/StatCard.vue'
import DarkModeToggle from '../.vitepress/theme/components/DarkModeToggle.vue'
import allNewsData from '../data/all_news.json'

const now = new Date()
const selectedMonth = ref(`${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}`)

const allItems = computed(() => {
  if (!allNewsData.news || !Array.isArray(allNewsData.news)) return []
  return allNewsData.news
})

const monthItems = computed(() => {
  const [year, month] = selectedMonth.value.split('-')
  return allItems.value.filter(i => {
    if (!i.publish_date) return false
    const d = i.publish_date.slice(0, 7)
    return d === `${year}-${month}`
  })
})

const monthStats = computed(() => {
  const items = monthItems.value
  return {
    total: items.length,
    papers: items.filter(i => i.category === '学术论文').length,
    opensource: items.filter(i => i.category === '开源发布').length,
    backdoor: items.filter(i => i.is_backdoor).length,
  }
})

const groupedByDate = computed(() => {
  const groups = {}
  monthItems.value.forEach(item => {
    const date = item.publish_date || 'unknown'
    if (!groups[date]) groups[date] = []
    groups[date].push(item)
  })
  const sorted = Object.entries(groups).sort(([a], [b]) => b.localeCompare(a))
  return sorted
})

const availableMonths = computed(() => {
  const months = new Set()
  allItems.value.forEach(i => {
    if (i.publish_date && i.publish_date.length >= 7) {
      months.add(i.publish_date.slice(0, 7))
    }
  })
  return Array.from(months).sort().reverse()
})

onMounted(() => {
  const stored = localStorage.getItem('mllm-dark-mode')
  if (stored === 'true') {
    document.documentElement.classList.add('dark')
  }
})
</script>

<DarkModeToggle />

<div class="page-container">
  <div class="page-header">
    <h1>月度汇总</h1>
    <div style="display: flex; gap: 12px; align-items: center;">
      <select v-model="selectedMonth" class="month-picker">
        <option v-for="m in availableMonths" :key="m" :value="m">
          {{ m.slice(0, 4) }}年{{ parseInt(m.slice(5, 7)) }}月
        </option>
      </select>
    </div>
  </div>

  <!-- Stats Cards -->
  <StatCard :stats="monthStats" />

  <!-- Daily Groups -->
  <div v-if="groupedByDate.length > 0">
    <div v-for="[date, items] in groupedByDate" :key="date" class="daily-group">
      <div class="group-header">
        <div class="group-title">{{ date }}</div>
        <div class="group-count">{{ items.length }} 条</div>
      </div>
      <div v-for="item in items" :key="item.id">
        <NewsCard :item="item" />
      </div>
    </div>
  </div>

  <div v-else class="empty-state">
    <div class="empty-icon">📊</div>
    <p>该月暂无采集数据</p>
  </div>
</div>
