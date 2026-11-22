<script setup>
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import AppHeader from '../components/AppHeader.vue'
import BottomNav from '../components/BottomNav.vue'
import legal from '../data/legal.json'
import legalEn from '../data/legal.en.json'
import { isEn, lp } from '../i18n'

// props.page = key in legal.json. Replace with CMS pages in Frappe (Web Page doctype).
const props = defineProps({ page: { type: String, required: true } })
const router = useRouter()
const doc = computed(() => (isEn.value ? legalEn : legal)[props.page])
// internal links in the HTML ("/akun", "/kebijakan-privasi") -> SPA navigation
function onClick(e) {
  const a = e.target.closest('a')
  if (a && a.getAttribute('href') && a.getAttribute('href').startsWith('/')) { e.preventDefault(); router.push(a.closest('[data-note]') ? a.getAttribute('href') : lp(a.getAttribute('href'))) }
}
</script>

<template>
  <div class="frame">
    <AppHeader />
    <main class="px-4 pt-4 pb-28">
      <div class="max-w-[640px] mx-auto">
        <header class="mb-6"><h1 class="text-2xl font-bold text-gray-900">{{ doc.title }}</h1><p class="mt-1 text-sm text-gray-500">{{ doc.subtitle }}</p></header>
        <article :class="['lg-art2', page === 'hapus-akun' && 'lg-bold']" class="rounded-2xl bg-white border border-gray-100 p-5 shadow-sm text-sm leading-relaxed text-gray-700" @click="onClick">
          <div v-if="doc.note" data-note class="rounded-xl bg-amber-50 border border-amber-200 px-4 py-3 mb-6"><p class="text-xs text-amber-800 leading-relaxed" v-html="doc.note"></p></div>
          <div class="lgb" v-html="doc.html"></div>
          <p v-if="doc.updated" class="upd">{{ isEn ? 'Last updated' : 'Terakhir diperbarui' }}: {{ doc.updated }}</p>
        </article>
      </div>
    </main>
  </div>
  <BottomNav />
</template>

<style scoped>
.lg-art2 :deep(.lgb > * + *) { margin-top: 8px; }
.lg-art2 :deep(.lgb > h2) { font-size: 16px; line-height: 24px; font-weight: 600; color: #111827; margin: 0; }
.lg-art2 :deep(.lgb > * + h2) { margin-top: 24px; }
.lg-art2 :deep(.lgb > h2 + *) { margin-top: 8px; }
.lg-art2 :deep(.lgb p), .lg-art2 :deep(.lgb ul), .lg-art2 :deep(.lgb ol) { margin-bottom: 0; }
.lg-art2.lg-bold :deep(.lgb > h2) { font-weight: 700; }
.lg-art2 :deep(ul), .lg-art2 :deep(ol) { padding-left: 20px; }
.lg-art2 :deep(ul) { list-style: disc; } .lg-art2 :deep(ol) { list-style: decimal; }
.lg-art2 :deep(li + li) { margin-top: 4px; }
.lg-art2 :deep(a) { text-decoration: underline; font-weight: 500; color: inherit; }
.lg-art2 .upd { margin-top: 24px; padding-top: 8px; border-top: 1px solid #f3f4f6; font-size: 12px; line-height: 16px; color: #9ca3af; }
</style>
