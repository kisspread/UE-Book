---
layout: page
title: 最近更新
---

# 最近更新

每周自动分析 Unreal Engine 引擎最新改动，追踪技术趋势。

<script setup>
import { ref, onMounted } from 'vue'
import { data as posts } from './posts.data.ts'
</script>

<div class="updates-list">
  <a v-for="post in posts" :key="post.url" :href="post.url" class="update-card">
    <div class="update-date">{{ post.date }}</div>
    <h3 class="update-title">{{ post.title }}</h3>
    <p class="update-excerpt">{{ post.excerpt }}</p>
  </a>
  <div v-if="posts.length === 0" class="empty-state">
    暂无更新，等待第一次 GitHub Action 生成...
  </div>
</div>

<style scoped>
.updates-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  max-width: 800px;
}
.update-card {
  display: block;
  padding: 1.25rem 1.5rem;
  border: 1px solid var(--vp-c-divider);
  border-radius: 8px;
  background: var(--vp-c-bg-soft);
  text-decoration: none;
  color: inherit;
  transition: border-color 0.2s, box-shadow 0.2s;
}
.update-card:hover {
  border-color: var(--vp-c-brand-1);
  box-shadow: 0 2px 12px rgba(0,0,0,0.06);
}
.update-date {
  font-size: 0.78rem;
  color: var(--vp-c-text-3);
  margin-bottom: 0.3rem;
}
.update-title {
  font-size: 1.1rem;
  font-weight: 600;
  color: var(--vp-c-text-1);
  margin: 0 0 0.4rem;
}
.update-excerpt {
  font-size: 0.85rem;
  color: var(--vp-c-text-2);
  margin: 0;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
.empty-state {
  text-align: center;
  padding: 3rem 1rem;
  color: var(--vp-c-text-3);
}
</style>
