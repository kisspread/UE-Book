<script setup>
import { computed } from 'vue'

const props = defineProps({
  modelValue: {
    type: Object,
    required: true
  },
  allPlugins: {
    type: Array,
    required: true
  },
  filteredCount: {
    type: Number,
    default: 0
  }
})

const emit = defineEmits(['update:modelValue'])

const filters = computed(() => props.modelValue)

function toggleSize(size) {
  const cur = filters.value.sizes || []
  const next = cur.includes(size) ? cur.filter(s => s !== size) : [...cur, size]
  emit('update:modelValue', { ...filters.value, sizes: next })
}
function toggleVersion(version) {
  const cur = filters.value.versions || []
  const next = cur.includes(version) ? cur.filter(v => v !== version) : [...cur, version]
  emit('update:modelValue', { ...filters.value, versions: next })
}
function toggleAge(age) {
  const cur = filters.value.ageTiers || []
  const next = cur.includes(age) ? cur.filter(a => a !== age) : [...cur, age]
  emit('update:modelValue', { ...filters.value, ageTiers: next })
}
function toggleCategory(cat) {
  const cur = filters.value.categories || []
  const next = cur.includes(cat) ? cur.filter(c => c !== cat) : [...cur, cat]
  emit('update:modelValue', { ...filters.value, categories: next })
}

// Counts are computed from ALL plugins, not filtered
const sizeCounts = computed(() => {
  const counts = {}
  for (const p of props.allPlugins) {
    const s = p.size
    counts[s] = (counts[s] || 0) + 1
  }
  return counts
})

const versionCounts = computed(() => {
  const counts = {}
  for (const p of props.allPlugins) {
    const v = p.version
    counts[v] = (counts[v] || 0) + 1
  }
  return counts
})

const ageCounts = computed(() => {
  const counts = {}
  for (const p of props.allPlugins) {
    const a = p.age_tier
    counts[a] = (counts[a] || 0) + 1
  }
  return counts
})

const categoryCounts = computed(() => {
  const counts = {}
  for (const p of props.allPlugins) {
    const c = p.category
    counts[c] = (counts[c] || 0) + 1
  }
  // sort by count desc
  return Object.entries(counts).sort((a, b) => b[1] - a[1])
})

const sizeChips = [ { key: 'small',  label: 'S'  }, { key: 'medium', label: 'M' }, { key: 'large', label: 'L' }, { key: 'xlarge', label: 'XL' } ]
const versionChips = [ { key: '5.7', label: '5.7' }, { key: '5.8', label: '5.8' } ]
const ageChips = [ { key: 'relic', label: '🏛️文物' }, { key: 'old', label: '👴老古董' }, { key: 'fresh', label: '🥩鲜肉' } ]

const hasFilters = computed(() => {
  const f = filters.value
  return (f.search && f.search.trim().length > 0) ||
    (f.sizes && f.sizes.length > 0) ||
    (f.versions && f.versions.length > 0) ||
    (f.ageTiers && f.ageTiers.length > 0) ||
    (f.categories && f.categories.length > 0)
})

function clearFilters() {
  emit('update:modelValue', { search: '', sizes: [], versions: [], ageTiers: [], categories: [] })
}

function updateSearch(e) {
  emit('update:modelValue', { ...filters.value, search: e.target.value })
}

function isActive(arr, key) {
  return arr && arr.includes(key)
}
</script>

