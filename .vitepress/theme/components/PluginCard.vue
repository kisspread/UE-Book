<script setup>
defineProps({
  plugin: { type: Object, required: true }
})

const sizeLabels = { small: '小型', medium: '中型', large: '大型', xlarge: '超大型' }
const ageLabels = { relic: '🏛️ 文物', old: '👴 老古董', fresh: '🥩 鲜肉' }
</script>

<template>
  <a :href="plugin.link" class="plugin-card">
    <div class="card-header">
      <div class="card-title-group">
        <span class="card-name">{{ plugin.name }}</span>
        <span class="card-name-cn">{{ plugin.name_cn }}</span>
      </div>
      <span class="card-ver" :class="plugin.version === '5.8' ? 'ver-58' : 'ver-57'">
        {{ plugin.version === '5.7' ? '默认' : plugin.version }}
      </span>
    </div>
    <p class="card-desc">{{ plugin.description_cn || plugin.description }}</p>
    <div class="card-tags">
      <span class="tag ts" :class="'ts-' + plugin.size">{{ sizeLabels[plugin.size] || plugin.size }}</span>
      <span class="tag tc">{{ plugin.category }}</span>
      <span class="tag ta" :class="'ta-' + plugin.age_tier">{{ ageLabels[plugin.age_tier] || plugin.age_tier }}</span>
    </div>
  </a>
</template>

<style scoped>
.plugin-card {
  display: flex;
  flex-direction: column;
  padding: 1rem 1.25rem;
  border: 1px solid var(--vp-c-divider);
  border-radius: 8px;
  background: var(--vp-c-bg-soft);
  text-decoration: none;
  color: inherit;
  transition: box-shadow 0.2s, border-color 0.2s, transform 0.2s;
}
.plugin-card:hover {
  border-color: var(--vp-c-brand-1);
  box-shadow: 0 4px 16px rgba(0,0,0,0.1);
  transform: translateY(-2px);
}
.dark .plugin-card:hover { box-shadow: 0 4px 16px rgba(0,0,0,0.4); }

.card-header {
  display: flex; align-items: flex-start; justify-content: space-between; gap: 0.5rem; margin-bottom: 0.4rem;
}
.card-title-group { display: flex; flex-direction: column; gap: 2px; min-width: 0; flex: 1; }
.card-name { font-weight: 600; font-size: 0.95rem; color: var(--vp-c-text-1); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.card-name-cn { font-size: 0.78rem; color: var(--vp-c-text-2); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }

.card-ver { font-size: 0.7rem; padding: 0.1em 0.45em; border-radius: 4px; font-weight: 600; flex-shrink: 0; }
.ver-57 { background: var(--vp-c-gray-soft, #e5e7eb); color: var(--vp-c-text-2); }
.ver-58 { background: var(--vp-c-green-soft, #d1fae5); color: var(--vp-c-green-1, #16a34a); }
.dark .ver-57 { background: var(--vp-c-bg-alt); color: var(--vp-c-text-3); }

.card-desc {
  font-size: 0.82rem; color: var(--vp-c-text-2); line-height: 1.5; margin: 0 0 0.75rem;
  display: -webkit-box;
  -webkit-line-clamp: 4;
  -webkit-box-orient: vertical;
  overflow: hidden;
  flex: 1;
}

.card-tags { display: flex; flex-wrap: wrap; gap: 0.35rem; }
.tag { font-size: 0.7rem; padding: 0.12em 0.5em; border-radius: 4px; font-weight: 500; white-space: nowrap; }

.ts-small  { background: var(--vp-c-indigo-soft, #e0e7ff); color: var(--vp-c-indigo-1, #4338ca); }
.ts-medium { background: var(--vp-c-yellow-soft, #fef3c7); color: var(--vp-c-yellow-1, #b45309); }
.ts-large  { background: var(--vp-c-pink-soft, #fce7f3);   color: var(--vp-c-pink-1, #be185d); }
.ts-xlarge { background: var(--vp-c-red-soft, #fee2e2);    color: var(--vp-c-red-1, #dc2626); }
.tc { background: var(--vp-c-bg-alt); color: var(--vp-c-text-2); }
.ta-relic { background: rgba(168,162,158,0.15); color: var(--vp-c-text-2); }
.ta-old   { background: var(--vp-c-yellow-soft, #fef3c7); color: var(--vp-c-yellow-1, #b45309); }
.ta-fresh { background: var(--vp-c-green-soft, #d1fae5); color: var(--vp-c-green-1, #16a34a); }

.dark .ts-small  { background: rgba(99,102,241,0.2); }
.dark .ts-medium { background: rgba(245,158,11,0.2); }
.dark .ts-large  { background: rgba(236,72,153,0.2); }
.dark .ts-xlarge { background: rgba(239,68,68,0.2); }
.dark .ta-relic { background: rgba(168,162,158,0.12); }
.dark .ta-old   { background: rgba(245,158,11,0.2); }
.dark .ta-fresh { background: rgba(34,197,94,0.2); }
</style>
