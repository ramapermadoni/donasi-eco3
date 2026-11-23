"""Adapter gateway pembayaran. Bawaan: SIMULATOR. Midtrans (Core API + Snap) aktif bila site_config midtrans_enabled=1 dan midtrans_server_key terisi.
Kode Midtrans ditulis dari dokumentasi dan diuji dengan respons tiruan; BELUM dicoba ke sandbox nyata (tunggu kunci).

Aturan: kunci server hanya di site_config (midtrans_server_key); klien hanya clientKey publik.
"""
import hashlib
import secrets

import frappe
from frappe import _


def server_key():
	return frappe.local.conf.get("midtrans_server_key")


def signature(order_id, status_code, gross_amount, key):
	return hashlib.sha512(f"{order_id}{status_code}{gross_amount}{key}".encode()).hexdigest()


SANDBOX = {"core": "https://api.sandbox.midtrans.com", "snap": "https://app.sandbox.midtrans.com"}
PRODUCTION = {"core": "https://api.midtrans.com", "snap": "https://app.midtrans.com"}
TIMEOUT = 15
EXPIRY_MIN = 24 * 60  # = Donation.expired_at (24 jam)
CORE_BANK = {"bni_va": "bni", "bri_va": "bri", "permata_va": "permata"}  # bank_transfer Core API
SNAP_ONLY = {"gopay": ["gopay"], "shopeepay": ["shopeepay"], "bsi_va": None, "other_va": None}  # None = semua metode Snap
STATUS_MAP = {"settlement": "paid", "capture": "paid", "expire": "expired", "cancel": "failed", "deny": "failed", "failure": "failed"}


class GatewayError(Exception):
	pass


def enabled():
	return bool(frappe.local.conf.get("midtrans_enabled") and server_key())


def _urls():
	return PRODUCTION if frappe.local.conf.get("midtrans_production") else SANDBOX


def _call(method, url, body=None):
	import requests

	r = requests.request(method, url, json=body, auth=(server_key(), ""), headers={"Accept": "application/json"}, timeout=TIMEOUT)
	try:
		j = r.json()
	except ValueError:
		raise GatewayError(f"respons bukan JSON (HTTP {r.status_code})")
	if r.status_code >= 500 or str(j.get("status_code", r.status_code)) not in ("200", "201", "407"):
		raise GatewayError(f"Midtrans {j.get('status_code', r.status_code)}: {str(j.get('status_message', ''))[:120]}")
	return j


def _customer(donor):
	d = donor or {}
	return {k: v for k, v in {"first_name": (d.get("name") or "")[:50] or None, "phone": d.get("phone")}.items() if v}


def charge(order_id, method, amount, donor=None):
	"""Kembalikan field Permintaan Pembayaran. Midtrans bila aktif, selain itu simulator."""
	if enabled():
		return _charge_midtrans(order_id, method, int(amount), donor)
	typ = method.method_type
	out = {"gateway": "simulator", "simulated": 1, "payment_type": typ}
	if typ == "qris":
		qr = f"00020101SIMULATOR{order_id}"
		out.update(qr_string=qr, qr_code_url=f"/api/method/donasionline.api.payment.qr_png?id={order_id.rsplit('-', 1)[0]}")
	elif typ == "virtual_account":
		out.update(va_bank=method.code.replace("_va", ""), va_number="9999" + "".join(secrets.choice("0123456789") for _ in range(12)))
	else:
		out.update(redirect_url=f"/simulator/{order_id}")
	return out


def _charge_midtrans(order_id, method, amount, donor):
	u = _urls()
	tx = {"order_id": order_id, "gross_amount": amount}
	base = {"transaction_details": tx, "customer_details": _customer(donor)}
	# samakan kedaluwarsa Midtrans dengan Donation (24 jam); bawaan Midtrans untuk QRIS hanya 15 menit
	core_exp = {"custom_expiry": {"expiry_duration": EXPIRY_MIN, "unit": "minute"}}
	snap_exp = {"expiry": {"duration": EXPIRY_MIN, "unit": "minutes"}}
	out = {"gateway": "midtrans", "simulated": 0, "payment_type": method.method_type}
	try:
		if method.code == "qris":
			j = _call("POST", u["core"] + "/v2/charge", {**base, **core_exp, "payment_type": "qris", "qris": {"acquirer": "gopay"}})
			url = next((a.get("url") for a in j.get("actions", []) if a.get("name") == "generate-qr-code"), None)
			out.update(qr_string=j.get("qr_string"), qr_code_url=url)
		elif method.code in CORE_BANK:
			bank = CORE_BANK[method.code]
			j = _call("POST", u["core"] + "/v2/charge", {**base, **core_exp, "payment_type": "bank_transfer", "bank_transfer": {"bank": bank}})
			va = (j.get("va_numbers") or [{}])[0].get("va_number") or j.get("permata_va_number")
			out.update(va_bank=bank, va_number=va)
		else:
			snap = {**base, **snap_exp}
			if SNAP_ONLY.get(method.code):
				snap["enabled_payments"] = SNAP_ONLY[method.code]
			j = _call("POST", u["snap"] + "/snap/v1/transactions", snap)
			out.update(snap_token=j.get("token"), redirect_url=j.get("redirect_url"))
	except (GatewayError, OSError) as e:
		frappe.logger("donasionline").error("Midtrans charge gagal (%s): %s", method.code, type(e).__name__ + ": " + str(e)[:150])
		frappe.throw(_("Pembayaran belum bisa dibuat. Coba lagi atau pilih metode lain."), frappe.ValidationError)
	out["raw_response"] = frappe.as_json({k: v for k, v in j.items() if k not in ("signature_key",)})[:4000]
	if not (out.get("va_number") or out.get("qr_string") or out.get("snap_token")):
		frappe.throw(_("Pembayaran belum bisa dibuat. Coba lagi atau pilih metode lain."), frappe.ValidationError)
	return out


def fetch_status(order_id):
	"""Status transaksi dari Midtrans (terautentikasi server key, jadi dipercaya). Kembalikan (status_internal|None, gross_amount) atau None."""
	if not enabled():
		return None
	try:
		j = _call("GET", _urls()["core"] + f"/v2/{order_id}/status")
	except (GatewayError, OSError):
		return None
	return STATUS_MAP.get(j.get("transaction_status")), j.get("gross_amount")
