<script setup>
import { ref, computed, onMounted, nextTick } from 'vue'

const props = defineProps({ modelValue: { type: String, default: '' }, length: { type: Number, default: 6 }, autofocus: { type: Boolean, default: true } })
const emit = defineEmits(['update:modelValue', 'complete'])

const els = ref([])
const digits = computed(() => Array.from({ length: props.length }, (_, i) => props.modelValue[i] || ''))

function set(v) {
  const val = v.replace(/\D/g, '').slice(0, props.length)
  emit('update:modelValue', val)
  if (val.length === props.length) emit('complete', val)
}
function focus(i) { nextTick(() => { const el = els.value[Math.max(0, Math.min(i, props.length - 1))]; el?.focus(); el?.select() }) }

function onInput(e, i) {
  const d = e.target.value.replace(/\D/g, '')
  e.target.value = digits.value[i] // controlled: render from model
  if (!d) return
  const next = props.modelValue.slice(0, i) + d + props.modelValue.slice(i + 1)
  set(next)
  focus(Math.min(i + d.length, props.length - 1))
}
function onKey(e, i) {
  if (e.key === 'Backspace') {
    e.preventDefault()
    if (digits.value[i]) set(props.modelValue.slice(0, i) + props.modelValue.slice(i + 1))
    else if (i > 0) { set(props.modelValue.slice(0, i - 1) + props.modelValue.slice(i)); focus(i - 1) }
  } else if (e.key === 'ArrowLeft') { e.preventDefault(); focus(i - 1) }
  else if (e.key === 'ArrowRight') { e.preventDefault(); focus(i + 1) }
}
function onPaste(e) {
  e.preventDefault()
  const t = (e.clipboardData?.getData('text') || '').replace(/\D/g, '').slice(0, props.length)
  if (!t) return
  set(t); focus(t.length)
}
onMounted(() => { if (props.autofocus) focus(props.modelValue.length) })
</script>

<template>
  <div class="otp" @paste="onPaste">
    <input v-for="(d, i) in digits" :key="i" :ref="(el) => (els[i] = el)" class="otp-box" :class="{ on: d }"
      type="text" inputmode="numeric" pattern="[0-9]*" maxlength="2" :value="d" :aria-label="`Digit ${i + 1}`"
      :autocomplete="i === 0 ? 'one-time-code' : 'off'" @input="onInput($event, i)" @keydown="onKey($event, i)" @focus="$event.target.select()" />
  </div>
</template>
