<script setup>
// Sheet "Ganti Foto Profil" di /akun. Logika disalin dari chunk /akun asli (komponen j):
//  - tab preset: POST /api/donor/avatar {preset:url} -> {ok, avatarUrl}
//  - tab unggah: pilih berkas -> pratinjau kanvas 480x480 (seret + zoom 1-3x) -> kanvas 512x512 webp q.85 (fallback jpeg) -> POST multipart field "file" -> {ok, avatarUrl}
// BELUM terverifikasi terhadap asli: tombol ini menulis data, jadi tidak pernah diklik di sedekah.id (hanya dibaca kodenya).
import { ref, watch, onBeforeUnmount } from 'vue'
import Icon from './Icon.vue'
import { t } from '../i18n'

const props = defineProps({ current: String, presets: Array })
const emit = defineEmits(['close', 'saved'])

const tab = ref('preset')
const cur = ref(props.current)
const file = ref(null)
const bmp = ref(null)
const noPrev = ref(false)
const zoom = ref(1)
const pos = ref({ x: 0, y: 0 })
const busy = ref(false)
const err = ref('')
const input = ref(null)
const canvas = ref(null)
let drag = null

function crop(b, z, p) {
  const s = Math.max(480 / b.width, 480 / b.height) * z, sw = 480 / s
  const mx = (b.width - sw) / 2, my = (b.height - sw) / 2
  return { sx: b.width / 2 - Math.max(-mx, Math.min(mx, p.x)) - sw / 2, sy: b.height / 2 - Math.max(-my, Math.min(my, p.y)) - sw / 2, sw, s }
}
async function post(init) {
  const r = await fetch('/api/donor/avatar', { method: 'POST', ...init })
  return [r, await r.json()]
}
async function pick(url) {
  if (busy.value) return
  cur.value = url; err.value = ''; busy.value = true
  try {
    const [r, a] = await post({ headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ preset: url }) })
    if (!r.ok || !a.ok || !a.avatarUrl) { err.value = a.error ?? t('akun.avatarError'); return }
    emit('saved', a.avatarUrl)
  } catch { err.value = t('akun.avatarError') } finally { busy.value = false }
}
async function upload() {
  if (!file.value) return
  err.value = ''; busy.value = true
  try {
    const fd = new FormData()
    if (bmp.value) {
      const c = document.createElement('canvas'); c.width = 512; c.height = 512
      const { sx, sy, sw } = crop(bmp.value, zoom.value, pos.value)
      c.getContext('2d').drawImage(bmp.value, sx, sy, sw, sw, 0, 0, 512, 512)
      const blob = (await new Promise((r) => c.toBlob(r, 'image/webp', 0.85))) ?? (await new Promise((r) => c.toBlob(r, 'image/jpeg', 0.85)))
      if (!blob) { err.value = t('akun.avatarError'); return }
      fd.append('file', blob, 'avatar.webp')
    } else fd.append('file', file.value)
    const [r, a] = await post({ body: fd })
    if (!r.ok || !a.ok || !a.avatarUrl) { err.value = a.error ?? t('akun.avatarError'); return }
    emit('saved', a.avatarUrl)
  } catch { err.value = t('akun.avatarError') } finally { busy.value = false }
}
function onFile(e) {
  const f = e.target.files?.[0] ?? null
  file.value = f; err.value = ''; noPrev.value = false; zoom.value = 1; pos.value = { x: 0, y: 0 }
  bmp.value?.close(); bmp.value = null
  if (f) createImageBitmap(f).then((b) => (bmp.value = b)).catch(() => (noPrev.value = true))
}
function draw() {
  const c = canvas.value; if (!c || !bmp.value) return
  const g = c.getContext('2d'); if (!g) return
  const { sx, sy, sw } = crop(bmp.value, zoom.value, pos.value)
  g.clearRect(0, 0, 480, 480); g.drawImage(bmp.value, sx, sy, sw, sw, 0, 0, 480, 480)
}
watch([bmp, zoom, pos, tab], () => requestAnimationFrame(draw), { flush: 'post' })
function down(e) { drag = { x: e.clientX, y: e.clientY }; e.currentTarget.setPointerCapture(e.pointerId) }
function move(e) {
  if (!drag || !bmp.value) return
  const rc = e.currentTarget.getBoundingClientRect(), { s } = crop(bmp.value, zoom.value, pos.value)
  const k = 480 / rc.width / s, dx = (e.clientX - drag.x) * k, dy = (e.clientY - drag.y) * k
  drag = { x: e.clientX, y: e.clientY }; pos.value = { x: pos.value.x + dx, y: pos.value.y + dy }
}
const up = () => { drag = null }
onBeforeUnmount(() => bmp.value?.close())
</script>

