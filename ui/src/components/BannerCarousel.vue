<script setup>
import { ref, onMounted, onBeforeUnmount } from 'vue'
import { lp } from '../i18n'
const props = defineProps({ banners: { type: Array, default: () => [] }, interval: { type: Number, default: 4000 } })
const i = ref(0)
let timer = null
function start() {
  clearInterval(timer)
  if (props.banners.length < 2) return
  timer = setInterval(() => { i.value = (i.value + 1) % props.banners.length }, props.interval)
}
function go(n) { i.value = n; start() }
onMounted(start)
onBeforeUnmount(() => clearInterval(timer))
</script>

<template>
  <div class="max-w-[480px] mx-auto sm:px-4 overflow-hidden">
    <div class="relative overflow-hidden">
      <div v-for="(b, n) in banners" :key="n" class="transition-opacity duration-500"
        :style="n === i ? 'position:relative;top:0;left:0;width:100%;opacity:1;pointer-events:auto' : 'position:absolute;top:0;left:0;width:100%;opacity:0;pointer-events:none'">
        <a class="block w-full" :href="lp(b.href)"><img :src="b.src" :alt="b.alt" style="display: block; width: 100%; height: auto" /></a>
      </div>
      <div class="absolute bottom-2 left-1/2 -translate-x-1/2 flex gap-1.5">
        <button v-for="(b, n) in banners" :key="n" class="rounded-full transition-all" :aria-label="'Banner ' + (n + 1)"
          :style="n === i ? 'width:20px;height:6px;background:white' : 'width:6px;height:6px;background:rgba(255,255,255,0.5)'" @click="go(n)"></button>
      </div>
    </div>
  </div>
</template>
