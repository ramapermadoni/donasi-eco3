<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import Icon from './Icon.vue'
import { t, lp, stripLocale } from '../i18n'
const route = useRoute()
const base = computed(() => stripLocale(route.path))
const home = computed(() => base.value === '/')
const jk = computed(() => base.value.startsWith('/jalankebaikan'))
</script>

<template>
  <div class="sticky top-14 z-30" style="background: #f5f6f8">
    <div class="max-w-[480px] mx-auto px-4 py-2.5">
      <div class="grid grid-cols-2 gap-2">
        <router-link class="h-9 flex items-center justify-center gap-1.5 rounded-full transition-all active:scale-[0.98]" active-class="" exact-active-class="" :to="lp('/')"
          :style="home ? 'background:#e1edf8;border:1px solid #b9d4ee' : 'background:#fff;border:1px solid #ececef'">
          <Icon name="house" class="w-[15px] h-[15px]" :stroke="home ? '#005399' : '#8a8f98'" stroke-width="2.2" />
          <span class="text-[12px] leading-none" :style="home ? 'font-weight:600;color:#1a1a1a' : 'font-weight:500;color:#8a8f98'">{{ t('nav.tabHome') }}</span>
        </router-link>
        <router-link class="h-9 flex items-center justify-center gap-1.5 rounded-full transition-all active:scale-[0.98]" active-class="" exact-active-class="" :to="lp('/jalankebaikan')"
          :style="jk ? 'background:#e1edf8;border:1px solid #b9d4ee' : 'background:#fff;border:1px solid #ececef'">
          <Icon name="route" class="w-[15px] h-[15px]" :stroke="jk ? '#005399' : '#8a8f98'" stroke-width="2.2" />
          <span class="text-[12px] leading-none" :style="jk ? 'font-weight:600;color:#1a1a1a' : 'font-weight:500;color:#8a8f98'">{{ t('nav.tabJalanKebaikan') }}</span>
        </router-link>
      </div>
    </div>
  </div>
</template>
