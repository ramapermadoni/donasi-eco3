<script setup>
const demoMode = import.meta.env.VITE_REAL_API === '0'
import { ref, reactive, computed, onMounted, onBeforeUnmount } from 'vue'
import { useRouter } from 'vue-router'
import Icon from '../components/Icon.vue'
import OtpInput from '../components/OtpInput.vue'
import { t, tr, lp, bcp } from '../i18n'
import { pad2 } from '../utils/format'
import { register, sendOtp, verifyOtp } from '../auth'

const router = useRouter()

const goals = computed(() => [0, 1, 2].map((i) => t('register.goal' + i)))
const sources = computed(() => [0, 1, 2, 3, 4].map((i) => t('register.source' + i)))
const months = computed(() => Array.from({ length: 12 }, (_, i) => new Date(2000, i, 1).toLocaleDateString(bcp(), { month: 'long' })))
const years = Array.from({ length: 80 }, (_, i) => new Date().getFullYear() - 10 - i)

const step = ref(1) // 1 goal · 2 source · 3 data · 4 otp
const goal = ref(-1) // index into goals
const source = ref(-1)
const f = reactive({ name: '', whatsapp: '', email: '', day: '', month: '', year: '', city: '', job: '' })
const errs = reactive({})
const apiErr = ref('')
const busy = ref(false)

/* city autocomplete — /wilayah.json is the list from sedekah.id/api/wilayah; swap for your Frappe endpoint */
const cities = ref([])
const cityLoading = ref(false)
const cityOpen = ref(false)
const cityQ = ref('')
const cityBox = ref(null)
const matches = computed(() => cities.value.filter((c) => cityQ.value.length >= 2 && (c.name.toLowerCase().includes(cityQ.value.toLowerCase()) || (c.province || '').toLowerCase().includes(cityQ.value.toLowerCase()))).slice(0, 30))
async function loadCities() {
  if (cities.value.length) return
  cityLoading.value = true
  try { cities.value = await (await fetch('/wilayah.json')).json() } catch { cities.value = [] } finally { cityLoading.value = false }
}
function pickCity(c) { f.city = c.name; cityQ.value = c.name; cityOpen.value = false; errs.city = '' }
const onDoc = (e) => { if (cityBox.value && !cityBox.value.contains(e.target)) cityOpen.value = false }
onMounted(() => document.addEventListener('mousedown', onDoc))
onBeforeUnmount(() => { document.removeEventListener('mousedown', onDoc); clearInterval(tick) })

const birthdate = computed(() => (f.day && f.month && f.year ? `${f.year}-${pad2(f.month)}-${pad2(f.day)}` : ''))
const normPhone = (v) => { const d = v.replace(/\D/g, ''); return d.startsWith('62') ? d : '62' + d.replace(/^0+/, '') }

/* hero copy per step */
const hero = computed(() => ({
  1: { h: [1, 2, 3, 4].map((i) => t('register.hero' + i)) },
  2: { t: t('register.benefit1Desc') },
  3: { t: t('register.benefit3Title'), s: t('register.benefit3Desc') },
  4: { t: t('register.benefit2Title'), s: t('register.benefit2Desc') },
}[step.value]))

const canNext = computed(() => (step.value === 1 ? goal.value >= 0 : step.value === 2 ? source.value >= 0 : true))

function back() { step.value === 1 ? router.push(lp('/akun')) : (step.value--, apiErr.value = '') }

async function submit() {
  Object.keys(errs).forEach((k) => delete errs[k])
  if (!f.name.trim()) errs.name = t('register.errName')
  if (!f.whatsapp.trim()) errs.whatsapp = t('register.errWhatsappRequired')
  else if (f.whatsapp.replace(/\D/g, '').length < 10) errs.whatsapp = t('register.errWhatsappInvalid')
  if (f.email.trim() && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(f.email)) errs.email = t('register.errEmailInvalid')
  if (!birthdate.value) errs.birthdate = t('register.errBirthdate')
  if (!f.city) errs.city = t('register.errCity')
  if (Object.keys(errs).length) return
  busy.value = true; apiErr.value = ''
  try {
    phone.value = await register({ name: f.name.trim(), phone: normPhone(f.whatsapp), email: f.email || null, birthdate: birthdate.value, city: f.city, job: f.job || null, goal: goals.value[goal.value], source: sources.value[source.value] })
    await sendOtp(phone.value, { allowNew: true, skip: true })
    step.value = 4; startTimer()
  } catch (e) { apiErr.value = e.message || t('register.errGeneric') } finally { busy.value = false }
}

