<script setup>
// Kartu "Lengkapi Nomor WhatsApp" di /akun (tampil bila akun belum punya nomor, mis. masuk lewat Google).
// Disalin dari chunk /akun asli: POST /api/donor/phone/request-otp {phone:'+62…'} -> {ok, phone, retryAfter?}; POST /api/donor/phone/verify-otp {phone, code} -> {ok}; sukses = reload.
// BELUM terverifikasi terhadap asli: akun uji punya nomor, jadi kartu ini tidak pernah tampil di sana.
import { ref, watch, onBeforeUnmount } from 'vue'
import Icon from './Icon.vue'
import { t, tr } from '../i18n'

const step = ref('input')
const num = ref('')
const phone = ref('')
const code = ref('')
const busy = ref(false)
const err = ref('')
const wait = ref(0)
let timer = null
watch(wait, (n) => { clearTimeout(timer); if (n > 0) timer = setTimeout(() => wait.value--, 1000) })
onBeforeUnmount(() => clearTimeout(timer))

async function post(url, body) {
  const r = await fetch(url, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body) })
  return [r, await r.json()]
}
async function sendOtp() {
  err.value = ''
  const d = num.value.replace(/\D/g, '')
  if (d.length < 9) { err.value = t('akun.errPhoneInvalid'); return }
  busy.value = true
  try {
    const [r, a] = await post('/api/donor/phone/request-otp', { phone: `+62${d}` })
    if (!r.ok || !a.ok) { err.value = a.error ?? t('akun.errSendCode'); if (a.retryAfter) wait.value = a.retryAfter; return }
    phone.value = a.phone ?? `62${d}`; step.value = 'otp'; wait.value = 60
  } catch { err.value = t('akun.errGeneric') } finally { busy.value = false }
}
async function verify() {
  err.value = ''
  if (code.value.length !== 6) { err.value = t('akun.cwErrOtpLen'); return }
  busy.value = true
  try {
    const [r, a] = await post('/api/donor/phone/verify-otp', { phone: phone.value, code: code.value })
    if (!r.ok || !a.ok) { err.value = a.error ?? t('akun.errCodeWrong'); return }
    window.location.reload()
  } catch { err.value = t('akun.errGeneric') } finally { busy.value = false }
}
const bold = { b: (i) => '<span style="font-weight: 700; color: #1a1a1a">' + i + '</span>' }
</script>

<template>
  <div class="rounded-2xl overflow-hidden" style="background: white; box-shadow: 0 2px 16px rgba(0, 83, 153, 0.2); border: 1px solid #c7dcf0">
    <div class="flex items-center gap-3 px-5 py-4" style="background: linear-gradient(135deg, #f0f6fc, #ffffff)">
      <div class="w-9 h-9 rounded-xl flex items-center justify-center flex-shrink-0" style="background: linear-gradient(135deg, var(--lime), var(--lime-dark))"><Icon name="message" class="w-4 h-4 text-[#fff]" /></div>
      <div>
        <p style="font-size: 14px; font-weight: 800; color: #1a1a1a">{{ t('akun.cwTitle') }}</p>
        <p style="font-size: 11px; color: #6b7280; margin-top: 1px">{{ t('akun.cwSubtitle') }}</p>
      </div>
    </div>
    <div class="px-5 pb-5 pt-3">
      <template v-if="step === 'input'">
        <label style="font-size: 11px; color: #9ca3af; font-weight: 500">{{ t('akun.whatsappNumber') }}</label>
        <div class="flex mt-1 rounded-xl border border-gray-200 overflow-hidden focus-within:border-[color:var(--lime)] transition-colors">
          <span class="px-3 py-2.5 bg-gray-100 text-sm font-semibold text-gray-600 border-r border-gray-200 flex-shrink-0">+62</span>
          <input type="tel" :value="num" :placeholder="t('akun.cwPlaceholder')" class="flex-1 px-3 py-2.5 outline-none text-sm bg-gray-50 min-w-0" style="color: #111" @input="num = $event.target.value.replace(/\D/g, ''); err = ''" />
        </div>
        <p v-if="err" class="mt-2 text-xs text-red-500">{{ err }}</p>
        <button :disabled="busy" class="w-full mt-3 py-3 rounded-xl font-bold text-[#fff] flex items-center justify-center gap-2 disabled:opacity-60 active:scale-[0.98] transition-transform" style="background: linear-gradient(135deg, var(--lime) 0%, var(--lime-dark) 100%); font-size: 14px" @click="sendOtp"><Icon v-if="busy" name="loader" class="w-4 h-4 animate-spin" /><template v-else>{{ t('akun.cwSendOtp') }}</template></button>
        <p class="mt-2 flex items-center justify-center gap-1" style="font-size: 10px; color: #9ca3af"><Icon name="shieldCheck" class="w-3 h-3" /> {{ t('akun.cwVerifiedHint') }}</p>
      </template>
      <template v-else>
        <button class="flex items-center gap-1 text-xs font-semibold mb-2" style="color: var(--lime-text)" @click="step = 'input'; code = ''; err = ''"><Icon name="chevronLeft" class="w-3 h-3" /> {{ t('akun.changeNumber') }}</button>
        <p style="font-size: 12px; color: #6b7280; line-height: 1.5" v-html="tr('akun.cwCodeSentTo', { phone }, bold)"></p>
        <input type="text" inputmode="numeric" maxlength="6" :value="code" placeholder="••••••" autofocus class="w-full mt-2.5 py-3 rounded-xl border-2 text-center outline-none" :style="{ fontSize: '22px', fontWeight: 700, letterSpacing: '0.35em', color: '#1a1a1a', borderColor: err ? '#e53e3e' : '#d1d5db' }" @input="code = $event.target.value.replace(/\D/g, '').slice(0, 6); $event.target.value = code; err = ''" />
        <p v-if="err" class="mt-2 text-xs text-red-500">{{ err }}</p>
        <button :disabled="busy || code.length !== 6" class="w-full mt-3 py-3 rounded-xl font-bold text-[#fff] flex items-center justify-center gap-2 disabled:opacity-60 active:scale-[0.98] transition-transform" style="background: linear-gradient(135deg, var(--lime) 0%, var(--lime-dark) 100%); font-size: 14px" @click="verify"><Icon v-if="busy" name="loader" class="w-4 h-4 animate-spin" /><template v-else>{{ t('akun.cwVerifySave') }}</template></button>
        <button :disabled="wait > 0 || busy" class="w-full mt-2 text-xs font-semibold disabled:opacity-50" style="color: var(--lime-text)" @click="wait <= 0 && !busy && sendOtp()">{{ wait > 0 ? t('akun.cwResendIn', { secs: wait }) : t('akun.resendCode') }}</button>
      </template>
    </div>
  </div>
</template>
