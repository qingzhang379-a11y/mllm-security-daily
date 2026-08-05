<template>
  <aside class="left-sidebar">
    <div class="filter-group">
      <div class="filter-label"><i class="fas fa-magnifying-glass"></i> 搜索</div>
      <input type="text" class="filter-input" placeholder="标题 / 摘要..." v-model="localSearch" @input="onSearch" />
    </div>

    <div class="filter-group">
      <div class="filter-label"><i class="fas fa-layer-group"></i> 资讯类型</div>
      <select class="filter-select" v-model="localCategory" @change="emitChange">
        <option value="">全部</option>
        <option value="学术论文">学术论文</option>
        <option value="官方新闻">官方新闻</option>
        <option value="开源发布">开源发布</option>
        <option value="会议动态">会议动态</option>
      </select>
    </div>

    <div class="filter-group">
      <div class="filter-label"><i class="fas fa-clock"></i> 时间范围</div>
      <select class="filter-select" v-model="localTimeRange" @change="emitChange">
        <option value="all">全部时间</option>
        <option value="7">近 7 天</option>
        <option value="30">近 30 天</option>
        <option value="90">近 90 天</option>
      </select>
    </div>

    <div class="filter-group">
      <div class="filter-label"><i class="fas fa-arrow-down-wide-short"></i> 排序</div>
      <select class="filter-select" v-model="localSort" @change="emitChange">
        <option value="date_desc">最新优先</option>
        <option value="date_asc">最早优先</option>
      </select>
    </div>

    <div class="filter-group" style="margin-bottom:0;">
      <label class="filter-switch">
        <input type="checkbox" v-model="localBackdoorOnly" @change="emitChange" />
        <i class="fas fa-triangle-exclamation"></i> 仅显示后门专题
      </label>
    </div>
  </aside>
</template>

<script setup>
import { ref, watch } from 'vue'

const props = defineProps({
  search: String, category: String, backdoorOnly: Boolean,
  timeRange: String, sort: String,
})
const emit = defineEmits(['update:search', 'update:category', 'update:backdoorOnly', 'update:timeRange', 'update:sort'])

const localSearch = ref(props.search || '')
const localCategory = ref(props.category || '')
const localBackdoorOnly = ref(props.backdoorOnly || false)
const localTimeRange = ref(props.timeRange || 'all')
const localSort = ref(props.sort || 'date_desc')

let deb = null
function onSearch() { clearTimeout(deb); deb = setTimeout(() => emit('update:search', localSearch.value), 300) }
function emitChange() {
  emit('update:category', localCategory.value); emit('update:backdoorOnly', localBackdoorOnly.value)
  emit('update:timeRange', localTimeRange.value); emit('update:sort', localSort.value)
}
watch(() => props.search, v => localSearch.value = v)
watch(() => props.category, v => localCategory.value = v)
watch(() => props.backdoorOnly, v => localBackdoorOnly.value = v)
watch(() => props.timeRange, v => localTimeRange.value = v)
watch(() => props.sort, v => localSort.value = v)
</script>
