import frappe


def execute():
	"""Single yang sudah tersimpan tidak mendapat default field baru: nyalakan mode gabung sekali."""
	frappe.db.set_single_value("Pengaturan Donasi", "serve_ui", 1)
