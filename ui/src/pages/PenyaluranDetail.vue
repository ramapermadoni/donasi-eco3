<script setup>
import { shareLink } from '../utils/share'
import { computed, reactive, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import Icon from '../components/Icon.vue'
import data from '../data/penyaluran.json'
import { t, lp } from '../i18n'
import { dariServer } from '../contentLoader'

// description is sanitized HTML (scrape step); sanitize server-side too in Frappe.
const route = useRoute()
const router = useRouter()
const remote = ref(null)
const loading = ref(false)
async function load() {
  if (!dariServer.value) return
  loading.value = true; remote.value = null
  try { const r = await fetch(`/api/penyaluran/${encodeURIComponent(route.params.slug)}`); remote.value = r.ok ? await r.json() : null } catch { remote.value = null }
  loading.value = false
}
watch(() => route.params.slug, load, { immediate: true })
// konten contoh sudah dibersihkan -> dari server; selain itu berkas statis bawaan
const item = computed(() => (dariServer.value ? remote.value : data.items.find((i) => i.slug === route.params.slug)))
const toast = reactive({ msg: '' })
function back() { window.history.length > 1 ? router.back() : router.push(lp('/penyaluran')) }
const share = () => shareLink(item.value.title, location.href, () => { toast.msg = 'Link disalin'; setTimeout(() => (toast.msg = ''), 1800) })
</script>

<template>
  <div class="frame" style="background: #fff">
    <div v-if="loading" class="wrap" style="padding: 80px 16px; text-align: center"><p style="color: #6b7280">{{ t('common.loading') }}</p></div>

    <div v-else-if="!item" class="wrap" style="padding: 80px 16px; text-align: center">
      <p style="font-weight: 600; margin-bottom: 12px">Berita penyaluran tidak ditemukan</p>
      <router-link :to="lp('/penyaluran')" class="more" style="justify-content: center">Kembali ke Penyaluran</router-link>
    </div>

    <div v-else class="pd">
      <div class="d-hero">
        <img :src="item.image" :alt="item.title" />
        <div class="d-shade" style="background: linear-gradient(to top, rgba(0,0,0,.6), rgba(0,0,0,.1), transparent)"></div>
        <button class="d-circle" style="left: 16px" aria-label="Kembali" @click="back"><Icon name="back" /></button>
        <button class="d-circle" style="right: 16px" aria-label="Bagikan" @click="share"><Icon name="share" /></button>
        <span class="pd-badge">{{ item.program || item.category }}</span>
      </div>

      <div class="pd-body">
        <h1>{{ item.title }}</h1>
        <div class="pd-meta">
          <span><Icon name="calendar" />{{ item.date }}</span>
          <span><Icon name="mapPin" />{{ item.location }}</span>
        </div>
        <div class="pd-hr"></div>
        <p class="pd-h">{{ t('penyaluran.detailHeading') }}</p>
        <div class="prose pd-prose" v-html="item.description"></div>
      </div>

      <div class="pd-bar">
        <button class="sh" aria-label="Bagikan" @click="share"><Icon name="share" /></button>
        <router-link :to="lp('/')" class="go"><Icon name="heart" />{{ t('penyaluran.donateNow') }}</router-link>
      </div>
      <div v-if="toast.msg" class="toast">{{ toast.msg }}</div>
    </div>
  </div>
</template>

<style scoped>
.pd-prose :deep(a) { color: #1a1a1a; text-decoration: underline; text-decoration-thickness: 1px; text-underline-offset: 2px; }
.pd-prose :deep(strong), .pd-prose :deep(b) { font-weight: 600; color: #1a1a1a; }
.pd-prose { padding-top: 8px; }
.pd-prose :deep(p) { line-height: 1.625; }
</style>
