<script setup>
import { shareLink } from '../utils/share'
import { initial } from '../utils/text'
import { rpSp } from '../utils/format'
import { ref, computed, watch, onMounted, onUnmounted, nextTick } from 'vue'
import { dariServer } from '../contentLoader'
import { useRoute, useRouter } from 'vue-router'
import data from '../data/sedekah'
import kabarAll from '../data/kabar.json'
import Icon from '../components/Icon.vue'
import DonateForm from '../components/DonateForm.vue'
import WakafStatus from '../components/WakafStatus.vue'
import BottomNav from '../components/BottomNav.vue'
import { donate, submitting } from '../donate'
import { t, lp, isEn } from '../i18n'
import { ctitle, cbody, compact } from '../campaignText'

const route = useRoute()
const router = useRouter()

const campaign = computed(() => data.campaigns.find((c) => c.slug === route.params.slug))
const detail = computed(() => data.details[route.params.slug] || {})
// sedekah.id: 8 campaign lain, campaign terbaru (featured) di urutan pertama
const others = computed(() => {
  const l = data.campaigns.filter((c) => c.slug !== route.params.slug)
  const f = data.campaigns.find((c) => c.slug === data.featured?.slug)
  return (f && f.slug !== route.params.slug ? [f, ...l.filter((c) => c !== f)] : l).slice(0, 8)
})

// Nominal terkumpul persis (raised_amount) disalin dari SSR sedekah.id; di Frappe pakai field campaign.raised_amount.
const RAISED = {"peduli-banjir-aceh": 0, "bantu-pakpandi-bertahan": 1668000, "petani-ubi-cilembu": 535000, "tpq-al-ihsan-bogor": 2575000, "tebar-10000-mushaf": 2173000, "dukung-mimpi-yaziz": 369002, "rtq-lubuk-linggau": 4195000, "bantu-khalisa-sembuh": 580000, "bantu-gilang-sembuh": 603400, "7-kilometer-untuk-air-bersih-hadirkan-sumur-bor-untuk-warga-desa-kedungbanteng": 3520000, "dapurpalestina": 104989456, "peduli-terdampak-karhutla": 18106500, "peduli-terdampak-gempa-ntt": 19636080, "dari-kamar-kos-menjadi-pusat-kebaikan-umat": 4026000, "gajian-makin-berkah-dengan-sedekah": 2199000, "mengalirkan-kebaikan-sedekah-atas-nama-orang-tua": 86338365, "pahala-berlipatt-dengan-sedekah-jumat": 10309000, "wakaf-masjid-5in1-rahmatan-lilalamin": 7805000, "wakaf-bisa-satu-niat-banyak-manfaat": 1819000, "peduli-terdampak-bencana": 4670000, "bangun-pesantren-almubarok": 510000, "dukung-petani-mustahik": 20000, "peduli-air-bersih": 1411862, "pelatihan-sistem-pendinginan": 165000, "mck-mushala-saadah": 5238713, "peduli-sahabat-mualaf": 153000, "bantu-meylani-sembuh": 128000, "air-bersih-lombok": 3858480, "masjid-baiturrahim-serang": 1043000, "aku-cinta-masjid": 4506785, "peduli-kebakaran-sulsel": 254000, "bbm-untuk-ojol": 50000, "darurat-warga-gaza-kehausan-tanpa-air-yang-mencukupi": 19850695, "rtq-sumbar": 5127546, "tanam-kebaikan": 85000, "banturashidshakeel": 710000, "bantukakekzulhartil": 175000, "bantusalwasembuh": 1189000, "asramatahfidzpreneur": 2556546, "bantufathursembuh": 435000, "bantuammarsembuh": 1210000, "bantuafzalsembuh": 815000, "sumur-bor-cianjur": 7255000, "pesantren-ahlul-bait": 2628000, "ruangbelajarlayak": 1932676, "mcksantricianjur": 3534000, "beasiswa-peduli-negeri-setiap-anak-berhak-belajar-setiap-mimpi-harus-dikejar": 2870000, "muharram-peduli-difabel": 470000, "peduli-yatim-palestina": 17548000, "berbagi-bahagia-bersama-yatim": 102623003, "kirim-bantuan-kemanusiaan-untuk-rakyat-gaza": 110083378, "sedekah-mushaf-al-quran": 7158000, "sedekah-daging-lintas-negeri": 11744000, "sedekah-daging-ke-pelosok-negeri": 2195000, "sedekah-daging-palestina": 84326306, "sedekah": 445959415}
// konten contoh sudah dibersihkan -> angka persis dari server (/api/campaigns/:slug), diambil tiap halaman dibuka; selain itu tabel bawaan RAISED
const live = ref(null)
async function loadLive() {
  live.value = null
  if (!dariServer.value) return
  try { const r = await fetch(`/api/campaigns/${encodeURIComponent(route.params.slug)}`); if (r.ok) live.value = await r.json() } catch { /* pakai angka dari bundel */ }
}
watch(() => route.params.slug, loadLive, { immediate: true })
const raisedFull = computed(() => (dariServer.value ? (live.value ? Number(live.value.raised_amount) : undefined) : RAISED[route.params.slug]))
const pct = computed(() => {
  const tg = live.value ? Number(live.value.target_amount) : 0
  return live.value && tg > 0 ? Math.floor((Number(live.value.raised_amount) * 100) / tg) : campaign.value.percent
})
const rupiah = (n) => rpSp(n || 0)
const target = computed(() => detail.value.target || 0)
const body = computed(() => cbody(route.params.slug, detail.value.description))

