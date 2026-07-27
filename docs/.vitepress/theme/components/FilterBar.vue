<template>
  <div class="filter-bar">
    <input
      type="text"
      v-model="localSearch"
      placeholder="搜索关键词..."
      @input="onSearch"
    />

    <select v-model="localCategory" @change="onFilterChange">
      <option value="">全部类型</option>
      <option value="学术论文">学术论文</option>
      <option value="官方新闻">官方新闻</option>
      <option value="开源发布">开源发布</option>
      <option value="会议动态">会议动态</option>
    </select>

    <label>
      <input type="checkbox" v-model="localBackdoorOnly" @change="onFilterChange" />
      仅后门专项
    </label>

    <label>
      <input type="checkbox" v-model="localTodayOnly" @change="onFilterChange" />
      仅今日新增
    </label>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'

const props = defineProps({
  search: { type: String, default: '' },
  category: { type: String, default: '' },
  backdoorOnly: { type: Boolean, default: false },
  todayOnly: { type: Boolean, default: false },
})

const emit = defineEmits(['update:search', 'update:category', 'update:backdoorOnly', 'update:todayOnly'])

const localSearch = ref(props.search)
const localCategory = ref(props.category)
const localBackdoorOnly = ref(props.backdoorOnly)
const localTodayOnly = ref(props.todayOnly)

let debounceTimer = null
function onSearch() {
  clearTimeout(debounceTimer)
  debounceTimer = setTimeout(() => {
    emit('update:search', localSearch.value)
  }, 300)
}

function onFilterChange() {
  emit('update:category', localCategory.value)
  emit('update:backdoorOnly', localBackdoorOnly.value)
  emit('update:todayOnly', localTodayOnly.value)
}

watch(() => props.search, (v) => { localSearch.value = v })
watch(() => props.category, (v) => { localCategory.value = v })
watch(() => props.backdoorOnly, (v) => { localBackdoorOnly.value = v })
watch(() => props.todayOnly, (v) => { localTodayOnly.value = v })
</script>
