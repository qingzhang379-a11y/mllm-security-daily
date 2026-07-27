<template>
  <div class="pagination" v-if="totalPages > 1">
    <button :disabled="current <= 1" @click="goTo(1)">«</button>
    <button :disabled="current <= 1" @click="goTo(current - 1)">‹</button>

    <template v-for="page in visiblePages" :key="page">
      <button
        v-if="page !== '...'"
        :class="{ active: page === current }"
        @click="goTo(page)"
      >
        {{ page }}
      </button>
      <span v-else style="padding: 0 4px;">...</span>
    </template>

    <button :disabled="current >= totalPages" @click="goTo(current + 1)">›</button>
    <button :disabled="current >= totalPages" @click="goTo(totalPages)">»</button>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  current: { type: Number, default: 1 },
  total: { type: Number, default: 0 },
  pageSize: { type: Number, default: 20 },
})

const emit = defineEmits(['update:current'])

const totalPages = computed(() => Math.max(1, Math.ceil(props.total / props.pageSize)))

const visiblePages = computed(() => {
  const pages = []
  const total = totalPages.value
  const cur = props.current

  if (total <= 7) {
    for (let i = 1; i <= total; i++) pages.push(i)
    return pages
  }

  pages.push(1)
  if (cur > 3) pages.push('...')

  const start = Math.max(2, cur - 1)
  const end = Math.min(total - 1, cur + 1)
  for (let i = start; i <= end; i++) pages.push(i)

  if (cur < total - 2) pages.push('...')
  pages.push(total)

  return pages
})

function goTo(page) {
  if (page < 1 || page > totalPages.value) return
  emit('update:current', page)
}
</script>
