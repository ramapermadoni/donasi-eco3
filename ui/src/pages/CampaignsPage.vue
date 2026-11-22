<script setup>
import { ref, computed } from 'vue'
import AppHeader from '../components/AppHeader.vue'
import BottomNav from '../components/BottomNav.vue'
import data from '../data/sedekah'
import { t, tr, lp, isEn } from '../i18n'
import { ctitle, cexcerpt, compact } from '../campaignText'

// Replace with Frappe: GET campaigns?category=&limit=&offset=
// Kategori per campaign disalin dari SSR sedekah.id/public/campaigns (hanya sebagian campaign yang punya kategori).
// Replace with Frappe: GET campaigns?category=&limit=&offset= (field `category` per campaign)
const feat = computed(() => data.campaigns.find((c) => c.slug === data.featured?.slug))
const rest = computed(() => data.campaigns.filter((c) => c.slug !== data.featured?.slug))
const cats = ['Semua', 'Kesehatan', 'Pendidikan', 'Bencana', 'Anak Yatim', 'Umkm', 'Alquran', 'Palestina', 'Qurban']
const catOf = {"bantu-pakpandi-bertahan": "Kesehatan", "tpq-al-ihsan-bogor": "Pendidikan", "dukung-mimpi-yaziz": "Pendidikan", "rtq-lubuk-linggau": "Pendidikan", "bantu-khalisa-sembuh": "Kesehatan", "bantu-gilang-sembuh": "Kesehatan", "7-kilometer-untuk-air-bersih-hadirkan-sumur-bor-untuk-warga-desa-kedungbanteng": "Kesehatan", "bangun-pesantren-almubarok": "Pendidikan", "bantu-meylani-sembuh": "Kesehatan", "dapurpalestina": "Palestina", "peduli-kebakaran-sulsel": "Bencana", "darurat-warga-gaza-kehausan-tanpa-air-yang-mencukupi": "Palestina", "banturashidshakeel": "Kesehatan", "bantukakekzulhartil": "Kesehatan", "bantusalwasembuh": "Kesehatan", "peduli-terdampak-karhutla": "Bencana", "peduli-terdampak-gempa-ntt": "Bencana", "bantufathursembuh": "Kesehatan", "bantuammarsembuh": "Kesehatan", "bantuafzalsembuh": "Kesehatan", "ruangbelajarlayak": "Pendidikan", "dari-kamar-kos-menjadi-pusat-kebaikan-umat": "Pendidikan", "beasiswa-peduli-negeri-setiap-anak-berhak-belajar-setiap-mimpi-harus-dikejar": "Anak Yatim", "muharram-peduli-difabel": "Anak Yatim", "peduli-yatim-palestina": "Palestina", "berbagi-bahagia-bersama-yatim": "Anak Yatim", "kirim-bantuan-kemanusiaan-untuk-rakyat-gaza": "Palestina", "sedekah-mushaf-al-quran": "Bencana", "sedekah-daging-palestina": "Bencana"}
const CAT_EN = { Semua: 'all', Kesehatan: 'Health', Pendidikan: 'Education', Bencana: 'Disaster Relief', 'Anak Yatim': 'Orphans', Umkm: 'Small Business', Alquran: 'Quran', Palestina: 'Palestine', Qurban: 'Qurban' } // label kategori dari API /en (penyaluran/meta?locale=en)
const catLabel = (c) => (c === 'Semua' ? t('campaignsList.all') : isEn.value ? CAT_EN[c] : c)
const target = computed(() => 'Rp ' + ((detail.value.target || 0) / 1e6).toFixed(1) + (isEn.value ? 'M' : ' jt'))
const cat = ref('Semua')
const list = computed(() => (cat.value === 'Semua' ? rest.value : rest.value.filter((c) => catOf[c.slug] === cat.value)))
const detail = computed(() => (feat.value ? data.details[feat.value.slug] || {} : {}))
const excerpt = computed(() => cexcerpt(data.featured?.slug, data.featured?.excerpt || '').slice(0, 220))
</script>

