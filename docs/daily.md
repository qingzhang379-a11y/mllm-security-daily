---
layout: page
---

<script setup>
import { ref, computed, onMounted } from 'vue'
import NewsCard from '../.vitepress/theme/components/NewsCard.vue'
import CopyReport from '../.vitepress/theme/components/CopyReport.vue'
import DarkModeToggle from '../.vitepress/theme/components/DarkModeToggle.vue'
import allNewsData from '../data/all_news.json'

const selectedDate = ref(new Date().toISOString().slice(0, 10))

const allItems = computed(() => {
  if (!allNewsData.news || !Array.isArray(allNewsData.news)) return []
  return allNewsData.news
})

const dayItems = computed(() => {
  return allItems.value.filter(i => i.publish_date === selectedDate.value)
})

const backdoorItems = computed(() => dayItems.value.filter(i => i.is_backdoor))
const normalItems = computed(() => dayItems.value.filter(i => !i.is_backdoor))

const availableDates = computed(() => {
  const dates = new Set()
  allItems.value.forEach(i => {
    if (i.publish_date) dates.add(i.publish_date)
  })
  return Array.from(dates).sort().reverse()
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
    <h1>每日日报归档</h1>
    <div style="display: flex; gap: 12px; align-items: center; flex-wrap: wrap;">
      <input
        type="date"
        v-model="selectedDate"
        class="date-picker"
        :max="new Date().toISOString().slice(0, 10)"
      />
      <CopyReport :items="dayItems" :date="selectedDate" />
    </div>
  </div>

  <div v-if="dayItems.length > 0">
    <div style="margin-bottom: 20px; font-size: 14px; color: var(--color-text-secondary);">
      {{ selectedDate }} — 共 {{ dayItems.length }} 条资讯
    </div>

    <!-- Backdoor Section -->
    <div v-if="backdoorItems.length > 0" class="daily-group">
      <div class="group-header">
        <div class="group-title" style="color: var(--color-backdoor);">📌 后门专项资讯</div>
        <div class="group-count">{{ backdoorItems.length }} 条</div>
      </div>
      <div v-for="item in backdoorItems" :key="item.id">
        <NewsCard :item="item" />
      </div>
    </div>

    <!-- Normal Section -->
    <div v-if="normalItems.length > 0" class="daily-group">
      <div class="group-header">
        <div class="group-title">📋 普通安全资讯</div>
        <div class="group-count">{{ normalItems.length }} 条</div>
      </div>
      <div v-for="item in normalItems" :key="item.id">
        <NewsCard :item="item" />
      </div>
    </div>
  </div>

  <div v-else class="empty-state">
    <div class="empty-icon">📅</div>
    <p>该日期暂无采集记录</p>
  </div>
</div>
