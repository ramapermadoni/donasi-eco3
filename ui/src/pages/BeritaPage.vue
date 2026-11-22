<script setup>
// Berita & Inspirasi = daftar penyaluran yang sama dengan PenyaluranPage; data & logika daftar/filter/paginasi ada di
// composables/useFeedList.js. Beda dari PenyaluranPage (sengaja dibiarkan): header dengan tombol kembali, tombol filter/urut berlabel,
// hitungan konten, kartu vertikal besar, status kosong dengan tombol reset, teks i18n berita.* (sheet memakai penyaluran.*).
import AppHeader from '../components/AppHeader.vue'
import BottomNav from '../components/BottomNav.vue'
import FeedCategoryChips from '../components/FeedCategoryChips.vue'
import FeedFooter from '../components/FeedFooter.vue'
import FeedSheets from '../components/FeedSheets.vue'
import { useRouter } from 'vue-router'
import { useFeedList } from '../composables/useFeedList'
import { t, lp } from '../i18n'

const router = useRouter()
const { items, total, hasMore, loading, loadingMore, category, location, program, sortKey, meta, filterOpen, sortOpen, activeFilterCount, loadMore, reset } = useFeedList()
function back() { window.history.length > 1 && document.referrer.startsWith(window.location.origin) ? router.back() : router.push(lp('/')) }
</script>

