<script setup>
import { computed } from 'vue'

const props = defineProps({
  modelValue: { type: Object, required: true },
  allPlugins: { type: Array, required: true },
  filteredCount: { type: Number, default: 0 }
})

const emit = defineEmits(['update:modelValue'])
const f = computed(() => props.modelValue)

function toggle(field, val) {
  const cur = f.value[field] || []
  const next = cur.includes(val) ? cur.filter(v => v !== val) : [...cur, val]
  emit('update:modelValue', { ...f.value, [field]: next })
}

function isActive(field, val) {
  return (f.value[field] || []).includes(val)
}

const counts = computed(() => {
  const c = { sizes: {}, versions: {}, ages: {}, categories: {} }
  for (const p of props.allPlugins) {
    c.sizes[p.size] = (c.sizes[p.size] || 0) + 1
    c.versions[p.version] = (c.versions[p.version] || 0) + 1
    c.ages[p.age_tier] = (c.ages[p.age_tier] || 0) + 1
    const cat = p.category || '未分类'
    c.categories[cat] = (c.categories[cat] || 0) + 1
  }
  c.categories = Object.entries(c.categories).sort((a, b) => b[1] - a[1])
  return c
})

function clearAll() {
  emit('update:modelValue', { search: '', sizes: [], versions: [], ageTiers: [], categories: [] })
}
</script>

<template>
  <!-- 1. 最外层换成一个全宇宙唯一的 class 名字 -->
  <div class="ue-book-sidebar-filter">
    <div class="sidebar-search">
      <input
        type="text"
        class="sidebar-search-input"
        placeholder="搜索..."
        :value="f.search || ''"
        @input="emit('update:modelValue', { ...f, search: $event.target.value })"
      />
    </div>

    <div class="sidebar-section">
      <div class="sidebar-section-title">插件体量</div>
      <div class="sidebar-chips">
        <button v-for="s in [{k:'small',l:'小型'},{k:'medium',l:'中型'},{k:'large',l:'大型'},{k:'xlarge',l:'超大型'}]"
          :key="s.k" class="sc" :class="{ on: isActive('sizes', s.k) }"
          @click="toggle('sizes', s.k)">{{ s.l }} <span class="n">{{ counts.sizes[s.k] || 0 }}</span></button>
      </div>
    </div>

    <div class="sidebar-section">
      <div class="sidebar-section-title">版本</div>
      <div class="sidebar-chips">
        <button class="sc" :class="{ on: isActive('versions', '5.7') }" @click="toggle('versions', '5.7')">默认（5.7） <span class="n">{{ counts.versions['5.7'] || 0 }}</span></button>
        <button class="sc" :class="{ on: isActive('versions', '5.8') }" @click="toggle('versions', '5.8')">5.8 <span class="n">{{ counts.versions['5.8'] || 0 }}</span></button>
      </div>
    </div>

    <div class="sidebar-section">
      <div class="sidebar-section-title">年代</div>
      <div class="sidebar-chips">
        <button class="sc" :class="{ on: isActive('ageTiers', 'relic') }" @click="toggle('ageTiers', 'relic')">🏛️上古文物<span class="n">{{ counts.ages.relic || 0 }}</span></button>
        <button class="sc" :class="{ on: isActive('ageTiers', 'old') }" @click="toggle('ageTiers', 'old')">👴 老古董<span class="n">{{ counts.ages.old || 0 }}</span></button>
        <button class="sc" :class="{ on: isActive('ageTiers', 'fresh') }" @click="toggle('ageTiers', 'fresh')">🥩 小鲜肉<span class="n">{{ counts.ages.fresh || 0 }}</span></button>
      </div>
    </div>

    <div class="sidebar-section">
      <div class="sidebar-section-title">分类</div>
      <div class="sidebar-chips sidebar-cats">
        <button v-for="[cat, n] in counts.categories" :key="cat"
          class="sc" :class="{ on: isActive('categories', cat) }"
          @click="toggle('categories', cat)">{{ cat }} <span class="n">{{ n }}</span></button>
      </div>
    </div>

    <div class="sidebar-footer">
      <span>共 {{ filteredCount }} 个</span>
      <a v-if="f.search || f.sizes.length || f.versions.length || f.ageTiers.length || f.categories.length"
        class="clear-link" @click.prevent="clearAll" href="#">清除</a>
    </div>
  </div>
</template>

<!-- 2. 去掉 scoped 属性 -->
<style>
/* 3. 在所有选择器前面加上 .ue-book-sidebar-filter 前缀 */
.ue-book-sidebar-filter {
  display: flex;
  flex-direction: column;
  gap: 12px;
}
.ue-book-sidebar-filter .sidebar-search-input {
  width: 100%;
  padding: 6px 10px;
  border: 1px solid var(--vp-c-divider);
  border-radius: 6px;
  background: var(--vp-c-bg-soft);
  color: var(--vp-c-text-1);
  font-size: 0.8rem;
  outline: none;
}
.ue-book-sidebar-filter .sidebar-search-input:focus {
  border-color: var(--vp-c-brand-1);
}
.ue-book-sidebar-filter .sidebar-section-title {
  font-size: 0.7rem;
  font-weight: 600;
  color: var(--vp-c-text-3);
  text-transform: uppercase;
  letter-spacing: 0.5px;
  margin-bottom: 4px;
}
.ue-book-sidebar-filter .sidebar-chips {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
}
.ue-book-sidebar-filter .sidebar-cats {
  max-height: 280px;
  overflow-y: auto;
}
.ue-book-sidebar-filter .sc {
  display: inline-flex;
  align-items: center;
  gap: 2px;
  padding: 1px 7px;
  font-size: 0.7rem;
  border-radius: 4px;
  border: 1px solid var(--vp-c-divider);
  background: transparent;
  color: var(--vp-c-text-2);
  cursor: pointer;
  transition: all 0.15s;
  white-space: nowrap;
}
.ue-book-sidebar-filter .sc:hover { 
  border-color: var(--vp-c-brand-1); 
  color: var(--vp-c-brand-1); 
}
.ue-book-sidebar-filter .sc.on { 
  background: var(--vp-c-brand-1); 
  color: var(--vp-c-white); 
  border-color: var(--vp-c-brand-1); 
}
.ue-book-sidebar-filter .n { 
  font-size: 0.6rem; 
  opacity: 0.65; 
}
.ue-book-sidebar-filter .sidebar-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 0.75rem;
  color: var(--vp-c-text-2);
  padding-top: 8px;
  border-top: 1px solid var(--vp-c-divider);
}
.ue-book-sidebar-filter .clear-link {
  color: var(--vp-c-brand-1);
  text-decoration: none;
  font-size: 0.72rem;
}
.ue-book-sidebar-filter .clear-link:hover { 
  text-decoration: underline; 
}
</style>
