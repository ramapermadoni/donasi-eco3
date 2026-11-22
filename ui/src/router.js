import { createRouter, createWebHistory } from 'vue-router'
import { setLocaleFromPath, pathFor } from './i18n'
import HomePage from './pages/HomePage.vue'
import JalanKebaikan from './pages/JalanKebaikan.vue'
import AkunPage from './pages/AkunPage.vue'
import RegisterPage from './pages/RegisterPage.vue'
import PenyaluranPage from './pages/PenyaluranPage.vue'
import LaporanPage from './pages/LaporanPage.vue'
import TemanPage from './pages/TemanPage.vue'
import DoaPage from './pages/DoaPage.vue'
import VideoPage from './pages/VideoPage.vue'
import PenyaluranDetail from './pages/PenyaluranDetail.vue'
import BeritaPage from './pages/BeritaPage.vue'
import ArtikelDetail from './pages/ArtikelDetail.vue'
import JalanKebaikanDetail from './pages/JalanKebaikanDetail.vue'
import ShadaqaRutin from './pages/ShadaqaRutin.vue'
import ShadaqaRutinSetup from './pages/ShadaqaRutinSetup.vue'
import ShadaqaRutinBayar from './pages/ShadaqaRutinBayar.vue'
import JejakKebaikan from './pages/JejakKebaikan.vue'
import CampaignsPage from './pages/CampaignsPage.vue'
import LegalPage from './pages/LegalPage.vue'
import QurbanPage from './pages/QurbanPage.vue'
import QurbanOrder from './pages/QurbanOrder.vue'
import DonasiPage from './pages/DonasiPage.vue'
import CampaignDetail from './pages/CampaignDetail.vue'
import MitraPage from './pages/MitraPage.vue'
import ZakatPage from './pages/ZakatPage.vue'
import WakafPage from './pages/WakafPage.vue'
import KalkulatorZakat from './pages/KalkulatorZakat.vue'
import MitraDetail from './pages/MitraDetail.vue'

const base = [
    { path: '/', component: HomePage },
    { path: '/jalankebaikan', component: JalanKebaikan },
    { path: '/akun', component: AkunPage },
    { path: '/auth/register', component: RegisterPage },
    { path: '/penyaluran', component: PenyaluranPage },
    { path: '/penyaluran/:slug', component: PenyaluranDetail },
    { path: '/berita', component: BeritaPage },
    { path: '/artikel/:slug', component: ArtikelDetail },
    { path: '/laporan', component: LaporanPage },
    { path: '/teman', component: TemanPage },
    { path: '/doa', component: DoaPage },
    { path: '/video', component: VideoPage },
    { path: '/jalankebaikan/:id', component: JalanKebaikanDetail },
    { path: '/shadaqa-rutin', component: ShadaqaRutin },
    { path: '/shadaqa-rutin/setup', component: ShadaqaRutinSetup },
    { path: '/shadaqa-rutin/bayar', component: ShadaqaRutinBayar },
    { path: '/jejak-kebaikan', component: JejakKebaikan },
    { path: '/public/campaigns', component: CampaignsPage },
    { path: '/syarat-ketentuan', component: LegalPage, props: { page: 'syarat-ketentuan' } },
    { path: '/kebijakan-privasi', component: LegalPage, props: { page: 'kebijakan-privasi' } },
    { path: '/hapus-akun', component: LegalPage, props: { page: 'hapus-akun' } },
    { path: '/qurban', component: QurbanPage },
    { path: '/qurban/pesan/:id', component: QurbanOrder },
    { path: '/donasi/:id', component: DonasiPage },
    { path: '/campaigns/:slug', component: CampaignDetail },
    { path: '/mitra', component: MitraPage },
    { path: '/zakat', component: ZakatPage },
    { path: '/wakaf', component: WakafPage },
    { path: '/kalkulatorzakat', component: KalkulatorZakat },
    // Harus paling akhir: slug mitra berada di root (/angga-nugroho), seperti situs asli.
    { path: '/:slug', component: MitraDetail },
]

// Setiap rute juga tersedia di /en (aslinya /en/donasi/* keluar dari prefiks -> redirect ke '/'). Slug mitra tetap paling akhir.
const en = base.filter((r) => !r.path.startsWith('/donasi/')).map((r) => ({ ...r, path: pathFor(r.path, 'en') }))
const routes = [...base.slice(0, -1), { path: '/en/donasi/:id', redirect: '/' }, ...en.slice(0, -1), en.at(-1), base.at(-1)]

const router = createRouter({ history: createWebHistory(), routes, scrollBehavior: () => ({ top: 0 }) })
router.beforeEach((to) => { setLocaleFromPath(to.path) })
export default router
