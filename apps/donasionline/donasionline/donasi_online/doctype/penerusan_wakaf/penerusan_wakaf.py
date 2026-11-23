"""Penerusan dana wakaf titipan ke nazhir mitra (F4, mode Titipan).

Saldo titipan per kampanye = donasi wakaf Paid - penerusan yang sudah di-Submit. Tidak boleh meneruskan lebih dari saldo.
Submit = dana benar-benar dikirim (wajib ada referensi transfer); tidak dapat diubah, hanya dibatalkan lalu diperbaiki.
PROVISIONAL: nilai bruto (fee gateway F25 belum diputuskan); jurnal wakaf belum diposting.
"""
import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt, getdate, today


def saldo_titipan(kampanye, kecuali=None):
	diterima = frappe.db.sql("select coalesce(sum(amount),0) from `tabDonation` where kampanye=%s and status='Paid'", kampanye)[0][0]
	q = "select coalesce(sum(jumlah),0) from `tabPenerusan Wakaf` where kampanye=%s and docstatus=1"
	args = [kampanye]
	if kecuali:
		q += " and name!=%s"
		args.append(kecuali)
	diteruskan = frappe.db.sql(q, args)[0][0]
	return flt(diterima) - flt(diteruskan)


class PenerusanWakaf(Document):
	def validate(self):
		c = frappe.db.get_value("Kampanye Donasi", self.kampanye, ["fund_type", "mitra"], as_dict=True)
		if not c or c.fund_type != "wakaf":
			frappe.throw(_("Kampanye harus bertipe wakaf."))
		if not c.mitra:
			frappe.throw(_("Kampanye ini belum terikat ke Mitra (nazhir tujuan)."))
		no = (frappe.db.get_value("Mitra", c.mitra, "nazhir_no_bwi") or "").strip()
		if not no:
			frappe.throw(_("Mitra tujuan belum punya nomor registrasi nazhir BWI."))
		self.mitra, self.nazhir_no_bwi = c.mitra, no
		if flt(self.jumlah) <= 0:
			frappe.throw(_("Jumlah harus lebih dari 0."))
		if getdate(self.tanggal) > getdate(today()):
			frappe.throw(_("Tanggal kirim tidak boleh di masa depan."))
		# kunci baris kampanye agar dua penerusan serentak tidak melewati saldo
		frappe.db.sql("select name from `tabKampanye Donasi` where name=%s for update", self.kampanye)
		self.saldo_sebelum = saldo_titipan(self.kampanye, kecuali=self.name)
		if flt(self.jumlah) > self.saldo_sebelum:
			frappe.throw(_("Jumlah melebihi saldo titipan kampanye ini (Rp {0}).").format(f"{self.saldo_sebelum:,.0f}"))

	def before_submit(self):
		if not (self.referensi_transfer or "").strip():
			frappe.throw(_("Referensi transfer wajib diisi sebelum Submit."))
