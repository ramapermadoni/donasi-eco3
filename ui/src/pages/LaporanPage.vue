<script setup>
import { ref, onMounted } from 'vue'
import AppHeader from '../components/AppHeader.vue'
import BottomNav from '../components/BottomNav.vue'
import Icon from '../components/Icon.vue'
import { t } from '../i18n'

// Replace with Frappe data: [{ id, judul, url_laporan, url_donatur }] (sedekah.id: GET /api/laporan)
const reports = ref([])
const loading = ref(true)
const openUrl = (u, target) => window.open(u, target)
onMounted(() => {
  fetch('/api/laporan').then((r) => r.json()).then((d) => { reports.value = Array.isArray(d) ? d : [] })
    .catch(() => {}).finally(() => { loading.value = false })
})
</script>

<template>
  <div class="frame">
    <AppHeader />
    <div class="min-h-screen max-w-[448px] mx-auto bg-white pb-28">
      <div class="px-4 pt-5 pb-3">
        <p style="font-size:15px;font-weight:700;color:#1a1a1a;margin-bottom:2px">{{ t('laporan.monthlyReports') }}</p>
        <p style="font-size:12px;color:#6b7280">{{ t('laporan.subtitle') }}</p>
      </div>
      <div class="px-4 space-y-3">
        <div v-if="loading" class="flex justify-center py-10"><Icon name="loader" class="w-6 h-6 animate-spin text-gray-300" /></div>
        <div v-else-if="reports.length === 0" class="text-center py-10">
          <Icon name="file" class="w-10 h-10 mx-auto mb-2 text-gray-200" />
          <p style="font-size:13px;color:#9ca3af">{{ t('laporan.empty') }}</p>
        </div>
        <div v-else v-for="r in reports" :key="r.id" class="flex items-center justify-between rounded-2xl bg-white px-4 py-4" style="box-shadow:0 1px 8px rgba(0,0,0,0.07), 0 0 0 1px rgba(0,0,0,0.04)">
          <span style="font-size:13px;font-weight:500;color:#374151">{{ r.judul }}</span>
          <div class="flex items-center gap-2 flex-shrink-0">
            <button v-if="r.url_laporan" class="flex items-center gap-1.5 px-3 py-1.5 rounded-full transition-all active:scale-95" style="background:#f97316;font-size:12px;font-weight:600;color:white;box-shadow:0 2px 6px rgba(249,115,22,0.3)" @click="openUrl(r.url_laporan, '_blank')"><Icon name="download" class="w-3 h-3" />{{ t('laporan.report') }}</button>
            <button v-if="r.url_donatur" class="flex items-center gap-1.5 px-3 py-1.5 rounded-full transition-all active:scale-95" style="background:#1a1a1a;font-size:12px;font-weight:600;color:white;box-shadow:0 2px 6px rgba(0,0,0,0.2)" @click="openUrl(r.url_donatur, '_blank')"><Icon name="users" class="w-3 h-3" />{{ t('laporan.donorList') }}</button>
          </div>
        </div>
      </div>
      <div class="px-4 mt-6">
        <div class="rounded-2xl px-4 py-3 flex gap-3 items-start" style="background:color-mix(in srgb, var(--lime) 6%, transparent);border:1px solid color-mix(in srgb, var(--lime) 15%, transparent)">
          <Icon name="file" class="w-4 h-4 flex-shrink-0 mt-0.5" style="color:var(--lime-text)" />
          <p style="font-size:11px;color:#374151;line-height:1.6">{{ t('laporan.note') }}</p>
        </div>
      </div>
    </div>
  </div>
  <BottomNav />
</template>
