<template>
  <AppLayout activeNav="sources">
    <!-- Stats Bar -->
    <div class="stats-bar">
      <div class="stat-card">
        <div class="stat-icon blue">📡</div>
        <div class="stat-info">
          <div class="stat-label">官方信源</div>
          <div class="stat-value">{{ sourceStats.totalSources }}</div>
          <div class="stat-sub">RSS + API + 爬虫</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon green">📰</div>
        <div class="stat-info">
          <div class="stat-label">资讯总量</div>
          <div class="stat-value">{{ totalItems }}</div>
          <div class="stat-sub">全部官方采集</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon red">⚠️</div>
        <div class="stat-info">
          <div class="stat-label">后门专项</div>
          <div class="stat-value red">{{ backdoorItems }}</div>
          <div class="stat-sub">攻击 / 防御 / 投毒</div>
        </div>
      </div>
    </div>

    <div class="main-layout">
      <!-- Left Sidebar -->
      <aside class="left-sidebar">
        <div class="filter-group">
          <div class="filter-label">采集规则</div>
          <div style="font-size:13px;color:var(--color-text-secondary);line-height:1.8;">
            <div>• 每日 UTC 02:00 自动采集</div>
            <div>• 严格遵守 robots.txt</div>
            <div>• URL + 标题双重去重</div>
            <div>• 海外源自动切换国内镜像</div>
          </div>
        </div>
        <div class="filter-group">
          <div class="filter-label">排除内容</div>
          <div style="font-size:13px;color:var(--color-text-secondary);line-height:1.8;">
            <div>✗ 个人博客 / 自媒体</div>
            <div>✗ 论坛讨论帖</div>
            <div>✗ 非官方解读文章</div>
          </div>
        </div>
      </aside>

      <!-- Center Content -->
      <main class="center-content">
        <div class="section-header">
          <div class="section-title">官方数据源清单</div>
          <div class="section-count">仅收录官方发布内容</div>
        </div>

        <div class="source-panel">
          <div class="source-group">
            <div class="filter-label" style="font-size:14px;margin-bottom:12px;">📄 学术论文源</div>
            <div v-for="s in paperSources" :key="s.name" class="source-row">
              <span class="source-name">{{ s.name }}</span>
              <span class="source-type">{{ s.type }}</span>
              <span class="source-method">{{ s.method }}</span>
            </div>
          </div>
          <div class="source-group">
            <div class="filter-label" style="font-size:14px;margin-bottom:12px;">🏢 企业官方 Blog</div>
            <div v-for="s in blogSources" :key="s.name" class="source-row">
              <span class="source-name">{{ s.name }}</span>
              <span class="source-type">{{ s.type }}</span>
              <span class="source-method">{{ s.method }}</span>
            </div>
          </div>
          <div class="source-group">
            <div class="filter-label" style="font-size:14px;margin-bottom:12px;">📦 开源发布源</div>
            <div v-for="s in openSources" :key="s.name" class="source-row">
              <span class="source-name">{{ s.name }}</span>
              <span class="source-type">{{ s.type }}</span>
              <span class="source-method">{{ s.method }}</span>
            </div>
          </div>
          <div class="source-group">
            <div class="filter-label" style="font-size:14px;margin-bottom:12px;">🌐 国内平台</div>
            <div v-for="s in cnSources" :key="s.name" class="source-row">
              <span class="source-name">{{ s.name }}</span>
              <span class="source-type">{{ s.type }}</span>
              <span class="source-method">{{ s.method }}</span>
            </div>
          </div>
        </div>

        <!-- ====== 关键词管理区域 ====== -->
        <div class="keyword-section" style="margin-top:28px;">
          <div class="section-header">
            <div class="section-title">🔑 采集关键词管理</div>
            <div class="section-count">编辑后点击「保存到仓库」，云端下次采集自动生效</div>
          </div>

          <div v-for="(g, gName) in editableKeywords" :key="gName" class="kw-group-card">
            <div class="kw-group-header" @click="toggleGroup(gName)">
              <span class="kw-group-name">{{ groupLabels[gName] || gName }}</span>
              <span class="kw-group-count">{{ g.en.length + g.zh.length }} 词</span>
              <span class="kw-expand-icon">{{ openGroups[gName] ? '▾' : '▸' }}</span>
            </div>
            <div v-show="openGroups[gName]" class="kw-group-body">
              <div class="kw-lang-row">
                <div class="kw-lang-label">🇬🇧 English ({{ g.en.length }})</div>
                <div class="kw-tags">
                  <span v-for="(w, wi) in g.en" :key="'en-'+wi" class="kw-tag">
                    {{ w }}
                    <button class="kw-del" @click="removeWord(gName, 'en', wi)">×</button>
                  </span>
                  <span v-if="g.en.length === 0" class="kw-empty">暂无英文词</span>
                </div>
              </div>
              <div class="kw-lang-row">
                <div class="kw-lang-label">🇨🇳 中文 ({{ g.zh.length }})</div>
                <div class="kw-tags">
                  <span v-for="(w, wi) in g.zh" :key="'zh-'+wi" class="kw-tag">
                    {{ w }}
                    <button class="kw-del" @click="removeWord(gName, 'zh', wi)">×</button>
                  </span>
                  <span v-if="g.zh.length === 0" class="kw-empty">暂无中文词</span>
                </div>
              </div>
              <div class="kw-add-row">
                <select v-model="addLang" class="kw-select">
                  <option value="en">EN</option>
                  <option value="zh">中文</option>
                </select>
                <input v-model="addWord" class="kw-input" placeholder="输入新词" @keyup.enter="addWordToGroup(gName)" />
                <button class="kw-add-btn" @click="addWordToGroup(gName)">添加</button>
              </div>
            </div>
          </div>

          <!-- Save Button -->
          <div class="kw-save-row">
            <button class="kw-save-btn" :disabled="saving" @click="saveToRepo">
              {{ saving ? '保存中...' : '💾 保存到仓库' }}
            </button>
            <button v-if="patSet" class="kw-clear-btn" @click="clearPat">清除本机 Token</button>
            <span class="kw-pat-status">{{ patSet ? '✅ 已配置 Token' : '首次保存需输入 GitHub Token' }}</span>
            <span v-if="saveMsg" class="kw-save-msg" :class="{ error: saveError }">{{ saveMsg }}</span>
          </div>
        </div>
      </main>

      <!-- Right Sidebar -->
      <aside class="right-sidebar">
        <div class="filter-label">RSS 订阅</div>
        <button class="topic-btn" @click="copyRss">
          <span class="topic-dot" style="background:#e86868;"></span>
          后门专题 RSS
          <span class="topic-count">{{ backdoorItems }}</span>
        </button>
        <button class="topic-btn" @click="copyAllRss">
          <span class="topic-dot" style="background:#5d9fd6;"></span>
          全量 RSS
        </button>
        <div style="font-size:11px;color:var(--color-text-secondary);margin-top:16px;line-height:1.6;">
          RSS 链接点击复制，可导入任意阅读器
        </div>
      </aside>
    </div>
  </AppLayout>
