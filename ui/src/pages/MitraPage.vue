<script setup>
import AppHeader from '../components/AppHeader.vue'
import BottomNav from '../components/BottomNav.vue'
import Icon from '../components/Icon.vue'
import MitraBadge from '../components/MitraBadge.vue'
import mitra from '../data/mitra.json'
import { lp } from '../i18n'
// Snapshot dari sedekah.id/mitra (tidak ada API JSON publik; halaman asli dirender server).
// Frappe: ganti dengan query Mitra (nama, slug, tipe, foto, jumlah campaign, total terkumpul).
</script>

<template>
  <div class="frame">
    <div style="background:#f5f6f8;min-height:100vh">
      <AppHeader />
      <div class="min-h-screen pb-28">
        <div class="max-w-[480px] mx-auto px-4">
          <div class="mt-4 rounded-2xl overflow-hidden" style="background:linear-gradient(135deg, #1a1a1a 0%, #2d2d2d 100%)">
            <div class="px-5 py-5">
              <h1 class="text-white text-lg font-bold">Mitra Sedekah</h1>
              <p class="text-white/70 text-sm mt-1">Personal, institusi &amp; komunitas yang menggalang kebaikan bersama donasi.</p>
            </div>
          </div>
          <div class="mt-4 grid grid-cols-2 gap-3">
            <router-link v-for="m in mitra" :key="m.slug" :to="lp('/' + m.slug)"
              class="rounded-2xl bg-white border border-gray-100 p-4 flex flex-col items-center text-center hover:shadow-md transition-shadow">
              <img :src="m.img" :alt="m.name" class="w-16 h-16 rounded-full object-cover" />
              <div class="mt-2.5 flex items-center gap-1 min-w-0">
                <span class="font-semibold text-gray-900 text-sm truncate">{{ m.name }}</span>
                <MitraBadge />
              </div>
              <span class="mt-0.5 text-[11px] font-medium text-gray-400 uppercase tracking-wide">{{ m.type }}</span>
              <div class="mt-3 pt-3 border-t border-gray-100 w-full flex items-center justify-between text-[11px] text-gray-500">
                <span class="inline-flex items-center gap-1"><Icon name="users" class="w-3 h-3" /> {{ m.count }} campaign</span>
              </div>
              <span class="mt-1 text-[13px] font-bold" style="color:#005399">{{ m.total }}</span>
            </router-link>
          </div>
        </div>
      </div>
    </div>
  </div>
  <BottomNav />
</template>
