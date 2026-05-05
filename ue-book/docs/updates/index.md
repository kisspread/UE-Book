---
title: 最近更新
---

<script setup>
import { onMounted } from 'vue'

onMounted(async () => {
  try {
    const res = await fetch('./latest.json')
    const { slug } = await res.json()
    window.location.href = './' + slug
  } catch (e) {}
})
</script>

# 最近更新

跳转至最新月报...
