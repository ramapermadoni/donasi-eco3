#!/usr/bin/env bash
# Terapkan kunci Midtrans dari .env ke site_config Frappe (kunci tidak dicetak). Jalankan dari root repo.
#   tools/terapkan_midtrans.sh            # pasang
#   tools/terapkan_midtrans.sh --matikan  # kembali ke simulator
set -euo pipefail
cd "$(dirname "$0")/.."
getv() { grep -E "^$1=" .env | head -1 | cut -d= -f2-; }
SITE="${SITE:-$(getv SITE_NAME)}"; SITE="${SITE:-donasi.localhost}"
bench() { docker compose exec -T backend bench --site "$SITE" "$@"; }

if [[ "${1:-}" == "--matikan" ]]; then
  bench set-config midtrans_enabled 0 >/dev/null; docker compose restart backend >/dev/null
  echo "Midtrans dimatikan di $SITE (kembali ke simulator)."; exit 0
fi

SK="$(getv MIDTRANS_SERVER_KEY)"; CK="$(getv MIDTRANS_CLIENT_KEY)"; PROD="$(getv MIDTRANS_IS_PRODUCTION)"; PROD="${PROD:-0}"
[[ -n "$SK" && -n "$CK" ]] || { echo "Isi MIDTRANS_SERVER_KEY dan MIDTRANS_CLIENT_KEY di .env dulu."; exit 1; }
if [[ "$PROD" != "1" ]]; then
  [[ "$SK" == SB-Mid-server-* ]] || { echo "Server key bukan sandbox (harus diawali SB-Mid-server-). Dibatalkan."; exit 1; }
  [[ "$CK" == SB-Mid-client-* ]] || { echo "Client key bukan sandbox (harus diawali SB-Mid-client-). Dibatalkan."; exit 1; }
fi

# Uji kunci: Midtrans menjawab {"status_code":"404"} (HTTP 200) bila kunci diterima dan order tidak ada; {"error":"Unauthorized"} bila salah.
URL="https://api.sandbox.midtrans.com"; [[ "$PROD" == "1" ]] && URL="https://api.midtrans.com"
RESP=$(printf 'user = "%s:"\n' "$SK" | curl -s -K - "$URL/v2/cek-kunci-donasi/status" || true)
[[ "$RESP" == *'"status_code":"404"'* ]] || { echo "Midtrans menolak kunci / tidak terjangkau (${RESP:0:60}). Tidak diterapkan."; exit 1; }

bench set-config midtrans_server_key "$SK" >/dev/null
bench set-config midtrans_client_key "$CK" >/dev/null
bench set-config midtrans_production "$([[ "$PROD" == "1" ]] && echo 1 || echo 0)" >/dev/null
bench set-config midtrans_enabled 1 >/dev/null
docker compose restart backend >/dev/null
echo "Midtrans aktif di $SITE (${SK:0:14}…, $([[ "$PROD" == "1" ]] && echo PRODUCTION || echo sandbox)). Backend dimulai ulang."
