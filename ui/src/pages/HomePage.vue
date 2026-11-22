<script setup>
import data from '../data/sedekah'
import AppHeader from '../components/AppHeader.vue'
import PillTabs from '../components/PillTabs.vue'
import BannerCarousel from '../components/BannerCarousel.vue'
import DonateForm from '../components/DonateForm.vue'
import DoaSection from '../components/DoaSection.vue'
import CampaignSection from '../components/CampaignSection.vue'
import AppFooter from '../components/AppFooter.vue'
import RegisterCta from '../components/RegisterCta.vue'
import HomePopups from '../components/HomePopups.vue'
import HomePopupMenu from '../components/HomePopupMenu.vue'
import BottomNav from '../components/BottomNav.vue'
import { donate, submitting } from '../donate'
import { t, isEn } from '../i18n'
import { computed } from 'vue'

const banners = data.banners
const feat = data.campaigns.find((c) => c.slug === data.featured?.slug)
// 20 kartu pilihan seperti beranda asli: 13 campaign feed terbaru lalu 7 kartu kurasi
const PILIHAN = ['peduli-banjir-aceh', 'bantu-pakpandi-bertahan', 'petani-ubi-cilembu', 'tpq-al-ihsan-bogor', 'tebar-10000-mushaf', 'dukung-mimpi-yaziz', 'rtq-lubuk-linggau', 'bantu-khalisa-sembuh', 'bantu-gilang-sembuh', '7-kilometer-untuk-air-bersih-hadirkan-sumur-bor-untuk-warga-desa-kedungbanteng', 'dapurpalestina', 'peduli-terdampak-karhutla', 'peduli-terdampak-gempa-ntt', 'dari-kamar-kos-menjadi-pusat-kebaikan-umat', 'gajian-makin-berkah-dengan-sedekah', 'mengalirkan-kebaikan-sedekah-atas-nama-orang-tua', 'pahala-berlipatt-dengan-sedekah-jumat', 'wakaf-masjid-5in1-rahmatan-lilalamin', 'wakaf-bisa-satu-niat-banyak-manfaat', 'peduli-terdampak-bencana']
const pilihan = PILIHAN.map((sl) => (sl === feat?.slug ? feat : data.campaigns.find((c) => c.slug === sl))).filter(Boolean)
const terbaru = pilihan.slice(0, 8)
// Kartu kurasi punya judul Inggris (headingEn) di sedekah.id /en; kartu feed tetap Indonesia
const HEADING_EN = {
  'dari-kamar-kos-menjadi-pusat-kebaikan-umat': 'More Than Just a Place to Pray',
  'gajian-makin-berkah-dengan-sedekah': 'Make Your Paycheck Even More Blessed Through Shadaqa',
  'mengalirkan-kebaikan-sedekah-atas-nama-orang-tua': 'Flowing Goodness: sedekah in Honor of Our Parents',
  'pahala-berlipatt-dengan-sedekah-jumat': 'Multiply Your Rewards with Friday sedekah',
  'wakaf-masjid-5in1-rahmatan-lilalamin': 'Complete the Mosque, Earn Rewards in Paradise',
  'wakaf-bisa-satu-niat-banyak-manfaat': 'One Good Deed Today',
  'peduli-terdampak-bencana': 'Care for Disaster Survivors',
}
const loc = (l) => computed(() => (isEn.value ? l.map((c) => (HEADING_EN[c.slug] ? { ...c, title: HEADING_EN[c.slug] } : c)) : l))
const pilihanL = loc(pilihan)
const terbaruL = loc(terbaru)
</script>

<template>
  <div class="frame">
    <div style="background: #f5f6f8; min-height: 100vh; overflow-x: hidden">
      <AppHeader />
      <PillTabs />
      <BannerCarousel :banners="banners" />
      <DonateForm :submitting="submitting" @submit="donate" />
      <DoaSection />
      <div class="pb-28">
        <CampaignSection :title="t('home.featuredCampaigns')" icon="target" :items="pilihanL" />
        <CampaignSection :title="t('home.latestCampaigns')" icon="clock" :items="terbaruL" more />
        <AppFooter />
      </div>
    </div>
  </div>
  <RegisterCta />
  <HomePopups />
  <HomePopupMenu />
  <BottomNav />
</template>
