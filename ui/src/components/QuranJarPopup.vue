<script setup>
// Quran Jar — disalin dari sedekah.id (popup di beranda). Tidak memakai API: ayat (Arab + terjemahan Kemenag RI) adalah
// data statis per perasaan di src/data/quranjar.json (159 ayat). Reaksi disimpan di localStorage `dtp_qj_react`.
import { lsGet, lsSet } from '../utils/storage'
import { ref, computed, onMounted, onBeforeUnmount, nextTick, watch } from 'vue'
import Icon from './Icon.vue'
import { t } from '../i18n'

const emit = defineEmits(['close'])

const EASE = 'cubic-bezier(0.23,1,0.32,1)'
const GRAD = 'linear-gradient(135deg, var(--lime) 0%, var(--lime-dark) 100%)'
const GLOW = '0 4px 12px color-mix(in srgb, var(--lime) 30%, transparent)'
const REACT_KEY = 'dtp_qj_react'
const REACTIONS = [
  { id: 'love', img: '/emoji/suka.webp' },
  { id: 'peluk', img: '/emoji/peluk.webp' },
  { id: 'nangis', img: '/emoji/nangis.webp' },
  { id: 'berkaca', img: '/emoji/berkaca.webp' },
]
// posisi gulungan di toples: [x, y, rotasi]
const STICKS = [[100, 132, -8], [60, 138, 20], [40, 150, -12], [92, 146, 8], [104, 160, -20], [46, 166, 10], [84, 164, -6], [106, 176, 14], [38, 182, -4], [76, 180, 18], [104, 192, -10], [46, 196, 6], [84, 200, -6], [62, 154, -16], [96, 186, 4], [52, 176, -22], [90, 126, 12], [70, 194, 10]]

const data = ref(null) // { moods, verses }
const visible = ref(false)
const mood = ref(null)
const cur = ref(null) // { m, i }
const busy = ref(false)
const flash = ref('') // umpan balik tombol: 'copy' | 'share' | 'fail'
const reacts = ref(loadReacts())
const dialog = ref(null)
const jarBtn = ref(null)
const cork = ref(null)
const pourEl = ref(null)
const card = ref(null)
let prevOverflow = ''
let pending = false
let flashTimer = null
const bags = {}

function loadReacts() {
  try {
    const o = JSON.parse(lsGet(REACT_KEY, '{}'))
    const ok = {}
    for (const [k, v] of Object.entries(o)) if (REACTIONS.some((r) => r.id === v)) ok[k] = v
    return ok
  } catch { return {} }
}
const mlabel = (id) => t(`quranJar.moods.${id}.label`)
const moodOf = (id) => data.value?.moods.find((m) => m.id === id)
const verse = computed(() => (cur.value && data.value ? data.value.verses[cur.value.m][cur.value.i] : null))
const shownMood = computed(() => moodOf(cur.value ? cur.value.m : mood.value))
const refKey = computed(() => {
  if (!verse.value) return null
  const m = /\[(\d+)\]:\s*([\d–-]+)/.exec(verse.value.r)
  return m ? `${m[1]}:${m[2].replace(/–/g, '-')}` : verse.value.r
})
// Teks polos (tanpa karakter khusus) supaya rapi ditempel di WhatsApp, catatan, atau surel: Arab, terjemahan, lalu rujukan.
const bersih = (t) => t.replace(/[‘’]/g, "'").replace(/[“”]/g, '"').replace(/\s+/g, ' ').trim()
const shareText = computed(() => (verse.value ? `${verse.value.a}\n\n${bersih(verse.value.t)}\n\n${verse.value.r}\n\nQuran Jar` : ''))

// Web Animations API (menghormati prefers-reduced-motion, seperti aslinya)
const anim = (el, kf, opts) =>
  !el || window.matchMedia('(prefers-reduced-motion: reduce)').matches || typeof el.animate !== 'function'
    ? Promise.resolve()
    : el.animate(kf, opts).finished.then(() => undefined, () => undefined)
