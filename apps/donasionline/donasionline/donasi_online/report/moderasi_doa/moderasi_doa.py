"""Moderasi doa: daftar doa publik + tombol sembunyikan/tampilkan untuk Petugas Donasi.

Laporan ini dibatasi peran (System Manager, Petugas Donasi). Data diambil tanpa izin DocType Donation karena petugas
tidak diberi akses penuh ke Donation; yang tampil hanya field yang diperlukan untuk moderasi.
"""
import frappe
from frappe import _


def execute(filters=None):
	filters = filters or {}
	frappe.only_for(["System Manager", "Petugas Donasi"])
	cond = {"status": "Paid", "message": ["is", "set"]}
	if filters.get("status") == "Tersembunyi":
		cond["doa_disembunyikan"] = 1
	elif filters.get("status") == "Tampil":
		cond["doa_disembunyikan"] = 0
	rows = frappe.get_all("Donation", cond, ["gateway_order_id", "paid_at", "donor_name", "is_anonymous", "message", "amin_count", "doa_disembunyikan", "doa_disembunyikan_alasan", "doa_disembunyikan_oleh"], order_by="paid_at desc", limit=500, ignore_permissions=True)
	data = [{
		"id": r.gateway_order_id, "paid_at": r.paid_at, "donor": "Hamba Allah" if r.is_anonymous else r.donor_name, "message": r.message, "amin": r.amin_count or 0,
		"status": "Tersembunyi" if r.doa_disembunyikan else "Tampil", "alasan": r.doa_disembunyikan_alasan or "", "oleh": r.doa_disembunyikan_oleh or "", "aksi": r.gateway_order_id,
	} for r in rows]
	cols = [
		{"label": _("Dibayar"), "fieldname": "paid_at", "fieldtype": "Datetime", "width": 140},
		{"label": _("Donatur"), "fieldname": "donor", "fieldtype": "Data", "width": 130},
		{"label": _("Doa"), "fieldname": "message", "fieldtype": "Data", "width": 360},
		{"label": _("Amin"), "fieldname": "amin", "fieldtype": "Int", "width": 60},
		{"label": _("Status"), "fieldname": "status", "fieldtype": "Data", "width": 100},
		{"label": _("Alasan"), "fieldname": "alasan", "fieldtype": "Data", "width": 160},
		{"label": _("Oleh"), "fieldname": "oleh", "fieldtype": "Data", "width": 130},
		{"label": _("Aksi"), "fieldname": "aksi", "fieldtype": "Data", "width": 110},
	]
	return cols, data
