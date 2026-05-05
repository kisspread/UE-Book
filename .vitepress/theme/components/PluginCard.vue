<script setup>
defineProps({
  plugin: {
    type: Object,
    required: true
  }
})

const sizeColors = {
  small:  'var(--vp-c-indigo-1, var(--vp-c-brand-1))',
  medium: 'var(--vp-c-yellow-1, #d97706)',
  large:  'var(--vp-c-pink-1, #db2777)',
  xlarge: 'var(--vp-c-red-1, #dc2626)'
}

const sizeLabels = {
  small: '小型', medium: '中型', large: '大型', xlarge: '超大型'
}

const ageLabels = {
  relic: '🏛️ 文物',
  old:   '👴 老古董',
  fresh: '🥩 鲜肉'
}

const ageColors = {
  relic: 'stone',
  old:   'amber',
  fresh: 'green'
}

function versionBadgeClass(version) {
  return version === '5.8' ? 'vp-version-badge vp-version-58' : 'vp-version-badge vp-version-57'
}
</script>

<template>
  <a :href="plugin.link" class="plugin-card">
    <div class="plugin-card-header">
      <div class="plugin-title-group">
        <span class="plugin-name">{{ plugin.name }}</span>
        <span class="plugin-name-cn">{{ plugin.name_cn }}</span>
      </div>
      <span :class="versionBadgeClass(plugin.version)">{{ plugin.version }}</span>
    </div>
    <p class="plugin-description">{{ plugin.description_cn || plugin.description }}</p>
    <div class="plugin-tags">
      <span class="plugin-tag tag-size" :class="'tag-size-' + plugin.size">
        {{ sizeLabels[plugin.size] || plugin.size }}
      </span>
      <span class="plugin-tag tag-category">{{ plugin.category }}</span>
      <span class="plugin-tag tag-age" :class="'tag-age-' + plugin.age_tier">
        {{ ageLabels[plugin.age_tier] || plugin.age_tier }}
      </span>
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
  transition: box-shadow 0.2s, transform 0.2s;
}
.plugin-card:hover {
  box-shadow: 0 4px 12px rgba(0,0,0,0.08);
  transform: translateY(-2px);
  border-color: var(--vp-c-brand-1);
}
.dark .plugin-card:hover {
  box-shadow: 0 4px 12px rgba(0,0,0,0.3);
}

.plugin-card-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 0.5rem;
  margin-bottom: 0.4rem;
}
.plugin-title-group {
  display: flex;
  flex-direction: column;
  gap: 2px;
  min-width: 0;
  flex: 1;
}
.plugin-name {
  font-weight: 600;
  font-size: 0.95rem;
  color: var(--vp-c-text-1);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.plugin-name-cn {
  font-size: 0.78rem;
  color: var(--vp-c-text-2);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.vp-version-badge {
  font-size: 0.7rem;
  padding: 0.1em 0.45em;
  border-radius: 4px;
  font-weight: 600;
  flex-shrink: 0;
}
.vp-version-57 {
  background: var(--vp-c-gray-soft, #e5e7eb);
  color: var(--vp-c-text-2);
}
.vp-version-58 {
  background: var(--vp-c-green-soft, #d1fae5);
  color: var(--vp-c-green-1, #16a34a);
}
.dark .vp-version-57 {
  background: var(--vp-c-bg-alt);
  color: var(--vp-c-text-3);
}

.plugin-description {
  font-size: 0.82rem;
  color: var(--vp-c-text-2);
  line-height: 1.5;
  margin: 0 0 0.75rem;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  flex: 1;
}

.plugin-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 0.35rem;
}
.plugin-tag {
  font-size: 0.7rem;
  padding: 0.12em 0.5em;
  border-radius: 4px;
  font-weight: 500;
  white-space: nowrap;
}

.tag-size-small  { background: var(--vp-c-indigo-soft, #e0e7ff); color: var(--vp-c-indigo-1, #4338ca); }
.tag-size-medium { background: var(--vp-c-yellow-soft, #fef3c7); color: var(--vp-c-yellow-1, #b45309); }
.tag-size-large  { background: var(--vp-c-pink-soft, #fce7f3);   color: var(--vp-c-pink-1, #be185d); }
.tag-size-xlarge { background: var(--vp-c-red-soft, #fee2e2);    color: var(--vp-c-red-1, #dc2626); }

.tag-category { background: var(--vp-c-bg-alt); color: var(--vp-c-text-2); }

.tag-age-relic { background: rgba(168,162,158,0.15); color: var(--vp-c-text-2); }
.tag-age-old   { background: var(--vp-c-yellow-soft, #fef3c7); color: var(--vp-c-yellow-1, #b45309); }
.tag-age-fresh { background: var(--vp-c-green-soft, #d1fae5); color: var(--vp-c-green-1, #16a34a); }

.dark .tag-size-small  { background: rgba(99,102,241,0.2); }
.dark .tag-size-medium { background: rgba(245,158,11,0.2); }
.dark .tag-size-large  { background: rgba(236,72,153,0.2); }
.dark .tag-size-xlarge { background: rgba(239,68,68,0.2); }
.dark .tag-age-relic { background: rgba(168,162,158,0.12); }
.dark .tag-age-old   { background: rgba(245,158,11,0.2); }
.dark .tag-age-fresh { background: rgba(34,197,94,0.2); }
</style>
