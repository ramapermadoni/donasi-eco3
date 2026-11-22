<script setup>
import { lsGet, lsSet } from '../utils/storage'
import { ref, onMounted } from 'vue'
import Icon from './Icon.vue'
import fallback from '../data/doa.json'
import { t, lp, bcp } from '../i18n'
import { timeAgo } from '../utils/time'
import { maskName } from '../utils/text'
import { rpTight } from '../utils/format'
// items: [{ name, doa }] (opsional). Bila kosong, ambil GET /api/doa (read-only) seperti sedekah.id; placeholder abu-abu selama memuat.
// Frappe hook: ganti fetch dengan daftar doa dari backend Frappe.
const props = defineProps({ items: { type: Array, default: () => [] } })
const list = ref(props.items.map((d) => ({ id: d.name + d.doa, message: d.doa, name: d.name, amount: '', iso: '', amin: 0 })))
const loading = ref(!props.items.length)
const amins = ref({})
const cap = 10

const mask = maskName
// nama anonim, nominal, dan waktu diformat saat render supaya ikut berganti bahasa tanpa memuat ulang
const nameOf = (d) => d.name ?? t('doa.anonymousDonor')
const amountOf = (d) => (d.usd != null ? '$' + (d.usd / 100).toFixed(2) : d.amt != null ? rpTight(Number(d.amt), bcp()) : d.amount)
function amin(d) {
  if ((amins.value[d.id] || 0) >= cap) return
  amins.value = { ...amins.value, [d.id]: (amins.value[d.id] || 0) + 1 }
  d.amin++
  lsSet('dtp_doa_amins', JSON.stringify(amins.value))
}
onMounted(async () => {
  try { amins.value = JSON.parse(lsGet('dtp_doa_amins') || '{}') } catch (e) { /* abaikan */ }
  if (props.items.length) return
  try {
    const r = await fetch('/api/doa')
    const j = r.ok ? await r.json() : []
    list.value = (j || []).map((e) => ({
      id: e.id, message: e.message, amin: e.amin_count,
      name: e.is_anonymous ? null : mask(e.donor_name),
      usd: e.currency === 'USD' ? e.amount : null, amt: e.currency === 'USD' ? null : e.amount, iso: e.paid_at,
    }))
  } catch (e) {
    list.value = fallback.slice(0, 5).map((e, n) => ({ id: 'f' + n, message: e.text, name: e.name, amount: e.amount, when: e.when, amin: Number(e.amin) || 0 }))
  }
  loading.value = false
})
</script>

<template>
  <div v-if="loading || list.length" class="px-4 pt-2 pb-6 max-w-[480px] mx-auto">
    <div class="flex items-center justify-between mb-3">
      <div class="flex items-center gap-2">
        <div class="w-7 h-7 rounded-lg flex items-center justify-center" style="background: var(--lime)"><Icon name="heart" class="w-3.5 h-3.5" fill="#fff" stroke="#fff" /></div>
        <p style="font-size: 14px; font-weight: 600; color: #1a1a1a">{{ t('doa.title') }}</p>
      </div>
      <router-link class="flex items-center gap-0.5 hover:opacity-70 transition-opacity" style="font-size: 11px; font-weight: 700; color: var(--lime-text)" :to="lp('/doa')">{{ t('doa.more') }}<Icon name="chevronRight" class="w-3 h-3" /></router-link>
    </div>
    <div v-if="loading" class="flex gap-3 overflow-x-auto pb-2 doa-noscroll" style="scrollbar-width: none">
      <div v-for="n in 3" :key="n" class="flex-shrink-0 rounded-2xl" style="width: calc((100% - 16px) / 3); min-width: 140px; height: 160px; background: linear-gradient(135deg, #f3f4f6, #e5e7eb)"></div>
    </div>
    <div v-else class="flex gap-3 overflow-x-auto pb-2 snap-x snap-mandatory scroll-smooth doa-noscroll" style="scrollbar-width: none; -ms-overflow-style: none; -webkit-overflow-scrolling: touch">
      <div v-for="d in list" :key="d.id" class="flex-shrink-0 rounded-2xl p-4 flex flex-col snap-start"
        style="width: calc((100% - 16px) / 3); min-width: 160px; background: linear-gradient(160deg, #ffffff 0%, #f0f6fc 100%); border: 1px solid #c7dcf0; box-shadow: 0 2px 12px color-mix(in srgb, var(--lime) 8%, transparent)">
        <Icon name="quote" class="w-4 h-4 mb-2" style="color: var(--lime)" fill="var(--lime)" />
        <p class="flex-1" style="font-size: 11.5px; line-height: 1.45; color: #374151; display: -webkit-box; -webkit-line-clamp: 5; -webkit-box-orient: vertical; overflow: hidden">{{ d.message }}</p>
        <div class="mt-3 pt-3 border-t border-gray-100">
          <p class="truncate" style="font-size: 11px; font-weight: 700; color: #1a1a1a">{{ nameOf(d) }}</p>
          <div class="flex items-center justify-between mt-0.5">
            <span style="font-size: 10px; font-weight: 700; color: var(--lime-text)">{{ amountOf(d) }}</span>
            <span style="font-size: 9px; color: #9ca3af">{{ d.iso ? timeAgo(d.iso) : d.when }}</span>
          </div>
          <button type="button" :disabled="(amins[d.id] || 0) >= cap" class="mt-2 w-full flex items-center justify-center gap-1.5 rounded-lg py-1.5 px-2 transition-all relative overflow-visible"
            :style="(amins[d.id] || 0) >= cap ? 'background:#f3f4f6;border:1px solid #e5e7eb;cursor:not-allowed;opacity:.7' : 'background:linear-gradient(135deg, var(--lime) 0%, var(--lime-dark) 100%);border:1px solid var(--lime-dark);cursor:pointer'"
            @click="amin(d)">
            <span style="font-size: 13px; line-height: 1">🤲</span>
            <span :style="'font-size:10px;font-weight:700;color:' + ((amins[d.id] || 0) >= cap ? '#9ca3af' : '#1a1a1a')">{{ (amins[d.id] || 0) >= cap ? t('doa.aminDone') : t('doa.amin') }} · {{ d.amin }}</span>
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.doa-noscroll::-webkit-scrollbar { display: none; }
</style>
