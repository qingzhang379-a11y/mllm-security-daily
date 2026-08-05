---
layout: page
---

<script setup>
import DailyPage from './.vitepress/theme/components/DailyPage.vue'
import indexData from './data/index.json'
</script>

<DailyPage :data="indexData" />
