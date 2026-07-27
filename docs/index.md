---
layout: home
---

<script setup>
import { ref, computed, onMounted } from 'vue'
import FilterBar from '../.vitepress/theme/components/FilterBar.vue'
import NewsCard from '../.vitepress/theme/components/NewsCard.vue'
import Pagination from '../.vitepress/theme/components/Pagination.vue'
import DarkModeToggle from '../.vitepress/theme/components/DarkModeToggle.vue'
import allNewsData from '../data/all_news.json'

const PAGE_SIZE = 20

const search = ref('')
const category = ref('')
const backdoorOnly = ref(false)
const todayOnly = ref(false)
const currentPage = ref(1)

const meta = computed(() => {
  return allNewsData.meta || { total_count: 0, last_updated: '', today_new: 0 }
})

const allItems = computed(() => {
  if (!allNewsData.news || !Array.isArray(allNewsData.news)) return []
  return allNewsData.news
})

const filteredItems = computed(() => {
  let items = allItems.value

  if (search.value) {
    const q = search.value.toLowerCase()
    items = items.filter(i =>
      i.title?.toLowerCase().includes(q) ||
      i.abstract?.toLowerCase().includes(q)
    )
  }

  if (category.value) {
    items = items.filter(i => i.category === category.value)
  }

  if (backdoorOnly.value) {
    items = items.filter(i => i.is_backdoor)
  }

  if (todayOnly.value) {
    const today = new Date().toISOString().slice(0, 10)
    items = items.filter(i => i.publish_date === today || i.is_today_new)
  }

  return items
})

const totalPages = computed(() => Math.ceil(filteredItems.value.length / PAGE_SIZE))

const pagedItems = computed(() => {
  const start = (currentPage.value - 1) * PAGE_SIZE
  return filteredItems.value.slice(start, start + PAGE_SIZE)
})

const backdoorCount = computed(() => {
  return allItems.value.filter(i => i.is_backdoor).length
})

const latestUpdate = computed(() => {
  const d = meta.value.last_updated
  if (!d) return '暂无'
  return d.slice(0, 10)
})

onMounted(() => {
  // Load dark mode preference
  const stored = localStorage.getItem('mllm-dark-mode')
  if (stored === 'true') {
    document.documentElement.classList.add('dark')
  }
})
</script>

<DarkModeToggle />

<div class="page-container">
  <!-- Status Bar -->
  <div class="status-bar">
    <div class="stat-item">
      最近更新: <span class="stat-value">{{ latestUpdate }}</span>
    </div>
    <div class="stat-item">
      采集总量: <span class="stat-value">{{ meta.total_count }}</span>
    </div>
    <div class="stat-item">
      今日新增: <span class="stat-value">{{ meta.today_new }}</span>
    </div>
    <div class="stat-item">
      后门专项: <span class="stat-value backdoor-count">{{ backdoorCount }}</span>
    </div>
  </div>

  <!-- Filter Bar -->
  <FilterBar
    v-model:search="search"
    v-model:category="category"
    v-model:backdoorOnly="backdoorOnly"
    v-model:todayOnly="todayOnly"
  />

  <!-- Results info -->
  <div style="font-size: 13px; color: var(--color-text-secondary); margin-bottom: 12px;">
    共 {{ filteredItems.length }} 条结果
  </div>

  <!-- News Cards -->
  <div v-if="pagedItems.length > 0">
    <div v-for="item in pagedItems" :key="item.id || item.origin_url">
      <NewsCard :item="item" />
    </div>
  </div>

  <div v-else class="empty-state">
    <div class="empty-icon">📭</div>
    <p>未找到匹配的资讯，请尝试其他关键词</p>
  </div>

  <!-- Pagination -->
  <Pagination
    v-model:current="currentPage"
    :total="filteredItems.length"
    :page-size="PAGE_SIZE"
  />
</div>
