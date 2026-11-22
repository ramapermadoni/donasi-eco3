<script setup>
import Icon from './Icon.vue'
import CampaignCard from './CampaignCard.vue'
defineProps({ title: String, items: { type: Array, default: () => [] }, icon: { type: String, default: 'target' }, more: Boolean })
</script>

<template>
  <div class="px-4 pt-2 pb-6 max-w-[480px] mx-auto">
    <div class="flex items-center gap-2 mb-3">
      <div class="w-7 h-7 rounded-lg flex items-center justify-center" style="background: var(--lime)"><Icon :name="icon" class="w-3.5 h-3.5" stroke="#fff" :fill="icon === 'target' ? '#fff' : 'none'" :stroke-width="icon === 'clock' ? 2.4 : 2" /></div>
      <p style="font-size: 14px; font-weight: 600; color: #1a1a1a">{{ title }}</p>
    </div>
    <div class="grid grid-cols-2 gap-3"><CampaignCard v-for="c in items" :key="c.slug" :c="c" /></div>
    <div v-if="more" class="h-12 flex items-center justify-center"></div>
  </div>
</template>
