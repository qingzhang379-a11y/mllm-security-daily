<template>
  <div class="category-panel">
    <div class="category-panel-header" @click="$emit('toggle')">
      <div class="panel-header-left">
        <div class="panel-icon" :class="config.cls">{{ config.icon }}</div>
        <div class="panel-title-text">
          <span class="panel-title">{{ category }}</span>
          <span class="panel-subtitle">{{ stats.total }} 条{{ stats.backdoor ? ` · 后门 ${stats.backdoor}` : '' }}</span>
        </div>
      </div>
      <span class="panel-toggle-icon">{{ collapsed ? '▼' : '▲' }}</span>
    </div>

    <div v-if="!collapsed" class="panel-body">
      <div v-if="items.length === 0" class="panel-empty">
        <template v-if="stats.total > 0">筛选无匹配结果</template>
        <template v-else>暂无资讯</template>
      </div>

      <template v-for="item in items" :key="item.id">
        <NewsCard :item="item" :view="view" />
      </template>

      <div v-if="stats.total > items.length" class="panel-footer" @click="$emit('toggle')">
        展开其余 {{ stats.total - items.length }} 条
      </div>
    </div>
  </div>
</template>

<script setup>
import NewsCard from './NewsCard.vue'

defineProps({
  category: { type: String, required: true },
  items: { type: Array, required: true },
  collapsed: { type: Boolean, default: true },
  stats: { type: Object, default: () => ({}) },
  config: { type: Object, default: () => ({ icon: '📄', cls: '' }) },
  view: { type: String, default: 'card' },
})

defineEmits(['toggle'])
</script>
