import frappe
from unittest import mock

from frappe.tests import IntegrationTestCase

from donasionline import gateway
from donasionline.api import donation, payment
from donasionline.setup import import_snapshot, seed


class R:
	def __init__(self, j, code=200):
		self._j, self.status_code = j, code

	def json(self):
		return self._j


class TestMidtrans(IntegrationTestCase):
	@classmethod
	def setUpClass(cls):
		super().setUpClass()
		seed.run()
		import_snapshot.run()
		frappe.db.commit()

	def setUp(self):
		frappe.set_user("Administrator")
		frappe.local.conf.update({"midtrans_enabled": 1, "midtrans_server_key": "SB-Mid-server-TEST", "midtrans_client_key": "SB-Mid-client-TEST"})
		frappe.local.conf.pop("midtrans_production", None)

	def tearDown(self):
		for k in ("midtrans_enabled", "midtrans_server_key", "midtrans_client_key"):
			frappe.local.conf.pop(k, None)
		frappe.db.rollback()

	def _donasi(self, amount=30000):
		return donation.create(campaign_id="sedekah", amount=amount, donor_name="Tes", donor_phone="081234567890")["donation_id"]

	def test_qris_core_api(self):
		resp = {"status_code": "201", "qr_string": "000201QR", "actions": [{"name": "generate-qr-code", "url": "https://api.sandbox.midtrans.com/qr/1"}]}
		with mock.patch("requests.request", return_value=R(resp)) as m:
			r = payment.create(self._donasi(), "qris")
		args, kw = m.call_args
		self.assertEqual(args, ("POST", "https://api.sandbox.midtrans.com/v2/charge"))
		self.assertEqual(kw["auth"], ("SB-Mid-server-TEST", ""))
		self.assertEqual(kw["json"]["payment_type"], "qris")
		self.assertEqual(kw["json"]["custom_expiry"], {"expiry_duration": 1440, "unit": "minute"})
		self.assertEqual(kw["json"]["transaction_details"]["order_id"], r["orderId"])
		self.assertEqual(kw["json"]["transaction_details"]["gross_amount"], 30000)
		self.assertEqual((r["qrString"], r["qrImageUrl"]), ("000201QR", "https://api.sandbox.midtrans.com/qr/1"))
		self.assertLessEqual(len(r["orderId"]), 50)

	def test_va_bni_dan_permata(self):
		with mock.patch("requests.request", return_value=R({"status_code": "201", "va_numbers": [{"bank": "bni", "va_number": "8810123"}]})) as m:
			r = payment.create(self._donasi(), "bni_va")
		self.assertEqual(m.call_args.kwargs["json"]["bank_transfer"], {"bank": "bni"})
		self.assertEqual(r["vaNumber"], "8810123")
		with mock.patch("requests.request", return_value=R({"status_code": "201", "permata_va_number": "7700123"})):
			r = payment.create(self._donasi(), "permata_va")
		self.assertEqual(r["vaNumber"], "7700123")

	def test_gopay_lewat_snap(self):
		with mock.patch("requests.request", return_value=R({"token": "snap-tok", "redirect_url": "https://app.sandbox.midtrans.com/snap/v4/redirection/x"}, 201)) as m:
			payment.create(self._donasi(), "gopay")
		self.assertEqual(m.call_args.args[1], "https://app.sandbox.midtrans.com/snap/v1/transactions")
		self.assertEqual(m.call_args.kwargs["json"]["enabled_payments"], ["gopay"])
		pr = frappe.get_all("Permintaan Pembayaran", fields=["snap_token", "gateway", "simulated"], order_by="creation desc", limit=1)[0]
		self.assertEqual((pr.snap_token, pr.gateway, pr.simulated), ("snap-tok", "midtrans", 0))

	def test_gagal_gateway_galat_generik_tanpa_kunci(self):
		with mock.patch("requests.request", return_value=R({"status_code": "401", "status_message": "Access denied SB-Mid-server-TEST"}, 401)):
			with self.assertRaises(frappe.ValidationError) as c:
				payment.create(self._donasi(), "qris")
		self.assertNotIn("SB-Mid", str(c.exception))
		self.assertEqual(frappe.db.count("Permintaan Pembayaran", {"status": "pending", "gateway": "midtrans"}), 0)

	def test_poll_status_menandai_lunas_sekali(self):
		with mock.patch("requests.request", return_value=R({"status_code": "201", "va_numbers": [{"bank": "bri", "va_number": "1"}]})):
			pid = self._donasi()
			payment.create(pid, "bri_va")
		with mock.patch("requests.request", return_value=R({"status_code": "200", "transaction_status": "settlement", "gross_amount": "30000.00"})):
			frappe.cache.delete_value(f"mt_poll:{donation.by_public_id(pid).name}")
			self.assertEqual(donation.status(pid)["status"], "paid")
		self.assertEqual(frappe.db.get_value("Donation", {"gateway_order_id": pid}, "status"), "Paid")

	def test_poll_jumlah_tidak_cocok_ditolak(self):
		with mock.patch("requests.request", return_value=R({"status_code": "201", "va_numbers": [{"bank": "bri", "va_number": "1"}]})):
			pid = self._donasi()
			payment.create(pid, "bri_va")
		with mock.patch("requests.request", return_value=R({"status_code": "200", "transaction_status": "settlement", "gross_amount": "1.00"})):
			frappe.cache.delete_value(f"mt_poll:{donation.by_public_id(pid).name}")
			with self.assertRaises(frappe.ValidationError):
				donation.status(pid)
		self.assertEqual(frappe.db.get_value("Donation", {"gateway_order_id": pid}, "status"), "Pending")

	def test_webhook_tanda_tangan_midtrans(self):
		with mock.patch("requests.request", return_value=R({"status_code": "201", "va_numbers": [{"bank": "bni", "va_number": "1"}]})):
			pid = self._donasi()
			oid = payment.create(pid, "bni_va")["orderId"]
		sig = gateway.signature(oid, "200", "30000.00", "SB-Mid-server-TEST")
		with self.assertRaises(frappe.PermissionError):
			payment.webhook(order_id=oid, status_code="200", gross_amount="30000.00", signature_key="salah", transaction_status="settlement")
		r = payment.webhook(order_id=oid, status_code="200", gross_amount="30000.00", signature_key=sig, transaction_status="settlement")
		self.assertEqual(r["status"], "paid")

	def test_webhook_order_tak_dikenal_dijawab_ok(self):
		sig = gateway.signature("payment_notif_test_X", "200", "10000.00", "SB-Mid-server-TEST")
		r = payment.webhook(order_id="payment_notif_test_X", status_code="200", gross_amount="10000.00", signature_key=sig, transaction_status="settlement")
		self.assertEqual(r, {"ok": True, "ignored": True})
