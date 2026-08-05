/**
 * 资讯笔记 composable（模块级单例，跨页面共享）
 * 笔记按资讯 ID 绑定，localStorage 持久化，刷新后仍可读取。
 */
import { reactive, ref } from 'vue'

const STORAGE_KEY = 'mllm-notes-v1'

// 全局笔记表：{ [itemId]: text }
const notes = reactive({})
// 当前打开的笔记抽屉对应的资讯 ID
const activeNoteId = ref('')

// 模块加载时从 localStorage 恢复（仅客户端；SSR 构建期无 localStorage）
if (typeof window !== 'undefined' && typeof localStorage !== 'undefined') {
  try {
    const raw = localStorage.getItem(STORAGE_KEY)
    if (raw) Object.assign(notes, JSON.parse(raw))
  } catch (e) {
    /* ignore corrupted storage */
  }
}

function persist() {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(notes))
  } catch (e) {
    /* storage full / unavailable - ignore */
  }
}

export function useNotes() {
  function openNote(id) {
    activeNoteId.value = id
  }

  function closeNote() {
    activeNoteId.value = ''
  }

  function getNote(id) {
    return notes[id] || ''
  }

  function hasNote(id) {
    return Boolean(notes[id] && notes[id].trim())
  }

  function saveNote(id, text) {
    if (text && text.trim()) {
      notes[id] = text
    } else {
      delete notes[id]
    }
    persist()
  }

  function clearNote(id) {
    delete notes[id]
    persist()
  }

  return {
    notes,
    activeNoteId,
    openNote,
    closeNote,
    getNote,
    hasNote,
    saveNote,
    clearNote,
  }
}
