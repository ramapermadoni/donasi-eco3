"""Donasi Paid yang belum punya jurnal penerimaan, beserta alasannya.

Memastikan donasi wakaf/fidyah/qurban (dan lainnya yang diblokir gerbang H.1) tidak hilang dari pandangan:
tercatat di Donation, dan terdaftar di sini sampai dijurnal susulan.
"""
import frappe
from frappe import _

from donasionline import journals


def execute(filters=None):
	filters = filters or {}
	cond = {"status": "Paid", "je_receipt": ["is", "not set"]}
	if filters.get("fund_type"):
		cond["fund_type"] = filters["fund_type"]
	rows = frappe.get_all("Donation", cond, ["name", "gateway_order_id", "paid_at", "fund_type", "campaign_title", "program", "amount", "gateway"], order_by="paid_at desc", limit=2000)
	s = journals.settings()
	data = []
	for r in rows:
		try:
			journals.check_gate(frappe.get_doc("Donation", r.name), s)
			alasan = _("Siap diposting (belum diproses)")
		except journals.PostingBlocked as e:
			alasan = str(e)
		data.append({**r, "alasan": alasan})
	cols = [
		{"label": _("Donasi"), "fieldname": "name", "fieldtype": "Link", "options": "Donation", "width": 130},
		{"label": _("Dibayar"), "fieldname": "paid_at", "fieldtype": "Datetime", "width": 150},
		{"label": _("Jenis dana"), "fieldname": "fund_type", "fieldtype": "Data", "width": 110},
		{"label": _("Kampanye"), "fieldname": "campaign_title", "fieldtype": "Data", "width": 200},
		{"label": _("Jumlah"), "fieldname": "amount", "fieldtype": "Currency", "width": 120},
		{"label": _("Gateway"), "fieldname": "gateway", "fieldtype": "Data", "width": 90},
		{"label": _("Mengapa belum dijurnal"), "fieldname": "alasan", "fieldtype": "Data", "width": 380},
	]
	return cols, data
