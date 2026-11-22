<script setup>
// Penanda scroll tak terbatas + spinner "memuat lagi" + "menampilkan semua". Dipakai PenyaluranPage dan BeritaPage
// (markup identik; hanya teks yang dikirim dari i18n masing-masing halaman).
import { ref, watch, onUnmounted } from 'vue'
import { FEED_LIMIT } from '../composables/useFeedList'
defineProps({ loading: Boolean, count: { type: Number, default: 0 }, loadingMore: Boolean, hasMore: Boolean, loadingMoreText: String, showingAllText: String })
const emit = defineEmits(['more'])
const sentinel = ref(null)
let io
watch(sentinel, (el) => { io?.disconnect(); if (el) { io = new IntersectionObserver((e) => e[0].isIntersecting && emit('more'), { rootMargin: '300px' }); io.observe(el) } })
onUnmounted(() => io?.disconnect())
</script>

<template>
  <template v-if="!loading && count">
    <div ref="sentinel" aria-hidden="true" class="h-1"></div>
    <div v-if="loadingMore" class="py-6 flex items-center justify-center gap-2">
      <svg class="w-4 h-4 animate-spin text-[color:var(--lime-text)]" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M21 12a9 9 0 1 1-6.219-8.56" /></svg>
      <span style="font-size: 12px; color: #9ca3af">{{ loadingMoreText }}</span>
    </div>
    <p v-if="!hasMore && count >= FEED_LIMIT" class="py-6 text-center" style="font-size: 11px; color: #9ca3af">{{ showingAllText }}</p>
  </template>
</template>