const shake = () => anim(jarBtn.value, [{ transform: 'rotate(0)' }, { transform: 'rotate(-6deg)' }, { transform: 'rotate(5deg)' }, { transform: 'rotate(-3deg)' }, { transform: 'rotate(0)' }], { duration: 420, easing: 'cubic-bezier(0.77,0,0.175,1)' })
const corkAnim = (open) => anim(cork.value, [{ transform: open ? 'none' : 'translate(18px,-30px) rotate(24deg)' }, { transform: open ? 'translate(18px,-30px) rotate(24deg)' : 'none' }], { duration: 260, easing: EASE, fill: 'forwards' })
function pour(color) {
  const el = pourEl.value
  if (!el) return Promise.resolve()
  el.style.background = color
  return anim(el, [{ transform: 'translate(-50%,20px) scaleX(.6)', opacity: 0 }, { transform: 'translate(-50%,-18px) scaleX(1)', opacity: 1, offset: 0.6 }, { transform: 'translate(-50%,-30px) scaleX(1)', opacity: 0 }], { duration: 420, easing: EASE })
}

// "kantong acak" per perasaan: semua ayat keluar sekali sebelum berulang; tidak mengulang ayat yang sama berturut-turut
function pickIndex(bag, len, last) {
  let b = bag && bag.length ? bag.slice() : []
  if (!b.length) {
    b = Array.from({ length: len }, (_, i) => i)
    for (let i = b.length - 1; i > 0; i--) { const j = Math.floor(Math.random() * (i + 1)); [b[i], b[j]] = [b[j], b[i]] }
    if (last != null && b.length > 1 && b[b.length - 1] === last) [b[0], b[b.length - 1]] = [b[b.length - 1], b[0]]
  }
  return [b.pop(), b]
}

async function draw() {
  if (!mood.value || busy.value || !data.value) return
  busy.value = true
  if (cur.value) await anim(card.value, [{ opacity: 1 }, { opacity: 0, transform: 'translateY(-6px)' }], { duration: 160, easing: EASE })
  await shake()
  corkAnim(true)
  await pour(moodOf(mood.value).color)
  pending = true
  const m = mood.value
  const last = cur.value && cur.value.m === m ? cur.value.i : null
  const [i, bag] = pickIndex(bags[m], data.value.verses[m].length, last)
  bags[m] = bag
  cur.value = { m, i }
  corkAnim(false)
}
// setelah kartu hasil muncul: animasi tirai + muncul berurutan
watch(cur, async () => {
  if (!cur.value || !pending) return
  pending = false
  await nextTick()
  const sc = dialog.value
  if (sc) sc.scrollTop = 0
  const el = card.value
  anim(el, [{ clipPath: 'inset(0 0 100% 0 round 20px)', transform: 'translateY(-8px)' }, { clipPath: 'inset(0 0 0% 0 round 20px)', transform: 'none' }], { duration: 360, easing: EASE })
  el?.querySelectorAll('[data-stagger]').forEach((n, i) => anim(n, [{ opacity: 0, transform: 'translateY(6px)' }, { opacity: 1, transform: 'none' }], { duration: 260, delay: 80 + 40 * i, easing: EASE, fill: 'backwards' }))
  busy.value = false
})

function react(id) {
  const k = refKey.value
  if (!k) return
  const t = { ...reacts.value }
  if (t[k] === id) delete t[k]; else t[k] = id
  reacts.value = t
  lsSet(REACT_KEY, JSON.stringify(t))
}
function tandai(k) { flash.value = k; clearTimeout(flashTimer); flashTimer = setTimeout(() => (flash.value = ''), 1800) }
// Clipboard API butuh HTTPS dan izin; di WebView atau http jatuh ke execCommand lewat textarea sementara.
async function tulisClipboard(teks) {
  try {
    if (navigator.clipboard?.writeText) { await navigator.clipboard.writeText(teks); return true }
  } catch { /* coba cara lama */ }
  try {
    const ta = document.createElement('textarea')
    ta.value = teks; ta.setAttribute('readonly', ''); ta.style.cssText = 'position:fixed;top:0;left:0;opacity:0'
    document.body.appendChild(ta); ta.select(); ta.setSelectionRange(0, teks.length)
    const ok = document.execCommand('copy')
    document.body.removeChild(ta)
    return ok
  } catch { return false }
}
async function copy(dari = 'copy') {
  if (!verse.value) return
  tandai((await tulisClipboard(shareText.value)) ? dari : 'fail')
}
async function share() {
  if (!verse.value) return
  if (typeof navigator.share !== 'function') return copy('share') // tanpa menu bagikan bawaan: salin dan beri tahu di tombol Bagikan
  try {
    await navigator.share({ title: 'Quran Jar', text: shareText.value })
  } catch (e) {
    if (e?.name !== 'AbortError') copy('share') // dibatalkan pengguna = diam; galat lain = salin
  }
}
function close() { visible.value = false; setTimeout(() => emit('close'), 180) }
const onKey = (e) => { if (e.key === 'Escape') close() }

