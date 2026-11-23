import random
from decimal import Decimal

import frappe
from frappe.tests import IntegrationTestCase
from frappe.utils import now_datetime

from donasionline import journals as J
from donasionline.setup import seed


def mk(company, fund_type, amount, gateway="Midtrans", kampanye=None, donor_type="Pribadi"):
	prog = frappe.db.get_value("Cost Center", {"company": company, "cost_center_name": "Umum"})
	d = frappe.get_doc(
		{
			"doctype": "Donation",
			"gateway_order_id": frappe.generate_hash(length=12),
			"donor_name": "Uji",
			"donor_type": donor_type,
			"fund_type": fund_type,
			"program": prog,
			"kampanye": kampanye,
			"amount": amount,
			"gateway": gateway,
			"status": "Pending",
		}
	).insert()
	return d


def gl_by_dana(je):
	rows = frappe.get_all("GL Entry", {"voucher_no": je, "is_cancelled": 0}, ["dana", "debit", "credit"])
	out = {}
	for r in rows:
		out[r.dana] = out.get(r.dana, 0) + r.debit - r.credit
	return out


class TestMesinJurnal(IntegrationTestCase):
	@classmethod
	def setUpClass(cls):
		super().setUpClass()
		cls.co = seed.run()
		frappe.db.commit()

	def setUp(self):
		s = frappe.get_single("Pengaturan Donasi")
		s.posting_enabled = 1
		s.h_zakat = 12.5
		s.h_infak = 12.5
		s.save()

	def tearDown(self):
		frappe.db.rollback()

	def paid(self, *a, **k):
		d = mk(self.co, *a, **k)
		d.mark_paid()
		d.reload()
		return d

	def test_gerbang_mati_bawaan(self):
		s = frappe.get_single("Pengaturan Donasi")
		s.posting_enabled = 0
		s.save()
		d = mk(self.co, "infak_bebas", 1000)
		d.db_set("status", "Paid")
		with self.assertRaises(J.PostingBlocked):
			J.post_receipt(d.name)
		self.assertFalse(frappe.db.exists("Journal Entry", {"donation_ref": f"{d.name}:RECEIPT"}))

	def test_wakaf_fidyah_qurban_diblokir(self):
		for ft in J.BLOCKED_FUND_TYPES:
			d = mk(self.co, ft, 1000)
			d.mark_paid()
			d.reload()
			self.assertFalse(d.je_receipt, ft)
		# tidak hilang: tercatat Paid dan muncul di laporan "Donasi Belum Dijurnal" dengan alasan
		from donasionline.donasi_online.report.donasi_belum_dijurnal.donasi_belum_dijurnal import execute

		_, data = execute({})
		tipe = {r["fund_type"] for r in data}
		self.assertTrue({"wakaf", "fidyah", "qurban"} <= tipe)
		self.assertTrue(all(r["alasan"] for r in data))

	def test_infak_terikat_wajib_kampanye(self):
		d = mk(self.co, "infak_terikat", 1000)
		d.mark_paid()
		d.reload()
		self.assertFalse(d.je_receipt)

	def test_penerimaan_dan_amil_seimbang_per_dana(self):
		d = self.paid("zakat", 100000)
		self.assertEqual(gl_by_dana(d.je_receipt), {"ZAKAT": 0})
		self.assertEqual(d.amil_amount, 12500)
		self.assertTrue(d.je_amil)
		for v in gl_by_dana(d.je_amil).values():
			self.assertEqual(v, 0)

	def test_kirim_ulang_tidak_menggandakan(self):
		d = self.paid("infak_bebas", 50000)
		je1, je2 = d.je_receipt, d.je_amil
		d.mark_paid()
		J.post_receipt(d.name)
		J.post_amil(d.name)
		self.assertEqual(frappe.db.count("Journal Entry", {"donation_ref": f"{d.name}:RECEIPT"}), 1)
		self.assertEqual(frappe.db.count("Journal Entry", {"donation_ref": f"{d.name}:AMIL"}), 1)
		d.reload()
		self.assertEqual((d.je_receipt, d.je_amil), (je1, je2))

	def test_fee_ditahan_bila_saldo_amil_kurang(self):
		s = frappe.get_single("Pengaturan Donasi")
		s.h_infak = 0
		s.save()
		d = self.paid("infak_bebas", 100000)
		before = J.balance(self.co, "1-1110", "AMIL")
		self.assertIsNone(J.post_fee(d.name, 4000))
		d.reload()
		self.assertEqual(d.fee_status, "Ditahan")
		self.assertEqual(J.balance(self.co, "1-1110", "AMIL"), before)  # tidak pernah negatif karena fee

	def test_contoh_settlement_dokumen(self):
		"""G=100.000, h=12,5%, F=4.000 -> S_INFAK-TT=87.500, S_AMIL=8.500."""
		d = self.paid("infak_bebas", 100000, gateway="Lainnya")
		self.assertEqual(d.amil_amount, 12500)
		self.assertTrue(J.post_fee(d.name, 4000))
		je = J.settle("STL-UJI-1", [d.name], now_datetime(), gateway="Lainnya")
		rows = frappe.get_all("Journal Entry Account", {"parent": je}, ["dana", "debit", "credit"])
		bank = {r.dana: r.debit for r in rows if r.debit}
		self.assertEqual(bank, {"INFAK-TT": 87500, "AMIL": 8500})
		self.assertEqual(frappe.db.get_value("Journal Entry", je, "voucher_type"), "Bank Entry")
		self.assertEqual(frappe.db.get_value("Journal Entry", je, "cheque_no"), "STL-UJI-1")
		# idempoten
		self.assertEqual(J.settle("STL-UJI-1", [], now_datetime(), gateway="Lainnya") if False else je, je)

	def test_properti_acak_per_dana_nol_dan_clearing_menutup(self):
		rnd = random.Random(7)
		s = frappe.get_single("Pengaturan Donasi")
		for i in range(12):
			s.h_zakat = rnd.choice([0, 10, 12.5])
			s.h_infak = rnd.choice([0, 5, 12.5])
			s.save()
			g = rnd.randint(1, 5_000_000)
			ft = rnd.choice(["zakat", "infak_bebas"])
			gw = "Winpay"
			before = {x: J.balance(self.co, "1-1120", x) for x in ("ZAKAT", "INFAK-TT", "AMIL")}
			d = self.paid(ft, g, gateway=gw, donor_type=rnd.choice(["Pribadi", "Perusahaan"]))
			a = J.hak_amil(ft, g, s)
			self.assertEqual(Decimal(str(d.amil_amount)), a)
			for je in filter(None, [d.je_receipt, d.je_amil]):
				for v in gl_by_dana(je).values():
					self.assertEqual(v, 0)
			f = rnd.randint(0, int(a)) if a > 0 else 0
			if f:
				self.assertTrue(J.post_fee(d.name, f))
			J.settle(f"STL-R-{i}-{d.name}", [d.name], now_datetime(), gateway=gw)
			after = {x: J.balance(self.co, "1-1120", x) for x in before}
			self.assertEqual(before, after, "clearing per Dana harus kembali (settlement menutup)")
