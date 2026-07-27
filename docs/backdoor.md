---
layout: page
---

<script setup>
import { ref, computed, onMounted } from 'vue'
import NewsCard from '../.vitepress/theme/components/NewsCard.vue'
import FilterBar from '../.vitepress/theme/components/FilterBar.vue'
import Pagination from '../.vitepress/theme/components/Pagination.vue'
import DarkModeToggle from '../.vitepress/theme/components/DarkModeToggle.vue'
import allNewsData from '../data/all_news.json'

const PAGE_SIZE = 20
const search = ref('')
const category = ref('')
const backdoorOnly = ref(true)
const todayOnly = ref(false)
const currentPage = ref(1)

const allItems = computed(() => {
  if (!allNewsData.news || !Array.isArray(allNewsData.news)) return []
  return allNewsData.news.filter(i => i.is_backdoor)
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

  return items
})

const totalPages = computed(() => Math.ceil(filteredItems.value.length / PAGE_SIZE))

const pagedItems = computed(() => {
  const start = (currentPage.value - 1) * PAGE_SIZE
  return filteredItems.value.slice(start, start + PAGE_SIZE)
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
    <h1>⚠️ MLLM 后门攻击与防御专题合集</h1>
    <div style="font-size: 14px; color: var(--color-text-secondary);">
      共收录 <strong style="color: var(--color-backdoor);">{{ allItems.length }}</strong> 篇后门专项文献
    </div>
  </div>

  <!-- Stats -->
  <div class="stat-cards">
    <div class="stat-card">
      <div class="stat-label">后门论文</div>
      <div class="stat-value stat-backdoor">{{ allItems.filter(i => i.category === '学术论文').length }}</div>
    </div>
    <div class="stat-card">
      <div class="stat-label">后门开源</div>
      <div class="stat-value">{{ allItems.filter(i => i.category === '开源发布').length }}</div>
    </div>
    <div class="stat-card">
      <div class="stat-label">后门新闻</div>
      <div class="stat-value">{{ allItems.filter(i => i.category === '官方新闻').length }}</div>
    </div>
    <div class="stat-card">
      <div class="stat-label">会议动态</div>
      <div class="stat-value">{{ allItems.filter(i => i.category === '会议动态').length }}</div>
    </div>
  </div>

  <FilterBar
    v-model:search="search"
    v-model:category="category"
    v-model:backdoorOnly="backdoorOnly"
    v-model:todayOnly="todayOnly"
  />

  <div style="font-size: 13px; color: var(--color-text-secondary); margin-bottom: 12px;">
    共 {{ filteredItems.length }} 条结果
  </div>

  <div v-if="pagedItems.length > 0">
    <div v-for="item in pagedItems" :key="item.id">
      <NewsCard :item="item" />
    </div>
  </div>

  <div v-else class="empty-state">
    <div class="empty-icon">🔍</div>
    <p>未找到匹配的后门专项资讯</p>
  </div>

  <Pagination
    v-model:current="currentPage"
    :total="filteredItems.length"
    :page-size="PAGE_SIZE"
  />
</div>
