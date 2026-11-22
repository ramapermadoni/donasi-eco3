<script setup>
import { initial } from '../utils/text'
import { computed } from 'vue'
import { t, tr, lp, isEn } from '../i18n'
import AppHeader from '../components/AppHeader.vue'
import BottomNav from '../components/BottomNav.vue'
import Icon from '../components/Icon.vue'
import data from '../data/teman.json'
// Replace with Frappe: paginated list of public donations (masked name, method, amount, time, campaign)

const PER = 10
const page = 1
const totalNum = computed(() => Number(String(data.total).replace(/\D/g, '')) || data.rows.length)
const pages = computed(() => Math.max(1, Math.ceil(totalNum.value / PER)))
// /en menampilkan format angka & waktu gaya Inggris (Rp2,000 · 3m ago)
const money = (v) => (isEn.value ? String(v).replace(/\./g, ',') : v)
const ago = (w) => (isEn.value ? String(w).replace(/^(\d+) mnt lalu$/, '$1m ago').replace(/^(\d+) jam lalu$/, '$1h ago').replace(/^(\d+) hari lalu$/, '$1d ago') : w)
const pageList = computed(() => {
  const e = page, a = pages.value, n = []
  if (a <= 5) for (let i = 1; i <= a; i++) n.push(i)
  else if (e <= 3) n.push(1, 2, 3, 4, '...', a)
  else if (e >= a - 2) n.push(1, '...', a - 3, a - 2, a - 1, a)
  else n.push(1, '...', e - 1, e, e + 1, '...', a)
  return n
})
const isAnon = (r) => !r.name || r.name === 'Teman Sedekah'
const who = (r) => (isAnon(r) ? t('teman.anonymousDonor') : r.name)
</script>

