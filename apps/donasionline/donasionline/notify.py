"""Pengiriman OTP/pengingat. Kanal dipilih di Pengaturan Donasi.otp_channel (USULAN; belum dicoba ke gateway nyata).

- WhatsApp: POST JSON ke URL gateway generik (badan dari template, header otorisasi dari token). Tidak terikat satu vendor.
- Email: frappe.sendmail ke email donor (butuh Email Account keluar di Frappe); email palsu @donor.invalid dilewati.
- Kode OTP TIDAK pernah ditulis ke log.
"""
import json

import frappe
from frappe import _

TIMEOUT = 10


def _settings():
	return frappe.get_single("Pengaturan Donasi")


def _wa(s, phone, message):
	url = (s.wa_url or "").strip()
	dev = frappe.local.conf.get("developer_mode")
	if not url or not (url.startswith("https://") or (dev and url.startswith("http://"))):
		raise ValueError("WA gateway URL kosong/bukan https")
	import requests

	# {phone}/{message} diganti SETELAH di-JSON-escape agar kutip di teks tidak merusak badan
	esc = lambda v: json.dumps(v)[1:-1]
	body = (s.wa_body or '{"target": "{phone}", "message": "{message}"}').replace("{phone}", esc(phone)).replace("{message}", esc(message))
	headers = {"Content-Type": "application/json"}
	token = s.get_password("wa_token", raise_exception=False)
	if token:
		headers[(s.wa_auth_header or "Authorization").strip()] = token
	r = requests.post(url, data=body.encode(), headers=headers, timeout=TIMEOUT)
	if r.status_code >= 300:
		raise RuntimeError(f"WA gateway status {r.status_code}")


def _email(phone, subject, message):
	to = frappe.db.get_value("Donor", {"phone": phone}, "email")
	if not to or to.endswith("@donor.invalid"):
		raise ValueError("donor tanpa email")
	frappe.sendmail(recipients=[to], subject=subject, message=message, now=True)


def send_otp(phone, code):
	"""True bila terkirim lewat kanal terpilih; False bila kanal 'Log saja'. Kanal gagal -> lempar galat generik."""
	if frappe.local.conf.get("donasionline_otp_dev_echo"):
		return False
	s = _settings()
	channel = s.otp_channel or "Log saja"
	if channel == "Log saja":
		frappe.logger("donasionline").warning("OTP dibuat untuk ...%s tetapi kanal 'Log saja': tidak terkirim", phone[-4:])
		return False
	msg = (s.otp_message or "Kode donasi Anda: {code}").replace("{code}", code)
	order = {"WhatsApp": ["wa"], "Email": ["email"], "WhatsApp lalu Email": ["wa", "email"]}[channel]
	for ch in order:
		try:
			_wa(s, phone, msg) if ch == "wa" else _email(phone, _("Kode donasi"), msg)
			return True
		except Exception as e:
			frappe.logger("donasionline").error("OTP %s gagal untuk ...%s: %s", ch, phone[-4:], type(e).__name__)  # tanpa kode
	frappe.throw(_("Kode belum bisa dikirim. Coba lagi beberapa saat."), frappe.ValidationError)


def send_reminder(donor, text, channel):
	"""Pengingat Rutin. channel 'wa'|'email'. True bila terkirim, False bila dilewati (kanal belum diatur / donor tanpa kontak),
	dan lempar galat bila gateway gagal (pemanggil mencatat 'Gagal'). Tidak bergantung pada Pengaturan.otp_channel."""
	d = frappe.db.get_value("Donor", donor, ["phone", "email"], as_dict=True)
	if not d:
		return False
	if channel == "wa":
		s = _settings()
		if not (s.wa_url or "").strip() or not d.phone:
			return False
		_wa(s, d.phone, text)
		return True
	if channel == "email":
		if not d.email or d.email.endswith("@donor.invalid"):
			return False
		_email(d.phone, _("Pengingat shadaqa rutin"), text)
		return True
	return False
