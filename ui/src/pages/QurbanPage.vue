<script setup>
import { pad2, rpTight } from '../utils/format'
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'
import AppHeader from '../components/AppHeader.vue'
import BottomNav from '../components/BottomNav.vue'
import Icon from '../components/Icon.vue'
import { packages, regions, eidDate, animalLabel, animalEmoji } from '../data/qurban'

// Replace with Frappe: GET qurban packages ?region=&animal=&sort= ; "Sedekah Daging" = free-amount programs
const tab = ref('qurban')
const region = ref('')
const animal = ref('')
const sort = ref('default')
const filterOpen = ref(false)
const now = ref(Date.now())
let t = null
onMounted(() => (t = setInterval(() => (now.value = Date.now()), 1000)))
onBeforeUnmount(() => clearInterval(t))

const diff = computed(() => Math.max(0, eidDate - now.value))
const cd = computed(() => ({ d: Math.floor(diff.value / 864e5), h: Math.floor(diff.value / 36e5) % 24, m: Math.floor(diff.value / 6e4) % 60, s: Math.floor(diff.value / 1e3) % 60 }))
const pad = pad2
const rupiah = rpTight
const list = computed(() => {
  let l = packages.filter((p) => (!region.value || p.region === region.value) && (!animal.value || (animal.value === 'goatsheep' ? ['goat', 'sheep'].includes(p.animal) : p.animal === animal.value)))
  if (sort.value === 'cheap') l = [...l].sort((a, b) => a.price - b.price)
  if (sort.value === 'expensive') l = [...l].sort((a, b) => b.price - a.price)
  return l
})
const flash = computed(() => packages.find((p) => p.limited))
const reset = () => { region.value = ''; animal.value = ''; sort.value = 'default' }
</script>

<template>
  <div class="frame">
    <AppHeader />
    <main class="qb">
      <div class="qb-note">Data paket di halaman ini adalah <b>contoh</b>; paket asli sedekah.id baru dibuka menjelang Idul Adha.</div>

      <div class="qb-tabs">
        <button :class="{ on: tab === 'qurban' }" @click="tab = 'qurban'">Qurban</button>
        <button :class="{ on: tab === 'daging' }" @click="tab = 'daging'">Sedekah Daging</button>
      </div>

      <div class="qb-eid">
        <div><small>Idul Adha</small><b>{{ cd.d }} hari lagi</b></div>
        <div class="cd"><span><i>{{ cd.d }}</i>H</span><span><i>{{ pad(cd.h) }}</i>J</span><span><i>{{ pad(cd.m) }}</i>M</span><span><i>{{ pad(cd.s) }}</i>D</span></div>
      </div>

      <template v-if="tab === 'qurban'">
        <router-link v-if="flash" :to="'/qurban/pesan/' + flash.id" class="qb-flash">
          <span class="ic">⚡</span>
          <div><b>Flash Sale</b><small>Penawaran spesial waktu terbatas — ambil sebelum kuota habis.</small></div>
          <Icon name="chevronRight" />
        </router-link>

        <div class="qb-head">
          <div><h2>Pilih Paket Qurban</h2><p>Tunaikan qurban dengan paket yang sesuai. Daging disalurkan ke yang berhak menerima.</p></div>
        </div>
        <div class="qb-bar"><span>{{ list.length }} paket</span><button :class="{ on: filterOpen }" @click="filterOpen = !filterOpen"><Icon name="route" /> Filter</button></div>
        <div v-if="filterOpen" class="qb-filter">
          <label>Wilayah<select class="input" v-model="region"><option value="">Semua wilayah</option><option v-for="r in regions" :key="r" :value="r">{{ r }}</option></select></label>
          <label>Hewan<select class="input" v-model="animal"><option value="">Semua hewan</option><option value="goatsheep">Kambing/Domba</option><option value="cow">Sapi</option><option value="camel">Unta</option></select></label>
          <label>Urutan<select class="input" v-model="sort"><option value="default">Rekomendasi</option><option value="cheap">Termurah</option><option value="expensive">Termahal</option></select></label>
          <button class="more" @click="reset">Reset filter</button>
        </div>

        <div class="qb-grid">
          <router-link v-for="p in list" :key="p.id" :to="'/qurban/pesan/' + p.id" class="qb-card">
            <div class="im"><span class="em">{{ animalEmoji[p.animal] }}</span><i v-if="p.limited">Terbatas</i></div>
            <div class="bd">
              <p class="t">{{ p.name }}</p>
              <p class="s">{{ animalLabel[p.animal] }} · {{ p.mode === 'whole' ? '1 Ekor' : 'Patungan' }} · {{ p.region }}</p>
              <p class="pr">{{ rupiah(p.price) }}<small>{{ p.mode === 'whole' ? ' / Per Ekor' : ' / bagian' }}</small></p>
              <span class="btn">Pilih</span>
            </div>
          </router-link>
        </div>
        <p v-if="!list.length" class="d-empty">Tidak ada paket untuk filter ini.</p>
      </template>

      <template v-else>
        <div class="qb-head"><div><h2>Sedekah Daging</h2><p>Berbagi daging untuk saudara-saudara yang membutuhkan. Donasi bebas nominal.</p></div></div>
        <div class="qb-grid"><router-link to="/" class="qb-card"><div class="im"><span class="em">🥩</span></div><div class="bd"><p class="t">Sedekah Daging Qurban</p><p class="s">Donasi bebas nominal</p><span class="btn">Donasi</span></div></router-link></div>
      </template>

      <div class="qb-about"><b>Tentang Qurban di donasi</b><p>Hewan qurban disalurkan langsung ke daerah yang membutuhkan oleh tim kami. Laporan pelaksanaan dikirim ke donatur via WhatsApp setelah 10 Dzulhijjah.</p></div>
    </main>
  </div>
  <BottomNav />
</template>
