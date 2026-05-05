<script setup>
import { ref, computed, onMounted } from 'vue'
import FilterBar from './FilterBar.vue'
import PluginCard from './PluginCard.vue'

const allPlugins = ref([])
const filters = ref({
  search: '',
  sizes: [],
  versions: [],
  ageTiers: [],
  categories: []
})

onMounted(async () => {
  try {
    const res = await fetch('/manifest.json')
    const data = await res.json()
    allPlugins.value = data.plugins || data
  } catch (e) {
    console.error('Failed to load plugins.json:', e)
  }
})

const filteredPlugins = computed(() => {
  let list = allPlugins.value

  if (filters.value.search) {
    const q = filters.value.search.toLowerCase()
    list = list.filter(p =>
      p.name.toLowerCase().includes(q) ||
      (p.name_cn && p.name_cn.toLowerCase().includes(q)) ||
      (p.description_cn && p.description_cn.includes(q)) ||
      (p.description && p.description.toLowerCase().includes(q))
    )
  }

  if (filters.value.sizes && filters.value.sizes.length > 0) {
    list = list.filter(p => filters.value.sizes.includes(p.size))
  }

  if (filters.value.categories && filters.value.categories.length > 0) {
    list = list.filter(p => filters.value.categories.includes(p.category))
  }

  if (filters.value.ageTiers && filters.value.ageTiers.length > 0) {
    list = list.filter(p => filters.value.ageTiers.includes(p.age_tier))
  }

  if (filters.value.versions && filters.value.versions.length > 0) {
    list = list.filter(p => filters.value.versions.includes(p.version))
  }

  return list
})

const filteredCount = computed(() => filteredPlugins.value.length)
</script>

<template>
  <div class="home-cards">
    <FilterBar
      v-model="filters"
      :all-plugins="allPlugins"
      :filtered-count="filteredCount"
    />

    <div v-if="allPlugins.length === 0" class="loading-state">
      加载中...
    </div>
    <div v-else-if="filteredPlugins.length === 0" class="empty-state">
      没有匹配的插件
    </div>
    <div v-else class="plugin-grid">
      <PluginCard
        v-for="plugin in filteredPlugins"
        :key="plugin.name + plugin.link"
        :plugin="plugin"
      />
    </div>
  </div>
</template>

<style scoped>
.home-cards {
  width: 100%;
}
.plugin-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 1rem;
}
.loading-state,
.empty-state {
  text-align: center;
  color: var(--vp-c-text-2);
  padding: 3rem 1rem;
  font-size: 0.95rem;
}
</style>
