<script setup>
import { lp } from '../i18n'
// c: { slug|href, image, title, raised, percent }
defineProps({ c: { type: Object, required: true } })
</script>

<template>
  <router-link class="bg-white rounded-2xl overflow-hidden border border-gray-100 hover:border-[color:var(--lime)] transition-colors active:scale-[0.98]" style="box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04)" :to="lp('/campaigns/' + c.slug)">
    <div class="relative w-full" style="aspect-ratio: 4/3; background: #f3f4f6">
      <img :src="c.image" :alt="c.title" class="absolute inset-0 w-full h-full object-cover" loading="lazy" />
    </div>
    <div class="p-3">
      <p class="text-[12.5px] font-bold text-gray-900 leading-snug mb-2" style="display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; min-height: 32px">{{ c.title }}</p>
      <div class="h-1.5 rounded-full bg-gray-100 overflow-hidden mb-1.5">
        <div class="h-full rounded-full transition-all" :style="{ width: Math.min(c.percent, 100) + '%', background: 'linear-gradient(90deg, var(--lime-dark) 0%, var(--lime) 100%)' }"></div>
      </div>
      <div class="flex items-center justify-between">
        <span class="text-[10.5px] font-semibold text-[color:var(--lime-text)]">{{ c.raised }}</span>
        <span class="text-[10px] text-gray-400">{{ c.percent }}%</span>
      </div>
    </div>
  </router-link>
</template>