<template>
  <div class="frame">
    <AppHeader />
    <div class="min-h-screen max-w-[448px] mx-auto bg-white pb-28 relative">
      <div class="px-4 pt-5 pb-4 border-b border-gray-100 flex items-center gap-3">
        <button :aria-label="t('berita.back')" class="w-9 h-9 rounded-xl flex items-center justify-center" style="background: #f7f8fa" @click="back">
          <svg class="w-4 h-4 text-gray-600" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m12 19-7-7 7-7" /><path d="M19 12H5" /></svg>
        </button>
        <div class="flex-1 min-w-0">
          <h2 style="font-size: 18px; font-weight: 800; color: #1a1a1a; line-height: 1.2">{{ t('berita.title') }}</h2>
          <p style="font-size: 11px; color: #6b7280">{{ t('berita.subtitle') }}</p>
        </div>
      </div>

      <div class="px-4 pt-4 flex items-center justify-between mb-3">
        <p style="font-size: 13px; font-weight: 600; color: #374151">{{ loading ? t('berita.loading') : t('berita.contentCount', { total }) }}</p>
        <div class="flex items-center gap-2">
          <button aria-label="Filter" class="h-8 px-3 flex items-center gap-1.5 rounded-lg relative" style="background: #f3f4f6; font-size: 12px; font-weight: 600; color: #374151" @click="filterOpen = true">
            <svg class="w-3.5 h-3.5 text-gray-500" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="21" x2="14" y1="4" y2="4" /><line x1="10" x2="3" y1="4" y2="4" /><line x1="21" x2="12" y1="12" y2="12" /><line x1="8" x2="3" y1="12" y2="12" /><line x1="21" x2="16" y1="20" y2="20" /><line x1="12" x2="3" y1="20" y2="20" /><line x1="14" x2="14" y1="2" y2="6" /><line x1="8" x2="8" y1="10" y2="14" /><line x1="16" x2="16" y1="18" y2="22" /></svg>Filter<span v-if="activeFilterCount > 0" class="ml-0.5 w-4 h-4 rounded-full flex items-center justify-center" style="background: var(--lime); font-size: 9px; font-weight: 700; color: #fff">{{ activeFilterCount }}</span>
          </button>
          <button :aria-label="t('berita.sort')" class="h-8 px-3 flex items-center gap-1.5 rounded-lg" style="background: #f3f4f6; font-size: 12px; font-weight: 600; color: #374151" @click="sortOpen = true">
            <svg class="w-3.5 h-3.5 text-gray-500" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="3" x2="21" y1="6" y2="6" /><line x1="3" x2="21" y1="12" y2="12" /><line x1="3" x2="21" y1="18" y2="18" /></svg>{{ t('berita.sort') }}
          </button>
        </div>
      </div>

      <div class="mb-4">
        <FeedCategoryChips v-model="category" :meta="meta" :all-label="t('berita.all')" />
      </div>

      <div class="px-4 flex flex-col gap-4">
        <div v-if="loading" class="py-16 flex flex-col items-center gap-3">
          <div class="w-8 h-8 rounded-full border-2 border-[color:var(--lime)] border-t-transparent animate-spin"></div>
          <p style="font-size: 13px; color: #9ca3af">{{ t('berita.loadingData') }}</p>
        </div>
        <div v-else-if="!items.length" class="py-16 flex flex-col items-center gap-3">
          <div class="w-14 h-14 rounded-full flex items-center justify-center" style="background: color-mix(in srgb, var(--lime) 8%, transparent)">
            <svg class="w-7 h-7" style="color: var(--lime-text)" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M4 22h16a2 2 0 0 0 2-2V4a2 2 0 0 0-2-2H8a2 2 0 0 0-2 2v16a2 2 0 0 1-2 2Zm0 0a2 2 0 0 1-2-2v-9c0-1.1.9-2 2-2h2" /><path d="M18 14h-8" /><path d="M15 18h-5" /><path d="M10 6h8v4h-8V6Z" /></svg>
          </div>
          <p style="font-size: 13px; color: #9ca3af; text-align: center">{{ t('berita.emptyFilter') }}</p>
          <button v-if="activeFilterCount > 0" class="mt-1 px-4 py-1.5 rounded-full" style="background: var(--lime); color: #fff; font-size: 12px; font-weight: 700" @click="reset">{{ t('berita.resetFilter') }}</button>
        </div>
        <router-link v-else v-for="e in items" :key="e.id" :to="lp('/penyaluran/' + e.slug)" class="w-full text-left rounded-2xl overflow-hidden border border-gray-100 hover:shadow-md transition-shadow block" style="background: white">
          <div class="relative w-full aspect-[16/10] bg-gray-100 overflow-hidden">
            <img :src="e.image_url" :alt="e.title" class="w-full h-full object-cover" loading="lazy" />
            <span class="absolute top-3 left-3 px-2.5 py-1 rounded-full" style="background: rgba(0, 0, 0, 0.6); backdrop-filter: blur(8px); color: white; font-size: 10px; font-weight: 700; letter-spacing: 0.02em">{{ meta.categoryLabels[e.category] ?? e.category }}</span>
          </div>
          <div class="px-4 py-3 flex flex-col gap-1.5">
            <p style="font-size: 11px; color: #9ca3af">{{ e.date_label }}</p>
            <p style="font-size: 14px; font-weight: 700; color: #1a1a1a; line-height: 1.35; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden">{{ e.title }}</p>
            <p style="font-size: 12px; color: #6b7280; line-height: 1.45; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden">{{ e.subtitle }}</p>
            <div class="flex items-center justify-between mt-1.5 pt-1.5 border-t border-gray-100">
              <div v-if="e.location" class="flex items-center gap-1 min-w-0 flex-1">
                <svg class="w-3 h-3 text-gray-400 flex-shrink-0" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M20 10c0 4.993-5.539 10.193-7.399 11.799a1 1 0 0 1-1.202 0C9.539 20.193 4 14.993 4 10a8 8 0 0 1 16 0" /><circle cx="12" cy="10" r="3" /></svg>
                <span style="font-size: 11px; color: #6b7280; white-space: nowrap; overflow: hidden; text-overflow: ellipsis">{{ e.location }}</span>
              </div>
              <span v-else></span>
              <div class="flex items-center gap-1 flex-shrink-0">
                <span style="font-size: 11px; color: var(--lime-text); font-weight: 600">{{ t('berita.read') }}</span>
                <svg class="w-3 h-3 text-[color:var(--lime-text)]" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12h14" /><path d="m12 5 7 7-7 7" /></svg>
              </div>
            </div>
          </div>
        </router-link>
      </div>

      <FeedFooter :loading="loading" :count="items.length" :loading-more="loadingMore" :has-more="hasMore" :loading-more-text="t('berita.loadingMore')" :showing-all-text="t('berita.showingAll', { total })" @more="loadMore" />

      <FeedSheets v-model:filter-open="filterOpen" v-model:sort-open="sortOpen" v-model:location="location" v-model:program="program" v-model:sort-key="sortKey" :meta="meta" @reset="reset" />
    </div>
  </div>
  <BottomNav />
</template>
