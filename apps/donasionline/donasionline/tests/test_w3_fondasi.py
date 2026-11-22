import frappe
from frappe.tests import IntegrationTestCase
from frappe.utils import nowdate

from donasionline.setup import chart, seed


def _je(company, rows, **kw):
	"""rows: (nomor_akun, debit, credit, dana)"""
	cc = frappe.db.get_value("Cost Center", {"company": company, "cost_center_name": "Umum"})
	doc = frappe.get_doc(
		{
			"doctype": "Journal Entry",
			"voucher_type": "Journal Entry",
			"company": company,
			"posting_date": nowdate(),
			"accounts": [
				{
					"account": seed.account_name(company, n),
					"debit_in_account_currency": d,
					"credit_in_account_currency": c,
					"dana": dana,
					"cost_center": cc,
				}
				for n, d, c, dana in rows
			],
			**kw,
		}
	)
	return doc


class TestFondasi(IntegrationTestCase):
	@classmethod
	def setUpClass(cls):
		super().setUpClass()
		cls.company = seed.run()

	def test_bagan_akun_86(self):
		n = frappe.db.count("Account", {"company": self.company, "account_number": ["like", "_-%"]})
		self.assertEqual(n, len(chart.ROWS))

	def test_seed_idempoten(self):
		before = {
			t: frappe.db.count(t)
			for t in ("Account", "Dana", "Cost Center", "Accounting Dimension Filter", "Accounting Dimension")
		}
		seed.run()
		after = {t: frappe.db.count(t) for t in before}
		self.assertEqual(before, after)

	def test_dimensi_mandatory(self):
		d = frappe.get_doc("Accounting Dimension", {"document_type": "Dana"})
		row = d.dimension_defaults[0]
		self.assertTrue(row.mandatory_for_bs and row.mandatory_for_pl)
		self.assertFalse(row.automatically_post_balancing_accounting_entry)

	def test_je_seimbang_per_dana_diterima(self):
		je = _je(self.company, [("1-1101", 1000, 0, "ZAKAT"), ("4-1100", 0, 1000, "ZAKAT")])
		je.insert()
		je.submit()
		self.assertEqual(je.docstatus, 1)

	def test_je_tak_seimbang_per_dana_ditolak(self):
		# total seimbang, tetapi tidak per Dana
		je = _je(self.company, [("1-1101", 1000, 0, "AMIL"), ("4-1100", 0, 1000, "ZAKAT")])
		je.insert()
		with self.assertRaises(frappe.ValidationError):
			je.submit()

	def test_akun_di_luar_filter_ditolak(self):
		# 4-1100 hanya boleh ZAKAT; kredit ke INFAK-TT harus ditolak
		je = _je(self.company, [("1-1101", 1000, 0, "INFAK-TT"), ("4-1100", 0, 1000, "INFAK-TT")])
		je.insert()
		with self.assertRaises(frappe.ValidationError):
			je.submit()

	def test_dana_kosong_ditolak(self):
		je = _je(self.company, [("1-1101", 1000, 0, None), ("4-1100", 0, 1000, None)])
		with self.assertRaises(frappe.ValidationError):
			je.insert()
			je.submit()
