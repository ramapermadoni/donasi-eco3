"""/api/payment/* dan webhook gateway."""
import io
import json

import frappe
from frappe import _
from frappe.rate_limiter import rate_limit
from frappe.utils import add_to_date, now_datetime

from donasionline import gateway
from donasionline.api.donation import by_public_id


def _method_json(m):
	return {"code": m.code, "name": m.method_name, "type": m.method_type, "feeFlat": m.fee_flat or 0, "feePercent": m.fee_percent or 0, "minAmount": m.min_amount or 0, "maxAmount": m.max_amount or 0, "iconUrl": m.icon_url}


@frappe.whitelist(allow_guest=True)
def methods():
	rows = frappe.get_all("Metode Pembayaran", {"enabled": 1}, ["*"], order_by="sort_order asc")
	return {"methods": [_method_json(m) for m in rows]}


@frappe.whitelist(allow_guest=True)
def instructions(code):
	if not frappe.db.exists("Metode Pembayaran", code):
		frappe.throw(_("Metode tidak ditemukan"), frappe.DoesNotExistError)
	m = frappe.get_doc("Metode Pembayaran", code)
	return [{"title": i.group_title, "steps": [s for s in (i.steps or "").split("\n") if s]} for i in m.instructions]


@frappe.whitelist(allow_guest=True)
def snap_config():
	"""Hanya kunci klien publik. JANGAN pernah mengirim server key."""
	return {"clientKey": frappe.local.conf.get("midtrans_client_key") or "", "isProduction": bool(frappe.local.conf.get("midtrans_production"))}


@frappe.whitelist(allow_guest=True, methods=["POST"])
@rate_limit(limit=20, seconds=60)
def create(donation_id, payment_method, **_ignored):
	d = by_public_id(donation_id)
	if d.status != "Pending":
		frappe.throw(_("Donasi tidak lagi menunggu pembayaran"), frappe.ValidationError)
	if not frappe.db.exists("Metode Pembayaran", payment_method):
		frappe.throw(_("Metode pembayaran tidak dikenal"), frappe.ValidationError)
	m = frappe.get_doc("Metode Pembayaran", payment_method)
	if not m.enabled:
		frappe.throw(_("Metode pembayaran nonaktif"), frappe.ValidationError)
	if d.amount < (m.min_amount or 0) or (m.max_amount and d.amount > m.max_amount):
		frappe.throw(_("Nominal di luar batas metode ini"), frappe.ValidationError)
	existing = frappe.db.get_value("Permintaan Pembayaran", {"donation": d.name, "payment_method": m.name, "status": "pending"})
	if existing:  # idempoten: ulangi permintaan -> pembayaran sama
		pr = frappe.get_doc("Permintaan Pembayaran", existing)
	else:
		oid = d.gateway_order_id + "-" + frappe.generate_hash(length=4)
		data = gateway.charge(oid, m, d.amount, {"name": d.donor_name, "phone": d.donor_phone})
		pr = frappe.get_doc({"doctype": "Permintaan Pembayaran", "donation": d.name, "order_id": oid, "payment_method": m.name, "status": "pending", "expires_at": d.expired_at, **data}).insert(ignore_permissions=True)
		frappe.db.set_value("Donation", d.name, "payment_method", m.name)
	return {"orderId": pr.order_id, "qrString": pr.qr_string, "qrImageUrl": pr.qr_code_url, "expiresAt": pr.expires_at, "vaNumber": pr.va_number, "redirectUrl": pr.redirect_url}


@frappe.whitelist(allow_guest=True)
def qr_png(id):
	d = by_public_id(id)
	pr = frappe.db.get_value("Permintaan Pembayaran", {"donation": d.name, "qr_string": ["is", "set"]}, "qr_string")
	if not pr:
		frappe.throw(_("QR tidak tersedia"), frappe.DoesNotExistError)
	try:
		import pyqrcode  # frappe menyertakan pyqrcode
		buf = io.BytesIO()
		pyqrcode.create(pr).png(buf, scale=6)
		frappe.local.response.filename = f"qris-{id}.png"
		frappe.local.response.filecontent = buf.getvalue()
		frappe.local.response.type = "download"
	except ImportError:
		frappe.throw(_("Pembuat QR tidak tersedia"))


STATUS_MAP = gateway.STATUS_MAP


@frappe.whitelist(allow_guest=True, methods=["POST"])
def webhook(order_id=None, status_code=None, gross_amount=None, signature_key=None, transaction_status=None, **_ignored):
	"""Notifikasi gateway: tanda tangan WAJIB valid; tanpa server key terkonfigurasi semua ditolak. Idempoten."""
	key = gateway.server_key()
	if not key:
		frappe.throw(_("Webhook tidak dikonfigurasi"), frappe.PermissionError)
	expected = gateway.signature(order_id, status_code, gross_amount, key)
	import secrets
	if not signature_key or not secrets.compare_digest(expected, str(signature_key)):
		frappe.throw(_("Tanda tangan tidak valid"), frappe.PermissionError)
	pr_name = frappe.db.get_value("Permintaan Pembayaran", {"order_id": order_id})
	if not pr_name:
		# tanda tangan sah tapi order tak dikenal (mis. "Test notification URL" Midtrans): jawab 200 agar tidak diulang terus
		return {"ok": True, "ignored": True}
	pr = frappe.get_doc("Permintaan Pembayaran", pr_name)
	new = STATUS_MAP.get(transaction_status)
	if not new:
		return {"ok": True, "ignored": True}
	return {"ok": True, **_apply_status(pr, new, gross_amount)}


def _apply_status(pr, new, gross_amount=None):
	"""Status hanya boleh maju: pending -> paid|failed|expired; paid final."""
	d = frappe.get_doc("Donation", pr.donation)
	if gross_amount is not None and float(gross_amount) != float(d.amount):
		frappe.throw(_("Jumlah tidak cocok"), frappe.ValidationError)
	if pr.status == "paid":
		return {"status": "paid", "noop": True}
	frappe.db.set_value("Permintaan Pembayaran", pr.name, "status", new)
	if new == "paid":
		d.reload()
		d.mark_paid()
	elif d.status == "Pending":
		frappe.db.set_value("Donation", d.name, "status", "Failed" if new == "failed" else "Expired")
	return {"status": new}


@frappe.whitelist(methods=["POST"])
def simulate_paid(donation_id):
	"""Hanya simulator, hanya Petugas/System Manager: menandai pembayaran simulasi lunas (untuk uji/demonstrasi)."""
	frappe.only_for(["System Manager", "Petugas Donasi"])
	d = by_public_id(donation_id)
	pr_name = frappe.db.get_value("Permintaan Pembayaran", {"donation": d.name, "simulated": 1, "status": "pending"})
	if not pr_name:
		frappe.throw(_("Tidak ada pembayaran simulasi yang menunggu"), frappe.ValidationError)
	return _apply_status(frappe.get_doc("Permintaan Pembayaran", pr_name), "paid")