<template>
  <div class="filter-bar">
    <div class="filter-search">
      <input
        type="text"
        class="filter-search-input"
        placeholder="搜索插件名称或描述..."
        :value="filters.search || ''"
        @input="updateSearch"
      />
    </div>

    <div class="filter-row">
      <span class="filter-label">Size</span>
      <div class="chip-group">
        <button
          v-for="chip in sizeChips"
          :key="chip.key"
          class="chip"
          :class="{ active: isActive(filters.sizes, chip.key) }"
          @click="toggleSize(chip.key)"
        >
          {{ chip.label }} <span class="chip-count">{{ sizeCounts[chip.key] || 0 }}</span>
        </button>
      </div>
    </div>

    <div class="filter-row">
      <span class="filter-label">Version</span>
      <div class="chip-group">
        <button
          v-for="chip in versionChips"
          :key="chip.key"
          class="chip"
          :class="{ active: isActive(filters.versions, chip.key) }"
          @click="toggleVersion(chip.key)"
        >
          {{ chip.label }} <span class="chip-count">{{ versionCounts[chip.key] || 0 }}</span>
        </button>
      </div>
    </div>

    <div class="filter-row">
      <span class="filter-label">Age</span>
      <div class="chip-group">
        <button
          v-for="chip in ageChips"
          :key="chip.key"
          class="chip"
          :class="{ active: isActive(filters.ageTiers, chip.key) }"
          @click="toggleAge(chip.key)"
        >
          {{ chip.label }} <span class="chip-count">{{ ageCounts[chip.key] || 0 }}</span>
        </button>
      </div>
    </div>

    <div class="filter-row">
      <span class="filter-label">Category</span>
      <div class="chip-group chip-group-categories">
        <button
          v-for="[cat, count] in categoryCounts"
          :key="cat"
          class="chip"
          :class="{ active: isActive(filters.categories, cat) }"
          @click="toggleCategory(cat)"
        >
          {{ cat }} <span class="chip-count">{{ count }}</span>
        </button>
      </div>
    </div>

    <div class="filter-footer">
      <span class="filter-result-count">显示 {{ filteredCount }} 个插件</span>
      <a v-if="hasFilters" class="filter-clear" href="javascript:void(0)" @click="clearFilters">清除过滤</a>
    </div>
  </div>
</template>

<style scoped>
.filter-bar {
  position: sticky;
  top: 64px;
  z-index: 10;
  background: var(--vp-c-bg);
  padding: 0.75rem 0 0.5rem;
  border-bottom: 1px solid var(--vp-c-divider);
  margin-bottom: 1.5rem;
}

.filter-search {
  margin-bottom: 0.5rem;
}
.filter-search-input {
  width: 100%;
  padding: 0.4rem 0.75rem;
  border: 1px solid var(--vp-c-divider);
  border-radius: 6px;
  background: var(--vp-c-bg-soft);
  color: var(--vp-c-text-1);
  font-size: 0.85rem;
  outline: none;
}
.filter-search-input:focus {
  border-color: var(--vp-c-brand-1);
}

.filter-row {
  display: flex;
  align-items: flex-start;
  gap: 0.5rem;
  margin-bottom: 0.4rem;
}
.filter-label {
  font-size: 0.75rem;
  font-weight: 600;
  color: var(--vp-c-text-2);
  white-space: nowrap;
  padding-top: 0.2rem;
  min-width: 4rem;
}

.chip-group {
  display: flex;
  flex-wrap: wrap;
  gap: 0.3rem;
}

.chip {
  display: inline-flex;
  align-items: center;
  gap: 0.25rem;
  padding: 0.15em 0.6em;
  font-size: 0.72rem;
  border-radius: 999px;
  border: 1px solid var(--vp-c-divider);
  background: var(--vp-c-bg-soft);
  color: var(--vp-c-text-2);
  cursor: pointer;
  transition: background 0.15s, border-color 0.15s, color 0.15s;
  white-space: nowrap;
}
.chip:hover {
  border-color: var(--vp-c-brand-1);
  color: var(--vp-c-brand-1);
}
.chip.active {
  background: var(--vp-c-brand-1);
  color: var(--vp-c-white);
  border-color: var(--vp-c-brand-1);
}
.chip.active .chip-count {
  color: var(--vp-c-white);
}

.chip-count {
  font-size: 0.65rem;
  opacity: 0.7;
}

.filter-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-top: 0.5rem;
  font-size: 0.8rem;
}
.filter-result-count {
  color: var(--vp-c-text-2);
  font-weight: 500;
}
.filter-clear {
  color: var(--vp-c-brand-1);
  text-decoration: none;
  font-size: 0.78rem;
}
.filter-clear:hover {
  text-decoration: underline;
}
</style>
