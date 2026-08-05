<template>
  <!-- 笔记抽屉：Teleport 到 body，从右侧滑出 -->
  <Teleport to="body">
    <Transition name="note-fade">
      <div v-if="visible" class="note-mask" @click.self="close"></div>
    </Transition>

    <Transition name="note-slide">
      <aside v-if="visible" class="note-drawer" role="dialog" aria-label="资讯笔记">
        <header class="note-drawer-header">
          <div class="note-drawer-title">
            <i class="fas fa-note-sticky"></i> 研究笔记
          </div>
          <button class="note-close-btn" @click="close" title="关闭">
            <i class="fas fa-xmark"></i>
          </button>
        </header>

        <div class="note-drawer-body">
          <!-- 当前资讯信息 -->
          <div class="note-target">
            <div class="note-target-title">{{ currentItem?.title || '' }}</div>
            <a
              v-if="currentItem?.origin_url"
              :href="currentItem.origin_url"
              target="_blank"
              rel="noopener noreferrer"
              class="note-target-link"
            >
              <i class="fas fa-arrow-up-right-from-square"></i>
              {{ currentItem.origin_url }}
            </a>
            <div v-else class="note-target-link muted">暂无来源链接</div>
          </div>

          <!-- 多行笔记编辑区 -->
          <div class="note-editor">
            <textarea
              class="note-textarea"
              v-model="draft"
              :placeholder="'记录你的想法…\n可多行输入，适配文献思路记录、实验备注等场景。'"
              spellcheck="false"
            ></textarea>
            <div class="note-editor-meta">
              <span v-if="draft.trim()" class="note-char-count">
                {{ draft.length }} 字
              </span>
              <span v-else class="note-char-count">空白笔记保存后自动清除</span>
            </div>
          </div>
        </div>

        <footer class="note-drawer-footer">
          <button class="note-btn note-btn-ghost" @click="onClear" :disabled="!draft.trim()">
            <i class="fas fa-eraser"></i> 清空笔记
          </button>
          <button class="note-btn note-btn-primary" @click="onSave" :disabled="!draft.trim()">
            <i class="fas fa-floppy-disk"></i> 保存笔记
          </button>
        </footer>
      </aside>
    </Transition>
  </Teleport>
</template>

<script setup>
import { ref, computed, watch, nextTick } from 'vue'
import { useNotes } from '../composables/useNotes.js'

const props = defineProps({
  // 当前抽屉展示的资讯（完整对象）
  item: { type: Object, default: null },
})

const emit = defineEmits(['close'])

const { getNote, saveNote, clearNote, closeNote } = useNotes()
const draft = ref('')

const visible = computed(() => Boolean(props.item))

// 打开抽屉时加载已有笔记
watch(
  () => props.item,
  (item) => {
    if (item) {
      draft.value = getNote(item.id || item.origin_url || '') || ''
      // 等待抽屉渲染完成后聚焦输入框
      nextTick(() => {
        const ta = document.querySelector('.note-textarea')
        if (ta) ta.focus()
      })
    } else {
      draft.value = ''
    }
  },
  { immediate: true }
)

const currentItem = computed(() => props.item)

function close() {
  closeNote()
  emit('close')
}

function onSave() {
  if (!props.item) return
  saveNote(props.item.id || props.item.origin_url || '', draft.value)
}

function onClear() {
  if (!props.item) return
  clearNote(props.item.id || props.item.origin_url || '')
  draft.value = ''
}
</script>
