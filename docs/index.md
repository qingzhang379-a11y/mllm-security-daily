---
layout: page
---

<script setup>
import HomePage from './.vitepress/theme/components/HomePage.vue'
import latestData from './data/latest.json'
</script>

<HomePage :data="latestData" />
