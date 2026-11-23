import frappe

from donasionline.setup import legal


def execute():
	"""Halaman legal yang sudah terimpor: ubah nama/email organisasi lain menjadi placeholder."""
	for n in frappe.get_all("Halaman Legal", pluck="name"):
		body = frappe.db.get_value("Halaman Legal", n, "body_html")
		new = legal.to_placeholders(body)
		if new != body:
			frappe.db.set_value("Halaman Legal", n, "body_html", new, update_modified=False)
