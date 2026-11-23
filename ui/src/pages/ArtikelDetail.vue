<script setup>
import { shareLink } from '../utils/share'
import { computed, reactive, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import Icon from '../components/Icon.vue'
import data from '../data/artikel.json'
import { lp, t } from '../i18n'
import { dariServer } from '../contentLoader'

// body is sanitized HTML (scrape step); sanitize server-side too in Frappe.
const route = useRoute()
const router = useRouter()
const remote = ref(null)
const loading = ref(false)
async function load() {
  if (!dariServer.value) return
  loading.value = true; remote.value = null
  try { const r = await fetch(`/api/artikel/${encodeURIComponent(route.params.slug)}`); remote.value = r.ok ? await r.json() : null } catch { remote.value = null }
  loading.value = false
}
watch(() => route.params.slug, load, { immediate: true })
// konten contoh sudah dibersihkan -> dari server; selain itu berkas statis bawaan
const item = computed(() => (dariServer.value ? remote.value : data.items.find((i) => i.slug === route.params.slug)))
const related = computed(() => {
  if (!item.value) return []
  if (dariServer.value) return item.value.relatedItems || []
  const bySlug = (s) => data.items.find((i) => i.slug === s)
  const picked = item.value.related.map(bySlug).filter(Boolean)
  return (picked.length ? picked : data.items.filter((i) => i.slug !== item.value.slug)).slice(0, 3)
})
const toast = reactive({ msg: '' })
function back() { window.history.length > 1 ? router.back() : router.push(lp('/berita')) }
const share = () => shareLink(item.value.title, location.href, () => { toast.msg = 'Link disalin'; setTimeout(() => (toast.msg = ''), 1800) })
</script>

<template>
  <div class="frame" style="background: white; min-height: 100vh">
    <div v-if="loading" class="px-4 py-20 text-center"><p style="color: #6b7280">{{ t('common.loading') }}</p></div>

    <div v-else-if="!item" class="px-4 py-20 text-center">
      <p class="font-semibold mb-3">Artikel tidak ditemukan</p>
      <router-link :to="lp('/berita')" class="text-[color:var(--lime-text)] font-semibold" style="font-size: 13px">Kembali ke Berita &amp; Inspirasi</router-link>
    </div>

    <div v-else class="min-h-screen max-w-[448px] mx-auto bg-white pb-28 relative">
      <div class="relative w-full" style="aspect-ratio: 16/9">
        <img :src="item.image" :alt="item.title" class="w-full h-full object-cover" />
        <div class="absolute inset-0 bg-gradient-to-t from-black/60 via-black/10 to-transparent"></div>
        <button class="absolute top-4 left-4 w-9 h-9 rounded-full flex items-center justify-center" style="background: rgba(0, 0, 0, 0.35); backdrop-filter: blur(8px)" aria-label="Kembali" @click="back"><Icon name="chevronLeft" class="w-5 h-5 text-white" /></button>
        <button class="absolute top-4 right-4 w-9 h-9 rounded-full flex items-center justify-center" style="background: rgba(0, 0, 0, 0.35); backdrop-filter: blur(8px)" aria-label="Bagikan" @click="share"><Icon name="share" class="w-4 h-4 text-white" /></button>
        <div class="absolute bottom-4 left-4"><span class="px-3 py-1 rounded-full text-white" style="font-size: 11px; font-weight: 700; background: rgba(26, 26, 26, 0.85); backdrop-filter: blur(6px)">{{ item.category }}</span></div>
      </div>

      <div class="px-5 pt-5">
        <h1 class="text-gray-900 mb-2" style="font-size: 19px; font-weight: 800; line-height: 1.3">{{ item.title }}</h1>
        <div class="flex flex-wrap items-center gap-x-2 gap-y-1 mb-5" style="font-size: 12px; color: #6b7280">
          <span class="inline-flex items-center gap-1.5"><Icon name="calendar" class="w-3.5 h-3.5 text-[color:var(--lime-text)]" />{{ item.dateLabel }}</span>
          <span aria-hidden="true">·</span>
          <span>Ditulis oleh <strong style="color: #374151; font-weight: 700">{{ item.author }}</strong></span>
          <span aria-hidden="true">·</span>
          <span class="inline-flex items-center gap-1" title="Ditinjau dengan prinsip BAL (Benar · Akurat · Lengkap)"><Icon name="badgeCheck" class="w-3.5 h-3.5 text-[color:var(--lime-text)]" />Ditinjau dengan prinsip BAL (Benar · Akurat · Lengkap)</span>
        </div>
        <div class="h-px bg-gray-100 mb-5"></div>
        <div class="penyaluran-body pb-4" style="font-size: 13.5px; color: #374151; line-height: 1.75" v-html="item.body"></div>
      </div>

      <div class="px-5 pt-2 pb-6">
        <div class="h-px bg-gray-100 mb-4"></div>
        <p class="mb-3" style="font-size: 15px; font-weight: 800; color: #1a1a1a">Artikel Terkait</p>
        <div class="flex flex-col gap-3">
          <router-link v-for="r in related" :key="r.slug" :to="lp('/artikel/' + r.slug)" class="flex gap-3 items-center rounded-xl p-2 -mx-2 hover:bg-gray-50 transition-colors">
            <div class="w-16 h-14 rounded-lg overflow-hidden flex-shrink-0" style="border: 1px solid #f3f4f6"><img :src="r.image" :alt="r.title" class="w-full h-full object-cover" loading="lazy" /></div>
            <p class="flex-1 min-w-0" style="font-size: 13px; font-weight: 600; color: #1a1a1a; line-height: 1.35">{{ r.title }}</p>
            <svg class="w-4 h-4 text-[color:var(--lime-text)] flex-shrink-0" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12h14" /><path d="m12 5 7 7-7 7" /></svg>
          </router-link>
        </div>
      </div>

      <div class="fixed bottom-0 left-1/2 -translate-x-1/2 w-full max-w-[448px] px-4 py-3 z-40" style="background: rgba(255, 255, 255, 0.95); backdrop-filter: blur(12px); border-top: 1px solid #f0f0f0; box-shadow: 0 -4px 20px rgba(0, 0, 0, 0.08)">
        <div class="flex gap-3">
          <button class="flex items-center justify-center rounded-2xl border-2 transition-all active:scale-95" style="width: 52px; height: 52px; border-color: var(--lime-dark); color: var(--lime-text); background: white" aria-label="Bagikan" @click="share"><Icon name="share" class="w-5 h-5" /></button>
          <router-link :to="lp('/')" class="flex-1 flex items-center justify-center gap-2 rounded-2xl text-[#fff] font-bold transition-all active:scale-95" style="height: 52px; background: linear-gradient(135deg, var(--lime) 0%, var(--lime-dark) 100%); font-size: 15px; font-weight: 700; box-shadow: 0 4px 16px color-mix(in srgb, var(--lime) 40%, transparent)"><Icon name="heart" class="w-4 h-4 fill-white" />Donasi Sekarang</router-link>
        </div>
      </div>
      <div v-if="toast.msg" class="toast">{{ toast.msg }}</div>
    </div>
  </div>
</template>

<style>
.penyaluran-body h1 { font-size: 1.25rem; font-weight: 800; margin: 1rem 0 0.5rem; color: #1a1a1a; }
.penyaluran-body h2 { font-size: 1.1rem; font-weight: 700; margin: 0.875rem 0 0.375rem; color: #1a1a1a; }
.penyaluran-body h3 { font-size: 1rem; font-weight: 600; margin: 0.75rem 0 0.25rem; color: #1a1a1a; }
.penyaluran-body p { margin-bottom: 0.75rem; }
.penyaluran-body ul { list-style-type: disc; padding-left: 1.4rem; margin: 0.5rem 0; }
.penyaluran-body ol { list-style-type: decimal; padding-left: 1.4rem; margin: 0.5rem 0; }
.penyaluran-body li { margin-bottom: 0.25rem; }
.penyaluran-body blockquote { border-left: 3px solid var(--lime-text); padding-left: 1rem; color: #6b7280; margin: 0.75rem 0; font-style: italic; }
.penyaluran-body code { background: #f3f4f6; padding: 0.1em 0.3em; border-radius: 3px; font-size: 0.85em; }
.penyaluran-body img { max-width: 100%; border-radius: 10px; margin: 0.75rem 0; }
.penyaluran-body a { color: var(--lime-text); text-decoration: underline; }
.penyaluran-body hr { border: none; border-top: 1px solid #e5e7eb; margin: 1rem 0; }
.penyaluran-body strong { font-weight: 700; color: #1a1a1a; }
</style>
