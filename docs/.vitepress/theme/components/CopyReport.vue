<template>
  <button class="copy-btn" :class="{ copied }" @click="copyText">
    {{ copied ? '✅ 已复制' : '📋 复制日报' }}
  </button>
</template>

<script setup>
import { ref } from 'vue'

const props = defineProps({
  items: { type: Array, required: true },
  date: { type: String, default: '' },
})

const copied = ref(false)

function copyText() {
  const lines = []
  lines.push(`MLLM 安全日报 - ${props.date || new Date().toISOString().slice(0, 10)}`)
  lines.push('='.repeat(50))
  lines.push(`总计 ${props.items.length} 条资讯`)
  lines.push('')

  const backdoorItems = props.items.filter(i => i.is_backdoor)
  const normalItems = props.items.filter(i => !i.is_backdoor)

  if (backdoorItems.length > 0) {
    lines.push('【后门专项】')
    backdoorItems.forEach((item, idx) => {
      lines.push(`${idx + 1}. [${item.category}] ${item.title}`)
      if (item.arxiv_id) lines.push(`   arXiv:${item.arxiv_id}`)
      lines.push(`   ${item.origin_url}`)
    })
    lines.push('')
  }

  if (normalItems.length > 0) {
    lines.push('【普通安全资讯】')
    normalItems.forEach((item, idx) => {
      lines.push(`${idx + 1}. [${item.category}] ${item.title}`)
      lines.push(`   ${item.origin_url}`)
    })
  }

  const text = lines.join('\n')
  navigator.clipboard.writeText(text).then(() => {
    copied.value = true
    setTimeout(() => { copied.value = false }, 2000)
  }).catch(() => {
    // fallback
    const ta = document.createElement('textarea')
    ta.value = text
    document.body.appendChild(ta)
    ta.select()
    document.execCommand('copy')
    document.body.removeChild(ta)
    copied.value = true
    setTimeout(() => { copied.value = false }, 2000)
  })
}
</script>