/* otp */
const phone = ref('')
const code = ref('')
const otpErr = ref('')
const secs = ref(0)
let tick = null
function startTimer() { secs.value = 60; clearInterval(tick); tick = setInterval(() => { if (--secs.value <= 0) clearInterval(tick) }, 1000) }
async function verify() {
  if (code.value.length !== 6) { otpErr.value = t('register.errOtpLen'); return }
  busy.value = true; otpErr.value = ''
  try { await verifyOtp(phone.value, code.value); router.push(lp('/akun')) } catch (e) { otpErr.value = e.message } finally { busy.value = false }
}
async function resend() { if (secs.value > 0) return; await sendOtp(phone.value, { allowNew: true }); startTimer() }

function next() { step.value < 3 ? (step.value++, step.value === 3 && loadCities()) : step.value === 3 ? submit() : verify() }
</script>

<template>
  <div class="desktop-bg" aria-hidden="true"></div>
  <div class="frame rg">
    <!-- top bar -->
    <div class="rg-bar">
      <button class="rg-x" :aria-label="step === 1 ? t('akun.avatarClose') : t('register.back')" @click="back"><Icon :name="step === 1 ? 'x' : 'back'" /></button>
      <span class="rg-ttl">{{ t('register.topTitle') }}</span>
      <div class="rg-brand"><i>D</i><b>DT</b><b class="dim">Peduli</b></div>
    </div>

    <!-- hero -->
    <div class="rg-hero">
      <span class="star" style="top: 16px; right: 32px; font-size: 24px; opacity: .3">✦</span>
      <span class="star" style="top: 40px; left: 24px; font-size: 14px; opacity: .2">✦</span>
      <div class="rg-hero-in">
        <h1 v-if="step === 1"><template v-for="(l, n) in hero.h" :key="n"><span :class="n % 2 ? 'k' : 'g'">{{ l }}</span><br /></template></h1>
        <div v-else class="rg-copy"><h2>{{ hero.t }}</h2><p v-if="hero.s">{{ hero.s }}</p></div>
        <div class="rg-prog">
          <div class="r"><span class="ic"><Icon name="heart" /></span><div><b>{{ t('register.activeProgram') }}</b><small>{{ t('register.readyToHelp') }}</small></div></div>
          <div class="trk"><i></i></div>
          <p>{{ t('register.donationTarget') }}</p>
        </div>
      </div>
      <div class="rg-dots"><i v-for="n in 3" :key="n" :class="{ on: n === Math.min(step, 3) }"></i></div>
    </div>

    <!-- body -->
    <div class="rg-body">
      <template v-if="step === 1">
        <p class="rg-q">{{ t('register.goalQuestion') }}</p>
        <button v-for="(g, gi) in goals" :key="gi" class="rg-opt" :class="{ on: goal === gi }" @click="goal = gi"><i></i><span>{{ g }}</span></button>
      </template>

      <template v-else-if="step === 2">
        <p class="rg-q">{{ t('register.sourceQuestion') }}</p>
        <button v-for="(s, si) in sources" :key="si" class="rg-opt" :class="{ on: source === si }" @click="source = si"><i></i><span>{{ s }}</span></button>
      </template>

      <template v-else-if="step === 3">
        <p class="rg-q">{{ t('register.fillData') }}</p>
        <p class="help" style="margin: -8px 0 12px">{{ t('register.requiredNote') }}</p>
        <div class="fields">
          <div><label class="fl">{{ t('register.fullName') }} <span class="req">*</span></label><input class="input" v-model="f.name" :placeholder="t('register.fullNamePlaceholder')" /><p v-if="errs.name" class="ak-err">{{ errs.name }}</p></div>
          <div><label class="fl">{{ t('register.whatsapp') }} <span class="req">*</span></label><input class="input" type="tel" inputmode="numeric" v-model="f.whatsapp" :placeholder="t('register.whatsappPlaceholder')" /><p v-if="errs.whatsapp" class="ak-err">{{ errs.whatsapp }}</p></div>
          <div><label class="fl">Email <span class="opt">{{ t('register.emailOptional') }}</span></label><input class="input" type="email" v-model="f.email" :placeholder="t('register.emailPlaceholder')" /><p v-if="errs.email" class="ak-err">{{ errs.email }}</p></div>
          <div>
            <label class="fl">{{ t('register.birthdate') }} <span class="req">*</span></label>
            <div class="ak-dob">
              <select class="input" :aria-label="t('register.birthDayAria')" v-model="f.day"><option value="">{{ t('register.birthDay') }}</option><option v-for="d in 31" :key="d" :value="d">{{ d }}</option></select>
              <select class="input" :aria-label="t('register.birthMonthAria')" v-model="f.month"><option value="">{{ t('register.birthMonth') }}</option><option v-for="(m, i) in months" :key="m" :value="i + 1">{{ m }}</option></select>
              <select class="input" :aria-label="t('register.birthYearAria')" v-model="f.year"><option value="">{{ t('register.birthYear') }}</option><option v-for="y in years" :key="y" :value="y">{{ y }}</option></select>
            </div>
            <p v-if="errs.birthdate" class="ak-err">{{ errs.birthdate }}</p>
          </div>
          <div ref="cityBox" style="position: relative">
            <label class="fl">{{ t('register.city') }} <span class="req">*</span></label>
            <input class="input" v-model="cityQ" :placeholder="cityLoading ? t('register.cityLoading') : t('register.cityPlaceholder')" @focus="cityOpen = true; loadCities()" @input="f.city = ''; cityOpen = true" />
            <div v-if="cityOpen" class="rg-dd">
              <p v-if="cityQ.length < 2">{{ t('register.cityMinChars') }}</p>
              <p v-else-if="!matches.length">{{ t('register.cityNotFound') }}</p>
              <button v-for="c in matches" :key="c.name + c.province" @click="pickCity(c)">{{ c.name }}<small>{{ c.province }}</small></button>
            </div>
            <p v-if="errs.city" class="ak-err">{{ errs.city }}</p>
          </div>
          <div><label class="fl">{{ t('register.job') }} <span class="opt">{{ t('register.emailOptional') }}</span></label><input class="input" v-model="f.job" :placeholder="t('register.jobPlaceholder')" /></div>
        </div>
        <p v-if="apiErr" class="ak-err" style="margin-top: 10px">{{ apiErr }}</p>
      </template>

      <template v-else>
        <p class="rg-q">{{ t('register.enterOtp') }}</p>
        <p class="ak-sent" v-html="tr('register.otpSentTo', { phone }).replace('<br>', ' ')"></p>
        <OtpInput v-model="code" style="margin-top: 14px" @complete="verify" />
        <p class="help" style="text-align: center">{{ t('akun.cwVerifiedHint') }}<template v-if="demoMode"> · demo: isi 6 angka apa saja</template></p>
        <p v-if="otpErr" class="ak-err">{{ otpErr }}</p>
        <button class="ak-link" :disabled="secs > 0" @click="resend">{{ secs > 0 ? t('register.resendIn', { secs }) : t('register.resendOtp') }}</button>
      </template>
    </div>

    <!-- bottom bar -->
    <div class="rg-foot">
      <button class="back" @click="back"><Icon name="back" /> {{ t('register.back') }}</button>
      <button class="nx" :disabled="!canNext || busy" @click="next">
        {{ busy ? (step === 4 ? t('register.verifying') : t('register.processing')) : step === 3 ? t('register.registerNow') : step === 4 ? t('register.verifyEnter') : t('register.next') }}
        <Icon v-if="step < 3 && !busy" name="chevronRight" />
      </button>
    </div>
  </div>
</template>

<style scoped>
.rg-prog b { line-height: 1.5; }
.rg-prog small { display: block; line-height: 1.5; }
.rg-prog p { line-height: 1.5; }
.rg-prog .ic svg { width: 14px; height: 14px; }
</style>
