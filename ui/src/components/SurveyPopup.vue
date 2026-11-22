<script setup>
import { lsGet, lsSet } from '../utils/storage'
// Survei kepuasan di /donasi/:id (status paid) — tiruan modul survei sedekah.id. Spec: docs/reference/survey-spec.md
// Kunci localStorage dtp_survey_<id> hanya ditulis setelah submit; skip/X/backdrop tidak menulis.
import { ref, onMounted, onBeforeUnmount } from 'vue'
import Icon from './Icon.vue'
import { t, apiHeaders } from '../i18n'

const props = defineProps({ donationId: String, preview: Boolean }) // preview (dev): abaikan kunci, POST tidak dikirim
const KEY = 'dtp_survey_' + props.donationId
const GRAD = 'linear-gradient(135deg, var(--lime) 0%, var(--lime-dark) 100%)'
const store = {
  get: () => lsGet(KEY),
  set: () => { lsSet(KEY, '1') },
}

const data = ref(null)
const open = ref(false)
const rating = ref(null)
const comment = ref('')
const submitting = ref(false)
const done = ref(false)
let cancelled = false
const timers = []
const later = (fn, ms) => timers.push(setTimeout(fn, ms))

const close = () => { open.value = false }

async function submit() {
  const s = data.value
  if (rating.value == null || !s?.question || !s.surveyId || submitting.value) return
  submitting.value = true
  try {
    if (props.preview) await new Promise((r) => setTimeout(r, 600))
    else await fetch('/api/satisfaction-survey', {
      method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ surveyId: s.surveyId, questionId: s.question.id, rating: rating.value, comment: comment.value.trim() || undefined, donationId: props.donationId }),
    })
    if (!props.preview) store.set()
    done.value = true
    later(() => { open.value = false }, 1900)
  } catch { open.value = false } finally { submitting.value = false }
}

onMounted(async () => {
  if (!props.preview && store.get() === '1') return
  try {
    const r = await fetch('/api/satisfaction-survey?donationId=' + encodeURIComponent(props.donationId), { headers: apiHeaders() })
    if (!r.ok) return
    const j = await r.json()
    if (cancelled || !(j.enabled && j.question && j.scale?.length)) return
    data.value = j
    later(() => { open.value = true }, 1200)
  } catch { /* diam */ }
})
onBeforeUnmount(() => { cancelled = true; timers.forEach(clearTimeout) })
</script>

