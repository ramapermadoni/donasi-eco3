<script setup>
import { ref, computed, onMounted } from 'vue'
import { lp } from '../i18n'
import ZakatAmount from '../components/ZakatAmount.vue'
import ZakatPayForm from '../components/ZakatPayForm.vue'

const TIPE = [
  { slug: 'zakat-penghasilan', id: 'zakatcamp-penghasilan-01', title: 'Zakat Penghasilan', label: 'Penghasilan', emoji: '💼', desc: 'Gaji & honor' },
  { slug: 'zakat-maal', id: 'zakatcamp-maal-000000001', title: 'Zakat Maal', label: 'Maal', emoji: '💰', desc: 'Harta simpanan' },
  { slug: 'zakat-emas', id: 'zakatcamp-emas-000000001', title: 'Zakat Emas & Perak', label: 'Emas & Perak', emoji: '🪙', desc: 'Logam mulia' },
  { slug: 'zakat-investasi', id: 'zakatcamp-investasi-0001', title: 'Zakat Investasi', label: 'Investasi', emoji: '📈', desc: 'Hasil investasi' },
  { slug: 'zakat-perniagaan', id: 'zakatcamp-perniagaan-001', title: 'Zakat Perniagaan', label: 'Perniagaan', emoji: '🏪', desc: 'Usaha & dagang' },
]
const type = ref(TIPE[0].slug)
const amount = ref(0)
const camp = computed(() => TIPE.find((x) => x.slug === type.value))
onMounted(() => {
  document.title = 'Tunaikan Zakat Online — Penghasilan, Maal, Emas, Perniagaan | sedekah.id | donasi'
  let m = document.querySelector('meta[name="description"]')
  if (!m) { m = document.createElement('meta'); m.name = 'description'; document.head.appendChild(m) }
  m.content = 'Bayar zakat penghasilan, maal, emas & perak, investasi, dan perniagaan secara online. Dikelola dan disalurkan DT Peduli (LAZNAS resmi).'
})
</script>

<template>
  <div class="frame" style="background: #f6f7f2">
    <div class="min-h-screen bg-[#f6f7f2]"><div class="max-w-lg mx-auto px-4 pt-6 pb-16">
      <div class="flex items-center gap-3 mb-1">
        <a class="w-9 h-9 rounded-full bg-white border border-gray-200 flex items-center justify-center text-gray-500" aria-label="Kembali" :href="lp('/')" @click.prevent="$router.push(lp('/'))">←</a>
        <h1 class="text-xl font-extrabold text-gray-900">Tunaikan Zakat</h1>
      </div>
      <p class="text-sm text-gray-500 ml-12 mb-5">Pilih jenis zakat, isi nominal, langsung tunaikan. Dikelola DT Peduli (LAZNAS).</p>
      <div class="space-y-4">
        <div>
          <p class="text-xs font-semibold text-gray-700 mb-2">Pilih jenis zakat</p>
          <div class="grid grid-cols-3 gap-2.5">
            <button v-for="x in TIPE" :key="x.slug" type="button" class="rounded-2xl p-3 flex flex-col items-center text-center transition-all"
              :class="type === x.slug ? 'bg-white border-2 border-[var(--lime)] shadow-md -translate-y-0.5' : 'bg-white border border-gray-200'" @click="type = x.slug">
              <span class="text-2xl leading-none" aria-hidden="true">{{ x.emoji }}</span>
              <span class="mt-1.5 text-[12px] font-bold leading-tight" :class="type === x.slug ? 'text-gray-900' : 'text-gray-600'">{{ x.label }}</span>
              <span class="mt-0.5 text-[10px] text-gray-400 leading-tight">{{ x.desc }}</span>
            </button>
          </div>
        </div>
        <ZakatAmount v-model="amount" label="Nominal zakat">
          <a class="mt-3 flex items-center gap-2 text-[12px] font-semibold text-[color:var(--lime-text)]" :href="lp('/kalkulatorzakat')" @click.prevent="$router.push(lp('/kalkulatorzakat'))">
            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-calculator w-3.5 h-3.5"><rect width="16" height="20" x="4" y="2" rx="2"/><line x1="8" x2="16" y1="6" y2="6"/><line x1="16" x2="16" y1="14" y2="18"/><path d="M16 10h.01"/><path d="M12 10h.01"/><path d="M8 10h.01"/><path d="M12 14h.01"/><path d="M8 14h.01"/><path d="M12 18h.01"/><path d="M8 18h.01"/></svg>Belum tahu nominalnya? Hitung di Kalkulator Zakat →
          </a>
        </ZakatAmount>
        <ZakatPayForm v-if="amount > 0" :key="camp.id" :campaign-id="camp.id" :campaign-title="camp.title" :amount="amount" cta-label="Zakat Sekarang" />
      </div>
      <p class="mt-8 text-center text-[11px] text-gray-400 leading-relaxed">Zakat disalurkan sesuai asnaf oleh DT Peduli (LAZNAS resmi SK Kemenag).</p>
    </div></div>
  </div>
</template>