onMounted(() => {
  import('../data/quranjar.json').then((m) => { data.value = m.default }).catch(() => {})
  window.addEventListener('keydown', onKey)
  prevOverflow = document.body.style.overflow
  document.body.style.overflow = 'hidden'
  requestAnimationFrame(() => { visible.value = true; setTimeout(() => dialog.value?.focus({ preventScroll: true }), 60) })
})
onBeforeUnmount(() => {
  window.removeEventListener('keydown', onKey)
  document.body.style.overflow = prevOverflow
  clearTimeout(flashTimer)
})
</script>

<template>
  <Teleport to="body">
    <div class="fixed inset-0 z-[70] flex items-center justify-center p-4" data-quran-jar-dialog>
      <div class="absolute inset-0 qj-fade" :class="{ on: visible }" style="background: rgba(8, 15, 44, 0.6); backdrop-filter: blur(2px)" aria-hidden="true" @click="close"></div>
      <div ref="dialog" tabindex="-1" role="dialog" aria-modal="true" aria-labelledby="quran-jar-title" data-jar-scroll
        class="relative w-full max-w-[400px] max-h-[88dvh] overflow-y-auto overscroll-contain rounded-[28px] bg-white p-5 outline-none qj-pop" :class="{ on: visible }"
        style="box-shadow: 0 24px 60px rgba(8, 15, 44, 0.4)">
        <h2 id="quran-jar-title" class="sr-only">{{ t('quranJar.eyebrow') }}</h2>
        <button type="button" :aria-label="t('quranJar.close')" data-jar-close class="absolute top-3 right-3 z-10 w-10 h-10 rounded-full bg-white/30 border border-white/50 text-[#1a1a1a] flex items-center justify-center active:scale-95 transition-transform" @click="close"><Icon name="x" class="w-[18px] h-[18px]" /></button>

        <div class="flex flex-col" data-quran-jar :data-state="cur ? 'result' : 'pick'">
          <!-- kepala: toples -->
          <div class="relative -mx-5 -mt-5 rounded-t-[28px] flex justify-center items-end overflow-hidden transition-[height] duration-300" :class="cur ? 'h-[124px]' : 'h-[212px]'" style="background: linear-gradient(135deg, var(--lime) 0%, var(--lime-dark) 55%, var(--lime-text) 100%)">
            <div aria-hidden="true" class="absolute -top-6 -left-6 w-24 h-24 rounded-full bg-white/15"></div>
            <div aria-hidden="true" class="absolute -bottom-5 -right-4 w-20 h-20 rounded-full bg-white/15"></div>
            <button type="button" :disabled="busy" :aria-label="cur ? t('quranJar.drawAnotherAria') : t('quranJar.shakeAria')" class="relative mb-3 active:scale-[0.97] transition-transform duration-[160ms]" @click="mood ? draw() : shake()">
              <div ref="jarBtn" style="transform-origin: 50% 100%" class="transition-[width] duration-300" :class="cur ? 'w-[74px]' : 'w-[132px]'">
                <svg viewBox="0 0 200 230" role="img" aria-label="Jar berisi gulungan ayat warna-warni" class="block w-full h-auto overflow-visible" data-jar-art>
                  <ellipse cx="100" cy="222" rx="70" ry="6" fill="#1a1a1a" opacity=".1" />
                  <g ref="cork" data-jar-cork style="transform-box: fill-box; transform-origin: 50% 100%">
                    <rect x="58" y="6" width="84" height="34" rx="8" fill="#C99A63" />
                    <g fill="#000" opacity=".14"><circle cx="74" cy="18" r="2" /><circle cx="96" cy="27" r="2.5" /><circle cx="120" cy="15" r="2" /><circle cx="130" cy="30" r="1.8" /></g>
                  </g>
                  <rect x="52" y="38" width="96" height="18" rx="5" fill="#FFFFFF" stroke="#c7dcf0" stroke-width="2" />
                  <path d="M50 50 C 80 57, 120 57, 150 50" fill="none" stroke="#B88A57" stroke-width="2.5" />
                  <rect x="30" y="54" width="140" height="162" rx="26" fill="#FFFFFF" stroke="#c7dcf0" stroke-width="2" />
                  <template v-if="data">
                    <g v-for="(s, n) in STICKS" :key="n" :transform="`translate(${s[0]} ${s[1]}) rotate(${s[2]} 28 4)`">
                      <rect width="56" height="8" rx="4" :fill="data.moods[n % data.moods.length].color"
                        :style="{ opacity: (cur?.m ?? mood) != null && (cur?.m ?? mood) !== data.moods[n % data.moods.length].id ? 0.22 : 1, transform: (cur?.m ?? mood) === data.moods[n % data.moods.length].id ? 'translateY(-4px)' : 'none', transition: 'opacity 200ms ease, transform 200ms cubic-bezier(0.23,1,0.32,1)' }" />
                    </g>
                  </template>
                  <rect x="56" y="80" width="88" height="44" rx="8" fill="#fff" stroke="#1a1a1a" stroke-width="1.2" />
                  <text x="100" y="101" text-anchor="middle" font-size="14" font-weight="700" fill="#1a1a1a" style="font-family: inherit; letter-spacing: -0.01em">Quran Jar</text>
                  <text x="100" y="116" text-anchor="middle" font-size="8.5" fill="#6b7280" style="font-family: inherit">{{ t('quranJar.jarTagline') }}</text>
                  <path d="M44 76 V 196" stroke="#fff" stroke-width="5" stroke-linecap="round" opacity=".9" />
                </svg>
              </div>
            </button>
            <div ref="pourEl" aria-hidden="true" class="pointer-events-none absolute left-1/2 top-3 w-16 h-3 rounded-full opacity-0"></div>
          </div>

          <!-- hasil -->
          <section v-if="cur && verse && shownMood && refKey" class="pt-3" aria-live="polite">
            <article ref="card" data-jar-card class="rounded-[20px] bg-white border border-gray-100 overflow-hidden" style="box-shadow: 0 8px 24px rgba(26, 26, 26, 0.08)">
              <div class="h-1.5" :style="{ background: shownMood.color }"></div>
              <div class="p-5 space-y-4">
                <p class="flex flex-wrap items-center gap-2 text-[12px] text-gray-500" data-stagger>
                  {{ t('quranJar.forLabel') }}
                  <span class="inline-flex items-center gap-1.5 rounded-full px-2.5 py-1 font-semibold text-gray-900" :style="{ background: shownMood.color + '24' }"><i class="w-2 h-2 rounded-full" :style="{ background: shownMood.color }" aria-hidden="true"></i>{{ mlabel(shownMood.id) }}</span>
                </p>
                <p class="text-[23px] leading-[2] text-right text-gray-900" dir="rtl" lang="ar" style="font-family: 'Amiri', 'Scheherazade New', 'Traditional Arabic', 'Noto Naskh Arabic', serif" data-stagger>{{ verse.a }}</p>
                <p class="text-[16px] leading-[1.65] text-gray-700" data-stagger>{{ verse.t }}</p>
                <p class="pt-3 border-t border-gray-100 text-[12px] font-extrabold text-[color:var(--lime-text)]" data-stagger>{{ verse.r }}</p>
              </div>
            </article>
            <div class="flex gap-2 mt-3" role="group" :aria-label="t('quranJar.reactionsAria')">
              <button v-for="r in REACTIONS" :key="r.id" type="button" :aria-pressed="reacts[refKey] === r.id" :aria-label="t(`quranJar.reactions.${r.id}`)" :title="t(`quranJar.reactions.${r.id}`)" :data-jar-react="r.id"
                class="flex-1 h-11 rounded-full flex items-center justify-center active:scale-[0.97] transition-[transform,background-color,box-shadow] duration-[160ms]"
                :class="reacts[refKey] === r.id ? 'bg-[color-mix(in_srgb,var(--lime)_25%,transparent)] shadow-[inset_0_0_0_1.5px_var(--lime-dark)]' : 'bg-gray-100'" @click="react(r.id)">
                <img :src="r.img" alt="" width="24" height="24" class="transition-transform duration-200" :class="reacts[refKey] === r.id && 'scale-110'" />
              </button>
            </div>
            <div class="grid grid-cols-[1.25fr_1fr_1fr] gap-2 mt-3 [&>button]:h-12 [&>button]:min-w-0 [&>button]:px-2 [&>button]:flex [&>button]:items-center [&>button]:justify-center [&>button]:gap-1.5 [&>button]:whitespace-nowrap">
              <button type="button" :disabled="busy" data-jar-again class="rounded-xl font-extrabold text-[14px] text-[#fff] active:scale-[0.97] transition-transform duration-[160ms]" :style="{ background: GRAD, boxShadow: GLOW }" @click="draw"><Icon name="refreshCw" class="w-4 h-4" :class="busy && 'animate-spin'" /> {{ t('quranJar.again') }}</button>
              <button type="button" data-jar-copy class="rounded-xl font-bold text-[14px] text-gray-700 bg-white border border-gray-200 active:scale-[0.97] transition-transform duration-[160ms]" @click="copy('copy')">
                <template v-if="flash === 'copy'"><Icon name="check" class="w-4 h-4" /> {{ t('quranJar.copiedShort') }}</template><template v-else-if="flash === 'fail'"><Icon name="x" class="w-4 h-4" /> Gagal</template><template v-else><Icon name="copy" class="w-4 h-4" /> {{ t('quranJar.copy') }}</template>
              </button>
              <button type="button" data-jar-share class="rounded-xl font-bold text-[14px] text-gray-700 bg-white border border-gray-200 active:scale-[0.97] transition-transform duration-[160ms]" @click="share"><template v-if="flash === 'share'"><Icon name="check" class="w-4 h-4" /> {{ t('quranJar.copiedShort') }}</template><template v-else><Icon name="share2" class="w-4 h-4" /> {{ t('quranJar.share') }}</template></button>
            </div>
            <button type="button" class="block mx-auto mt-2 h-11 px-3 text-[12px] font-semibold text-gray-900 underline decoration-[color:var(--lime)] decoration-2 underline-offset-4" @click="!busy && (cur = null)">{{ t('quranJar.back') }}</button>
          </section>

          <!-- pilih perasaan -->
          <section v-else class="pt-4" aria-labelledby="jar-pick-title">
            <h3 id="jar-pick-title" class="text-[20px] font-extrabold text-gray-900 leading-tight">{{ t('quranJar.title') }}</h3>
            <p class="text-[12px] text-gray-500 mt-1">{{ t('quranJar.subtitle') }}</p>
            <div class="grid grid-cols-2 min-[420px]:grid-cols-3 gap-2 mt-4" role="radiogroup" :aria-label="t('quranJar.moodsAria')">
              <button v-for="m in data?.moods || []" :key="m.id" type="button" role="radio" :aria-checked="mood === m.id" :data-mood="m.id"
                class="flex flex-col items-start gap-0.5 min-h-[58px] px-2.5 py-2.5 rounded-[16px] border-[1.5px] text-left active:scale-[0.97] transition-[transform,border-color,background-color] duration-[160ms]"
                :style="mood === m.id ? { borderColor: m.color, background: m.color + '1f' } : { borderColor: '#f3f4f6', background: '#fff' }" @click="mood = m.id">
                <span class="flex items-center gap-1.5 min-w-0 max-w-full text-[13.5px] font-semibold text-gray-900"><i class="w-2.5 h-2.5 rounded-full shrink-0" :style="{ background: m.color }" aria-hidden="true"></i><span class="truncate">{{ mlabel(m.id) }}</span></span>
                <span class="text-[12px] text-gray-500">{{ t(`quranJar.moods.${m.id}.hint`) }}</span>
              </button>
            </div>
            <button type="button" :disabled="!mood || busy || !data" data-jar-draw
              class="w-full h-12 mt-4 rounded-xl font-extrabold text-[14px] text-[#1a1a1a] active:scale-[0.97] transition-transform duration-[160ms] disabled:shadow-none disabled:bg-gray-100 disabled:text-gray-400 disabled:active:scale-100"
              :style="mood && data ? { background: GRAD, boxShadow: GLOW } : undefined" @click="draw">{{ data ? (mood ? t('quranJar.cta') : t('quranJar.ctaIdle')) : t('quranJar.loading') }}</button>
          </section>
          <p class="mt-2 text-center text-[11px] text-gray-400">{{ t('quranJar.source') }}</p>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<style scoped>
.qj-fade { opacity: 0; transition: opacity 200ms; }
.qj-fade.on { opacity: 1; }
.qj-pop { opacity: 0; transform: scale(0.96); transition: opacity 240ms cubic-bezier(0.23, 1, 0.32, 1), transform 240ms cubic-bezier(0.23, 1, 0.32, 1); }
.qj-pop.on { opacity: 1; transform: none; }
@media (prefers-reduced-motion: reduce) { .qj-fade, .qj-pop { transition: none; } }
</style>
