<script setup>
// Status publik wakaf: dibuka/belum, nazhir tujuan, dan penerusan dana. Data: GET /api/campaigns/:slug/wakaf (mode terhubung).
// Tanpa data (mode demo / bukan wakaf / galat) komponen tidak menampilkan apa pun.
import { ref, watch } from 'vue'
import { t, isEn } from '../i18n'
import { rpSp } from '../utils/format'

const props = defineProps({ slug: { type: String, required: true } })
const emit = defineEmits(['loaded'])
const st = ref(null)

async function load() {
  st.value = null
  try {
    const r = await fetch(`/api/campaigns/${encodeURIComponent(props.slug)}/wakaf`)
    if (!r.ok) return
    const j = await r.json()
    if (j && j.wakaf) { st.value = j; emit('loaded', j) }
  } catch { /* mode demo atau server tak tersedia */ }
}
watch(() => props.slug, load, { immediate: true })

const day = (d) => new Date(d).toLocaleDateString(isEn.value ? 'en-GB' : 'id-ID', { day: 'numeric', month: 'long', year: 'numeric' })
</script>

<template>
  <section v-if="st" class="rounded-2xl bg-white border border-gray-200 p-4" aria-live="polite">
    <div class="flex items-center justify-between gap-3">
      <p class="text-[15px] font-bold text-gray-900">{{ t('wakafStatus.title') }}</p>
      <span class="text-[11px] font-bold px-2.5 py-1 rounded-full" :style="st.open ? 'background:#e6f0fa;color:#005399' : 'background:#fef3c7;color:#92400e'">{{ st.open ? t('wakafStatus.open') : t('wakafStatus.closed') }}</span>
    </div>

    <p v-if="!st.open" class="mt-2 text-[13px] text-gray-600 leading-relaxed">{{ t('wakafStatus.closedNote') }}</p>

    <template v-else>
      <p class="mt-2 text-[13px] text-gray-600 leading-relaxed">{{ st.mode === 'titipan' ? t('wakafStatus.modeTitipan') : t('wakafStatus.modeDikelola') }}</p>
      <div v-if="st.nazhir" class="mt-3 rounded-xl bg-gray-50 px-3 py-2.5">
        <p class="text-[11px] text-gray-500">{{ t('wakafStatus.nazhir') }}</p>
        <p class="text-[14px] font-semibold text-gray-900">{{ st.nazhir.name }}</p>
        <p class="text-[12px] text-gray-500">{{ t('wakafStatus.bwi') }}: {{ st.nazhir.noBwi }}</p>
      </div>

      <div v-if="st.mode === 'titipan'" class="mt-3 grid grid-cols-3 gap-2 text-center">
        <div class="rounded-xl bg-gray-50 py-2"><p class="text-[11px] text-gray-500">{{ t('wakafStatus.received') }}</p><p class="text-[13px] font-bold text-gray-900">{{ rpSp(st.received) }}</p></div>
        <div class="rounded-xl py-2" style="background:#e6f0fa"><p class="text-[11px] text-gray-500">{{ t('wakafStatus.forwarded') }}</p><p class="text-[13px] font-bold" style="color:#005399">{{ rpSp(st.forwarded) }}</p></div>
        <div class="rounded-xl bg-gray-50 py-2"><p class="text-[11px] text-gray-500">{{ t('wakafStatus.remaining') }}</p><p class="text-[13px] font-bold text-gray-900">{{ rpSp(st.remaining) }}</p></div>
      </div>

      <div v-if="st.mode === 'titipan'" class="mt-3">
        <p class="text-[12px] font-semibold text-gray-700">{{ t('wakafStatus.history') }}</p>
        <p v-if="!st.forwards.length" class="mt-1 text-[12px] text-gray-400">{{ t('wakafStatus.none') }}</p>
        <ul v-else class="mt-1 divide-y divide-gray-100">
          <li v-for="(f, i) in st.forwards" :key="i" class="flex items-center justify-between py-1.5 text-[13px]"><span class="text-gray-600">{{ day(f.date) }}</span><span class="font-semibold text-gray-900">{{ rpSp(f.amount) }}</span></li>
        </ul>
        <p class="mt-2 text-[11px] text-gray-400 leading-relaxed">{{ t('wakafStatus.note') }}</p>
      </div>
    </template>
  </section>
</template>
