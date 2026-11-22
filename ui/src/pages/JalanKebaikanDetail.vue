<script setup>
import { lp } from '../i18n'
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import Icon from '../components/Icon.vue'
import AppHeader from '../components/AppHeader.vue'
import BottomNav from '../components/BottomNav.vue'
import MissionRunner from '../components/MissionRunner.vue'
import missions from '../data/missions'
import { auth } from '../auth'

const route = useRoute()
const mission = computed(() => missions.find((x) => x.slug === route.params.id))
</script>

<template>
  <div class="frame" style="background: #f5f6f8">
    <AppHeader />
    <div class="min-h-screen pb-28">
      <div class="max-w-[480px] mx-auto px-4">
        <router-link :to="lp('/jalankebaikan')" class="inline-flex items-center gap-1 text-sm text-gray-500 hover:text-gray-700 mt-4"><Icon name="back" class="w-4 h-4" /> Kebaikan lain</router-link>
        <div class="mt-3 rounded-2xl bg-white border border-gray-100 p-5">
          <p v-if="!mission" class="text-center text-sm text-gray-500 py-8">Kebaikan tidak ditemukan.</p>
          <template v-else>
            <h1 class="text-center text-base font-bold text-gray-900">{{ mission.title }}</h1>
            <div v-if="!auth.user" class="text-center py-8">
              <div class="text-4xl mb-3">🔑</div>
              <p class="text-sm text-gray-600">Masuk dulu untuk mulai berbuat baik.</p>
              <router-link :to="lp('/akun?next=' + encodeURIComponent('/jalankebaikan/' + mission.slug))" class="inline-block mt-4 px-6 py-3 rounded-xl bg-[color:var(--lime)] text-[#1a1a1a] font-bold text-sm">Masuk / Daftar</router-link>
            </div>
            <MissionRunner v-else :mission="mission" />
          </template>
        </div>
      </div>
    </div>
  </div>
  <BottomNav />
</template>
