<template>
  <AppLayout activeNav="backdoor">
    <!-- Stats Bar -->
    <div class="stats-bar">
      <div class="stat-card">
        <div class="stat-icon red">⚠️</div>
        <div class="stat-info">
          <div class="stat-label">后门文献总数</div>
          <div class="stat-value red">{{ backdoorItems.length }}</div>
          <div class="stat-sub">持续追踪更新</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon green">🛡️</div>
        <div class="stat-info">
          <div class="stat-label">攻击方向</div>
          <div class="stat-value">{{ attackCount }}</div>
          <div class="stat-sub">注入 / 投毒 / 触发器</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon blue">🔒</div>
        <div class="stat-info">
          <div class="stat-label">防御方向</div>
          <div class="stat-value">{{ defenseCount }}</div>
          <div class="stat-sub">检测 / 移除 / 净化</div>
        </div>
      </div>
    </div>

    <div class="main-layout">
      <!-- Left Sidebar -->
      <aside class="left-sidebar">
        <div class="filter-group">
          <div class="filter-label">搜索</div>
          <input type="text" class="filter-input" placeholder="搜索后门文献..." v-model="search" />
        </div>
        <div class="filter-group">
          <div class="filter-label">方向</div>
          <select class="filter-select" v-model="direction">
            <option value="">全部方向</option>
            <option value="attack">攻击方向</option>
            <option value="defense">防御方向</option>
          </select>
        </div>
        <div class="filter-group" style="margin-bottom:0;">
          <div class="filter-label">资讯类型</div>
          <select class="filter-select" v-model="category">
            <option value="">全部类型</option>
            <option value="学术论文">学术论文</option>
            <option value="开源发布">开源发布</option>
            <option value="官方新闻">官方新闻</option>
          </select>
        </div>
      </aside>

      <!-- Center Content -->
      <main class="center-content">
        <div class="section-header">
          <div class="section-title">MLLM 后门攻击与防御专题合集</div>
          <div class="section-count">{{ filteredItems.length }} 条结果</div>
        </div>

        <div v-if="filteredItems.length" class="card-grid">
          <NewsCard v-for="item in filteredItems" :key="item.id" :item="item" />
        </div>
        <div v-else style="text-align:center;padding:60px 20px;color:var(--color-text-secondary);font-size:14px;">
          暂无后门专项资讯
        </div>
      </main>

      <!-- Right Sidebar: direction categories -->
      <aside class="right-sidebar">
        <div class="filter-label">攻击 / 防御方向</div>
        <button
          v-for="t in directionTopics"
          :key="t.key"
          class="topic-btn"
          :class="{ active: direction === t.key }"
          @click="direction = direction === t.key ? '' : t.key"
        >
          <span class="topic-dot" :style="{ background: t.color }"></span>
          {{ t.label }}
          <span class="topic-count">{{ t.count }}</span>
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

const search = ref('')
const direction = ref('')
const category = ref('')

const DIRECTION_KEYWORDS = {
  'attack': {
    label: '攻击方向',
    color: '#e86868',
    kws: ['backdoor attack', 'attack', 'injection', 'poisoning', 'trojan', 'trigger', '后门攻击', '注入', '投毒']
  },
  'defense': {
    label: '防御方向',
    color: '#5cb884',
    kws: ['backdoor defense', 'defense', 'detection', 'removal', 'purification', 'mitigation', '后门防御', '检测', '去除', '净化', '防御']
  },
}

const indexItems = computed(() => {
  if (props.data && props.data.items) return props.data.items
  return []
})

const backdoorItems = computed(() => indexItems.value.filter(i => i.is_backdoor))

const attackCount = computed(() => backdoorItems.value.filter(i => {
  const t = (i.title || '').toLowerCase()
  return DIRECTION_KEYWORDS.attack.kws.some(k => t.includes(k))
}).length)

const defenseCount = computed(() => backdoorItems.value.filter(i => {
  const t = (i.title || '').toLowerCase()
  return DIRECTION_KEYWORDS.defense.kws.some(k => t.includes(k))
}).length)

const directionTopics = computed(() => [
  { key: 'attack', label: '后门攻击', color: '#e86868', count: attackCount.value },
  { key: 'defense', label: '后门防御', color: '#5cb884', count: defenseCount.value },
])

const filteredItems = computed(() => {
  let arr = backdoorItems.value
  if (search.value) {
    const q = search.value.toLowerCase()
    arr = arr.filter(i => (i.title || '').toLowerCase().includes(q))
  }
  if (direction.value) {
    const kws = DIRECTION_KEYWORDS[direction.value].kws
    arr = arr.filter(i => {
      const t = (i.title || '').toLowerCase()
      return kws.some(k => t.includes(k))
    })
  }
  if (category.value) arr = arr.filter(i => i.category === category.value)
  return arr
})
</script>