<template>
  <Teleport to="body">
    <Transition name="sv-fade">
      <div v-if="data && open" class="fixed inset-0 z-[70] flex items-end justify-center sm:items-center" style="background: rgba(0,0,0,0.45)" @click="close">
        <div class="sv-sheet relative w-full sm:max-w-[440px] bg-white rounded-t-[28px] sm:rounded-[28px] px-5 pb-7" style="padding-top: 70px; box-shadow: 0 -8px 40px rgba(0,0,0,0.18)" @click.stop>
          <button type="button" :aria-label="t('survey.close')" class="absolute top-3.5 right-3.5 z-20 w-8 h-8 rounded-full flex items-center justify-center text-gray-400 hover:text-gray-600 hover:bg-gray-100 transition-colors" @click="close"><Icon name="x" style="font-size: 18px" /></button>

          <div class="absolute left-1/2 -translate-x-1/2 z-10" style="top: -52px">
            <img :src="data.imageUrl ? encodeURI(data.imageUrl) : '/review-kepuasan-pelanggan.png'" :alt="t('survey.imageAlt')" width="116" height="116" class="drop-shadow-lg" style="object-fit: contain" />
          </div>

          <div v-if="done" class="py-8 text-center">
            <div class="sv-pop w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-3" style="background: var(--lime)"><Icon name="check" style="font-size: 32px; color: #fff; stroke-width: 3" /></div>
            <p class="text-[17px] font-bold text-gray-800">{{ t('survey.thanksTitle') }}</p>
            <p class="text-[13px] text-gray-500 mt-1">{{ t('survey.thanksBody') }}</p>
          </div>
          <template v-else>
            <h3 class="text-center text-[19px] font-extrabold text-gray-900 leading-tight">{{ data.title ?? t('survey.headline') }}</h3>
            <p class="text-center text-[13.5px] text-gray-500 mt-1.5 mb-5 px-2 leading-snug">{{ data.question.text }}</p>

            <div class="grid gap-2" :style="{ gridTemplateColumns: `repeat(${data.scale.length}, minmax(0, 1fr))` }">
              <button v-for="(e, n) in data.scale" :key="n" type="button" class="flex flex-col items-center rounded-xl p-1.5 transition-all active:scale-95"
                :style="{ background: rating === n + 1 ? 'color-mix(in srgb, var(--lime) 22%, transparent)' : '#f1f3f5', boxShadow: rating === n + 1 ? '0 0 0 2px var(--lime)' : 'none' }" @click="rating = n + 1">
                <div class="w-full aspect-square flex items-center justify-center mb-1.5" style="background: white; border-radius: 0 0 0 12px; box-shadow: 0 1px 3px rgba(0,0,0,0.06)">
                  <span style="font-size: 22px; line-height: 1">{{ e.emoji }}</span>
                </div>
                <span class="text-center leading-tight" :style="{ fontSize: data.scale.length >= 5 ? '9.5px' : '10.5px', fontWeight: rating === n + 1 ? 700 : 500, color: rating === n + 1 ? '#005399' : '#6b7280' }">{{ e.label }}</span>
              </button>
            </div>

            <div class="sv-grow" :class="{ on: rating != null && data.commentEnabled }">
              <div class="overflow-hidden">
                <div v-if="rating != null && data.commentEnabled" class="mt-4">
                  <div class="flex items-center justify-between mb-1.5">
                    <label class="text-[12px] font-semibold text-gray-600">{{ t('survey.commentLabel') }}</label>
                    <span class="text-[11px] text-gray-400">{{ t('survey.commentOptional') }}</span>
                  </div>
                  <textarea v-model="comment" rows="2" maxlength="1000" :placeholder="data.commentPrompt || t('survey.commentPlaceholder')" class="w-full rounded-xl border border-gray-200 px-3 py-2.5 text-[13px] text-gray-700 outline-none resize-none focus:border-gray-400 transition-colors"></textarea>
                </div>
              </div>
            </div>

            <button type="button" class="mt-5 w-full py-3.5 rounded-2xl text-center font-bold transition-all active:scale-[0.98] flex items-center justify-center gap-2" :disabled="rating == null || submitting"
              :style="{ background: rating == null ? '#e5e7eb' : GRAD, color: rating == null ? '#9ca3af' : '#1a1a1a', fontSize: '14px', boxShadow: rating == null ? 'none' : '0 4px 16px color-mix(in srgb, var(--lime) 35%, transparent)' }" @click="submit">
              <Icon v-if="submitting" name="loader" class="animate-spin" style="font-size: 16px" />
              {{ submitting ? t('survey.submitting') : t('survey.submit') }}
            </button>
            <button type="button" class="mt-2.5 w-full text-center text-[12.5px] text-gray-400 hover:text-gray-600 transition-colors" @click="close">{{ t('survey.skip') }}</button>
          </template>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<style>
.sv-fade-enter-active, .sv-fade-leave-active { transition: opacity .3s ease; }
.sv-fade-enter-from, .sv-fade-leave-to { opacity: 0; }
.sv-fade-enter-active .sv-sheet { animation: sv-up .38s cubic-bezier(.22, 1, .36, 1); }
.sv-fade-leave-active .sv-sheet { animation: sv-up .3s ease-in reverse forwards; }
@keyframes sv-up { from { transform: translateY(100%); opacity: .5; } to { transform: none; opacity: 1; } }
.sv-grow { display: grid; grid-template-rows: 0fr; opacity: 0; transition: grid-template-rows .25s ease, opacity .25s ease; }
.sv-grow.on { grid-template-rows: 1fr; opacity: 1; }
.sv-grow > div { min-height: 0; }
.sv-pop { animation: sv-pop .5s cubic-bezier(.34, 1.56, .64, 1); }
@keyframes sv-pop { from { transform: scale(0); } to { transform: scale(1); } }
</style>
