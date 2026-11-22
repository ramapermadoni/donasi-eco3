<script setup>
// Baris chip kategori (geser horizontal). Dipakai PenyaluranPage dan BeritaPage; pembungkus (batang progres / margin) tetap di halaman.
defineProps({ meta: { type: Object, required: true }, allLabel: String })
const category = defineModel({ type: String })
</script>

<template>
  <div class="flex gap-2 overflow-x-auto px-4 pb-1" style="scrollbar-width: none; -ms-overflow-style: none">
    <button v-for="c in meta.categories" :key="c" class="flex-shrink-0 px-4 py-1.5 rounded-full border transition-all"
      :style="{ fontSize: '12px', fontWeight: category === c ? 700 : 500, background: category === c ? '#1a1a1a' : 'white', color: category === c ? 'white' : '#374151', borderColor: category === c ? '#1a1a1a' : '#e5e7eb', boxShadow: category === c ? '0 2px 8px rgba(0,0,0,0.2)' : 'none' }"
      @click="category = c">{{ c === 'Semua' ? allLabel : meta.categoryLabels[c] ?? c }}</button>
  </div>
</template>
