<template>
  <AppLayout activeNav="daily">
    <!-- Stats Bar -->
    <div class="stats-bar">
      <div class="stat-card">
        <div class="stat-icon green">📅</div>
        <div class="stat-info">
          <div class="stat-label">归档日期</div>
          <div class="stat-value">{{ selectedDate }}</div>
          <div class="stat-sub">每日采集自动归档</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon blue">📰</div>
        <div class="stat-info">
          <div class="stat-label">当日资讯</div>
          <div class="stat-value">{{ dayItems.length }}</div>
          <div class="stat-sub">后门 {{ backdoorItems.length }} 条</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon red">⚠️</div>
        <div class="stat-info">
          <div class="stat-label">后门专项</div>
          <div class="stat-value red">{{ backdoorItems.length }}</div>
          <div class="stat-sub">攻击 / 防御 / 投毒</div>
        </div>
      </div>
    </div>

    <div class="main-layout">
      <!-- Left Sidebar: Date picker + filters -->
      <aside class="left-sidebar">
        <div class="filter-group">
          <div class="filter-label">选择日期</div>
          <input
            type="date"
            class="filter-input"
            v-model="selectedDate"
            :max="maxDate"
          />
        </div>
        <div class="filter-group">
          <div class="filter-label">搜索</div>
          <input type="text" class="filter-input" placeholder="当日内容搜索..." v-model="search" />
        </div>
        <div class="filter-group" style="margin-bottom:0;">
          <label class="filter-switch">
            <input type="checkbox" v-model="backdoorOnly" />
            仅显示后门专题
          </label>
        </div>
      </aside>

      <!-- Center Content -->
      <main class="center-content">
        <div class="section-header">
          <div class="section-title">{{ selectedDate }} 资讯</div>
          <div class="section-count">{{ filteredItems.length }} 条结果</div>
        </div>

        <div v-if="filteredItems.length" class="card-grid">
          <NewsCard v-for="item in filteredItems" :key="item.id || item.origin_url" :item="item" />
        </div>
        <div v-else style="text-align:center;padding:60px 20px;color:var(--color-text-secondary);font-size:14px;">
          该日期暂无采集记录
        </div>
      </main>

      <!-- Right Sidebar -->
      <aside class="right-sidebar">
        <div class="filter-label">可用日期</div>
        <button
          v-for="d in availableDates.slice(0, 10)"
          :key="d"
          class="topic-btn"
          :class="{ active: d === selectedDate }"
          @click="selectedDate = d"
        >
          {{ d }}
        </button>
      </aside>
    </div>
  </AppLayout>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import AppLayout from './AppLayout.vue'
import NewsCard from './NewsCard.vue'

const props = defineProps({
  data: { type: Object, default: () => ({ items: [] }) }
})

const maxDate = new Date().toISOString().slice(0, 10)
const selectedDate = ref(maxDate)
const search = ref('')
const backdoorOnly = ref(false)

// Index contains lightweight metadata (id, title, date, category, is_backdoor)
const indexItems = computed(() => {
  if (props.data && props.data.items) return props.data.items
  return []
})

const availableDates = computed(() => {
  const dates = new Set()
  indexItems.value.forEach(i => { if (i.publish_date) dates.add(i.publish_date) })
  return Array.from(dates).sort().reverse()
})

const dayItems = computed(() => {
  return indexItems.value.filter(i => i.publish_date === selectedDate.value)
})

const backdoorItems = computed(() => dayItems.value.filter(i => i.is_backdoor))

const filteredItems = computed(() => {
  let arr = dayItems.value
  if (search.value) {
    const q = search.value.toLowerCase()
    arr = arr.filter(i => (i.title || '').toLowerCase().includes(q))
  }
  if (backdoorOnly.value) arr = arr.filter(i => i.is_backdoor)
  return arr
})

// When data changes, reset to the latest available date
watch(indexItems, () => {
  if (availableDates.value.length > 0) {
    selectedDate.value = availableDates.value[0]
  }
}, { immediate: true })
</script>
