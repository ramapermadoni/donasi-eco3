import json
from unittest import mock

import frappe
from frappe.tests import IntegrationTestCase

from donasionline import notify


class Resp:
	def __init__(self, code=200):
		self.status_code = code


class TestKanalOTP(IntegrationTestCase):
	def setUp(self):
		frappe.local.conf.pop("donasionline_otp_dev_echo", None)
		s = frappe.get_single("Pengaturan Donasi")
		s.otp_channel = "WhatsApp"
		s.wa_url = "https://wa.example.test/send"
		s.wa_token = "Bearer rahasia"
		s.wa_auth_header = "Authorization"
		s.wa_body = '{"target": "{phone}", "message": "{message}"}'
		s.otp_message = 'Kode "{code}" untuk Anda'
		s.save(ignore_permissions=True)

	def test_wa_terkirim_badan_json_valid(self):
		with mock.patch("requests.post", return_value=Resp(200)) as m:
			self.assertTrue(notify.send_otp("6281234567890", "123456"))
		kw = m.call_args.kwargs
		body = json.loads(kw["data"])  # kutip di teks tidak merusak JSON
		self.assertEqual(body, {"target": "6281234567890", "message": 'Kode "123456" untuk Anda'})
		self.assertEqual(kw["headers"]["Authorization"], "Bearer rahasia")
		self.assertEqual(kw["timeout"], 10)

	def test_wa_gagal_lempar_galat_generik_tanpa_kode(self):
		with mock.patch("requests.post", return_value=Resp(500)):
			with self.assertRaises(frappe.ValidationError) as c:
				notify.send_otp("6281234567890", "654321")
		self.assertNotIn("654321", str(c.exception))

	def test_wa_url_http_ditolak_di_produksi(self):
		frappe.db.set_single_value("Pengaturan Donasi", "wa_url", "http://wa.example.test/send")
		frappe.local.conf.developer_mode = 0
		with mock.patch("requests.post") as m:
			with self.assertRaises(frappe.ValidationError):
				notify.send_otp("6281234567890", "111111")
		m.assert_not_called()

	def test_log_saja_tidak_mengirim(self):
		frappe.db.set_single_value("Pengaturan Donasi", "otp_channel", "Log saja")
		with mock.patch("requests.post") as m:
			self.assertFalse(notify.send_otp("6281234567890", "111111"))
		m.assert_not_called()

	def test_wa_lalu_email_fallback_email_palsu_dilewati(self):
		frappe.db.set_single_value("Pengaturan Donasi", "otp_channel", "WhatsApp lalu Email")
		with mock.patch("requests.post", return_value=Resp(500)), mock.patch("frappe.sendmail") as sm:
			with self.assertRaises(frappe.ValidationError):
				notify.send_otp("6280000000000", "222222")  # donor tidak ada -> email dilewati
		sm.assert_not_called()
