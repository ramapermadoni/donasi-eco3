import frappe


def execute():
	"""Wakaf yang sudah ada: lembaga berperan sebagai perantara (titipan) dulu; mode 'Dikelola lembaga' dipilih sengaja nanti."""
	for n in frappe.get_all("Kampanye Donasi", {"fund_type": "wakaf"}, pluck="name"):
		frappe.db.set_value("Kampanye Donasi", n, "wakaf_mode", "Titipan ke nazhir mitra")
