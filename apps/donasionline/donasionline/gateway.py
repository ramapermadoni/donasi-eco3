"""Adapter gateway pembayaran. Bawaan: SIMULATOR (tanpa jaringan). Midtrans nyata BELUM diimplementasi/diuji.

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


def charge(order_id, method, amount):
	"""Kembalikan field Permintaan Pembayaran. Hanya simulator saat ini."""
	if frappe.local.conf.get("midtrans_enabled"):
		frappe.throw(_("Integrasi Midtrans belum diimplementasi; gunakan sandbox setelah dirancang (W6 lanjutan)."))
	typ = method.method_type
	out = {"gateway": "simulator", "simulated": 1, "payment_type": typ}
	if typ == "qris":
		qr = f"00020101SIMULATOR{order_id}"
		out.update(qr_string=qr, qr_code_url=f"/api/method/donasionline.api.payment.qr_png?id={order_id}")
	elif typ == "virtual_account":
		out.update(va_bank=method.code.replace("_va", ""), va_number="9999" + "".join(secrets.choice("0123456789") for _ in range(12)))
	else:
		out.update(redirect_url=f"/simulator/{order_id}")
	return out