<template>
  <div class="frame">
    <AppHeader />
    <main class="pb-28 max-w-[480px] mx-auto">
      <section v-if="feat" class="px-4 pt-4">
        <router-link :to="lp('/campaigns/' + feat.slug)" class="block rounded-2xl overflow-hidden bg-white border border-gray-100 active:scale-[0.99] transition-transform" style="box-shadow: 0 4px 16px rgba(0, 0, 0, 0.06)">
          <div class="relative w-full" style="aspect-ratio: 16/9; background: #f3f4f6">
            <img :src="feat.image" :alt="ctitle(feat)" class="absolute inset-0 w-full h-full object-cover" />
            <div class="absolute top-3 left-3 px-2.5 py-1 rounded-full text-[10px] font-bold uppercase tracking-wide" style="background: linear-gradient(135deg, var(--lime) 0%, var(--lime-dark) 100%); color: #fff; box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15)">{{ t('campaignsList.latestCampaign') }}</div>
          </div>
          <div class="p-4">
            <h2 class="text-[16px] font-bold text-gray-900 leading-snug mb-2">{{ ctitle(feat) }}</h2>
            <p v-if="excerpt" class="text-[13px] text-gray-500 leading-relaxed mb-3" style="display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden">{{ excerpt }}</p>
            <div class="h-2 rounded-full bg-gray-100 overflow-hidden mb-1.5"><div class="h-full rounded-full" :style="{ width: Math.min(feat.percent, 100) + '%', background: 'linear-gradient(90deg, var(--lime-dark) 0%, var(--lime) 100%)' }"></div></div>
            <div class="flex items-center justify-between">
              <span class="text-[12px] font-bold text-[color:var(--lime-text)]">{{ compact(feat.raised) }}</span>
              <span class="text-[11px] text-gray-400">{{ t('campaignsList.ofTarget', { pct: feat.percent, target }) }}</span>
            </div>
            <div class="mt-3 flex items-center justify-between">
              <span class="text-[11px] text-gray-500">{{ t('campaignsList.viewDetail') }}</span>
              <span class="flex items-center gap-1 px-3 py-1.5 rounded-full text-[12px] font-bold" style="background: linear-gradient(135deg, var(--lime-dark) 0%, var(--lime) 100%); color: #fff">{{ t('campaignsList.donate') }} <svg class="w-3 h-3" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12h14" /><path d="m12 5 7 7-7 7" /></svg></span>
            </div>
          </div>
        </router-link>
      </section>

      <section class="pt-5">
        <div class="px-4 mb-3 flex items-center gap-2">
          <div class="w-7 h-7 rounded-lg flex items-center justify-center" style="background: var(--lime)">
            <svg class="w-3.5 h-3.5" viewBox="0 0 24 24" fill="#1a1a1a" stroke="#1a1a1a" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10" /><circle cx="12" cy="12" r="6" /><circle cx="12" cy="12" r="2" /></svg>
          </div>
          <p style="font-size: 14px; font-weight: 800; color: #1a1a1a">{{ t('campaignsList.exploreCategories') }}</p>
        </div>
        <div class="flex gap-2 overflow-x-auto px-4 pb-2" style="scrollbar-width: none; -ms-overflow-style: none">
          <button v-for="c in cats" :key="c" class="flex-shrink-0 px-4 py-2 rounded-full text-[12px] font-bold transition-all"
            :style="{ background: cat === c ? 'linear-gradient(135deg, var(--lime-dark) 0%, var(--lime) 100%)' : '#fff', color: cat === c ? '#1a1a1a' : '#6b7280', border: cat === c ? 'none' : '1.5px solid #e5e7eb', boxShadow: cat === c ? '0 4px 12px color-mix(in srgb, var(--lime) 30%, transparent)' : 'none' }"
            @click="c === 'Qurban' ? $router.push(lp('/qurban')) : (cat = c)">{{ catLabel(c) }}</button>
        </div>
      </section>

      <section class="px-4 pt-4">
        <div class="flex items-center justify-between mb-3">
          <p style="font-size: 13px; color: #6b7280; font-weight: 600">{{ t('campaignsList.campaignCount', { count: list.length }) }}{{ cat !== 'Semua' ? t('campaignsList.inCategory', { cat: catLabel(cat) }) : '' }}</p>
        </div>
        <div v-if="!list.length" class="rounded-2xl bg-white border border-gray-100 p-8 text-center">
          <p class="text-sm text-gray-500 mb-1" v-html="tr('campaignsList.emptyCategory', { cat: catLabel(cat) })"></p>
          <button class="mt-2 text-[12px] font-bold inline-flex items-center gap-1" style="color: var(--lime-text)" @click="cat = 'Semua'">{{ t('campaignsList.viewAll') }} <svg class="w-3 h-3" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m9 18 6-6-6-6" /></svg></button>
        </div>
        <div v-else class="grid grid-cols-2 gap-3">
          <router-link v-for="c in list" :key="c.slug" :to="lp('/campaigns/' + c.slug)" class="bg-white rounded-2xl overflow-hidden border border-gray-100 hover:border-[color:var(--lime)] transition-colors active:scale-[0.98]" style="box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04)">
            <div class="relative w-full" style="aspect-ratio: 4/3; background: #f3f4f6">
              <img :src="c.image" :alt="ctitle(c)" class="absolute inset-0 w-full h-full object-cover" loading="lazy" />
              <span v-if="catOf[c.slug]" class="absolute top-2 left-2 px-2 py-0.5 rounded-full text-[9px] font-bold uppercase tracking-wide" style="background: rgba(255, 255, 255, 0.92); color: var(--lime-text)">{{ catLabel(catOf[c.slug]) }}</span>
            </div>
            <div class="p-3">
              <p class="text-[12.5px] font-bold text-gray-900 leading-snug mb-2" style="display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; min-height: 32px">{{ ctitle(c) }}</p>
              <div class="h-1.5 rounded-full bg-gray-100 overflow-hidden mb-1.5"><div class="h-full rounded-full" :style="{ width: Math.min(c.percent, 100) + '%', background: 'linear-gradient(90deg, var(--lime-dark) 0%, var(--lime) 100%)' }"></div></div>
              <div class="flex items-center justify-between">
                <span class="text-[10.5px] font-semibold text-[color:var(--lime-text)]">{{ compact(c.raised) }}</span>
                <span class="text-[10px] text-gray-400">{{ c.percent }}%</span>
              </div>
            </div>
          </router-link>
        </div>
      </section>
    </main>
  </div>
  <BottomNav />
</template>
