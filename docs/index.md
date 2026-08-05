---
layout: page
---

<script setup>
import HomePage from './.vitepress/theme/components/HomePage.vue'
import allData from './data/all_news.json'
</script>

<HomePage :data="allData" />
