/**
 * 资讯笔记 composable（模块级单例，跨页面共享）
 * 笔记按资讯 ID 绑定，localStorage 持久化，刷新后仍可读取。
 * 每条笔记包含：text（正文）、rating（重要程度 1-5）。
 * 已读状态独立存储（readSet）。
 */
import { reactive, ref } from 'vue'

const STORAGE_KEY = 'mllm-notes-v1'
const READ_KEY = 'mllm-read-v1'

// 全局笔记表：{ [itemId]: { text, rating } }（兼容旧格式 { [itemId]: string }）
const notes = reactive({})
// 全局已读表：{ [itemId]: true }
const readSet = reactive({})
// 当前打开的笔记抽屉对应的资讯 ID
const activeNoteId = ref('')

// 是否已从 localStorage 恢复过（模块级单例，hydration 时只会恢复一次）
let restored = false

function restore() {
  // 仅客户端可恢复；SSR 构建/渲染期跳过
  if (typeof window === 'undefined' || typeof localStorage === 'undefined') return
  if (restored) return
  restored = true
  try {
    const raw = localStorage.getItem(STORAGE_KEY)
    if (raw) Object.assign(notes, JSON.parse(raw))
  } catch (e) {
    /* ignore corrupted storage */
  }
  try {
    const raw = localStorage.getItem(READ_KEY)
    if (raw) Object.assign(readSet, JSON.parse(raw))
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

function persistRead() {
  try {
    localStorage.setItem(READ_KEY, JSON.stringify(readSet))
  } catch (e) {
    /* storage full / unavailable - ignore */
  }
}

export function useNotes() {
  // 客户端 hydration 后首次调用时从 localStorage 恢复（SSR 期跳过）
  restore()

  function openNote(id) {
    activeNoteId.value = id
  }

  function closeNote() {
    activeNoteId.value = ''
  }

  // 笔记正文（兼容旧字符串格式）
  function getNote(id) {
    const n = notes[id]
    if (!n) return ''
    return typeof n === 'string' ? n : n.text || ''
  }

  // 重要程度（0 表示未评分）
  function getRating(id) {
    const n = notes[id]
    if (!n || typeof n === 'string') return 0
    return n.rating || 0
  }

  function hasNote(id) {
    return Boolean(getNote(id).trim())
  }

  function saveNote(id, text, rating = 0) {
    const r = Math.max(0, Math.min(5, Math.floor(Number(rating) || 0)))
    const t = text || ''
    if (t.trim() || r > 0) {
      notes[id] = { text: t, rating: r }
    } else {
      delete notes[id]
    }
    persist()
  }

  function clearNote(id) {
    delete notes[id]
    persist()
  }

  // 已读状态
  function isRead(id) {
    return Boolean(readSet[id])
  }

  function toggleRead(id) {
    if (readSet[id]) delete readSet[id]
    else readSet[id] = true
    persistRead()
  }

  return {
    notes,
    readSet,
    activeNoteId,
    openNote,
    closeNote,
    getNote,
    getRating,
    hasNote,
    saveNote,
    clearNote,
    isRead,
    toggleRead,
  }
}
