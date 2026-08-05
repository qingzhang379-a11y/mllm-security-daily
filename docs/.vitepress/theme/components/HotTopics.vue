<template>
  <aside class="right-sidebar">
    <div class="filter-label"><i class="fas fa-fire"></i> 热门专题</div>
    <button
      v-for="t in topics"
      :key="t.key"
      class="topic-btn"
      :class="{ active: activeTopic === t.key }"
      :style="btnStyle(t)"
      @click="select(t.key)"
    >
      <span class="topic-dot" :style="{ background: t.color }"></span>
      <span class="topic-label">{{ t.label }}</span>
      <span class="topic-count">
        <i class="fas fa-chart-simple"></i> {{ t.count }}
      </span>
    </button>
  </aside>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  topics: { type: Array, default: () => [] },
  activeTopic: { type: String, default: '' },
})
const emit = defineEmits(['select'])
function select(key) { emit('select', key) }

// Dynamic sizing based on count data (data-driven, no hardcoding)
const maxCount = computed(() => Math.max(1, ...props.topics.map(t => t.count)))

function btnStyle(t) {
  const ratio = t.count / maxCount.value
  return {
    fontSize: `${13 + ratio * 3}px`,
    fontWeight: 500 + Math.round(ratio * 200),
  }
}
</script>
