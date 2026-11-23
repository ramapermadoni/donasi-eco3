import random

import frappe
from frappe.tests import IntegrationTestCase
from frappe.utils import add_days, nowdate

from donasionline import gateway
from donasionline.api import auth, baik, campaign, content, doa, donation, donor, gamification, notification, payment, recurring, survey, zakat
from donasionline.api import _util
from donasionline.api.catalog import ENDPOINTS
from donasionline.setup import import_snapshot, seed


def phone():
	return "0812" + "".join(random.choice("0123456789") for _ in range(8))


class TestApi(IntegrationTestCase):
	@classmethod
	def setUpClass(cls):
		super().setUpClass()
		cls.co = seed.run()
		import_snapshot.run()
		frappe.db.commit()

	def setUp(self):
		frappe.set_user("Administrator")
		frappe.local.conf.donasionline_otp_dev_echo = True
		frappe.local.conf.pop("midtrans_server_key", None)

	def tearDown(self):
		frappe.set_user("Administrator")
		frappe.db.rollback()

	# --- pembantu ---
	def new_donor(self, email=None):
		p = phone()
		r = auth.register_donor(name="Tes Donor", phone=p, email=email)
		v = auth.verify_otp(p, r["dev_code"])
		frappe.set_user(frappe.db.get_value("Donor", {"phone": _util.norm_phone(p)}, "user"))
		return v

	def make_donation(self, slug="sedekah", amount=10000, **kw):
		r = donation.create(campaign_id=slug, amount=amount, donor_name="Tes", donor_phone="081234567890", **kw)
		return r["donation_id"]

	def pay(self, pid):
		d = donation.by_public_id(pid)
		d.mark_paid()
		return d

	# --- katalog ---
	def test_katalog_setiap_method_ada_dan_whitelisted_dan_tesnya_ada(self):
		for http, path, m, guest, test, _ in ENDPOINTS:
			fn = frappe.get_attr("donasionline.api." + m) if "." in m else None
			self.assertTrue(fn, m)
			self.assertIn(fn, frappe.whitelisted, m)
			self.assertEqual(fn in frappe.guest_methods, guest, f"{m} guest")
			self.assertTrue(hasattr(self, test), f"{test} untuk {m}")

	# --- auth ---
	def test_auth_alur_register_otp_login_me_logout(self):
		frappe.set_user("Guest")
		self.assertIsNone(auth.me()["user"])
		p = phone()
		r = auth.register_donor(name="Siti Aminah", phone=p, email=None, city="Bandung")
		self.assertTrue(r["ok"])
		v = auth.verify_otp(p, r["dev_code"])
		self.assertTrue(v["ok"] and v["user"]["name"] == "Siti Aminah")
		self.assertEqual(auth.me()["user"]["phone"], _util.norm_phone(p))
		auth.logout()
		self.assertIsNone(auth.me()["user"])
		# login ulang lewat request_otp
		frappe.set_user("Guest")
		r2 = auth.request_otp(p)
		self.assertTrue(auth.verify_otp(p, r2["dev_code"])["ok"])
		# daftar ganda ditolak
		frappe.set_user("Guest")
		with self.assertRaises(frappe.ValidationError):
			auth.register_donor(name="Dup", phone=p)
		# nomor belum terdaftar -> needs_register
		q = phone()
		rq = auth.request_otp(q)
		self.assertTrue(auth.verify_otp(q, rq["dev_code"])["needs_register"])

	def test_otp_salah_dan_percobaan_dibatasi(self):
		frappe.set_user("Guest")
		p = phone()
		r = auth.request_otp(p)
		for _ in range(5):
			with self.assertRaises(frappe.ValidationError):
				auth.verify_otp(p, "000000" if r["dev_code"] != "000000" else "111111")
		with self.assertRaises(frappe.ValidationError):
			auth.verify_otp(p, r["dev_code"])  # kode benar pun ditolak setelah 5 gagal
		with self.assertRaises(frappe.ValidationError):
			auth.request_otp("123")  # nomor tak valid

	def test_otp_tanpa_dev_echo_tidak_membocorkan_kode(self):
		frappe.local.conf.donasionline_otp_dev_echo = False
		frappe.set_user("Guest")
		r = auth.request_otp(phone())
		self.assertNotIn("dev_code", r)

	def test_hapus_akun_anonimkan(self):
		self.new_donor()
		pid = self.make_donation()
		with self.assertRaises(frappe.ValidationError):
			auth.delete_account("salah")
		user = frappe.session.user
		auth.delete_account("HAPUS")
		self.assertEqual(frappe.db.get_value("User", user, "enabled"), 0)
		dn = donation.by_public_id(pid)
		self.assertIsNone(dn.donor)
		self.assertEqual(dn.donor_name, "Hamba Allah")

	def test_profil_dan_donor(self):
		frappe.set_user("Guest")
		with self.assertRaises(frappe.AuthenticationError):
			donor.stats()
		self.new_donor()
		self.assertTrue(donor.update_profile("Nama Baru", "a@b.co")["ok"])
		self.assertEqual(auth.me()["user"]["name"], "Nama Baru")
		with self.assertRaises(frappe.ValidationError):
			donor.update_profile("X")

	# --- donasi & pembayaran ---
	def test_donasi_validasi_dan_atribusi(self):
		frappe.set_user("Guest")
		with self.assertRaises(frappe.ValidationError):
			donation.create(campaign_id="sedekah", amount=2999)
		with self.assertRaises(frappe.DoesNotExistError):
			donation.create(campaign_id="tidak-ada", amount=5000)
		mitra = frappe.get_all("Mitra", pluck="slug", limit=1)[0]
		pid = donation.create(campaign_id=_util.GENERAL_ID, amount=5000, ref=mitra, utm_source="ig" * 80)["donation_id"]
		d = donation.by_public_id(pid)
		self.assertFalse(d.name == pid or pid.startswith("DON-"))
		self.assertEqual((d.mitra, d.status, d.kampanye), (mitra, "Pending", "sedekah"))
		self.assertEqual(len(d.utm_source), 100)
		d2 = donation.by_public_id(donation.create(campaign_id="zakatcamp-maal-000000001", amount=50000, ref="mitra-tak-ada")["donation_id"])
		self.assertEqual((d2.kampanye, d2.fund_type, d2.mitra), ("zakat-maal", "zakat", None))
		self.assertEqual(donation.by_public_id(donation.create(campaign_id="sedekah", amount=3000)["donation_id"]).donor_name, "Hamba Allah")

	def test_donasi_pembayaran_webhook_paid(self):
		self.new_donor()
		pid = self.make_donation(amount=25000)
		st = donation.status(pid)
		self.assertEqual(st["status"], "pending")
		with self.assertRaises(frappe.ValidationError):
			payment.create(pid, "metode-ngawur")
		frappe.set_user("Guest")  # pembayaran dari tamu juga boleh
		r = payment.create(pid, "qris")
		self.assertTrue(r["qrString"] and r["orderId"])
		self.assertEqual(payment.create(pid, "qris")["orderId"], r["orderId"])  # idempoten
		pay = donation.status(pid)["metadata"]
		self.assertTrue(pay["qrString"])
		payment.qr_png(pid)
		self.assertEqual(frappe.local.response.type, "download")
		self.assertTrue(frappe.local.response.filecontent.startswith(b"\x89PNG"))
		# webhook: tanpa kunci = ditolak
		args = dict(order_id=r["orderId"], status_code="200", gross_amount="25000.00", transaction_status="settlement")
		with self.assertRaises(frappe.PermissionError):
			payment.webhook(signature_key="x", **args)
		frappe.local.conf.midtrans_server_key = "SB-KUNCI-UJI"
		with self.assertRaises(frappe.PermissionError):
			payment.webhook(signature_key="salah", **args)
		sig = gateway.signature(args["order_id"], args["status_code"], args["gross_amount"], "SB-KUNCI-UJI")
		with self.assertRaises(frappe.ValidationError):
			payment.webhook(signature_key=gateway.signature(args["order_id"], "200", "99999.00", "SB-KUNCI-UJI"), **{**args, "gross_amount": "99999.00"})
		out = payment.webhook(signature_key=sig, **args)
		self.assertEqual(out["status"], "paid")
		self.assertEqual(payment.webhook(signature_key=sig, **args)["noop"], True)  # kirim ulang aman
		self.assertEqual(donation.status(pid)["status"], "paid")
		self.assertEqual(frappe.db.count("Doa Amin", {"donation": donation.by_public_id(pid).name}), 0)
		# pembayaran setelah paid ditolak
		with self.assertRaises(frappe.ValidationError):
			payment.create(pid, "qris")
		# statistik donor
		d = donation.by_public_id(pid)
		frappe.set_user(frappe.db.get_value("Donor", d.donor, "user"))
		self.assertEqual(donor.stats()["totalCount"], 1)
		self.assertEqual(donor.donations()[0]["status"], "paid")

	def test_webhook_memicu_jurnal_bila_gerbang_aktif(self):
		s = frappe.get_single("Pengaturan Donasi")
		s.posting_enabled, s.h_infak = 1, 0
		s.save()
		pid = self.make_donation(amount=40000)
		frappe.set_user("Guest")
		r = payment.create(pid, "qris")
		frappe.local.conf.midtrans_server_key = "K"
		a = dict(order_id=r["orderId"], status_code="200", gross_amount="40000.00", transaction_status="settlement")
		payment.webhook(signature_key=gateway.signature(a["order_id"], "200", a["gross_amount"], "K"), **a)
		d = donation.by_public_id(pid)
		self.assertTrue(d.je_receipt)
		self.assertEqual(frappe.db.count("Journal Entry", {"donation_ref": f"{d.name}:RECEIPT"}), 1)

	def test_simulate_paid_hanya_petugas(self):
		pid = self.make_donation()
		payment.create(pid, "qris")
		self.new_donor()
		with self.assertRaises(frappe.PermissionError):
			payment.simulate_paid(pid)
		frappe.set_user("Administrator")
		self.assertEqual(payment.simulate_paid(pid)["status"], "paid")

	# --- doa, amin, notifikasi ---
	def test_doa_amin_notifikasi(self):
		self.new_donor()
		pid = self.make_donation(message="Semoga berkah", amount=7000)
		self.pay(pid)
		owner_user = frappe.session.user
		self.assertEqual(doa.list_doa(take=5)[0]["message"], "Semoga berkah")
		self.assertTrue(doa.for_amin(limit=30))
		frappe.set_user("Guest")
		doa.amin(pid, 3)
		self.assertEqual(doa.amin(pid, 9)["ok"], True)  # sisa jatah 7 -> total 10
		self.assertTrue(doa.amin(pid, 1).get("capped"))
		self.assertEqual(frappe.db.get_value("Donation", {"gateway_order_id": pid}, "amin_count"), 10)
		frappe.set_user(owner_user)
		n = notification.list_notifications()
		self.assertEqual(n["unread"], 1)
		self.assertEqual(n["items"][0]["total_aminers"], 10)
		self.assertEqual(donor.my_doa()["doas"][0]["amin_count"], 10)
		notification.mark_read()
		self.assertEqual(notification.list_notifications()["unread"], 0)
		frappe.set_user("Guest")
		self.assertEqual(notification.list_notifications(), {"unread": 0, "items": []})
		with self.assertRaises(frappe.DoesNotExistError):
			doa.amin("id-ngawur", 1)

	# --- konten ---
	def test_kampanye(self):
		frappe.set_user("Guest")
		f = campaign.list_campaigns(limit=5)["campaigns"]
		self.assertEqual(len(f), 5)
		self.assertTrue(all(c["slug"] and "raised_amount" in c for c in f))
		self.assertNotIn("zakat-maal", [c["slug"] for c in campaign.list_campaigns(limit=500)["campaigns"]])  # kampanye sistem tak tampil
		d = campaign.detail(f[0]["slug"])
		self.assertTrue(d["title"] and "<script" not in d["description"])
		pid = self.make_donation(slug=f[0]["slug"], amount=9000)
		self.pay(pid)
		dn = campaign.donors(f[0]["slug"], limit=1)
		self.assertGreaterEqual(dn["total"], 1)
		self.assertEqual(campaign.list_campaigns(limit=500)["campaigns"][0]["raised_amount"] >= 0, True)
		self.assertIn("items", campaign.updates(f[0]["slug"]))
		with self.assertRaises(frappe.DoesNotExistError):
			campaign.detail("tidak-ada")

	def test_konten_publik(self):
		frappe.set_user("Guest")
		self.assertEqual(len(payment.methods()["methods"]), 8)
		self.assertTrue(payment.instructions("qris"))
		self.assertEqual(set(payment.snap_config()), {"clientKey", "isProduction"})
		self.assertNotIn("server", str(payment.snap_config()).lower())
		g = zakat.gold_price()
		self.assertGreater(g["pricePerGram"], 0)
		p = content.penyaluran_list(limit=5)
		self.assertEqual((len(p["items"]), p["total"]), (5, 24))
		self.assertTrue(content.penyaluran_list(sort="a-z")["items"])
		self.assertIn("categories", content.penyaluran_meta())
		self.assertEqual(content.laporan_list(), [])
		self.assertTrue(content.video_latest()["video"])
		self.assertEqual(len(content.video_list()), 12)
		self.assertFalse(content.popup_menu()["enabled"])
		a = content.artikel_list(limit=3)
		self.assertEqual((len(a["items"]), a["total"]), (3, 30))
		self.assertTrue(content.artikel_detail(a["items"][0]["slug"])["body"])
		self.assertTrue(content.wilayah(q="Bandung"))
		self.assertEqual(len(content.banners()), 5)
		self.assertEqual(len(content.quran_jar()), 6)
		self.assertEqual(len(content.mitra_list()), 22)
		self.assertTrue(content.mitra_detail(content.mitra_list()[0]["slug"])["name"])
		for slug in ("syarat-ketentuan", "kebijakan-privasi", "hapus-akun"):
			for lang in ("id", "en"):
				self.assertTrue(content.legal(slug, lang)["html"])
		self.assertEqual(auth.google_status(), {"enabled": False})
		self.assertNotIn("sedekah.id", content.legal("syarat-ketentuan", "id")["title"].lower())

	def test_survei(self):
		frappe.set_user("Guest")
		s = survey.get(donation="apa-saja", lang="id")
		self.assertTrue(s["enabled"] and len(s["scale"]) == 5)
		self.assertTrue(survey.submit(s["surveyId"], 4, "mantap", "apa-saja")["ok"])
		with self.assertRaises(frappe.ValidationError):
			survey.submit(s["surveyId"], 9)
		with self.assertRaises(frappe.DoesNotExistError):
			survey.submit("SRV-NGAWUR", 1)
		self.assertFalse(survey.get(lang="en")["enabled"])  # belum ada survei EN

	def test_baik_start_claim_release(self):
		frappe.set_user("Guest")
		ms = baik.missions()
		self.assertEqual(len(ms), 3)
		with self.assertRaises(frappe.AuthenticationError):
			baik.start(ms[0]["slug"])
		self.new_donor()
		slug = ms[0]["slug"]
		frappe.db.set_value("Misi Kebaikan", slug, {"min_duration_sec": 0, "target_count": 3})
		pool = frappe.db.get_value("Misi Kebaikan", slug, "sponsor_pool")
		before = frappe.db.get_value("Pool Sponsor Kebaikan", pool, "pool_available")
		s = baik.start(slug)
		self.assertLess(frappe.db.get_value("Pool Sponsor Kebaikan", pool, "pool_available"), before)  # reservasi
		with self.assertRaises(frappe.ValidationError):
			baik.start(slug)  # sudah berjalan
		with self.assertRaises(frappe.ValidationError):
			baik.claim(s["sessionId"], 1)  # target belum tercapai
		r = baik.claim(s["sessionId"], 3)
		self.assertTrue(r["voucherAmount"])
		with self.assertRaises(frappe.ValidationError):
			baik.claim(s["sessionId"], 3)  # tak bisa klaim dua kali
		self.assertEqual(frappe.db.count("Donation", {"baik_session": s["sessionId"]}), 0)  # tanpa Donation/jurnal (E18)
		s2 = baik.start(slug)
		baik.release(s2["sessionId"])
		self.assertEqual(frappe.db.get_value("Sesi Kebaikan", s2["sessionId"], "status"), "Dilepas")
		self.assertEqual(frappe.db.get_value("Pool Sponsor Kebaikan", pool, "pool_available"), before - frappe.db.get_value("Misi Kebaikan", slug, "voucher_amount"))
		# sesi orang lain tak bisa dilepas
		self.new_donor()
		with self.assertRaises(frappe.PermissionError):
			baik.release(s2["sessionId"])

	def test_gamifikasi_klaim(self):
		self.new_donor()
		g = gamification.get()
		self.assertEqual(g["points"], 0)
		self.assertEqual(g["level"]["currentName"], "Orang Baik")
		rw = frappe.get_all("Hadiah Gamifikasi", {"out_of_stock": 0}, ["name", "point_cost"], limit=1)[0]
		with self.assertRaises(frappe.ValidationError):
			gamification.claim_reward(rw.name, "A", "081", "Jl")  # klaim mati bawaan
		frappe.db.set_single_value("Pengaturan Gamifikasi", "claim_enabled", 1)
		with self.assertRaises(frappe.ValidationError):
			gamification.claim_reward(rw.name, "A", "081", "Jl")  # poin kurang
		self.pay(self.make_donation(amount=rw.point_cost + 1000))
		self.assertGreaterEqual(gamification.get()["points"], rw.point_cost)
		with self.assertRaises(frappe.ValidationError):
			gamification.claim_reward(rw.name, " ", "081", "Jl")
		self.assertTrue(gamification.claim_reward(rw.name, "Budi", "0812", "Jl. Mawar")["ok"])
		self.assertEqual(gamification.get()["points"], 1000)  # poin terpotong

	def test_rutin_jadwal_eksekusi_streak(self):
		self.new_donor()
		with self.assertRaises(frappe.ValidationError):
			recurring.create("daily", 7, 4000)
		with self.assertRaises(frappe.ValidationError):
			recurring.create("hourly", 7, 6000)
		s = recurring.create("daily", 7, 6000, method="qris", remind_wa=1)
		self.assertEqual(recurring.me()["schedules"][0]["id"], s["id"])
		e = recurring.execute(s["id"], prayerNote="doa rutin")
		self.assertEqual(recurring.execute(s["id"])["donation_id"], e["donation_id"])  # idempoten per tanggal
		d = donation.by_public_id(e["donation_id"])
		self.assertEqual((d.recurring_schedule, d.status, d.donation_type), (s["id"], "Pending", "recurring"))
		self.pay(e["donation_id"])
		self.assertEqual(recurring.streak()["streak"], 1)
		self.assertEqual(str(frappe.db.get_value("Jadwal Rutin", s["id"], "next_run")), add_days(nowdate(), 1))
		self.pay(e["donation_id"])
		self.assertEqual(recurring.streak()["streak"], 1)  # bayar ulang tidak menaikkan streak
		with self.assertRaises(frappe.ValidationError):
			recurring.execute_makeup(s["id"], nowdate())  # hanya tanggal lampau
		mk = recurring.execute_makeup(s["id"], add_days(nowdate(), -2))
		self.assertTrue(mk["donation_id"])
		self.assertEqual(recurring.set_state(s["id"], "pause")["status"], "Dijeda")
		with self.assertRaises(frappe.ValidationError):
			recurring.execute(s["id"])
		self.assertEqual(recurring.set_state(s["id"], "resume")["status"], "Aktif")
		self.assertTrue(recurring.update(s["id"], is_anonymous=1)["is_anonymous"])
		# scheduler: jadwal jatuh tempo membuat Donation pending sekali saja
		frappe.db.set_value("Jadwal Rutin", s["id"], "next_run", add_days(nowdate(), -5))
		before = frappe.db.count("Donation", {"recurring_schedule": s["id"]})
		recurring.run_due()
		recurring.run_due()
		self.assertEqual(frappe.db.count("Donation", {"recurring_schedule": s["id"]}), before + 1)
		self.assertEqual(frappe.db.count("Log Pengingat Rutin", {"schedule": s["id"]}) >= 1, True)
		recurring.set_state(s["id"], "cancel")
		self.assertEqual(recurring.me()["schedules"], [])
		# orang lain tak boleh
		self.new_donor()
		with self.assertRaises(frappe.PermissionError):
			recurring.execute(s["id"])

	def _jadwal_jatuh_tempo(self, wa=1, email=0, hour=0):
		self.new_donor()
		s = recurring.create(freq="daily", hour=hour, amount=10000, remind_wa=wa, remind_email=email)
		frappe.set_user("Administrator")
		frappe.db.set_value("Jadwal Rutin", s["id"], "next_run", add_days(nowdate(), -1))
		# isolasi: jadwal lain di site uji tidak ikut
		frappe.db.set_value("Jadwal Rutin", {"name": ["!=", s["id"]]}, "status", "Dijeda")
		frappe.db.set_single_value("Pengaturan Donasi", "wa_url", "https://wa.example.test/send")
		return s["id"]

	def test_pengingat_wa_terkirim_sekali_per_eksekusi(self):
		from unittest import mock

		sid = self._jadwal_jatuh_tempo()
		with mock.patch("requests.post", return_value=mock.Mock(status_code=200)) as m:
			recurring.run_due()
			recurring.run_due()  # jam berikutnya: eksekusi sudah ada, tidak kirim lagi
		self.assertEqual(m.call_count, 1)
		self.assertIn("/donasi/", m.call_args.kwargs["data"].decode())
		self.assertEqual(frappe.get_all("Log Pengingat Rutin", {"schedule": sid}, pluck="status"), ["Terkirim"])

	def test_pengingat_gateway_gagal_dicatat_dan_tidak_menghentikan(self):
		from unittest import mock

		sid = self._jadwal_jatuh_tempo()
		with mock.patch("requests.post", return_value=mock.Mock(status_code=500)):
			recurring.run_due()
		self.assertEqual(frappe.get_all("Log Pengingat Rutin", {"schedule": sid}, pluck="status"), ["Gagal"])
		self.assertEqual(frappe.db.count("Donation", {"recurring_schedule": sid}), 1)  # donasi tetap dibuat

	def test_pengingat_dilewati_bila_gateway_belum_diatur_atau_belum_jam(self):
		from unittest import mock

		sid = self._jadwal_jatuh_tempo()
		frappe.db.set_single_value("Pengaturan Donasi", "wa_url", "")
		with mock.patch("requests.post") as m:
			recurring.run_due()
		m.assert_not_called()
		self.assertEqual(frappe.get_all("Log Pengingat Rutin", {"schedule": sid}, pluck="status"), ["Dilewati"])
		# jadwal HARI INI dengan jam di masa depan: belum dieksekusi
		sid2 = self._jadwal_jatuh_tempo(hour=23)
		frappe.db.set_value("Jadwal Rutin", sid2, "next_run", nowdate())
		from unittest import mock as _m
		with _m.patch("frappe.utils.now_datetime", return_value=frappe.utils.get_datetime(nowdate() + " 08:00:00")):
			recurring.run_due()
		self.assertEqual(frappe.db.count("Donation", {"recurring_schedule": sid2}), 0)

	def test_import_snapshot_idempoten(self):
		before = {t: frappe.db.count(t) for t in ("Kampanye Donasi", "Mitra", "Penyaluran", "Artikel", "Wilayah", "Ayat Quran Jar", "Halaman Legal")}
		import_snapshot.run()
		self.assertEqual(before, {t: frappe.db.count(t) for t in before})
		self.assertEqual(before["Kampanye Donasi"], 63)
