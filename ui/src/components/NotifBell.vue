<script setup>
import { ssGet, ssSet, lsGet, lsSet } from '../utils/storage'
import { ref, computed, onMounted, onBeforeUnmount, watch } from 'vue'
import Icon from './Icon.vue'
import { lp, t, bcp } from '../i18n'
import { auth } from '../auth'
import { statusOf, canMakeup } from '../rutin'
import { loadRutin, nowISO } from '../rutinStore'
import { rpTight } from '../utils/format'

const SEEN = 'doa_notif_mini_shown_v1'
const root = ref(null)
const panel = ref(false)
const mini = ref(false)
const data = ref({ unread: 0, items: [] })
let timer

// Pengingat Shadaqa Rutin LOKAL (hanya di sini; tidak dikirim/ditandai-baca ke server). Item: hari H (DUE) dan terlewat yang
// masih bisa digenapi. Status baca per nomor di localStorage. Tanpa jadwal aktif atau tamu: tidak ada item (lonceng seperti asli).
const RKEY = 'sedekah_rutin_bell_read_'
const tick = ref(0)
const readKeys = ref([])
const phone = () => auth.user?.phone || ''
const loadRead = () => { try { const a = JSON.parse(lsGet(RKEY + phone()) || '[]'); readKeys.value = Array.isArray(a) ? a : [] } catch { readKeys.value = [] } }
const dateLong = (iso) => new Intl.DateTimeFormat(bcp(), { day: 'numeric', month: 'long', year: 'numeric', timeZone: 'UTC' }).format(new Date(iso + 'T00:00:00Z'))
const local = computed(() => {
  void tick.value
  const p = phone()
  if (!p) return []
  try {
    const today = nowISO()
    const { schedule, occs } = loadRutin(p, today)
    if (!schedule || schedule.status !== 'ACTIVE' || schedule.reminders?.bell === false) return []
    const out = []
    for (const o of occs) {
      const st = statusOf(o, today)
      if (st === 'DUE') out.unshift({ key: 'due:' + o.date, date: o.date, title: t('shadaqaRutin.bellDue'), sub: t('shadaqaRutin.bellDueSub', { amount: rpTight(o.amount, bcp()) }) })
      else if (st === 'MISSED' && canMakeup(o, today)) out.push({ key: 'missed:' + o.date, date: o.date, title: t('shadaqaRutin.bellMissed', { date: dateLong(o.date) }), sub: t('shadaqaRutin.bellMissedSub') })
    }
    return out
  } catch { return [] }
})
const localUnread = computed(() => local.value.filter((i) => !readKeys.value.includes(i.key)).length)
const unread = computed(() => data.value.unread + localUnread.value)
const refreshLocal = () => { loadRead(); tick.value++ }

const teks = (it) => {
  const n = it.aminers?.[0] ?? 'Seseorang'
  const t = it.total_aminers
  if (t <= 1) return `${n} mengaminkan doa anda`
  if (t === 2 && it.aminers[1]) return `${n} dan ${it.aminers[1]} mengaminkan doa anda`
  return `${n} dan ${t - 1} orang lainnya mengaminkan doa anda`
}

function open() {
  panel.value = true
  mini.value = false
  refreshLocal()
  if (local.value.length) {
    const all = [...new Set([...readKeys.value, ...local.value.map((i) => i.key)])]
    readKeys.value = all
    lsSet(RKEY + phone(), JSON.stringify(all))
  }
  if (data.value.unread > 0) {
    data.value = { ...data.value, unread: 0 }
    fetch('/api/notifications', { method: 'POST', credentials: 'same-origin' }).catch(() => {})
  }
}
const toggle = () => (panel.value ? (panel.value = false) : open())
const outside = (e) => { if (root.value && !root.value.contains(e.target)) panel.value = false }
watch(panel, (v) => (v ? document.addEventListener('mousedown', outside) : document.removeEventListener('mousedown', outside)))

