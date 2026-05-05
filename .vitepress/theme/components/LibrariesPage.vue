<script setup>
import { ref, computed, onMounted } from 'vue'

const allItems = ref([])
const search = ref('')
const activeCategories = ref([])
const lang = ref('cn')  // 'cn' or 'en'
const slideMap = ref({}) // { index: slideNumber }

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
      item.desc_en.toLowerCase().includes(q) ||
      item.desc_cn.toLowerCase().includes(q)
    )
  }
  return list
})

function toggleCategory(cat) {
  const idx = activeCategories.value.indexOf(cat)
  if (idx >= 0) activeCategories.value.splice(idx, 1)
  else activeCategories.value.push(cat)
}

function getSlide(index) {
  return slideMap.value[index] || 0
}

function setSlide(index, val, max) {
  slideMap.value = { ...slideMap.value, [index]: Math.max(0, Math.min(val, max - 1)) }
}

function nextSlide(index, max) {
  setSlide(index, getSlide(index) + 1, max)
}

function prevSlide(index, max) {
  setSlide(index, getSlide(index) - 1, max)
}

function desc(item) {
  return lang.value === 'cn' ? (item.desc_cn || item.desc_en) : item.desc_en
}
</script>

<template>
  <div class="libs-page">
    <!-- Search + Filters -->
    <div class="libs-toolbar">
      <input
        class="libs-search"
        type="text"
        placeholder="搜索开源库..."
        v-model="search"
      />
      <div class="libs-filters">
        <button
          class="chip"
          :class="{ on: activeCategories.length === 0 }"
          @click="activeCategories = []"
        >全部 <span class="n">{{ allItems.length }}</span></button>
        <button
          v-for="[cat, count] in categories"
          :key="cat"
          class="chip"
          :class="{ on: activeCategories.includes(cat) }"
          @click="toggleCategory(cat)"
        >{{ cat }} <span class="n">{{ count }}</span></button>
      </div>
      <div class="libs-meta">
        <span class="libs-count">显示 {{ filtered.length }} / {{ allItems.length }} 个</span>
        <button class="lang-toggle" @click="lang = lang === 'cn' ? 'en' : 'cn'">
          {{ lang === 'cn' ? 'EN' : '中' }}
        </button>
      </div>
    </div>

    <!-- Cards Grid -->
    <div v-if="filtered.length === 0" class="empty-state">
      没有匹配的项目
    </div>
    <div v-else class="libs-grid">
      <div
        v-for="(item, index) in filtered"
        :key="item.name"
        class="lib-card"
      >
        <!-- Image carousel or placeholder -->
        <div class="lib-visual">
          <div
            v-if="item.images.length > 0"
            class="carousel"
          >
            <div
              class="carousel-track"
              :style="{ transform: `translateX(-${getSlide(index) * 100}%)` }"
            >
              <div
                v-for="(img, i) in item.images"
                :key="i"
                class="carousel-slide"
              >
                <img :src="img" :alt="item.name + ' screenshot ' + (i+1)" loading="lazy" />
              </div>
            </div>
            <!-- Controls -->
            <button
              v-if="item.images.length > 1 && getSlide(index) > 0"
              class="carousel-btn prev"
              @click="prevSlide(index, item.images.length)"
            >‹</button>
            <button
              v-if="item.images.length > 1 && getSlide(index) < item.images.length - 1"
              class="carousel-btn next"
              @click="nextSlide(index, item.images.length)"
            >›</button>
            <div v-if="item.images.length > 1" class="carousel-dots">
              <span
                v-for="(_, i) in item.images"
                :key="i"
                class="dot"
                :class="{ active: getSlide(index) === i }"
                @click="setSlide(index, i, item.images.length)"
              ></span>
            </div>
          </div>
          <div v-else class="lib-visual-placeholder">
            <span class="placeholder-name">{{ item.name }}</span>
          </div>
        </div>

        <!-- Info -->
        <div class="lib-info">
          <div class="lib-header">
            <a :href="item.github" target="_blank" class="lib-name">{{ item.name }}</a>
            <span class="lib-cat">{{ item.category }}</span>
          </div>
          <p class="lib-desc">{{ desc(item) }}</p>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.libs-page {
  max-width: 100%;
}

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

.libs-meta {
  display: flex;
  align-items: center;
  justify-content: space-between;
}
.libs-count { font-size: 0.78rem; color: var(--vp-c-text-3); }

.lang-toggle {
  padding: 3px 12px;
  border-radius: 4px;
  font-size: 0.78rem;
  font-weight: 600;
  border: 1px solid var(--vp-c-divider);
  background: var(--vp-c-bg-soft);
  color: var(--vp-c-text-2);
  cursor: pointer;
}
.lang-toggle:hover { border-color: var(--vp-c-brand-1); color: var(--vp-c-brand-1); }

/* Grid */
.libs-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 1.25rem;
}
@media (max-width: 768px) {
  .libs-grid { grid-template-columns: 1fr; }
}

/* Card */
.lib-card {
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

/* Visual area */
.lib-visual {
  width: 100%;
  height: 220px;
  overflow: hidden;
  position: relative;
  background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
}

.lib-visual-placeholder {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 100%;
  height: 100%;
}
.placeholder-name {
  font-size: 1.3rem;
  font-weight: 700;
  color: rgba(255,255,255,0.15);
  letter-spacing: 0.05em;
  text-transform: capitalize;
}

/* Carousel */
.carousel {
  position: relative;
  width: 100%;
  height: 100%;
}
.carousel-track {
  display: flex;
  height: 100%;
  transition: transform 0.35s ease;
}
.carousel-slide {
  flex-shrink: 0;
  width: 100%;
  height: 100%;
}
.carousel-slide img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.carousel-btn {
  position: absolute;
  top: 50%;
  transform: translateY(-50%);
  width: 32px;
  height: 32px;
  border-radius: 50%;
  border: none;
  background: rgba(0,0,0,0.5);
  color: #fff;
  font-size: 1.2rem;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0;
  transition: opacity 0.2s;
  z-index: 2;
}
.lib-card:hover .carousel-btn { opacity: 1; }
.carousel-btn.prev { left: 8px; }
.carousel-btn.next { right: 8px; }

.carousel-dots {
  position: absolute;
  bottom: 8px;
  left: 50%;
  transform: translateX(-50%);
  display: flex;
  gap: 5px;
  z-index: 2;
}
.dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: rgba(255,255,255,0.4);
  cursor: pointer;
  transition: background 0.2s;
}
.dot.active { background: #fff; }

/* Info */
.lib-info {
  padding: 1rem 1.25rem;
}
.lib-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.5rem;
  margin-bottom: 0.5rem;
}
.lib-name {
  font-size: 1rem;
  font-weight: 700;
  color: var(--vp-c-text-1);
  text-decoration: none;
}
.lib-name:hover { color: var(--vp-c-brand-1); }
.lib-cat {
  font-size: 0.7rem;
  padding: 2px 8px;
  border-radius: 4px;
  background: var(--vp-c-bg-alt);
  color: var(--vp-c-text-2);
  white-space: nowrap;
}
.lib-desc {
  font-size: 0.85rem;
  color: var(--vp-c-text-2);
  line-height: 1.55;
  margin: 0;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.empty-state {
  text-align: center;
  padding: 3rem;
  color: var(--vp-c-text-3);
}
</style>
