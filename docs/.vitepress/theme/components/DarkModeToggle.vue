<template>
  <button class="dark-toggle-btn" @click="toggle" :title="isDark ? '亮色模式' : '暗色模式'">
    {{ isDark ? '☀️' : '🌙' }}
  </button>
</template>

<script setup>
import { ref, onMounted } from 'vue'

const isDark = ref(false)

onMounted(() => {
  const stored = localStorage.getItem('mllm-dark-mode')
  isDark.value = stored !== null ? stored === 'true' : window.matchMedia('(prefers-color-scheme: dark)').matches
  apply()
})

function toggle() {
  isDark.value = !isDark.value
  apply()
}

function apply() {
  document.documentElement.classList.toggle('dark', isDark.value)
  localStorage.setItem('mllm-dark-mode', String(isDark.value))
}
</script>