</template>

<script setup>
import { ref, computed, reactive } from 'vue'
import AppLayout from './AppLayout.vue'

const props = defineProps({
  data: { type: Object, default: () => ({ items: [] }) },
  keywords: { type: Object, default: () => ({ groups: {} }) },
})

const indexItems = computed(() => {
  if (props.data && props.data.items) return props.data.items
  return []
})
const totalItems = computed(() => indexItems.value.length)
const backdoorItems = computed(() => indexItems.value.filter(i => i.is_backdoor).length)
const sourceStats = computed(() => ({
  totalSources: paperSources.value.length + blogSources.value.length + openSources.value.length + cnSources.value.length,
}))

// Source lists (hardcoded as before)
const paperSources = computed(() => [
  { name: 'arXiv API (MLLM+Backdoor)', type: '预印本', method: 'API 检索' },
  { name: 'arXiv API (VLM+Backdoor)', type: '预印本', method: 'API 检索' },
  { name: 'arXiv API (MLLM+Safety)', type: '预印本', method: 'API 检索' },
  { name: 'arXiv API (MLLM+Jailbreak)', type: '预印本', method: 'API 检索' },
  { name: 'CVPR / ICCV / ECCV', type: '顶会', method: 'Proceeding 页面' },
  { name: 'NeurIPS / ICML / ICLR', type: '顶会', method: 'Proceeding 页面' },
  { name: 'ACL / AAAI', type: '顶会', method: 'Proceeding 页面' },
])
const blogSources = computed(() => [
  { name: 'OpenAI Blog', type: '官方', method: 'RSS' },
  { name: 'Google DeepMind Blog', type: '官方', method: 'RSS' },
  { name: 'Meta AI Blog', type: '官方', method: 'RSS' },
  { name: 'Microsoft Research', type: '官方', method: 'RSS' },
  { name: 'Anthropic Blog', type: '官方', method: 'RSS' },
])
const openSources = computed(() => [
  { name: 'Hugging Face Blog', type: '官方', method: 'RSS' },
  { name: 'Hugging Face Papers', type: '官方', method: 'RSS' },
])
const cnSources = computed(() => [
  { name: '机器之心 (官方首发)', type: '学术媒体', method: 'RSS / 爬虫' },
  { name: '智源社区 (官方稿件)', type: '学术社区', method: '爬虫' },
  { name: 'BAAI 智源研究院', type: '研究院', method: '爬虫' },
  { name: 'Qwen 团队 Blog', type: '企业', method: '爬虫' },
])

