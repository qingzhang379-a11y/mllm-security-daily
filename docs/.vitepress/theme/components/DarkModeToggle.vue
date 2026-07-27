<template>
  <div class="dark-toggle" @click="toggle" :title="isDark ? '切换到亮色模式' : '切换到暗色模式'">
    {{ isDark ? '☀️' : '🌙' }}
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'

const isDark = ref(false)

onMounted(() => {
  // Check system preference
  const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches
  // Check stored preference
  const stored = localStorage.getItem('mllm-dark-mode')
  isDark.value = stored !== null ? stored === 'true' : prefersDark
  applyTheme()
})

function toggle() {
  isDark.value = !isDark.value
  applyTheme()
}

function applyTheme() {
  document.documentElement.classList.toggle('dark', isDark.value)
  localStorage.setItem('mllm-dark-mode', String(isDark.value))
}
</script>
