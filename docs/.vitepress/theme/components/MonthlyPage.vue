<template>
  <AppLayout activeNav="monthly">
    <!-- Stats Bar -->
    <div class="stats-bar">
      <div class="stat-card">
        <div class="stat-icon blue">📊</div>
        <div class="stat-info">
          <div class="stat-label">当月资讯</div>
          <div class="stat-value">{{ monthItems.length }}</div>
          <div class="stat-sub">{{ selectedMonth }}</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon green">📄</div>
        <div class="stat-info">
          <div class="stat-label">论文数量</div>
          <div class="stat-value">{{ paperCount }}</div>
          <div class="stat-sub">学术论文类</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon purple">📦</div>
        <div class="stat-info">
          <div class="stat-label">开源项目</div>
          <div class="stat-value">{{ openSourceCount }}</div>
          <div class="stat-sub">开源发布类</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon red">⚠️</div>
        <div class="stat-info">
          <div class="stat-label">后门文献</div>
          <div class="stat-value red">{{ backdoorCount }}</div>
          <div class="stat-sub">攻击 / 防御 / 投毒</div>
        </div>
      </div>
    </div>

    <div class="main-layout">
      <!-- Left Sidebar -->
      <aside class="left-sidebar">
        <div class="filter-group">
          <div class="filter-label">选择月份</div>
          <select class="filter-select" v-model="selectedMonth">
            <option v-for="m in availableMonths" :key="m" :value="m">
              {{ m.slice(0,4) }}年{{ parseInt(m.slice(5,7)) }}月
            </option>
          </select>
        </div>
        <div class="filter-group">
          <div class="filter-label">搜索</div>
          <input type="text" class="filter-input" placeholder="月内搜索..." v-model="search" />
        </div>
        <div class="filter-group" style="margin-bottom:0;">
          <label class="filter-switch">
            <input type="checkbox" v-model="backdoorOnly" />
            仅显示后门专题
          </label>
        </div>
      </aside>

      <!-- Center: group by date -->
      <main class="center-content">
        <div class="section-header">
          <div class="section-title">{{ selectedMonth }} 月度汇总</div>
          <div class="section-count">{{ filteredItems.length }} 条结果</div>
        </div>

        <div v-if="groupedByDate.length">
          <div v-for="[date, items] in groupedByDate" :key="date" style="margin-bottom:20px;">
            <div class="section-title" style="font-size:14px;margin-bottom:10px;">
              {{ date }}
              <span style="font-weight:400;font-size:12px;color:var(--color-text-secondary);margin-left:8px;">
                {{ items.length }} 条
              </span>
            </div>
            <div class="card-grid">
              <NewsCard v-for="item in items" :key="item.id" :item="item" />
            </div>
          </div>
        </div>
        <div v-else style="text-align:center;padding:60px 20px;color:var(--color-text-secondary);font-size:14px;">
          该月暂无采集数据
        </div>
      </main>

      <!-- Right: month trend -->
      <aside class="right-sidebar">
        <div class="filter-label">数据分布</div>
        <button
          v-for="cat in ['学术论文','官方新闻','开源发布','会议动态']"
          :key="cat"
          class="topic-btn"
          @click="categoryFilter = categoryFilter === cat ? '' : cat"
          :class="{ active: categoryFilter === cat }"
        >
          {{ cat }}
          <span class="topic-count">{{ categoryCounts[cat] || 0 }}</span>
        </button>
      </aside>
    </div>
  </AppLayout>
</template>

<script setup>
import { ref, computed } from 'vue'
import AppLayout from './AppLayout.vue'
import NewsCard from './NewsCard.vue'

const props = defineProps({
  data: { type: Object, default: () => ({ items: [] }) }
})

const now = new Date()
const selectedMonth = ref(`${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}`)
const search = ref('')
const backdoorOnly = ref(false)
const categoryFilter = ref('')

const indexItems = computed(() => {
  if (props.data && props.data.items) return props.data.items
  return []
})

const availableMonths = computed(() => {
  const months = new Set()
  indexItems.value.forEach(i => {
    if (i.publish_date && i.publish_date.length >= 7) {
      months.add(i.publish_date.slice(0, 7))
    }
  })
  return Array.from(months).sort().reverse()
})

const monthItems = computed(() => {
  return indexItems.value.filter(i => (i.publish_date || '').slice(0, 7) === selectedMonth.value)
})

const paperCount = computed(() => monthItems.value.filter(i => i.category === '学术论文').length)
const openSourceCount = computed(() => monthItems.value.filter(i => i.category === '开源发布').length)
const backdoorCount = computed(() => monthItems.value.filter(i => i.is_backdoor).length)

const categoryCounts = computed(() => {
  const c = {}
  monthItems.value.forEach(i => { c[i.category] = (c[i.category] || 0) + 1 })
  return c
})

const filteredItems = computed(() => {
  let arr = monthItems.value
  if (search.value) {
    const q = search.value.toLowerCase()
    arr = arr.filter(i => (i.title || '').toLowerCase().includes(q))
  }
  if (backdoorOnly.value) arr = arr.filter(i => i.is_backdoor)
  if (categoryFilter.value) arr = arr.filter(i => i.category === categoryFilter.value)
  return arr
})

const groupedByDate = computed(() => {
  const groups = {}
  filteredItems.value.forEach(i => {
    const d = i.publish_date || 'unknown'
    if (!groups[d]) groups[d] = []
    groups[d].push(i)
  })
  return Object.entries(groups).sort(([a], [b]) => b.localeCompare(a))
})
</script>
