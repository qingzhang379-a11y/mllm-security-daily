<template>
  <a
    class="news-card"
    :class="[
      categoryClass,
      { 'card-backdoor': item.is_backdoor }
    ]"
    :href="item.origin_url"
    target="_blank"
    rel="noopener noreferrer"
  >
    <div class="card-header">
      <!-- Category icon (linear) -->
      <span class="cat-icon" :class="categoryClass">
        <i :class="categoryIcon"></i>
      </span>

      <!-- Backdoor warning badge (coexists with category border) -->
      <span v-if="item.is_backdoor" class="tag tag-backdoor">
        <i class="fas fa-triangle-exclamation"></i> 后门专项
      </span>

      <span class="tag tag-source">
        <i class="fas fa-building"></i> {{ item.source }}
      </span>

      <span class="card-time">
        <i class="fas fa-clock"></i> {{ item.publish_date }}
      </span>
    </div>

    <h3 class="card-title">{{ item.title }}</h3>

    <p v-if="item.abstract" class="card-abstract">{{ item.abstract }}</p>

    <div class="card-footer">
      <span v-if="item.arxiv_id" class="tag tag-arxiv">
        <i class="fas fa-scroll"></i> arXiv:{{ item.arxiv_id }}
      </span>
      <span class="spacer"></span>
      <a v-if="item.pdf_url" :href="item.pdf_url" target="_blank" @click.stop>
        <i class="fas fa-file-pdf"></i> PDF
      </a>
      <a :href="item.origin_url" target="_blank" @click.stop>
        <i class="fas fa-arrow-up-right-from-square"></i> 原文
      </a>
      <!-- 笔记按钮：已有笔记时显示小圆点 -->
      <button class="note-btn card-note-btn" @click.stop="onOpenNote" title="资讯笔记">
        <i class="fas fa-note-sticky"></i> 笔记
        <span v-if="hasSavedNote" class="note-dot"></span>
      </button>
    </div>
  </a>

  <!-- 笔记抽屉 -->
  <NoteDrawer :item="noteItem" @close="noteItem = null" />
</template>

<script setup>
import { ref, computed } from 'vue'
import NoteDrawer from './NoteDrawer.vue'
import { useNotes } from '../composables/useNotes.js'

const props = defineProps({ item: { type: Object, required: true } })

const { hasNote } = useNotes()
const noteItem = ref(null)

// 是否有已保存的笔记（小圆点标记）
const hasSavedNote = computed(() => hasNote(props.item.id || props.item.origin_url || ''))

function onOpenNote() {
  noteItem.value = props.item
}

const CATEGORY_MAP = {
  '学术论文': { cls: 'cat-paper', icon: 'fas fa-file-lines' },
  '官方新闻': { cls: 'cat-news', icon: 'fas fa-newspaper' },
  '开源发布': { cls: 'cat-opensource', icon: 'fas fa-code' },
  '会议动态': { cls: 'cat-conference', icon: 'fas fa-calendar-days' },
}

const categoryClass = computed(() => {
  const cfg = CATEGORY_MAP[props.item.category]
  return cfg ? cfg.cls : 'cat-default'
})

const categoryIcon = computed(() => {
  const cfg = CATEGORY_MAP[props.item.category]
  return cfg ? cfg.icon : 'fas fa-circle-info'
})
</script>
