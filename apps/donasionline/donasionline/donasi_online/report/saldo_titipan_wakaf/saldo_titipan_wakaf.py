"""Per kampanye wakaf: diterima (Paid), sudah diteruskan ke nazhir, dan sisa yang masih harus diteruskan."""
import frappe
from frappe import _


def execute(filters=None):
	data = []
	for c in frappe.get_all("Kampanye Donasi", {"fund_type": "wakaf"}, ["name", "title", "nama_kampanye", "mitra", "wakaf_mode"], order_by="name"):
		terima = frappe.db.sql("select coalesce(sum(amount),0), count(*) from `tabDonation` where kampanye=%s and status='Paid'", c.name)[0]
		kirim = frappe.db.sql("select coalesce(sum(jumlah),0) from `tabPenerusan Wakaf` where kampanye=%s and docstatus=1", c.name)[0][0]
		if not (terima[1] or kirim) and not c.mitra:
			continue
		data.append({"kampanye": c.name, "judul": c.title or c.nama_kampanye, "mode": c.wakaf_mode, "mitra": c.mitra, "donasi": terima[1],
			"diterima": terima[0], "diteruskan": kirim, "sisa": float(terima[0]) - float(kirim)})
	cols = [
		{"label": _("Kampanye"), "fieldname": "kampanye", "fieldtype": "Link", "options": "Kampanye Donasi", "width": 170},
		{"label": _("Judul"), "fieldname": "judul", "fieldtype": "Data", "width": 220},
		{"label": _("Mode"), "fieldname": "mode", "fieldtype": "Data", "width": 150},
		{"label": _("Nazhir tujuan"), "fieldname": "mitra", "fieldtype": "Link", "options": "Mitra", "width": 130},
		{"label": _("Donasi"), "fieldname": "donasi", "fieldtype": "Int", "width": 70},
		{"label": _("Diterima"), "fieldname": "diterima", "fieldtype": "Currency", "width": 120},
		{"label": _("Sudah diteruskan"), "fieldname": "diteruskan", "fieldtype": "Currency", "width": 130},
		{"label": _("Sisa harus diteruskan"), "fieldname": "sisa", "fieldtype": "Currency", "width": 140},
	]
	return cols, data
