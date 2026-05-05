<script setup>
import { ref, computed, onMounted } from 'vue'
import MarkdownIt from 'markdown-it'

const md = new MarkdownIt({ html: false, linkify: true, breaks: true })

const allItems = ref([])
const search = ref('')
const activeCategories = ref([])

onMounted(async () => {
  try {
    const res = await fetch('/libraries/data.json')
    allItems.value = await res.json()
  } catch (e) {
    console.error('Failed to load libraries data:', e)
  }
})

const categories = computed(() => {
  const counts = {}
  allItems.value.forEach(item => {
    counts[item.category] = (counts[item.category] || 0) + 1
  })
  return Object.entries(counts).sort((a, b) => b[1] - a[1])
})

const filtered = computed(() => {
  let list = allItems.value
  if (activeCategories.value.length) {
    list = list.filter(item => activeCategories.value.includes(item.category))
  }
  if (search.value) {
    const q = search.value.toLowerCase()
    list = list.filter(item =>
      item.name.toLowerCase().includes(q) ||
      item.content.toLowerCase().includes(q)
    )
  }
  return list
})

function toggleCategory(cat) {
  const idx = activeCategories.value.indexOf(cat)
  if (idx >= 0) activeCategories.value.splice(idx, 1)
  else activeCategories.value.push(cat)
}

function renderMd(text) {
  if (!text) return ''
  return md.render(text)
}
</script>

<template>
  <div class="libs-page">
    <!-- Toolbar -->
    <div class="libs-toolbar">
      <input class="libs-search" type="text" placeholder="搜索开源库..." v-model="search" />
      <div class="libs-filters">
        <button class="chip" :class="{ on: activeCategories.length === 0 }" @click="activeCategories = []">
          全部 <span class="n">{{ allItems.length }}</span>
        </button>
        <button v-for="[cat, count] in categories" :key="cat" class="chip"
          :class="{ on: activeCategories.includes(cat) }" @click="toggleCategory(cat)">
          {{ cat }} <span class="n">{{ count }}</span>
        </button>
      </div>
      <div class="libs-meta">
        <span class="libs-count">显示 {{ filtered.length }} / {{ allItems.length }} 个</span>
      </div>
    </div>

    <!-- Masonry -->
    <div v-if="filtered.length === 0" class="empty-state">没有匹配的项目</div>
    <div v-else class="masonry">
      <div v-for="item in filtered" :key="item.name" class="lib-card">
        <div class="lib-body">
          <div class="lib-header">
            <a :href="item.github" target="_blank" rel="noopener" class="lib-name">{{ item.name }}</a>
            <span class="lib-cat">{{ item.category }}</span>
          </div>
          <div class="lib-content" v-html="renderMd(item.content)"></div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.libs-page { max-width: 100%; }

.libs-toolbar {
  position: sticky;
  top: 64px;
  z-index: 10;
  background: var(--vp-c-bg);
  padding: 0.75rem 0;
  border-bottom: 1px solid var(--vp-c-divider);
  margin-bottom: 1.5rem;
}

.libs-search {
  width: 100%;
  padding: 8px 12px;
  border: 1px solid var(--vp-c-divider);
  border-radius: 6px;
  background: var(--vp-c-bg-soft);
  color: var(--vp-c-text-1);
  font-size: 0.9rem;
  outline: none;
  margin-bottom: 0.75rem;
}
.libs-search:focus { border-color: var(--vp-c-brand-1); }

.libs-filters {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin-bottom: 0.5rem;
}

.chip {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 3px 10px;
  border-radius: 14px;
  font-size: 0.75rem;
  border: 1px solid var(--vp-c-divider);
  background: transparent;
  color: var(--vp-c-text-2);
  cursor: pointer;
  transition: all 0.15s;
  white-space: nowrap;
}
.chip:hover { border-color: var(--vp-c-brand-1); color: var(--vp-c-brand-1); }
.chip.on { background: var(--vp-c-brand-1); color: var(--vp-c-white); border-color: var(--vp-c-brand-1); }
.chip .n { font-size: 0.65rem; opacity: 0.65; }

.libs-meta { display: flex; align-items: center; justify-content: flex-end; }
.libs-count { font-size: 0.78rem; color: var(--vp-c-text-3); }

/* Masonry */
.masonry {
  columns: 2;
  column-gap: 1.25rem;
}
@media (max-width: 768px) {
  .masonry { columns: 1; }
}

.lib-card {
  break-inside: avoid;
  margin-bottom: 1.25rem;
  border: 1px solid var(--vp-c-divider);
  border-radius: 10px;
  overflow: hidden;
  background: var(--vp-c-bg-soft);
  transition: box-shadow 0.2s, border-color 0.2s;
}
.lib-card:hover {
  border-color: var(--vp-c-brand-1);
  box-shadow: 0 4px 20px rgba(0,0,0,0.08);
}

.lib-body { padding: 1rem 1.25rem; }

.lib-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.5rem;
  margin-bottom: 0.6rem;
}
.lib-name {
  font-size: 1.05rem;
  font-weight: 700;
  color: var(--vp-c-text-1);
  text-decoration: none;
}
.lib-name:hover { color: var(--vp-c-brand-1); }
.lib-cat {
  font-size: 0.68rem;
  padding: 2px 8px;
  border-radius: 4px;
  background: var(--vp-c-bg-alt);
  color: var(--vp-c-text-2);
  white-space: nowrap;
  flex-shrink: 0;
}

/* Content */
.lib-content {
  font-size: 0.85rem;
  color: var(--vp-c-text-2);
  line-height: 1.65;
  word-break: break-word;
}
.lib-content :deep(img) {
  max-width: 100%;
  max-height: 320px;
  object-fit: cover;
  border-radius: 6px;
  margin: 0.5rem 0;
  display: block;
}
.lib-content :deep(a) {
  color: var(--vp-c-brand-1);
  text-decoration: none;
}
.lib-content :deep(a:hover) { text-decoration: underline; }
.lib-content :deep(code) {
  font-size: 0.8rem;
  padding: 1px 4px;
  border-radius: 3px;
  background: var(--vp-c-bg-alt);
}
.lib-content :deep(h4) {
  font-size: 0.9rem;
  font-weight: 600;
  color: var(--vp-c-text-1);
  margin: 0.8rem 0 0.3rem;
}
.lib-content :deep(strong) {
  color: var(--vp-c-text-1);
  font-weight: 600;
}

.empty-state {
  text-align: center;
  padding: 3rem;
  color: var(--vp-c-text-3);
}
</style>
