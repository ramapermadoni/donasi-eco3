"""Seed fondasi keuangan (docs/psak/05 bagian A-C). Idempoten. USULAN/PROVISIONAL.

Pakai:  bench --site <site> execute donasionline.setup.seed.run
"""

import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_field

from donasionline.setup import chart

COMPANY_NAME = "Donasi Online"
COMPANY_ABBR = "DON"


def run(company=COMPANY_NAME, abbr=COMPANY_ABBR):
	frappe.flags.in_install = True  # hindari proteksi setup wizard saat seed
	company = ensure_company(company, abbr)
	ensure_fiscal_year(company)
	ensure_dana()
	ensure_dimensions(company)
	ensure_cost_centers(company)
	ensure_dimension_filters(company)
	ensure_custom_fields()
	ensure_default_accounts(company)
	ensure_settings(company)
	frappe.db.commit()
	return company


# --- Company dan bagan akun ---
def ensure_company(name, abbr):
	if not frappe.db.exists("Company", name):
		frappe.local.flags.ignore_chart_of_accounts = True
		try:
			doc = frappe.get_doc(
				{
					"doctype": "Company",
					"company_name": name,
					"abbr": abbr,
					"default_currency": "IDR",
					"country": "Indonesia",
				}
			)
			doc.insert(ignore_permissions=True)
		finally:
			frappe.local.flags.ignore_chart_of_accounts = False
	if not frappe.db.exists("Account", {"company": name, "account_number": "1-0000"}):
		from erpnext.accounts.doctype.account.chart_of_accounts.chart_of_accounts import create_charts

		create_charts(name, custom_chart=chart.tree())
	return name


def ensure_fiscal_year(company):
	from frappe.utils import getdate, nowdate

	year = getdate(nowdate()).year
	fy_name = str(year)
	if not frappe.db.exists("Fiscal Year", fy_name):
		frappe.get_doc(
			{
				"doctype": "Fiscal Year",
				"year": fy_name,
				"year_start_date": f"{year}-01-01",
				"year_end_date": f"{year}-12-31",
				"companies": [{"company": company}],
			}
		).insert(ignore_permissions=True)
	elif not frappe.db.exists("Fiscal Year Company", {"parent": fy_name, "company": company}):
		fy = frappe.get_doc("Fiscal Year", fy_name)
		fy.append("companies", {"company": company})
		fy.save(ignore_permissions=True)


# --- Dana, dimensi ---
def ensure_dana():
	for code, name, jenis in chart.DANA:
		if not frappe.db.exists("Dana", code):
			frappe.get_doc({"doctype": "Dana", "dana_code": code, "dana_name": name, "jenis": jenis}).insert(
				ignore_permissions=True
			)


def _ensure_dimension(document_type, label, fieldname, company, mandatory):
	from erpnext.accounts.doctype.accounting_dimension.accounting_dimension import (
		make_dimension_in_accounting_doctypes,
	)

	name = frappe.db.get_value("Accounting Dimension", {"document_type": document_type})
	if name:
		doc = frappe.get_doc("Accounting Dimension", name)
	else:
		doc = frappe.new_doc("Accounting Dimension")
		doc.document_type = document_type
		doc.label = label
		doc.fieldname = fieldname
	row = next((r for r in doc.get("dimension_defaults") if r.company == company), None)
	if not row:
		row = doc.append("dimension_defaults", {"company": company})
	row.mandatory_for_bs = 1 if mandatory else 0
	row.mandatory_for_pl = 1 if mandatory else 0
	row.automatically_post_balancing_accounting_entry = 0  # D0: harus nonaktif
	doc.disabled = 0
	doc.save(ignore_permissions=True)
	# on_update hanya mengantre (queue long): panggil langsung (idempoten)
	make_dimension_in_accounting_doctypes(doc=doc)


