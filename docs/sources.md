---
layout: page
---

<script setup>
import SourcesPage from './.vitepress/theme/components/SourcesPage.vue'
import indexData from './data/index.json'
</script>

<SourcesPage :data="indexData" />
