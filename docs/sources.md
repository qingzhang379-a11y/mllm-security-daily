---
layout: page
---

<script setup>
import SourcesPage from './.vitepress/theme/components/SourcesPage.vue'
import indexData from './data/index.json'
import keywordsData from './data/keywords.json'
</script>

<SourcesPage :data="indexData" :keywords="keywordsData" />
