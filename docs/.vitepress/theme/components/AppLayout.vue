<template>
  <div>
    <!-- Top Navigation (shared across all pages) -->
    <nav class="top-nav">
      <div class="top-nav-inner">
        <a :href="basePath" class="site-title" style="text-decoration:none;">MLLM 安全日报</a>
        <div class="nav-links">
          <a :href="basePath" class="nav-link" :class="{ active: activeNav === 'home' }"><i class="fas fa-house"></i> 首页</a>
          <a :href="basePath + 'daily'" class="nav-link" :class="{ active: activeNav === 'daily' }"><i class="fas fa-calendar-day"></i> 每日归档</a>
          <a :href="basePath + 'monthly'" class="nav-link" :class="{ active: activeNav === 'monthly' }"><i class="fas fa-chart-column"></i> 月度汇总</a>
          <a :href="basePath + 'backdoor'" class="nav-link" :class="{ active: activeNav === 'backdoor' }"><i class="fas fa-shield-halved"></i> 后门专题</a>
          <a :href="basePath + 'sources'" class="nav-link" :class="{ active: activeNav === 'sources' }"><i class="fas fa-rss"></i> 数据源订阅</a>
        </div>
        <button class="theme-toggle" @click="toggleTheme" title="主题切换">
          {{ isDark ? '☀️' : '🌙' }}
        </button>
      </div>
    </nav>

    <!-- Page Content -->
    <slot />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'

defineProps({
  activeNav: { type: String, default: 'home' },
})

const basePath = import.meta.env.BASE_URL || '/'

const isDark = ref(true)
function toggleTheme() {
  isDark.value = !isDark.value
  document.documentElement.classList.toggle('dark', isDark.value)
  localStorage.setItem('mllm-dark-mode', String(isDark.value))
}
onMounted(() => {
  // Respect saved preference; default to dark for research dashboard
  const stored = localStorage.getItem('mllm-dark-mode')
  isDark.value = stored === null ? true : stored === 'true'
  document.documentElement.classList.toggle('dark', isDark.value)
})
</script>
