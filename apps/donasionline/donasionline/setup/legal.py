"""Halaman legal: ubah isi bawaan (salinan dari organisasi lain) menjadi bertanda {{org_*}} dan koreksi klaim yang tidak sesuai sistem ini. Idempoten."""
import re

# (pola, pengganti) berurutan
RULES = [
	(r"donasi@dtp\.id", "{{org_email}}"),
	(r"donasi\s*/\s*DT Peduli", "{{org_name}}"),
	(r"DT Peduli", "{{org_name}}"),
	# klaim integrasi: sistem ini hanya memakai Midtrans (WinPay/PayPal tidak diimplementasi)
	(r"Midtrans,\s*WinPay,\s*PayPal,?\s*(dan lainnya|and others)", r"Midtrans"),
]
LABEL = {"org_name": "nama lembaga", "org_email": "email kontak", "org_address": "alamat", "org_license": "nomor izin"}


def to_placeholders(html):
	for pat, rep in RULES:
		html = re.sub(pat, rep, html or "")
	return html


def render(html, settings):
	"""Isi {{org_*}} dari Pengaturan Donasi (di-escape); kosong -> tanda [belum diisi] agar terlihat."""
	from html import escape

	def sub(m):
		key = m.group(1)
		val = (settings.get(key) or "").strip()
		return escape(val) if val else f'<mark>[{LABEL.get(key, key)} belum diisi]</mark>'

	return re.sub(r"\{\{(org_name|org_email|org_address|org_license)\}\}", sub, html or "")
