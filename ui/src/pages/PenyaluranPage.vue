<script setup>
// Daftar penyaluran (inspirasi). Data & logika daftar/filter/paginasi ada di composables/useFeedList.js (dipakai juga BeritaPage).
// Beda dari BeritaPage (sengaja dibiarkan): header, kartu daftar horizontal, banner "Berita & Inspirasi", ikon filter/urut tanpa label,
// batang progres kategori, status kosong tanpa tombol reset, teks i18n penyaluran.*.
import AppHeader from '../components/AppHeader.vue'
import BottomNav from '../components/BottomNav.vue'
import FeedCategoryChips from '../components/FeedCategoryChips.vue'
import FeedFooter from '../components/FeedFooter.vue'
import FeedSheets from '../components/FeedSheets.vue'
import { useFeedList } from '../composables/useFeedList'
import { t, tr, lp } from '../i18n'

const { items, total, hasMore, loading, loadingMore, category, location, program, sortKey, meta, filterOpen, sortOpen, activeFilterCount, barWidth, loadMore, reset } = useFeedList()
</script>

<template>
  <div class="frame">
    <AppHeader />
    <div class="min-h-screen max-w-[448px] mx-auto bg-white pb-28 relative">
      <div class="px-4 pt-5 pb-4 border-b border-gray-100"><h2 style="font-size: 20px; font-weight: 800; color: #1a1a1a">{{ t('penyaluran.title') }}</h2></div>

      <div class="px-4 pt-5 pb-3">
        <p style="font-size: 15px; font-weight: 700; color: #1a1a1a; margin-bottom: 2px">{{ t('penyaluran.newsInspiration') }}</p>
        <p style="font-size: 12px; color: #6b7280">{{ t('penyaluran.newsInspirationSub') }}</p>
      </div>

      <div class="px-4 mb-5">
        <div class="rounded-2xl px-4 py-4 flex items-center justify-between gap-3" style="background: linear-gradient(135deg, #1a1a1a 0%, #2d2d2d 100%); box-shadow: 0 4px 18px rgba(0, 0, 0, 0.2)">
          <div class="flex items-center gap-3 flex-1 min-w-0">
            <div class="w-10 h-10 rounded-xl flex items-center justify-center flex-shrink-0" style="background: rgba(255, 255, 255, 0.18)">
              <svg class="w-5 h-5 text-white" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M4 22h16a2 2 0 0 0 2-2V4a2 2 0 0 0-2-2H8a2 2 0 0 0-2 2v16a2 2 0 0 1-2 2Zm0 0a2 2 0 0 1-2-2v-9c0-1.1.9-2 2-2h2" /><path d="M18 14h-8" /><path d="M15 18h-5" /><path d="M10 6h8v4h-8V6Z" /></svg>
            </div>
            <p style="font-size: 13px; font-weight: 600; color: white; line-height: 1.45" v-html="tr('penyaluran.bannerText', {}, { br: () => '<br>' })"></p>
          </div>
          <router-link :to="lp('/berita')" class="flex items-center gap-1 flex-shrink-0 px-3 py-1.5 rounded-full" style="background: rgba(255, 255, 255, 0.2); font-size: 12px; font-weight: 700; color: white; border: 1px solid rgba(255, 255, 255, 0.35); white-space: nowrap">
            {{ t('penyaluran.view') }} <svg class="w-3.5 h-3.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12h14" /><path d="m12 5 7 7-7 7" /></svg>
          </router-link>
        </div>
      </div>

      <div class="px-4 mb-3">
        <p style="font-size: 15px; font-weight: 700; color: #1a1a1a; margin-bottom: 2px">{{ t('penyaluran.donorGreeting') }}</p>
        <p style="font-size: 12px; color: #6b7280">{{ t('penyaluran.donorGreetingSub') }}</p>
      </div>

      <div class="px-4 flex items-center justify-between mb-3">
        <p style="font-size: 13px; font-weight: 600; color: #374151">{{ t('penyaluran.distributionNews') }}</p>
        <div class="flex items-center gap-2">
          <button aria-label="Filter" class="w-7 h-7 flex items-center justify-center rounded-lg relative" style="background: #f3f4f6" @click="filterOpen = true">
            <svg class="w-3.5 h-3.5 text-gray-500" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="21" x2="14" y1="4" y2="4" /><line x1="10" x2="3" y1="4" y2="4" /><line x1="21" x2="12" y1="12" y2="12" /><line x1="8" x2="3" y1="12" y2="12" /><line x1="21" x2="16" y1="20" y2="20" /><line x1="12" x2="3" y1="20" y2="20" /><line x1="14" x2="14" y1="2" y2="6" /><line x1="8" x2="8" y1="10" y2="14" /><line x1="16" x2="16" y1="18" y2="22" /></svg>
            <span v-if="activeFilterCount > 0" class="absolute -top-1 -right-1 w-3.5 h-3.5 rounded-full flex items-center justify-center" style="background: var(--lime); font-size: 9px; font-weight: 700; color: #fff">{{ activeFilterCount }}</span>
          </button>
          <button :aria-label="t('penyaluran.sort')" class="w-7 h-7 flex items-center justify-center rounded-lg" style="background: #f3f4f6" @click="sortOpen = true">
            <svg class="w-3.5 h-3.5 text-gray-500" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="3" x2="21" y1="6" y2="6" /><line x1="3" x2="21" y1="12" y2="12" /><line x1="3" x2="21" y1="18" y2="18" /></svg>
          </button>
        </div>
      </div>

      <div class="relative mb-3">
        <FeedCategoryChips v-model="category" :meta="meta" :all-label="t('penyaluran.all')" />
        <div class="px-4 mt-2"><div class="h-1 rounded-full bg-gray-100 overflow-hidden"><div class="h-full rounded-full transition-all" :style="{ width: barWidth + '%', background: 'linear-gradient(90deg, var(--lime), var(--lime-dark))' }"></div></div></div>
      </div>

      <div class="divide-y divide-gray-100">
        <div v-if="loading" class="py-16 flex flex-col items-center gap-3">
          <div class="w-8 h-8 rounded-full border-2 border-[color:var(--lime)] border-t-transparent animate-spin"></div>
          <p style="font-size: 13px; color: #9ca3af">{{ t('penyaluran.loadingData') }}</p>
        </div>
        <div v-else-if="!items.length" class="py-16 flex flex-col items-center gap-3 px-4">
          <div class="w-14 h-14 rounded-full flex items-center justify-center" style="background: color-mix(in srgb, var(--lime) 8%, transparent)">
            <svg class="w-7 h-7" style="color: var(--lime-text)" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M4 22h16a2 2 0 0 0 2-2V4a2 2 0 0 0-2-2H8a2 2 0 0 0-2 2v16a2 2 0 0 1-2 2Zm0 0a2 2 0 0 1-2-2v-9c0-1.1.9-2 2-2h2" /><path d="M18 14h-8" /><path d="M15 18h-5" /><path d="M10 6h8v4h-8V6Z" /></svg>
          </div>
          <p style="font-size: 13px; color: #9ca3af; text-align: center">{{ t('penyaluran.emptyCategory') }}</p>
        </div>
        <router-link v-else v-for="e in items" :key="e.id" :to="lp('/penyaluran/' + e.slug)" class="w-full flex gap-3 px-4 py-4 hover:bg-gray-50 active:bg-gray-100 transition-colors text-left">
          <div class="w-24 h-20 rounded-xl overflow-hidden flex-shrink-0" style="border: 1px solid #f3f4f6"><img :src="e.image_url" :alt="e.title" class="w-full h-full object-cover" loading="lazy" /></div>
          <div class="flex-1 min-w-0 flex flex-col justify-center gap-1">
            <p style="font-size: 13px; font-weight: 700; color: #1a1a1a; line-height: 1.35">{{ e.title }}</p>
            <p style="font-size: 11px; color: #9ca3af">{{ e.date_label }}</p>
            <p style="font-size: 12px; color: #6b7280">{{ e.subtitle }}</p>
            <div class="flex items-center gap-1 mt-0.5">
              <span style="font-size: 11px; color: var(--lime-text); font-weight: 600">{{ t('penyaluran.readMore') }}</span>
              <svg class="w-3 h-3 text-[color:var(--lime-text)]" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12h14" /><path d="m12 5 7 7-7 7" /></svg>
            </div>
          </div>
        </router-link>
      </div>

      <FeedFooter :loading="loading" :count="items.length" :loading-more="loadingMore" :has-more="hasMore" :loading-more-text="t('penyaluran.loadingMore')" :showing-all-text="t('penyaluran.showingAll', { total })" @more="loadMore" />

      <FeedSheets v-model:filter-open="filterOpen" v-model:sort-open="sortOpen" v-model:location="location" v-model:program="program" v-model:sort-key="sortKey" :meta="meta" @reset="reset" />
    </div>
  </div>
  <BottomNav />
</template>