<template>
  <div class="frame">
    <AppHeader />
    <div class="min-h-screen pb-28 bg-white">
      <div class="max-w-[480px] mx-auto" style="background:linear-gradient(160deg, #e8f0fe 0%, #ffffff 40%);min-height:100vh">
        <div class="relative overflow-hidden pt-6 pb-6" style="background:linear-gradient(135deg, #1a1a1a 0%, #2d2d2d 100%)">
          <div class="absolute -top-8 -right-8 w-36 h-36 rounded-full bg-white/10"></div>
          <div class="absolute top-4 -right-2 w-20 h-20 rounded-full bg-black/10"></div>
          <div class="absolute -bottom-4 -left-6 w-28 h-28 rounded-full bg-white/10"></div>
          <div class="relative z-10 px-4">
            <h1 class="text-white" style="font-size:22px;font-weight:800;line-height:1.2">{{ t('teman.title') }}</h1>
            <p class="text-white/70 mt-1" style="font-size:13px">{{ t('teman.donorsCount', { count: money(data.total) }) }}</p>
          </div>
          <div class="absolute bottom-0 left-0 right-0 h-1" style="background:rgba(0,0,0,0.15)"></div>
        </div>

        <div class="px-4">
          <div class="mt-4 rounded-2xl overflow-hidden" style="background:white;box-shadow:0 2px 20px color-mix(in srgb, var(--lime) 8%, transparent), 0 1px 4px rgba(0,0,0,0.04);border:1px solid color-mix(in srgb, var(--lime) 8%, transparent)">
            <div class="grid px-4 py-3" style="grid-template-columns:1fr 1fr 1fr;background:linear-gradient(90deg, color-mix(in srgb, var(--lime) 5%, transparent) 0%, rgba(0,71,179,0.03) 100%);border-bottom:1px solid color-mix(in srgb, var(--lime) 8%, transparent)">
              <span style="font-size:11px;font-weight:700;color:#374151">{{ t('teman.colDonor') }}</span>
              <span style="font-size:11px;font-weight:700;color:var(--lime-text);text-align:center">{{ t('teman.colAmount') }}</span>
              <span style="font-size:11px;font-weight:700;color:#374151;text-align:right">{{ t('teman.colTime') }}</span>
            </div>
            <div v-if="data.rows.length === 0" class="py-12 text-center">
              <Icon name="heart" class="w-10 h-10 text-gray-200 mx-auto mb-3" />
              <p style="font-size:13px;color:#9ca3af">{{ t('teman.empty') }}</p>
            </div>
            <div v-for="(r, n) in data.rows" :key="n" class="grid px-4 py-3.5 items-center transition-colors hover:bg-blue-50/30" :style="{ gridTemplateColumns: '1fr 1fr 1fr', borderBottom: n < data.rows.length - 1 ? '1px solid #f3f4f6' : 'none' }">
              <div class="flex items-center gap-2 min-w-0">
                <div class="w-7 h-7 rounded-full flex items-center justify-center flex-shrink-0" :style="{ background: isAnon(r) ? 'linear-gradient(135deg, #e5e7eb, #d1d5db)' : 'linear-gradient(135deg, var(--lime), var(--lime-dark))' }">
                  <span :style="{ fontSize: '10px', fontWeight: 700, color: isAnon(r) ? '#9ca3af' : '#1a1a1a' }">{{ isAnon(r) ? '?' : initial(r.name) }}</span>
                </div>
                <span class="truncate" :style="{ fontSize: '12px', fontWeight: isAnon(r) ? 400 : 600, color: isAnon(r) ? '#9ca3af' : '#374151', fontStyle: isAnon(r) ? 'italic' : 'normal' }">{{ who(r) }}</span>
              </div>
              <div class="flex flex-col items-center gap-0.5">
                <div class="relative inline-flex items-center justify-center flex-shrink-0" style="width:36px;height:24px;background:white;border-radius:6px;border:1px solid #f3f4f6;padding:2px">
                  <img v-if="r.logo" :src="r.logo" :alt="r.method" class="object-contain" style="position:absolute;height:100%;width:100%;left:0;top:0;right:0;bottom:0;color:transparent;padding:3px" />
                </div>
                <span style="font-size:12px;font-weight:700;color:#1a1a1a">{{ money(r.amount) }}</span>
              </div>
              <div class="text-right">
                <span style="font-size:11px;color:#9ca3af">{{ ago(r.when) }}</span>
                <div v-if="r.campaign" class="mt-0.5 truncate ml-auto max-w-[215px]" style="font-size:9px;color:#d1d5db;font-weight:500">{{ r.campaign }}</div>
              </div>
            </div>
          </div>

          <div class="mt-3 text-center">
            <p style="font-size:11px;color:#9ca3af">{{ t('teman.showing', { start: 1, end: data.rows.length, total: money(data.total) }) }}</p>
          </div>

          <div v-if="pages > 1" class="mt-3 flex items-center justify-center gap-1.5">
            <span aria-disabled="true" class="w-8 h-8 flex items-center justify-center rounded-lg border border-gray-200 bg-white text-gray-500 opacity-30"><Icon name="chevronLeft" class="w-4 h-4" /></span>
            <template v-for="(p, i) in pageList" :key="i">
              <span v-if="p === '...'" class="w-8 h-8 flex items-center justify-center text-gray-400" style="font-size:13px">···</span>
              <a v-else class="w-8 h-8 flex items-center justify-center rounded-lg border transition-all" :style="p === page ? 'font-size:13px;font-weight:700;background:linear-gradient(135deg, var(--lime), var(--lime-dark));color:#fff;border-color:var(--lime);box-shadow:0 2px 8px color-mix(in srgb, var(--lime) 30%, transparent)' : 'font-size:13px;font-weight:500;background:white;color:#374151;border-color:#e5e7eb;box-shadow:none'" href="#" @click.prevent>{{ p }}</a>
            </template>
            <a class="w-8 h-8 flex items-center justify-center rounded-lg border border-gray-200 bg-white text-gray-500 hover:bg-gray-50 transition-all" href="#" @click.prevent><Icon name="chevronRight" class="w-4 h-4" /></a>
          </div>

          <a class="mt-6 rounded-2xl bg-white border border-gray-100 p-4 flex items-center gap-3 hover:shadow-md transition-shadow" :href="lp('https://sedekah.id/mitra')">
            <div class="w-11 h-11 rounded-xl flex items-center justify-center flex-shrink-0" style="background:linear-gradient(135deg, var(--lime), var(--lime-dark))"><Icon name="users" class="w-5 h-5" style="color:#fff" /></div>
            <div class="min-w-0 flex-1">
              <p class="text-sm font-bold text-gray-900">Mitra Sedekah</p>
              <p class="text-xs text-gray-500 mt-0.5">Personal, institusi &amp; komunitas yang menggalang kebaikan bersama.</p>
            </div>
            <Icon name="chevronRight" class="w-5 h-5 text-gray-400 flex-shrink-0" />
          </a>

          <div class="mt-6 mb-4 rounded-2xl overflow-hidden" style="background:linear-gradient(135deg, #1a1a1a 0%, #2d2d2d 100%);box-shadow:0 4px 20px color-mix(in srgb, var(--lime) 25%, transparent)">
            <div class="px-5 pt-5 pb-4 flex items-center gap-3">
              <div class="w-10 h-10 rounded-xl flex items-center justify-center flex-shrink-0" style="background:linear-gradient(135deg, var(--lime), var(--lime-dark))"><Icon name="heart" class="w-5 h-5" style="fill:#fff;stroke:#fff" /></div>
              <div>
                <div style="font-size:16px;font-weight:800;color:white;line-height:1.1">sedekah<span style="color:var(--lime)">.id</span></div>
                <div style="font-size:10px;color:rgba(255,255,255,0.6);font-weight:500">{{ t('teman.platformTagline') }}</div>
              </div>
            </div>
            <div class="mx-4 mb-4 rounded-xl px-4 py-3" style="background:rgba(255,255,255,0.1)">
              <p style="font-size:11px;font-weight:700;color:var(--lime);margin-bottom:4px">{{ t('teman.aboutTitle') }}</p>
              <p style="font-size:11px;color:rgba(255,255,255,0.8);line-height:1.6" v-html="tr('teman.aboutText', {}, { b: (i) => '<strong style=&quot;color:white&quot;>' + i + '</strong>' })"></p>
            </div>
            <div class="mx-4 mb-5 rounded-xl px-4 py-3" style="background:rgba(0,0,0,0.15)">
              <div class="flex items-center gap-1.5 mb-2"><Icon name="shield" class="w-3.5 h-3.5" style="color:var(--lime)" /><p style="font-size:11px;font-weight:700;color:var(--lime)">Disclaimer</p></div>
              <p style="font-size:10.5px;color:rgba(255,255,255,0.7);line-height:1.7" v-html="tr('teman.disclaimer')"></p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
  <BottomNav />
</template>
