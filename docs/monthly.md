---
layout: page
---

<script setup>
import MonthlyPage from './.vitepress/theme/components/MonthlyPage.vue'
import indexData from './data/index.json'
</script>

<MonthlyPage :data="indexData" />
