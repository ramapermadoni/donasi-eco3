<script setup>
import Icon from './Icon.vue'
import { t, lp } from '../i18n'
const year = new Date().getFullYear()
</script>

<template>
  <footer class="px-4 pt-6 pb-4">
    <div class="max-w-[448px] mx-auto">
      <div class="rounded-2xl bg-white/70 backdrop-blur-sm border border-gray-100 p-4 shadow-sm">
        <div class="flex gap-3">
          <div class="flex-shrink-0"><div class="w-8 h-8 rounded-full bg-[color:color-mix(in_srgb,var(--lime-dark)_10%,transparent)] flex items-center justify-center"><Icon name="shieldCheck" class="w-4 h-4 text-[color:var(--lime-text)]" /></div></div>
          <p class="text-xs leading-relaxed text-gray-600">{{ t('home.footerDisclaimer') }}</p>
        </div>
      </div>
      <div class="mt-3 flex items-center justify-center gap-3 text-[11px] text-gray-500">
        <router-link class="hover:text-[color:var(--lime-text)] hover:underline" :to="lp('/syarat-ketentuan')">{{ t('home.termsLink') }}</router-link>
        <span class="text-gray-300">•</span>
        <router-link class="hover:text-[color:var(--lime-text)] hover:underline" :to="lp('/kebijakan-privasi')">{{ t('home.privacyLink') }}</router-link>
      </div>
      <p class="mt-2 text-center text-[10px] text-gray-400">© {{ year }} donasi</p>
    </div>
  </footer>
</template>