<template>
  <div class="fixed inset-0 z-[70] flex items-end justify-center bg-black/40" @click="emit('close')">
    <div class="w-full max-w-[480px] bg-white rounded-t-3xl p-5 pb-8 max-h-[85vh] overflow-y-auto" @click.stop>
      <div class="flex items-center justify-between mb-4">
        <p class="font-bold text-gray-900">{{ t('akun.avatarTitle') }}</p>
        <button :aria-label="t('akun.avatarClose')" @click="emit('close')"><Icon name="x" class="text-gray-400" style="width: 20px; height: 20px" /></button>
      </div>
      <div class="grid grid-cols-2 gap-2 mb-4">
        <button v-for="k in ['preset', 'upload']" :key="k" class="py-2 rounded-xl text-[13px] font-bold border" :class="tab === k ? 'bg-[color:var(--lime)] border-[color:var(--lime)] text-[#1a1a1a]' : 'bg-white border-gray-200 text-gray-500'" @click="tab = k">{{ t(k === 'preset' ? 'akun.avatarTabPreset' : 'akun.avatarTabUpload') }}</button>
      </div>
      <div v-if="tab === 'preset'" class="grid grid-cols-3 gap-3">
        <button v-for="u in presets" :key="u" :disabled="busy" class="relative" @click="pick(u)">
          <img :src="u" alt="" class="w-full aspect-square rounded-full object-cover border-4" :class="[cur === u ? 'border-[color:var(--lime)]' : 'border-transparent', busy && cur !== u ? 'opacity-50' : '']" />
          <span v-if="cur === u" class="absolute bottom-0 right-0 w-6 h-6 rounded-full bg-[color:var(--lime)] flex items-center justify-center"><Icon v-if="busy" name="loader" class="text-[#1a1a1a] animate-spin" style="width: 13px; height: 13px" /><Icon v-else name="check" class="text-[#1a1a1a]" style="width: 14px; height: 14px" /></span>
        </button>
      </div>
      <div v-else>
        <input ref="input" type="file" accept="image/*" class="hidden" @change="onFile" />
        <button v-if="!file" class="w-full rounded-2xl border-2 border-dashed border-gray-200 py-6 flex flex-col items-center gap-2" @click="input.click()">
          <svg class="text-gray-400" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" /><polyline points="17 8 12 3 7 8" /><line x1="12" x2="12" y1="3" y2="15" /></svg>
          <span class="text-[12px] font-semibold text-gray-500">{{ t('akun.avatarPickFile') }}</span>
          <span class="text-[10px] text-gray-400">JPG/PNG · maks 5MB</span>
        </button>
        <div v-if="file && bmp" class="flex flex-col items-center gap-3">
          <canvas ref="canvas" width="480" height="480" class="w-[240px] h-[240px] rounded-full border-4 border-[color:var(--lime)] cursor-move" style="touch-action: none" @pointerdown="down" @pointermove="move" @pointerup="up" @pointercancel="up"></canvas>
          <p class="text-[11px] text-gray-400">{{ t('akun.avatarDragHint') }}</p>
          <div class="flex items-center gap-2 w-full px-4">
            <svg class="text-gray-400 shrink-0" width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="8" /><line x1="21" x2="16.65" y1="21" y2="16.65" /><line x1="11" x2="11" y1="8" y2="14" /><line x1="8" x2="14" y1="11" y2="11" /></svg>
            <input v-model.number="zoom" type="range" min="1" max="3" step="0.01" class="w-full accent-[color:var(--lime)]" />
          </div>
          <button class="text-[12px] font-semibold text-[color:var(--lime-text)]" @click="input.click()">{{ t('akun.avatarChangePhoto') }}</button>
        </div>
        <div v-if="file && !bmp" class="rounded-2xl bg-gray-50 border border-gray-200 p-4 text-center">
          <p v-if="noPrev" class="text-[12px] text-gray-500">{{ t('akun.avatarNoPreview') }}</p>
          <Icon v-else name="loader" class="w-5 h-5 animate-spin mx-auto text-gray-400" />
          <button class="mt-2 text-[12px] font-semibold text-[color:var(--lime-text)]" @click="input.click()">{{ t('akun.avatarChangePhoto') }}</button>
        </div>
      </div>
      <p v-if="err" class="text-xs text-red-600 mt-3">{{ err }}</p>
      <p v-if="tab === 'preset'" class="mt-4 text-center text-[11px] text-gray-400">{{ t('akun.avatarTapHint') }}</p>
      <button v-else :disabled="busy || !file || (!bmp && !noPrev)" class="mt-4 w-full py-3 rounded-xl bg-[color:var(--lime)] text-[#1a1a1a] font-bold text-sm disabled:opacity-50 flex items-center justify-center gap-2" @click="upload"><Icon v-if="busy" name="loader" class="w-4 h-4 animate-spin" /><template v-else>{{ t('akun.avatarSave') }}</template></button>
    </div>
  </div>
</template>
