<script setup>
// Pengendali popup beranda — meniru sedekah.id: sekali per hari (localStorage `doa_amin_popup_date` untuk jatah doa/video,
// `quran_jar_popup_date` untuk Quran Jar; nilainya tanggal lokal tanpa nol di depan, mis. 2026-11-20).
// Bila jatah doa/video belum terpakai, urutan ["doa","video","quranjar"] diacak (Fisher-Yates) dan sumber pertama yang tersedia menang;
// bila hanya jatah Quran Jar yang tersisa, hanya Quran Jar. Popup dibuka 400 ms setelah pemenang ditentukan.
import { lsGet, lsSet } from '../utils/storage'
import { ref, onMounted, onBeforeUnmount } from 'vue'
import QuranJarPopup from './QuranJarPopup.vue'
import DoaAminPopup from './DoaAminPopup.vue'

const MIX_KEY = 'doa_amin_popup_date'
const JAR_KEY = 'quran_jar_popup_date'
const AMIN_KEY = 'dtp_doa_amins'

const kind = ref(null) // 'mix' | 'jar'
const open = ref(false)
const doas = ref([])
const video = ref(null)
let cancelled = false
let timer = null

const today = () => { const d = new Date(); return `${d.getFullYear()}-${d.getMonth() + 1}-${d.getDate()}` }
const localAmins = () => { try { return JSON.parse(lsGet(AMIN_KEY, '{}')) } catch { return {} } }
const shuffle = (rnd = Math.random) => {
  const a = ['doa', 'video', 'quranjar']
  for (let i = a.length - 1; i > 0; i--) { const j = Math.floor(rnd() * (i + 1)); [a[i], a[j]] = [a[j], a[i]] }
  return a
}

const sources = {
  async doa() {
    const r = await fetch('/api/doa/untuk-diaminkan?limit=12').catch(() => null)
    if (!r?.ok) return false
    const data = await r.json()
    const l = localAmins()
    const list = (data ?? []).filter((d) => (l[d.id] ?? 0) === 0).slice(0, 3)
    if (!list.length || cancelled) return false
    doas.value = list
    return true
  },
  async video() {
    const r = await fetch('/api/video/latest').catch(() => null)
    if (!r?.ok) return false
    const { video: v } = await r.json()
    if (!v || cancelled) return false
    video.value = v
    return true
  },
  async quranjar() { if (!cancelled) kind.value = 'jar'; return !cancelled },
}

onMounted(async () => {
  let mix = false, jar = false
  try { mix = localStorage.getItem(MIX_KEY) !== today(); jar = localStorage.getItem(JAR_KEY) !== today() } catch { return }
  if (!mix && !jar) return
  let winner = null
  for (const name of mix ? shuffle() : jar ? ['quranjar'] : []) {
    if (await sources[name]()) { winner = name; break }
  }
  if (mix) lsSet(MIX_KEY, today())
  if (winner === 'quranjar') lsSet(JAR_KEY, today())
  if (winner && !cancelled) {
    if (winner !== 'quranjar') kind.value = 'mix'
    timer = setTimeout(() => { if (!cancelled) open.value = true }, 400)
  }
})
onBeforeUnmount(() => { cancelled = true; clearTimeout(timer) })
</script>

<template>
  <template v-if="open">
    <QuranJarPopup v-if="kind === 'jar'" @close="open = false" />
    <DoaAminPopup v-else-if="kind === 'mix'" :doas="doas" :video="video" @close="open = false" />
  </template>
</template>