// ===== 关键词管理 =====
const groupLabels = {
  safety_filter: '🔒 Safety 安全筛选器（门禁）',
  backdoor: '🐞 Backdoor 后门攻击',
  security: '🛡️ Security 安全通用',
  trustworthy: '🤝 Trustworthy 可信性',
  testing: '🧪 Testing 安全测试/验证',
  robustness: '💪 Robustness 鲁棒性',
}

const openGroups = reactive({
  safety_filter: true,
  backdoor: false,
  security: false,
  trustworthy: false,
  testing: false,
  robustness: false,
})
function toggleGroup(name) { openGroups[name] = !openGroups[name] }

// 初始化 editableKeywords 从 props.keywords
const editableKeywords = reactive({})
function initKeywords() {
  const raw = (props.keywords && props.keywords.groups) || {}
  const groups = ['safety_filter', 'backdoor', 'security', 'trustworthy', 'testing', 'robustness']
  for (const g of groups) {
    const src = raw[g] || { en: [], zh: [] }
    editableKeywords[g] = {
      en: [...(src.en || [])],
      zh: [...(src.zh || [])],
    }
  }
}
initKeywords()

// 添加/删除词
const addLang = ref('en')
const addWord = ref('')
function addWordToGroup(gName) {
  const w = addWord.value.trim()
  if (!w) return
  const lang = addLang.value
  const list = editableKeywords[gName][lang]
  if (list.includes(w)) {
    alert(`「${w}」已存在`)
    return
  }
  list.push(w)
  addWord.value = ''
}
function removeWord(gName, lang, idx) {
  editableKeywords[gName][lang].splice(idx, 1)
}

// 保存到仓库（通过 GitHub API 直接写入 keywords.yaml）
const basePath = import.meta.env.BASE_URL || '/'
const saving = ref(false)
const saveMsg = ref('')
const saveError = ref(false)

// GitHub PAT 管理（存在浏览器 localStorage，用于调 GitHub API 写回 keywords.yaml）
// 注意：localStorage 仅客户端可用，SSR 阶段不能访问，故初始 false + onMounted 里检测
const PAT_KEY = 'mllm_github_pat'
const patSet = ref(false)

