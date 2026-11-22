<script setup>
import { computed } from 'vue'
import icons from '../icons'
const props = defineProps({ name: String })
const paths = computed(() => icons[props.name] || '')
</script>

<template>
  <svg xmlns="http://www.w3.org/2000/svg" width="1em" height="1em" viewBox="0 0 24 24" fill="none" stroke="currentColor"
    stroke-width="2" stroke-linecap="round" stroke-linejoin="round" v-html="paths" />
</template>
