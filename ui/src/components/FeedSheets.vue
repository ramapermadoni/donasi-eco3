<script setup>
// Sheet "Filter" dan "Urutkan" (bottom sheet). Dipakai PenyaluranPage dan BeritaPage; markup dan teks identik
// (kedua halaman memakai kunci i18n penyaluran.* untuk sheet).
import { t } from '../i18n'
import { FEED_SORTS as SORTS } from '../composables/useFeedList'
defineProps({ meta: { type: Object, required: true } })
defineEmits(['reset'])
const filterOpen = defineModel('filterOpen', { type: Boolean })
const sortOpen = defineModel('sortOpen', { type: Boolean })
const location = defineModel('location')
const program = defineModel('program')
const sortKey = defineModel('sortKey', { type: String })
const setLocation = (x) => { location.value = x }
const setProgram = (x) => { program.value = x }
</script>

<template>
  <!-- Filter -->
  <div v-if="filterOpen" class="fixed inset-0 z-[60] flex items-end justify-center" role="dialog" aria-modal="true">
    <div class="absolute inset-0 bg-black/40" @click="filterOpen = false"></div>
    <div class="relative w-full max-w-[448px] bg-white rounded-t-3xl shadow-2xl pb-4 max-h-[85vh] flex flex-col">
      <div class="pt-3 flex justify-center"><div class="w-10 h-1 rounded-full bg-gray-300"></div></div>
      <div class="px-5 py-3 flex items-center justify-between">
        <h3 style="font-size: 15px; font-weight: 700; color: #1a1a1a">{{ t('penyaluran.filter') }}</h3>
        <button class="w-8 h-8 rounded-full flex items-center justify-center hover:bg-gray-100" :aria-label="t('penyaluran.close')" @click="filterOpen = false"><svg class="w-4 h-4 text-gray-500" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M18 6 6 18" /><path d="m6 6 12 12" /></svg></button>
      </div>
      <div class="overflow-y-auto px-5 pb-2">
        <div v-for="g in [{ t: t('penyaluran.location'), o: meta.locations, v: location, e: t('penyaluran.noLocations'), set: setLocation }, { t: t('penyaluran.program'), o: meta.programs, v: program, e: t('penyaluran.noPrograms'), set: setProgram }]" :key="g.t" class="py-3 border-b border-gray-100 last:border-b-0">
          <p style="font-size: 12px; font-weight: 700; color: #374151; margin-bottom: 8px">{{ g.t }}</p>
          <p v-if="!g.o.length" style="font-size: 12px; color: #9ca3af">{{ g.e }}</p>
          <div v-else class="flex flex-wrap gap-2">
            <button v-for="opt in [null, ...g.o]" :key="opt ?? 'all'" class="px-3 py-1.5 rounded-full border transition-all"
              :style="{ fontSize: '12px', fontWeight: g.v === opt ? 700 : 500, background: g.v === opt ? '#1a1a1a' : 'white', color: g.v === opt ? 'white' : '#374151', borderColor: g.v === opt ? '#1a1a1a' : '#e5e7eb' }"
              @click="g.set(opt === null || g.v === opt ? null : opt)">{{ opt ?? t('penyaluran.all') }}</button>
          </div>
        </div>
      </div>
      <div class="px-5 pt-3 border-t border-gray-100 mt-2 flex gap-2">
        <button class="flex-1 py-2.5 rounded-xl border border-gray-200 text-gray-700" style="font-size: 13px; font-weight: 600" @click="$emit('reset')">{{ t('penyaluran.reset') }}</button>
        <button class="flex-1 py-2.5 rounded-xl" style="background: var(--lime); color: #fff; font-size: 13px; font-weight: 700" @click="filterOpen = false">{{ t('penyaluran.apply') }}</button>
      </div>
    </div>
  </div>

  <!-- Urutkan -->
  <div v-if="sortOpen" class="fixed inset-0 z-[60] flex items-end justify-center" role="dialog" aria-modal="true">
    <div class="absolute inset-0 bg-black/40" @click="sortOpen = false"></div>
    <div class="relative w-full max-w-[448px] bg-white rounded-t-3xl shadow-2xl pb-4 max-h-[85vh] flex flex-col">
      <div class="pt-3 flex justify-center"><div class="w-10 h-1 rounded-full bg-gray-300"></div></div>
      <div class="px-5 py-3 flex items-center justify-between">
        <h3 style="font-size: 15px; font-weight: 700; color: #1a1a1a">{{ t('penyaluran.sort') }}</h3>
        <button class="w-8 h-8 rounded-full flex items-center justify-center hover:bg-gray-100" :aria-label="t('penyaluran.close')" @click="sortOpen = false"><svg class="w-4 h-4 text-gray-500" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M18 6 6 18" /><path d="m6 6 12 12" /></svg></button>
      </div>
      <div class="overflow-y-auto px-5 pb-2"><div class="py-2">
        <button v-for="[k, l] in SORTS" :key="k" class="w-full flex items-center justify-between py-3 border-b border-gray-100 last:border-b-0" @click="sortKey = k; sortOpen = false">
          <span :style="{ fontSize: '14px', fontWeight: sortKey === k ? 700 : 500, color: sortKey === k ? '#1a1a1a' : '#374151' }">{{ t('penyaluran.' + l) }}</span>
          <svg v-if="sortKey === k" class="w-4 h-4" style="color: var(--lime-text)" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M20 6 9 17l-5-5" /></svg>
        </button>
      </div></div>
    </div>
  </div>
</template>
