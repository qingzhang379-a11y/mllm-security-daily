<template>
  <a
    class="news-card"
    :class="{ 'card-backdoor': item.is_backdoor }"
    :href="item.origin_url"
    target="_blank"
    rel="noopener noreferrer"
  >
    <div class="card-header">
      <span class="tag tag-category">{{ categoryLabel }}</span>
      <span v-if="item.is_backdoor" class="tag tag-backdoor">⚠️ 后门专项</span>
      <span>{{ item.publish_date }}</span>
    </div>

    <h3 class="card-title">
      {{ item.title }}
    </h3>

    <p v-if="item.abstract" class="card-abstract" :title="item.abstract">
      {{ item.abstract }}
    </p>

    <div class="card-footer">
      <span class="tag tag-source">{{ item.source }}</span>

      <template v-if="item.arxiv_id">
        <span class="tag tag-default">arXiv: {{ item.arxiv_id }}</span>
      </template>

      <span v-if="item.pdf_url" style="margin-left: auto;">
        <a :href="item.pdf_url" target="_blank" @click.stop>📄 PDF</a>
      </span>

      <a :href="item.origin_url" target="_blank" @click.stop>🔗 原文</a>
    </div>
  </a>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  item: { type: Object, required: true },
})

const categoryLabel = computed(() => {
  const map = {
    '学术论文': '📄 学术论文',
    '官方新闻': '🏢 官方新闻',
    '开源发布': '📦 开源发布',
    '会议动态': '🎯 会议动态',
  }
  return map[props.item.category] || props.item.category
})
</script>
