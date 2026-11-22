<script setup>
import { nf, parseDigits } from '../utils/format'
// Kartu nominal zakat/wakaf: chip + input Rp. Teks hard-coded Indonesia (seperti aslinya, juga di /en).
import { ref, computed } from 'vue'
const props = defineProps({ label: String, modelValue: Number })
const emit = defineEmits(['update:modelValue'])
const CHIPS = [50000, 100000, 250000, 500000, 1000000, 2500000]
const chipLabel = (e) => (e >= 1e6 ? `${e / 1e6} jt` : `${e / 1e3} rb`)
const parse = parseDigits
const chip = ref(0)
const raw = ref('')
const amount = computed(() => (raw.value ? parse(raw.value) : chip.value))
const shown = computed(() => (raw.value ? nf(parse(raw.value)) : ''))
const emitAmt = () => emit('update:modelValue', amount.value)
function pick(c) { chip.value = c; raw.value = ''; emitAmt() }
function typed(e) { raw.value = e.target.value; emit('update:modelValue', amount.value); e.target.value = shown.value }
</script>

<template>
  <div class="bg-white rounded-2xl border border-gray-100 p-5">
    <p class="text-xs font-semibold text-gray-700 mb-2">{{ label }}</p>
    <div class="grid grid-cols-3 gap-2 mb-2.5">
      <button v-for="c in CHIPS" :key="c" type="button" class="py-2.5 rounded-xl text-[13px] font-semibold border"
        :class="!raw && c === chip ? 'bg-[var(--lime)] border-[var(--lime)] text-[#fff]' : 'bg-white border-gray-200 text-gray-600'" @click="pick(c)">{{ chipLabel(c) }}</button>
    </div>
    <div class="flex items-center rounded-xl border border-gray-200 focus-within:border-[var(--lime)] overflow-hidden">
      <span class="px-3 py-2.5 text-sm text-gray-400 bg-gray-50 border-r border-gray-100">Rp</span>
      <input inputmode="numeric" placeholder="Nominal lain" class="w-full px-3 py-2.5 text-sm focus:outline-none" :value="shown" @input="typed" />
    </div>
    <slot />
  </div>
</template>