const tab = ref('about')
const expanded = ref(false)
const sheet = ref(false)
const toast = ref('')

const clamp = ref(false)
const descEl = ref(null)
function measure() { nextTick(() => { if (descEl.value && descEl.value.scrollHeight > 488) clamp.value = true }) }
// konten contoh sudah dibersihkan -> kabar dari server (/api/campaigns/:slug/updates); selain itu berkas statis bawaan
const kabarRemote = ref([])
async function loadKabar() {
  if (!dariServer.value) return
  kabarRemote.value = []
  try { const r = await fetch(`/api/campaigns/${encodeURIComponent(route.params.slug)}/updates`); kabarRemote.value = r.ok ? (await r.json()).items || [] : [] } catch { kabarRemote.value = [] }
}
watch(() => route.params.slug, loadKabar, { immediate: true })
const kabar = computed(() => (dariServer.value ? kabarRemote.value : kabarAll[route.params.slug] || []))

/* ---- donatur (live: /api/campaigns/:slug/donors, scroll tak terbatas) ---- */
const donors = ref([])
const donorTotal = ref(0)
const donorMore = ref(false)
const donorLoading = ref(false)
const donorLoaded = ref(false)
const sentinel = ref(null)
let io
const AVA = ['var(--lime)', 'var(--lime-dark)', 'var(--lime)', 'var(--lime-dark)']
const nm = (x) => (x.is_anonymous ? t('campaignDetail.anonymousDonor') : x.donor_name)
async function loadDonors(reset = false) {
  if (donorLoading.value) return
  if (reset) { donors.value = []; donorMore.value = false; donorLoaded.value = false }
  donorLoading.value = true
  try {
    const r = await fetch(`/api/campaigns/${route.params.slug}/donors?offset=${donors.value.length}&limit=20`)
    if (!r.ok) throw new Error()
    const j = await r.json()
    const seen = new Set(donors.value.map((x) => x.paid_at + x.donor_name + x.amount))
    donors.value.push(...j.donors.filter((x) => !seen.has(x.paid_at + x.donor_name + x.amount)))
    donorTotal.value = j.total
    donorMore.value = j.hasMore
  } catch { donorMore.value = false } finally { donorLoading.value = false; donorLoaded.value = true }
}
function ago(ts) {
  const n = Math.floor((Date.now() - new Date(ts).getTime()) / 864e5), en = isEn.value
  if (n <= 0) return en ? 'Today' : 'Hari ini'
  if (n < 7) return en ? `${n}d ago` : `${n} hari lalu`
  if (n < 35) return en ? `${Math.floor(n / 7)}w ago` : `${Math.floor(n / 7)} minggu lalu`
  return en ? `${Math.floor(n / 30)}mo ago` : `${Math.floor(n / 30)} bulan lalu`
}
function observe() { io?.disconnect(); if (sentinel.value) { io = new IntersectionObserver((e) => { if (e[0].isIntersecting && donorMore.value) loadDonors() }, { rootMargin: '200px' }); io.observe(sentinel.value) } }
watch(tab, async (v) => { if (v === 'donors') { if (!donorLoaded.value) await loadDonors(); await nextTick(); observe() } })
onUnmounted(() => io?.disconnect())
async function loadDonorTotal() {
  try {
    const r = await fetch(`/api/campaigns/${route.params.slug}/donors?offset=0&limit=1`)
    if (r.ok) donorTotal.value = (await r.json()).total || 0
  } catch { /* abaikan */ }
}
onMounted(() => { loadDonorTotal(); measure(); setTimeout(measure, 500) })
watch(tab, (v) => { if (v === 'about') { measure(); setTimeout(measure, 500) } })

