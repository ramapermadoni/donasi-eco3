// Daftar penyaluran dengan scroll tak terbatas + filter/urut, dipakai PenyaluranPage dan BeritaPage
// (keduanya memang daftar /api/penyaluran yang sama; hanya tampilan kartunya beda).
// Disalin dari sedekah.id: GET /api/penyaluran?limit=5&offset=&sort=&category=&location=&program=
// dan GET /api/penyaluran/meta (lokasi, program, kategori). Di Frappe ganti dua fetch ini dengan frappe.call.
// Murni logika (tanpa DOM): uji di docs/tools/feedlist-test.mjs lewat opsi `fetcher`.
import { ref, computed, watch, onMounted } from 'vue'
import { locale, apiHeaders } from '../i18n'

export const FEED_LIMIT = 5
export const FEED_SORTS = [['terbaru', 'sortNewest'], ['terlama', 'sortOldest'], ['a-z', 'sortAZ'], ['z-a', 'sortZA']]

export function useFeedList() {
  const items = ref([])
  const total = ref(0)
  const hasMore = ref(false)
  const loading = ref(true)
  const loadingMore = ref(false)
  const category = ref('Semua')
  const location = ref(null)
  const program = ref(null)
  const sortKey = ref('terbaru')
  const meta = ref({ locations: [], programs: [], categories: ['Semua'], categoryLabels: {} })
  const filterOpen = ref(false)
  const sortOpen = ref(false)
  let gen = 0

  const activeFilterCount = computed(() => (location.value ? 1 : 0) + (program.value ? 1 : 0) + (category.value !== 'Semua' ? 1 : 0))
  const barWidth = computed(() => ((meta.value.categories.indexOf(category.value) + 1) / Math.max(meta.value.categories.length, 1)) * 100)

  async function fetchPage(offset, replace, g) {
    const q = new URLSearchParams({ limit: String(FEED_LIMIT), offset: String(offset), sort: sortKey.value })
    if (category.value !== 'Semua') q.set('category', category.value)
    if (location.value) q.set('location', location.value)
    if (program.value) q.set('program', program.value)
    try {
      const r = await fetch('/api/penyaluran?' + q, { headers: apiHeaders() })
      const j = await r.json().catch(() => ({ items: [], total: 0, hasMore: false }))
      if (g !== gen) return
      const list = Array.isArray(j.items) ? j.items : []
      items.value = replace ? list : [...items.value, ...list]
      total.value = Number(j.total ?? 0)
      hasMore.value = !!j.hasMore
    } catch {
      if (g !== gen) return
      if (replace) items.value = []
      hasMore.value = false
    }
  }
  function reload() {
    const g = ++gen
    loading.value = true
    loadingMore.value = false // loadMore lama sudah basi (g !== gen); jangan biarkan tersangkut true
    fetchPage(0, true, g).finally(() => { if (g === gen) loading.value = false })
  }
  function loadMore() {
    if (loadingMore.value || loading.value || !hasMore.value) return
    const g = gen
    loadingMore.value = true
    fetchPage(items.value.length, false, g).finally(() => { if (g === gen) loadingMore.value = false })
  }
  function reset() { location.value = null; program.value = null; category.value = 'Semua' }

  watch([category, location, program, sortKey], reload)
  onMounted(async () => {
    reload()
    try {
      const m = await fetch('/api/penyaluran/meta?locale=' + locale.value).then((r) => (r.ok ? r.json() : null))
      if (m) meta.value = { locations: m.locations || [], programs: m.programs || [], categories: m.categories?.length ? m.categories : ['Semua'], categoryLabels: m.categoryLabels || {} }
    } catch { /* tetap default */ }
  })

  return { items, total, hasMore, loading, loadingMore, category, location, program, sortKey, meta, filterOpen, sortOpen, activeFilterCount, barWidth, reload, loadMore, reset }
}
