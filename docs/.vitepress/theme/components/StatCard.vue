<template>
  <div class="stat-cards">
    <div class="stat-card">
      <div class="stat-label">当月资讯总数</div>
      <div class="stat-value">{{ stats.total || 0 }}</div>
    </div>
    <div class="stat-card">
      <div class="stat-label">论文数量</div>
      <div class="stat-value">{{ stats.papers || 0 }}</div>
    </div>
    <div class="stat-card">
      <div class="stat-label">开源项目</div>
      <div class="stat-value">{{ stats.opensource || 0 }}</div>
    </div>
    <div class="stat-card">
      <div class="stat-label">后门相关文献</div>
      <div class="stat-value stat-backdoor">{{ stats.backdoor || 0 }}</div>
    </div>
  </div>
</template>

<script setup>
defineProps({
  stats: { type: Object, default: () => ({}) },
})
</script>
