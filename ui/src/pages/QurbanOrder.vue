<script setup>
import { rpTight } from '../utils/format'
import { ref, reactive, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import Icon from '../components/Icon.vue'
import BottomNav from '../components/BottomNav.vue'
import payment from '../data/payment.json'
import { packages, animalLabel, animalEmoji } from '../data/qurban'
import { auth } from '../auth'

// Real flow (when packages exist): POST /api/donations {type, qty, pekurban[]...} then POST /api/payment/create
const route = useRoute()
const router = useRouter()
const pkg = computed(() => packages.find((p) => p.id === route.params.id))
const MAX = 10
const qty = ref(1)
const names = reactive([''])
const f = reactive({ name: auth.user?.name || '', hide: false, email: '', doa: '' })
const method = ref('')
const err = ref('')
const rupiah = rpTight
const total = computed(() => (pkg.value ? pkg.value.price * qty.value : 0))
const mdef = computed(() => payment.find((m) => m.name === method.value))
const methodErr = computed(() => (mdef.value && total.value < mdef.value.minAmount ? `Minimum ${rupiah(mdef.value.minAmount)} untuk ${mdef.value.name}. Naikkan quantity atau pilih metode lain.` : ''))
const usable = computed(() => payment.filter((m) => total.value <= m.maxAmount))
function setQty(n) { qty.value = Math.min(MAX, Math.max(1, n)); while (names.length < qty.value) names.push(''); names.length = qty.value }
function pay() {
  err.value = ''
  if (!f.name.trim()) return (err.value = 'Nama donatur wajib diisi')
  if (names.some((n) => !n.trim())) return (err.value = 'Nama pekurban wajib diisi')
  if (!method.value) return (err.value = 'Pilih metode pembayaran')
  if (methodErr.value) return (err.value = methodErr.value)
  alert(`Pesanan qurban ${rupiah(total.value)} dicatat (demo, belum terhubung backend pembayaran).`)
}
</script>

<template>
  <div class="frame" style="background: #fff">
    <div class="qo">
      <div class="jd-top"><button class="doa-back" aria-label="Kembali" @click="router.push('/qurban')"><Icon name="back" /></button><span>Pesan Qurban</span></div>
      <div v-if="!pkg" class="d-empty" style="padding: 60px 16px">Paket tidak ditemukan.</div>
      <div v-else class="qo-in">
        <div class="qo-pk"><span class="em">{{ animalEmoji[pkg.animal] }}</span><div><b>{{ pkg.name }}</b><small>{{ animalLabel[pkg.animal] }} · {{ pkg.region }}</small></div></div>

        <div class="qo-row"><span>Harga</span><b>{{ rupiah(pkg.price) }}</b></div>
        <div class="qo-row"><span>Jumlah</span>
          <div class="qo-qty"><button @click="setQty(qty - 1)">−</button><b>{{ qty }}</b><button @click="setQty(qty + 1)">+</button></div>
        </div>
        <p class="help" style="text-align: right">Maksimal {{ MAX }} per transaksi</p>
        <div class="qo-row tot"><span>Total bayar</span><b>{{ rupiah(total) }}</b></div>

        <p class="sr-h">Nama Pekurban (Sahibul Qurban)</p>
        <p class="help" style="margin: -6px 0 8px">Nama yang akan dicatat sebagai pekurban (bisa berbeda dari nama donatur). Contoh: "Ahmad bin Yusuf", "Fatimah binti Abdullah".</p>
        <input v-for="(n, i) in names" :key="i" class="input" style="margin-bottom: 8px" v-model="names[i]" :placeholder="`Nama pekurban ke-${i + 1}`" />

        <p class="sr-h">Data Donatur</p>
        <input class="input" v-model="f.name" placeholder="Nama donatur *" style="margin-bottom: 8px" />
        <label class="check"><input type="checkbox" v-model="f.hide" /><span>Sembunyikan nama saya di daftar publik (Teman Sedekah)</span></label>
        <input class="input" type="email" v-model="f.email" placeholder="Email (opsional)" style="margin-top: 8px" />
        <textarea class="textarea" rows="2" v-model="f.doa" placeholder="Tulis doa (opsional)" style="margin-top: 8px"></textarea>

        <p class="sr-h">Metode Pembayaran</p>
        <select class="input" v-model="method" style="margin-top: 0"><option value="">Pilih Metode</option><option v-for="m in usable" :key="m.code" :value="m.name">{{ m.name }}</option></select>
        <p v-if="methodErr" class="ak-err">{{ methodErr }}</p>

        <div class="qo-terms">
          <b>Ketentuan Penyaluran</b>
          <ol>
            <li>Distribusi hewan qurban sepenuhnya dikelola oleh <b>lembaga penyelenggara</b>.</li>
            <li>Dalam kondisi darurat lembaga penyelenggara berhak untuk mengkonversi Hewan Qurban Kambing ke Sapi/Unta berjamaah dan sebaliknya dengan menyesuaikan berat hewan qurban di wilayah distribusi sesuai dengan harga beli.</li>
            <li>Laporan pelaksanaan dapat diakses secara online maksimal <b>H+14</b> setelah pendistribusian selesai.</li>
          </ol>
        </div>

        <p v-if="err" class="ak-err">{{ err }}</p>
        <button class="cta" style="margin-top: 14px" @click="pay">Bayar {{ rupiah(total) }}</button>
        <p class="help" style="text-align: center; margin-top: 8px">Dengan menekan tombol di atas, Anda menyatakan dana ini dari sumber halal.</p>
      </div>
    </div>
  </div>
  <BottomNav />
</template>
