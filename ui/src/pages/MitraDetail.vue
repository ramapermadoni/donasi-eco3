<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import AppHeader from '../components/AppHeader.vue'
import BottomNav from '../components/BottomNav.vue'
import Icon from '../components/Icon.vue'
import MitraBadge from '../components/MitraBadge.vue'
import mitra from '../data/mitra.json'
import { lp } from '../i18n'

const route = useRoute()
const m = computed(() => mitra.find((x) => x.slug === route.params.slug))
</script>

<template>
  <div class="frame">
    <div style="background:#f5f6f8;min-height:100vh">
      <AppHeader />
      <div class="min-h-screen pb-28">
        <div v-if="!m" class="max-w-[480px] mx-auto px-4 pt-20 text-center text-sm text-gray-500">Halaman tidak ditemukan.</div>
        <div v-else class="max-w-[480px] mx-auto px-4">
          <div class="mt-4 rounded-2xl bg-white border border-gray-100 p-6 flex flex-col items-center text-center">
            <img :src="m.img" :alt="m.name" class="w-24 h-24 rounded-full object-cover" />
            <h1 class="mt-3 text-xl font-bold text-gray-900 flex items-center gap-1.5">{{ m.name }}<MitraBadge cls="w-5 h-5" /></h1>
            <span class="mt-1 text-[11px] font-semibold text-gray-400 uppercase tracking-wider">{{ m.type }}</span>
            <div class="mt-4 flex items-center gap-6 text-center">
              <div><p class="text-lg font-bold text-gray-900">{{ m.campaigns.length }}</p><p class="text-[11px] text-gray-400">Campaign</p></div>
              <div class="w-px h-8 bg-gray-100"></div>
              <div><p class="text-lg font-bold" style="color:#005399">{{ m.campaigns.length ? m.total : 'Rp 0' }}</p><p class="text-[11px] text-gray-400">Terkumpul</p></div>
            </div>
            <div v-if="m.ig" class="mt-4 flex flex-wrap items-center justify-center gap-2">
              <a :href="m.ig" target="_blank" rel="noopener noreferrer"
                class="inline-flex items-center gap-1.5 px-3.5 py-2 rounded-xl border border-gray-200 text-sm font-medium text-gray-700 hover:bg-gray-50 transition-colors"><Icon name="instagram" class="w-4 h-4" /> Instagram</a>
            </div>
          </div>
          <h2 class="mt-6 mb-3 text-sm font-bold text-gray-900 px-1">Campaign {{ m.name }}</h2>
          <div v-if="!m.campaigns.length" class="rounded-2xl border border-dashed border-gray-200 bg-white p-8 text-center text-sm text-gray-500">Belum ada campaign aktif.</div>
          <div v-else class="grid grid-cols-2 gap-3">
            <router-link v-for="c in m.campaigns" :key="c.slug" :to="lp('/campaigns/' + c.slug)"
              class="rounded-2xl bg-white border border-gray-100 overflow-hidden hover:shadow-md transition-shadow">
              <div class="aspect-[4/3] bg-gray-100"><img :src="c.img" :alt="c.title" class="w-full h-full object-cover" /></div>
              <div class="p-3">
                <p class="text-[13px] font-semibold text-gray-900 leading-snug line-clamp-2 min-h-[34px]">{{ c.title }}</p>
                <div class="mt-2 h-1.5 rounded-full bg-gray-100 overflow-hidden"><div class="h-full rounded-full" :style="{ width: c.pct + '%', background: 'var(--lime)' }"></div></div>
                <div class="mt-1.5 flex items-center justify-between text-[11px]">
                  <span class="font-bold" style="color:#005399">{{ c.raised }}</span><span class="text-gray-400">{{ c.pct }}%</span>
                </div>
              </div>
            </router-link>
          </div>
        </div>
      </div>
    </div>
  </div>
  <BottomNav />
</template>