watch(() => auth.user?.phone, refreshLocal)
onMounted(async () => {
  refreshLocal()
  try {
    const r = await fetch('/api/notifications', { credentials: 'same-origin' })
    const d = await r.json()
    data.value = { unread: d.unread || 0, items: d.items || [] }
  } catch { /* diam */ }
  if (unread.value > 0) {
    try {
      let seen = false
      seen = ssGet(SEEN) === '1'
      if (!seen) {
        ssSet(SEEN, '1')
        mini.value = true
        timer = setTimeout(() => (mini.value = false), 5000)
      }
    } catch { /* diam */ }
  }
})
onBeforeUnmount(() => { clearTimeout(timer); document.removeEventListener('mousedown', outside) })
</script>

<template>
  <div ref="root" class="relative">
    <button class="w-9 h-9 rounded-xl flex items-center justify-center relative" style="background: #f7f8fa" aria-label="Notifikasi" @click="toggle">
      <Icon name="bell" class="w-4 h-4 text-gray-500" />
      <span v-if="unread > 0" class="absolute -top-1 -right-1 min-w-[16px] h-4 px-1 rounded-full text-[10px] font-bold text-white flex items-center justify-center" style="background: #ff3b30">{{ unread > 9 ? '9+' : unread }}</span>
    </button>
    <button v-if="mini && !panel && unread > 0" class="absolute right-0 top-11 z-50 flex items-center gap-1.5 rounded-full bg-[#1a1a1a] text-white text-[12px] font-semibold px-3 py-2 shadow-lg whitespace-nowrap" style="animation: notifPop 200ms ease" @click="open">
      <Icon name="sparkles" class="w-3.5 h-3.5" style="color: var(--lime)" /> {{ unread }} notifikasi
    </button>
    <div v-if="panel" class="absolute right-0 top-11 z-50 w-[300px] max-h-[60vh] overflow-y-auto rounded-2xl bg-white" style="box-shadow: 0 12px 32px rgba(0,0,0,0.16), 0 2px 8px rgba(0,0,0,0.08); border: 1px solid #eee">
      <ul v-if="local.length" data-t="rutin-bell-list" class="divide-y divide-gray-50 border-b border-gray-100">
        <li v-for="it in local" :key="it.key">
          <router-link :to="lp('/shadaqa-rutin/bayar?date=' + it.date)" :data-t="'rutin-bell-' + it.key" class="block px-4 py-3 hover:bg-gray-50" @click="panel = false">
            <p class="text-[12.5px] font-semibold text-gray-800 leading-snug">{{ it.title }}</p>
            <p class="text-[11px] text-gray-400 leading-snug mt-1">{{ it.sub }}</p>
          </router-link>
        </li>
      </ul>
      <div v-if="!local.length || data.items.length" class="px-4 py-3 border-b border-gray-100 flex items-center gap-2">
        <Icon name="sparkles" class="w-4 h-4" style="color: var(--lime-text)" />
        <p class="text-[13px] font-bold text-gray-800">Doa yang diaminkan</p>
      </div>
      <div v-if="!data.items.length && !local.length" class="px-4 py-8 text-center">
        <Icon name="bell" class="w-8 h-8 mx-auto mb-2 text-gray-200" />
        <p class="text-[12px] text-gray-400">Belum ada yang mengaminkan doamu.</p>
      </div>
      <ul v-else-if="data.items.length" class="divide-y divide-gray-50">
        <li v-for="it in data.items" :key="it.doa_id" class="px-4 py-3">
          <p class="text-[12.5px] font-semibold text-gray-800 leading-snug">{{ teks(it) }}</p>
          <p v-if="it.message" class="text-[11px] text-gray-400 leading-snug mt-1 line-clamp-2 italic">“{{ it.message }}”</p>
        </li>
      </ul>
      <router-link :to="lp('/akun')" class="block px-4 py-3 border-t border-gray-100 text-center text-[12px] font-bold hover:bg-gray-50" style="color: var(--lime-text)" @click="panel = false">Lihat doa saya</router-link>
    </div>
  </div>
</template>

<style>
@keyframes notifPop { from { transform: translateY(-6px); opacity: 0 } to { transform: translateY(0); opacity: 1 } }
</style>
