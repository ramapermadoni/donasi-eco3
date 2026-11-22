// POST JSON; header ekstra (mis. X-Locale) dan keepalive diteruskan per pemanggil.
export async function postJson(url, body, { headers = {}, keepalive } = {}) {
  const r = await fetch(url, { method: 'POST', headers: { 'Content-Type': 'application/json', ...headers }, body: JSON.stringify(body), ...(keepalive === undefined ? {} : { keepalive }) })
  return { r, j: await r.json().catch(() => ({})) }
}