import { onMounted } from 'vue'
onMounted(() => {
  if (typeof localStorage !== 'undefined') {
    patSet.value = !!localStorage.getItem(PAT_KEY)
  }
})

function getPat() {
  let pat = localStorage.getItem(PAT_KEY)
  if (!pat) {
    pat = prompt(
      '需要 GitHub Personal Access Token 才能写回仓库。\n\n' +
      '请在 GitHub: Settings → Developer settings → Personal access tokens → ' +
      'Fine-grained tokens 创建（仓库 mllm-security-daily，Contents 读写权限），然后粘贴到这里。\n\n' +
      '（该 Token 仅保存在你本机浏览器 localStorage）'
    )
    if (!pat) return null
    localStorage.setItem(PAT_KEY, pat)
    patSet.value = true
  }
  return pat
}
function clearPat() {
  localStorage.removeItem(PAT_KEY)
  patSet.value = false
  saveMsg.value = '已清除本机 Token'
  saveError.value = false
}

async function saveToRepo() {
  saving.value = true
  saveMsg.value = ''
  saveError.value = false

  try {
    const token = getPat()
    if (!token) {
      saveMsg.value = '未提供 Token，已取消保存'
      saveError.value = false
      return
    }
    const authHeader = { Authorization: `Bearer ${token}`, Accept: 'application/vnd.github+json' }

    const owner = 'qingzhang379-a11y'
    const repo = 'mllm-security-daily'
    const path = 'collector/config/keywords.yaml'
    const apiBase = `https://api.github.com/repos/${owner}/${repo}/contents/${path}`

    // 获取当前文件 SHA
    const getResp = await fetch(apiBase, { headers: authHeader })
    if (!getResp.ok) {
      throw new Error(`获取文件信息失败 (HTTP ${getResp.status})${getResp.status === 401 ? '，Token 无效或无权限' : ''}`)
    }
    const fileInfo = await getResp.json()
    const sha = fileInfo.sha

    // 构造 YAML 内容
    const yamlLines = [
      '# ===== 采集关键词（由前端数据源页编辑）=====',
      `# 更新时间: ${new Date().toISOString()}`,
      '# 每次采集时 KeywordMatcher 按这些词过滤/分类资讯',
      '',
    ]
    for (const g of ['safety_filter', 'backdoor', 'security', 'trustworthy', 'testing', 'robustness']) {
      const src = editableKeywords[g]
      yamlLines.push(`${g}:`, `  en:`)
      for (const w of src.en) yamlLines.push(`    - "${w}"`)
      yamlLines.push(`  zh:`)
      for (const w of src.zh) yamlLines.push(`    - "${w}"`)
    }
    const content = yamlLines.join('\n')

    // base64 编码
    const bytes = new TextEncoder().encode(content)
    let binary = ''
    for (let i = 0; i < bytes.length; i++) binary += String.fromCharCode(bytes[i])
    const b64Content = btoa(binary)

    const putResp = await fetch(apiBase, {
      method: 'PUT',
      headers: { ...authHeader, 'Content-Type': 'application/json' },
      body: JSON.stringify({
        message: `chore(keywords): update from sources page ${new Date().toISOString().slice(0, 10)}`,
        content: b64Content,
        sha: sha,
      })
    })

    if (!putResp.ok) {
      const errBody = await putResp.json().catch(() => ({}))
      throw new Error(errBody.message || `保存失败 (HTTP ${putResp.status})`)
    }

    saveMsg.value = '✅ 关键词已写回仓库，下次云端采集自动生效！'
    saveError.value = false
  } catch (e) {
    saveMsg.value = `❌ ${e.message}`
    saveError.value = true
  } finally {
    saving.value = false
  }
}

function copyRss() {
  navigator.clipboard.writeText('https://your-domain/rss-backdoor.xml')
  alert('后门专题 RSS 链接已复制')
}
function copyAllRss() {
  navigator.clipboard.writeText('https://your-domain/rss.xml')
  alert('全量 RSS 链接已复制')
}
</script>

