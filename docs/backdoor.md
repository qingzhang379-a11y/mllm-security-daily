---
layout: page
---

<script setup>
import BackdoorPage from './.vitepress/theme/components/BackdoorPage.vue'
import indexData from './data/index.json'
</script>

<BackdoorPage :data="indexData" />
