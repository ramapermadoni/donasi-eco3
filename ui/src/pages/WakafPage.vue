<script setup>
import { ref, onMounted } from 'vue'
import { lp } from '../i18n'
import ZakatAmount from '../components/ZakatAmount.vue'
import ZakatPayForm from '../components/ZakatPayForm.vue'

const amount = ref(0)
onMounted(() => {
  document.title = 'Wakaf Online — Wakaf Umum Produktif | sedekah.id | donasi'
  let m = document.querySelector('meta[name="description"]')
  if (!m) { m = document.createElement('meta'); m.name = 'description'; document.head.appendChild(m) }
  m.content = 'Tunaikan wakaf umum secara online. Dikelola dan disalurkan DT Peduli (LAZNAS resmi) untuk program wakaf produktif yang manfaatnya terus mengalir.'
})
</script>

<template>
  <div class="frame" style="background: #f6f7f2">
    <div class="min-h-screen bg-[#f6f7f2]"><div class="max-w-lg mx-auto px-4 pt-6 pb-16">
      <div class="flex items-center gap-3 mb-1">
        <a class="w-9 h-9 rounded-full bg-white border border-gray-200 flex items-center justify-center text-gray-500" aria-label="Kembali" :href="lp('/')" @click.prevent="$router.push(lp('/'))">←</a>
        <h1 class="text-xl font-extrabold text-gray-900">Tunaikan Wakaf</h1>
      </div>
      <p class="text-sm text-gray-500 leading-relaxed mb-5">Wakaf adalah investasi akhirat terbaik. Harta yang Anda wakafkan akan terus menghasilkan pahala jariyah, mengalir tanpa henti meskipun Anda telah tiada.</p>
      <div class="space-y-4">
        <ZakatAmount v-model="amount" label="Nominal wakaf" />
        <ZakatPayForm v-if="amount > 0" campaign-id="wakafcamp-umum-000000001" campaign-title="Wakaf Umum" :amount="amount" cta-label="Wakaf Sekarang" footer-note="Wakaf dikelola & disalurkan oleh DT Peduli (LAZNAS resmi)." />
      </div>
      <p class="mt-8 text-center text-[11px] text-gray-400 leading-relaxed">Wakaf disalurkan untuk program produktif oleh DT Peduli (LAZNAS resmi SK Kemenag).</p>
    </div></div>
  </div>
</template>