<style scoped>
.source-panel {
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  padding: 24px;
}
.source-group { margin-bottom: 28px; }
.source-group:last-child { margin-bottom: 0; }
.source-row {
  display: flex; align-items: center; gap: 12px;
  padding: 10px 12px; border-bottom: 1px solid var(--color-border);
  font-size: 13px;
}
.source-row:last-child { border-bottom: none; }
.source-name { flex: 1; color: var(--color-text); font-weight: 500; }
.source-type {
  padding: 2px 8px; border-radius: 4px;
  background: var(--color-primary-glow);
  color: var(--color-primary-light); font-size: 11px;
  white-space: nowrap;
}
.source-method { font-size: 11px; color: var(--color-text-secondary); white-space: nowrap; width: 90px; text-align: right; }

/* ===== 关键词管理样式 ===== */
.keyword-section {
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  padding: 20px 24px;
}
.kw-group-card {
  border: 1px solid var(--color-border);
  border-radius: 8px;
  margin-bottom: 12px;
  overflow: hidden;
}
.kw-group-header {
  display: flex; align-items: center; gap: 12px;
  padding: 12px 16px;
  cursor: pointer;
  background: var(--color-primary-glow);
  user-select: none;
}
.kw-group-name { flex: 1; font-weight: 600; font-size: 14px; }
.kw-group-count { font-size: 12px; color: var(--color-text-secondary); }
.kw-expand-icon { font-size: 12px; transition: transform .2s; }
.kw-group-body { padding: 12px 16px; }
.kw-lang-row { margin-bottom: 12px; }
.kw-lang-label { font-size: 12px; color: var(--color-text-secondary); margin-bottom: 6px; }
.kw-tags { display: flex; flex-wrap: wrap; gap: 6px; }
.kw-tag {
  display: inline-flex; align-items: center; gap: 4px;
  padding: 3px 8px; border-radius: 4px;
  background: var(--color-primary-glow);
  border: 1px solid var(--color-border);
  font-size: 12px;
}
.kw-del {
  background: none; border: none; cursor: pointer;
  color: #e86868; font-size: 14px; line-height: 1; padding: 0 2px;
}
.kw-empty { font-size: 12px; color: var(--color-text-secondary); font-style: italic; }
.kw-add-row {
  display: flex; gap: 8px; align-items: center;
  margin-top: 8px;
}
.kw-select {
  padding: 4px 8px; border-radius: 4px; border: 1px solid var(--color-border);
  background: var(--color-surface); color: var(--color-text); font-size: 12px;
}
.kw-input {
  flex: 1; padding: 6px 10px; border-radius: 4px; border: 1px solid var(--color-border);
  background: var(--color-surface); color: var(--color-text); font-size: 13px;
}
.kw-add-btn {
  padding: 6px 14px; border-radius: 4px; border: none;
  background: var(--color-primary); color: #fff; cursor: pointer;
  font-size: 12px;
}
.kw-save-row {
  display: flex; align-items: center; gap: 16px;
  margin-top: 20px; padding-top: 16px;
  border-top: 1px solid var(--color-border);
}
.kw-save-btn {
  padding: 10px 28px; border-radius: 6px; border: none;
  background: var(--color-primary); color: #fff; cursor: pointer;
  font-size: 14px; font-weight: 500;
}
.kw-save-btn:disabled { opacity: .6; cursor: not-allowed; }
.kw-clear-btn {
  padding: 8px 14px; border-radius: 6px; border: 1px solid var(--color-border);
  background: transparent; color: var(--color-text-secondary); cursor: pointer;
  font-size: 12px;
}
.kw-pat-status { font-size: 12px; color: var(--color-text-secondary); }
.kw-save-msg { font-size: 13px; }
.kw-save-msg.error { color: #e86868; }
</style>