def ensure_dimensions(company):
	_ensure_dimension("Dana", "Dana", "dana", company, mandatory=True)
	# Nama "Campaign" dilarang (bentrok CRM): pakai Kampanye Donasi, label/fieldname "Kampanye"
	_ensure_dimension("Kampanye Donasi", "Kampanye", "kampanye", company, mandatory=False)


# --- Cost Center (Program) ---
def ensure_cost_centers(company):
	abbr = frappe.db.get_value("Company", company, "abbr")
	parent = frappe.db.get_value("Cost Center", {"company": company, "is_group": 1, "parent_cost_center": ["in", ["", None]]})
	if not parent:
		parent = f"{company} - {abbr}"
	for prog in chart.PROGRAMS + ["Operasional Amil"]:
		if not frappe.db.exists("Cost Center", {"company": company, "cost_center_name": prog}):
			frappe.get_doc(
				{
					"doctype": "Cost Center",
					"cost_center_name": prog,
					"company": company,
					"parent_cost_center": parent,
					"is_group": 0,
				}
			).insert(ignore_permissions=True)


# --- Accounting Dimension Filter per Dana ---
def account_name(company, number):
	return frappe.db.get_value("Account", {"company": company, "account_number": number}, "name")


def ensure_dimension_filters(company):
	for danas, numbers in chart.FILTERS.items():
		first = account_name(company, numbers[0])
		existing = frappe.db.get_value(
			"Applicable On Account",
			{"applicable_on_account": first, "parenttype": "Accounting Dimension Filter"},
			"parent",
		)
		accounts = []
		for n in numbers:
			acc = account_name(company, n)
			if not acc:
				frappe.throw(f"Akun {n} tidak ditemukan di {company}")
			accounts.append({"applicable_on_account": acc})
		payload = {
			"accounting_dimension": "Dana",
			"allow_or_restrict": "Allow",
			"company": company,
			"apply_restriction_on_values": 1,
			"accounts": accounts,
			"dimensions": [{"accounting_dimension": "Dana", "dimension_value": d} for d in danas],
		}
		if existing:
			doc = frappe.get_doc("Accounting Dimension Filter", existing)
			doc.update({k: v for k, v in payload.items() if k not in ("accounts", "dimensions")})
			doc.set("accounts", accounts)
			doc.set("dimensions", payload["dimensions"])
			doc.save(ignore_permissions=True)
		else:
			doc = frappe.get_doc({"doctype": "Accounting Dimension Filter", **payload})
			doc.insert(ignore_permissions=True)


# --- Custom field idempotensi ---
def ensure_custom_fields():
	create_custom_field(
		"Journal Entry",
		{
			"fieldname": "donation_ref",
			"label": "Donation Ref",
			"fieldtype": "Data",
			"unique": 1,
			"no_copy": 1,
			"read_only": 1,
			"insert_after": "title",
			"description": "Kunci idempoten {ID}:{PERISTIWA}[:n]; tidak pernah ''.",
		},
	)


def ensure_default_accounts(company):
	"""Default akun Company (ignore_chart_of_accounts melewati set_default_accounts)."""
	vals = {
		"default_cash_account": account_name(company, "1-1101"),
		"default_bank_account": account_name(company, "1-1101"),
		"round_off_account": account_name(company, "5-3500"),
		"default_expense_account": account_name(company, "5-3500"),
		"default_income_account": account_name(company, "4-3900"),
	}
	for k, v in vals.items():
		if v and not frappe.db.get_value("Company", company, k):
			frappe.db.set_value("Company", company, k, v)


def ensure_settings(company):
	s = frappe.get_single("Pengaturan Donasi")
	if not s.company:
		s.company = company
	if not s.cost_center_operasional:
		s.cost_center_operasional = frappe.db.get_value(
			"Cost Center", {"company": company, "cost_center_name": "Operasional Amil"}
		)
	s.posting_enabled = 0  # gerbang H.1: mati bawaan
	s.save(ignore_permissions=True)