watch(() => route.params.slug, () => { tab.value = 'about'; expanded.value = false; sheet.value = false; donors.value = []; donorLoaded.value = false; donorTotal.value = 0; clamp.value = false; window.scrollTo(0, 0); loadDonorTotal(); measure() })

function back() { window.history.length > 1 ? router.back() : router.push(lp('/')) }

const share = () => shareLink(campaign.value.title, location.href, () => say('Link disalin'))
function say(m) { toast.value = m; setTimeout(() => (toast.value = ''), 1800) }

async function submit(payload) {
  await donate(payload, route.params.slug, detail.value.eventSlug || null)
  sheet.value = false
}
</script>

<template>
  <div class="frame" style="background: #f5f6f8; min-height: 100vh">
    <div v-if="!campaign" class="px-4 py-20 text-center">
      <p class="font-semibold mb-3">Campaign tidak ditemukan</p>
      <router-link :to="lp('/')" class="text-[color:var(--lime-text)] font-semibold" style="font-size: 13px">Kembali ke beranda</router-link>
    </div>

    <div v-else class="min-h-screen bg-white pb-28 max-w-[480px] mx-auto relative">
      <!-- hero -->
      <div class="relative w-full" style="aspect-ratio: 16/9">
        <img :src="campaign.image" :alt="ctitle(campaign)" class="w-full h-full object-cover" />
        <div class="absolute inset-0 bg-gradient-to-t from-black/50 via-transparent to-transparent"></div>
        <button class="absolute top-4 left-4 w-9 h-9 rounded-full flex items-center justify-center" style="background: rgba(0, 0, 0, 0.35); backdrop-filter: blur(8px)" aria-label="Kembali" @click="back"><Icon name="chevronLeft" class="w-5 h-5 text-white" /></button>
        <button class="absolute top-4 right-4 w-9 h-9 rounded-full flex items-center justify-center" style="background: rgba(0, 0, 0, 0.35); backdrop-filter: blur(8px)" aria-label="Bagikan" @click="share"><Icon name="share" class="w-4 h-4 text-white" /></button>
      </div>

      <div class="px-4 pt-4 space-y-4">
        <h1 class="text-[20px] leading-snug text-[color:var(--lime-text)]">{{ ctitle(campaign) }}</h1>

        <!-- progress -->
        <div class="bg-gradient-to-br from-[color:color-mix(in_srgb,var(--lime)_5%,transparent)] to-[color:color-mix(in_srgb,var(--lime-dark)_5%,transparent)] p-4 rounded-2xl border border-[color:color-mix(in_srgb,var(--lime)_10%,transparent)]">
          <div class="h-2.5 w-full bg-gray-200 rounded-full overflow-hidden mb-3"><div class="h-full rounded-full transition-all duration-700" :style="{ width: Math.min(pct, 100) + '%', background: 'linear-gradient(90deg, var(--lime-dark), var(--lime))' }"></div></div>
          <div class="flex items-baseline justify-between mb-3 gap-2">
            <span class="text-[color:var(--lime-text)] text-[18px] font-bold">{{ raisedFull != null ? rupiah(raisedFull) : campaign.raised }}</span>
            <span class="text-[13px] text-gray-500 text-right">{{ t('campaignDetail.ofTarget', { pct: pct, target: rupiah(target) }) }}</span>
          </div>
          <div class="flex items-center gap-2 pt-3 border-t border-gray-200">
            <template v-if="detail.organizer">
              <img v-if="detail.organizer.avatar" :src="detail.organizer.avatar" :alt="detail.organizer.name" class="w-8 h-8 rounded-full object-cover flex-shrink-0" />
              <div v-else class="w-8 h-8 rounded-full flex items-center justify-center text-[13px] font-bold flex-shrink-0" style="background: var(--lime); color: #fff">{{ initial(detail.organizer.name) }}</div>
              <span class="text-[14px] text-gray-600 flex items-center gap-1">{{ detail.organizer.name }}<Icon name="badgeCheck" class="w-4 h-4 flex-shrink-0" :aria-label="t('campaignDetail.verified')" style="color: #1d9bf0; fill: #1d9bf0; stroke: #fff; stroke-width: 2.2" /></span>
            </template>
            <div v-if="donorTotal > 0" class="ml-auto flex items-center gap-1 text-[13px] text-gray-500"><Icon name="users" class="w-3.5 h-3.5" /><span>{{ donorTotal }}</span></div>
          </div>
        </div>

        <!-- tabs -->
        <div class="flex gap-1 bg-gray-100 p-1 rounded-xl">
          <button v-for="it in [['about', 'tabAbout'], ['donors', 'tabDonors'], ['updates', 'tabNews']]" :key="it[0]" class="flex-1 py-2 rounded-lg text-[13px] font-medium transition-all"
            :style="{ background: tab === it[0] ? 'white' : 'transparent', color: tab === it[0] ? 'var(--lime-text)' : '#6b7280', boxShadow: tab === it[0] ? '0 1px 4px rgba(0,0,0,0.08)' : 'none' }" @click="tab = it[0]">{{ t('campaignDetail.' + it[1]) }}</button>
        </div>

        <div v-if="tab === 'about'" class="pb-4">
          <WakafStatus v-if="/wakaf/.test(route.params.slug)" class="mb-4" :slug="route.params.slug" />
          <template v-if="body">
            <div ref="descEl" class="relative overflow-hidden transition-all" :style="{ maxHeight: expanded ? '99999px' : '480px' }">
              <!-- description HTML comes from your own backend (sanitized on scrape) -->
              <div class="max-w-none text-gray-700 leading-relaxed text-[15px]" v-html="body"></div>
              <div v-if="!expanded && clamp" class="absolute bottom-0 left-0 right-0 h-16 pointer-events-none" style="background: linear-gradient(to bottom, rgba(255, 255, 255, 0) 0%, rgba(255, 255, 255, 1) 100%)"></div>
            </div>
            <div v-if="clamp" class="mt-3 flex justify-center">
              <button class="flex items-center gap-1 px-5 py-2 rounded-full text-[13px] font-bold transition-all hover:opacity-90 active:scale-[0.97]" style="color: var(--lime-text); background: #fff8ed; border: 1px solid color-mix(in srgb, var(--lime) 40%, transparent)" @click="expanded = !expanded">
                <template v-if="expanded">{{ t('campaignDetail.showLess') }} <Icon name="chevronUp" class="w-3.5 h-3.5" /></template>
                <template v-else>{{ t('campaignDetail.readMore') }} <Icon name="chevronDown" class="w-3.5 h-3.5" /></template>
              </button>
            </div>
          </template>
          <p v-else class="text-gray-400 text-sm text-center py-8">{{ t('campaignDetail.noDescription') }}</p>
        </div>

        <!-- donatur -->
        <div v-else-if="tab === 'donors'" class="space-y-3 pb-4">
          <div class="flex items-center gap-2 pb-2 border-b border-gray-100">
            <Icon name="users" class="w-4 h-4 text-[color:var(--lime-text)]" />
            <span class="text-[14px] text-gray-600"><span class="font-semibold text-[color:var(--lime-text)]">{{ donorTotal }}</span> {{ t('campaignDetail.donatedSuffix') }}</span>
          </div>
          <p v-if="donorLoaded && !donors.length" class="text-sm text-gray-400 text-center py-8">{{ t('campaignDetail.beFirstDonor') }}</p>
          <template v-else>
            <div v-for="(x, i) in donors" :key="x.paid_at + i" class="bg-gradient-to-br from-white to-gray-50 p-4 rounded-xl border border-gray-100">
              <div class="flex items-start gap-3 mb-2">
                <div class="w-10 h-10 rounded-full flex items-center justify-center text-white text-[14px] font-bold flex-shrink-0" :style="{ background: AVA[i % AVA.length] }">{{ initial(x.donor_name) }}</div>
                <div class="flex-1 min-w-0">
                  <div class="flex items-center gap-2 mb-1">
                    <span class="text-[14px] text-gray-900 font-medium truncate">{{ nm(x) }}</span>
                    <span class="text-[12px] text-gray-400 flex-shrink-0">· {{ ago(x.paid_at) }}</span>
                  </div>
                  <span class="text-[14px] text-[color:var(--lime-text)] font-semibold">{{ rupiah(x.amount) }}</span>
                </div>
              </div>
              <p v-if="x.message" class="text-[13px] text-gray-600 leading-relaxed italic">“{{ x.message }}”</p>
            </div>
            <div v-if="donorMore" ref="sentinel" aria-hidden="true" class="h-1"></div>
            <div v-if="donorLoading" class="py-4 flex items-center justify-center gap-2"><Icon name="loader" class="w-4 h-4 animate-spin text-[color:var(--lime-text)]" /><span class="text-xs text-gray-500">{{ t('campaignDetail.loadingMoreDonors') }}</span></div>
            <p v-else-if="donors.length > 20 && !donorMore" class="text-center text-[11px] text-gray-400 py-3">{{ t('campaignDetail.showingAllDonors', { count: donorTotal }) }}</p>
          </template>
        </div>

        <!-- kabar terbaru -->
        <div v-else class="relative space-y-6 pb-4">
          <p v-if="!kabar.length" class="text-sm text-gray-400 text-center py-8">{{ t('campaignDetail.noUpdates') }}</p>
          <template v-else>
            <div class="absolute left-5 top-5 bottom-5 w-0.5" style="background: linear-gradient(to bottom, var(--lime), color-mix(in srgb, var(--lime) 27%, transparent), transparent)"></div>
            <div v-for="(k, i) in kabar" :key="k.id" class="relative flex gap-4">
              <div class="relative z-10 flex-shrink-0">
                <div class="w-10 h-10 rounded-full border-4 border-white shadow-md flex items-center justify-center" :style="{ background: i % 2 === 0 ? 'var(--lime)' : 'var(--lime-dark)' }"><div class="w-2 h-2 rounded-full bg-white"></div></div>
              </div>
              <div class="flex-1 bg-white rounded-2xl border border-gray-100 overflow-hidden shadow-sm">
                <img v-if="k.image_url" :src="k.image_url" :alt="k.title" class="w-full object-cover" style="aspect-ratio: 16/9" />
                <div class="p-4">
                  <div class="flex items-center justify-between mb-1.5"><span class="text-[15px] text-[color:var(--lime-text)] font-semibold">{{ k.title }}</span><span class="text-[12px] text-gray-400 flex-shrink-0 ml-2">{{ k.date_label }}</span></div>
                  <p class="text-[13px] text-gray-600 leading-relaxed">{{ k.subtitle }}</p>
                </div>
              </div>
            </div>
          </template>
        </div>
      </div>

      <!-- other campaigns -->
      <div v-if="others.length" class="pt-4 pb-2">
        <div class="px-4 flex items-center justify-between mb-3">
          <p class="text-[15px] font-bold text-gray-900">{{ t('campaignDetail.otherCampaigns') }}</p>
          <router-link :to="lp('/public/campaigns')" class="text-[12px] font-semibold flex items-center gap-0.5" style="color: var(--lime-text)">{{ t('campaignDetail.seeAll') }} <Icon name="chevronRight" class="w-3 h-3" /></router-link>
        </div>
        <div class="flex gap-3 overflow-x-auto pb-2 px-4 snap-x snap-mandatory" style="scrollbar-width: none; -ms-overflow-style: none">
          <router-link v-for="c in others" :key="c.slug" :to="lp('/campaigns/' + c.slug)" class="flex-shrink-0 w-[160px] snap-start bg-white rounded-2xl border border-gray-100 overflow-hidden active:scale-[0.98] transition-transform" style="box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04)">
            <div class="relative w-full" style="aspect-ratio: 4/3; background: #f3f4f6"><img :src="c.image" :alt="ctitle(c)" class="absolute inset-0 w-full h-full object-cover" loading="lazy" /></div>
            <div class="p-2.5">
              <p class="text-[12px] font-bold text-gray-900 leading-snug mb-2" style="display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; min-height: 30px">{{ ctitle(c) }}</p>
              <div class="h-1.5 rounded-full bg-gray-100 overflow-hidden mb-1.5"><div class="h-full rounded-full" :style="{ width: Math.min(c.percent, 100) + '%', background: 'linear-gradient(90deg, var(--lime-dark) 0%, var(--lime) 100%)' }"></div></div>
              <div class="flex items-center justify-between"><span class="text-[10px] font-semibold text-[color:var(--lime-text)]">{{ compact(c.raised) }}</span><span class="text-[10px] text-gray-400">{{ c.percent }}%</span></div>
            </div>
          </router-link>
        </div>
      </div>

      <!-- sticky CTA -->
      <div class="fixed bottom-0 left-0 right-0 z-30 bg-white border-t" style="box-shadow: 0 -4px 16px rgba(0, 0, 0, 0.06)">
        <div class="max-w-[480px] mx-auto px-4 py-3">
          <button class="w-full py-4 rounded-2xl text-white font-bold text-[15px] transition-all active:scale-[0.98]" style="background: linear-gradient(135deg, var(--lime-dark) 0%, var(--lime) 100%); box-shadow: 0 6px 24px color-mix(in srgb, var(--lime) 35%, transparent)" @click="sheet = true">{{ t('campaignDetail.donateNow') }}</button>
        </div>
      </div>

      <!-- bottom sheet (isi = DonateForm; alur donasi nyata tidak diubah) -->
      <template v-if="sheet">
        <div class="fixed inset-0 bg-black/40 z-40" @click="sheet = false"></div>
        <div class="fixed bottom-0 left-0 right-0 z-50 flex justify-center">
          <div class="w-full max-w-[480px] bg-white rounded-t-3xl px-4 pb-8 pt-3" style="box-shadow: 0 -8px 40px rgba(0, 0, 0, 0.12); max-height: 92vh; overflow-y: auto; -webkit-overflow-scrolling: touch">
            <div class="flex justify-center mb-4"><div class="w-10 h-1 bg-gray-300 rounded-full"></div></div>
            <div class="flex items-center justify-between mb-4">
              <p class="text-[15px] font-semibold text-gray-800">{{ isEn ? 'Choose donation amount' : 'Pilih Nominal Donasi' }}</p>
              <button class="p-1.5 rounded-full hover:bg-gray-100 transition-colors" aria-label="Tutup" @click="sheet = false"><Icon name="x" class="w-4 h-4 text-gray-500" /></button>
            </div>
            <DonateForm sheet :submitting="submitting" @submit="submit" />
          </div>
        </div>
      </template>
      <div v-if="toast" class="toast">{{ toast }}</div>
    </div>
  </div>
  <BottomNav hide-tabs />
</template>
