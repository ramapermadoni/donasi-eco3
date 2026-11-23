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

	def test_wakaf_dua_mode_berjalan_bersamaan(self):
		wk = frappe.db.get_value("Kampanye Donasi", {"fund_type": "wakaf", "is_active": 1})
		self.assertTrue(wk)
		ps = frappe.get_single("Pengaturan Donasi")

		def lembaga(terdaftar, no=""):
			ps.update({"nazhir_terdaftar": terdaftar, "nazhir_no_bwi": no})
			ps.flags.ignore_mandatory = True
			ps.save(ignore_permissions=True)
			frappe.clear_cache(doctype="Pengaturan Donasi")

		def coba(slug):
			return donation.create(campaign_id=slug, amount=10000, donor_name="Tes")["donation_id"]

		# kampanye kedua (titipan), kampanye pertama tetap dikelola lembaga
		tp = frappe.get_doc({"doctype": "Kampanye Donasi", "kode_kampanye": "WK-TITIPAN-UJI", "nama_kampanye": "Wakaf Titipan Uji", "slug": "wakaf-titipan-uji", "fund_type": "wakaf",
			"wakaf_mode": "Titipan ke nazhir mitra", "program": frappe.db.get_value("Kampanye Donasi", wk, "program"), "is_active": 1, "status": "active"}).insert(ignore_permissions=True)
		frappe.db.set_value("Kampanye Donasi", wk, "wakaf_mode", "Dikelola lembaga")

		lembaga(0)  # lembaga belum nazhir, mitra belum ada: dua-duanya ditolak
		for k in (wk, tp.name):
			with self.assertRaises(frappe.ValidationError):
				coba(k)
		lembaga(1)  # centang tanpa nomor: tetap ditolak
		with self.assertRaises(frappe.ValidationError):
			coba(wk)
		lembaga(1, "W.1/TES")  # lembaga nazhir -> dikelola buka; titipan tetap tertutup (tanpa mitra)
		self.assertTrue(coba(wk))
		with self.assertRaises(frappe.ValidationError):
			coba(tp.name)
		mt = frappe.get_doc({"doctype": "Mitra", "slug": "mitra-nazhir-uji", "mitra_name": "Mitra Nazhir Uji", "mitra_type": "nazhir", "nazhir_no_bwi": "N.9/TES"}).insert(ignore_permissions=True)
		frappe.db.set_value("Kampanye Donasi", tp.name, "mitra", mt.name)
		self.assertTrue(coba(tp.name))  # titipan buka lewat mitra
		lembaga(0)  # lembaga dicabut: titipan tetap jalan, dikelola tertutup
		self.assertTrue(coba(tp.name))
		with self.assertRaises(frappe.ValidationError):
			coba(wk)

	def test_penerusan_wakaf_ke_nazhir(self):
		from donasionline.donasi_online.doctype.penerusan_wakaf.penerusan_wakaf import saldo_titipan
		from donasionline.donasi_online.report.saldo_titipan_wakaf.saldo_titipan_wakaf import execute as laporan

		wk = frappe.db.get_value("Kampanye Donasi", {"fund_type": "wakaf", "is_active": 1})
		# donasi wakaf Paid 100.000 (gerbang dibuka: mitra bernazhir terikat)
		mt = frappe.get_doc({"doctype": "Mitra", "slug": "mitra-nazhir-pw", "mitra_name": "Nazhir PW", "mitra_type": "nazhir", "nazhir_no_bwi": "N.1/TES"}).insert(ignore_permissions=True)
		frappe.db.set_value("Kampanye Donasi", wk, {"mitra": mt.name, "wakaf_mode": "Titipan ke nazhir mitra"})
		base = saldo_titipan(wk)
		pid = donation.create(campaign_id=wk, amount=100000, donor_name="Tes")["donation_id"]
		self.pay(pid)
		self.assertEqual(saldo_titipan(wk), base + 100000)

		def baru(jumlah, ref="TRF-1", **kw):
			return frappe.get_doc({"doctype": "Penerusan Wakaf", "kampanye": wk, "tanggal": nowdate(), "jumlah": jumlah, "referensi_transfer": ref, **kw})

		with self.assertRaises(frappe.ValidationError):
			baru(0).insert(ignore_permissions=True)
		with self.assertRaises(frappe.ValidationError):  # melebihi saldo
			baru(base + 100001).insert(ignore_permissions=True)
		with self.assertRaises(frappe.ValidationError):  # bukan wakaf
			frappe.get_doc({"doctype": "Penerusan Wakaf", "kampanye": "sedekah", "tanggal": nowdate(), "jumlah": 1000}).insert(ignore_permissions=True)
		d1 = baru(60000, ref="").insert(ignore_permissions=True)
		self.assertEqual((d1.mitra, d1.nazhir_no_bwi), (mt.name, "N.1/TES"))
		with self.assertRaises(frappe.ValidationError):  # referensi wajib saat Submit
			d1.submit()
		d1.reload()
		self.assertEqual(d1.docstatus, 0)
		d1.referensi_transfer = "TRF-001"
		d1.save(ignore_permissions=True)
		d1.submit()
		self.assertEqual(saldo_titipan(wk), base + 40000)
		with self.assertRaises(frappe.ValidationError):  # sisa 40.000 + base; melebihi
			baru(base + 40001).insert(ignore_permissions=True)
		_, rows = laporan({})
		r = next(x for x in rows if x["kampanye"] == wk)
		self.assertEqual((r["diteruskan"] >= 60000, r["sisa"]), (True, base + 40000))
		d1.cancel()  # pembatalan mengembalikan saldo
		self.assertEqual(saldo_titipan(wk), base + 100000)
		# mitra tanpa nomor BWI: ditolak
		frappe.db.set_value("Mitra", mt.name, "nazhir_no_bwi", "")
		with self.assertRaises(frappe.ValidationError):
			baru(1000).insert(ignore_permissions=True)

	def test_wakaf_status_publik(self):
		wk = frappe.db.get_value("Kampanye Donasi", {"fund_type": "wakaf", "is_active": 1})
		frappe.set_user("Guest")
		self.assertEqual(campaign.wakaf_status("sedekah"), {"wakaf": False})
		r = campaign.wakaf_status(wk)
		self.assertEqual((r["wakaf"], r["mode"], r["open"], r["nazhir"]), (True, "titipan", False, None))  # belum ada nazhir: tertutup
		frappe.set_user("Administrator")
		mt = frappe.get_doc({"doctype": "Mitra", "slug": "mitra-nazhir-pub", "mitra_name": "Nazhir Publik", "mitra_type": "nazhir", "nazhir_no_bwi": "N.7/TES"}).insert(ignore_permissions=True)
		frappe.db.set_value("Kampanye Donasi", wk, "mitra", mt.name)
		self.pay(donation.create(campaign_id=wk, amount=50000, donor_name="Tes")["donation_id"])
		pw = frappe.get_doc({"doctype": "Penerusan Wakaf", "kampanye": wk, "tanggal": nowdate(), "jumlah": 20000, "referensi_transfer": "RAHASIA-123", "catatan": "internal"}).insert(ignore_permissions=True)
		pw.submit()
		frappe.set_user("Guest")
		r = campaign.wakaf_status(wk)
		self.assertTrue(r["open"])
		self.assertEqual(r["nazhir"], {"name": "Nazhir Publik", "noBwi": "N.7/TES"})
		self.assertEqual(r["received"] - r["forwarded"], r["remaining"])
		self.assertEqual(r["forwards"][0]["amount"], 20000)
		self.assertNotIn("RAHASIA-123", str(r))  # bukti/referensi transfer tidak bocor
		self.assertNotIn("internal", str(r))

	def test_konten_contoh_tandai_bersihkan_dan_bundle(self):
		from donasionline.setup import konten_contoh

		ps = frappe.get_single("Pengaturan Donasi")
		ps.konten_contoh_dibersihkan = 0
		ps.flags.ignore_mandatory = True
		ps.save(ignore_permissions=True)
		frappe.clear_cache(doctype="Pengaturan Donasi")
		# impor snapshot menandai contoh; sistem & milik sendiri tidak
		sistem_n = frappe.db.count("Kampanye Donasi", {"is_system": 1})
		self.assertEqual(frappe.db.count("Kampanye Donasi", {"is_system": 1, "is_sample": 1}), 0)
		konten_contoh.lindungi()
		for slug in konten_contoh.RESERVED:  # kampanye inti tidak pernah contoh
			if frappe.db.exists("Kampanye Donasi", slug):
				self.assertEqual(frappe.db.get_value("Kampanye Donasi", slug, "is_sample"), 0, slug)
		self.assertTrue(frappe.db.count("Kampanye Donasi", {"is_sample": 1}))
		self.assertEqual(content.bundle(), {"replace": False})  # belum dibersihkan: UI tetap statis
		milik = frappe.get_doc({"doctype": "Kampanye Donasi", "kode_kampanye": "MILIK-1", "nama_kampanye": "Kampanye Milik Sendiri", "slug": "milik-sendiri", "fund_type": "infak_bebas",
			"program": frappe.db.get_value("Kampanye Donasi", {"is_system": 1}, "program"), "target_amount": 2000000, "status": "aktif", "is_active": 1, "is_sample": 0}).insert(ignore_permissions=True)
		# satu kampanye contoh sudah menerima donasi -> tidak boleh dihapus
		ber = frappe.db.get_value("Kampanye Donasi", {"is_sample": 1, "is_active": 1, "status": ["!=", "draft"]})
		self.pay(donation.create(campaign_id=ber, amount=10000, donor_name="Tes")["donation_id"])
		sim = konten_contoh.bersihkan(dry_run=1)  # simulasi: tidak mengubah apa pun
		self.assertTrue(sim["dry_run"] and ber in sim["dinonaktifkan"])
		self.assertTrue(frappe.db.exists("Kampanye Donasi", ber))
		self.assertEqual(content.bundle(), {"replace": False})
		konten_contoh.bersihkan(dry_run=0, commit=0)  # tes tidak boleh meng-commit
		self.assertEqual(frappe.db.count("Kampanye Donasi", {"is_sample": 1, "is_active": 1}), 0)
		self.assertTrue(frappe.db.exists("Kampanye Donasi", ber))  # catatan keuangan terjaga (nonaktif)
		self.assertEqual(frappe.db.get_value("Kampanye Donasi", ber, "is_active"), 0)
		self.assertTrue(frappe.db.exists("Kampanye Donasi", milik.name))  # milik sendiri utuh
		self.assertEqual(frappe.db.get_value("Kampanye Donasi", "sedekah", "is_active"), 1)  # kampanye umum tetap aktif
		self.assertEqual(frappe.db.count("Kampanye Donasi", {"is_system": 1}), sistem_n)
		for dt in ("Penyaluran", "Artikel", "Video Donasi", "Banner"):
			self.assertEqual(frappe.db.count(dt, {"is_sample": 1}), 0, dt)
		frappe.clear_cache(doctype="Pengaturan Donasi")
		b = content.bundle()
		self.assertTrue(b["replace"])
		self.assertEqual(sorted(c["slug"] for c in b["campaigns"]), ["milik-sendiri", "sedekah"])  # milik sendiri + kampanye umum yang dilindungi
		self.assertEqual(b["totalCampaigns"], 2)
		self.assertEqual(set(b["campaigns"][0]), {"slug", "image", "title", "raised", "percent"})
		self.assertEqual(set(b["details"]["milik-sendiri"]), {"target", "organizer", "description"})
		self.assertEqual((b["banners"], b["videos"]), ([], []))
		# impor ulang tidak membuat contoh lagi (make() dilewati; JANGAN memanggil run(): ia commit dan akan meng-commit pembersihan ini)
		self.assertFalse(import_snapshot.make("Kampanye Donasi", "contoh-baru-xyz", {"kode_kampanye": "contoh-baru-xyz", "nama_kampanye": "X", "slug": "contoh-baru-xyz", "fund_type": "infak_bebas", "program": milik.program}))
		self.assertFalse(frappe.db.exists("Kampanye Donasi", "contoh-baru-xyz"))

	def test_detail_konten_server(self):
		pn = frappe.get_all("Penyaluran", ["slug", "title"], limit=1)[0]
		d = content.penyaluran_detail(pn.slug)
		self.assertEqual(d["slug"], pn.slug)
		self.assertTrue({"title", "date", "image", "location", "program", "category", "description"} <= set(d))
		with self.assertRaises(frappe.DoesNotExistError):
			content.penyaluran_detail("tidak-ada-xyz")
		ar = frappe.get_all("Artikel", ["slug"], limit=1)[0]
		a = content.artikel_detail(ar.slug)
		self.assertTrue({"title", "image", "dateLabel", "author", "body", "related", "relatedItems"} <= set(a))
		self.assertRegex(a["dateLabel"], r"^\d{1,2} [A-Z][a-z]+ \d{4}$")
		self.assertTrue(a["relatedItems"] and all({"slug", "title", "image"} <= set(r) for r in a["relatedItems"]))
		self.assertNotIn(ar.slug, [r["slug"] for r in a["relatedItems"]])
		with self.assertRaises(frappe.DoesNotExistError):
			content.artikel_detail("tidak-ada-xyz")
		# kabar kampanye: bentuk sama dengan data statis UI
		pw = frappe.get_all("Penyaluran", {"kampanye": ["is", "set"]}, ["kampanye"], limit=1)
		if pw:
			slug = frappe.db.get_value("Kampanye Donasi", pw[0].kampanye, "slug")
			it = campaign.updates(slug)["items"][0]
			self.assertTrue({"id", "title", "subtitle", "date_label", "image_url"} <= set(it))

	def test_terkumpul_kampanye_live_dari_donasi_paid(self):
		slug = "sedekah"
		sebelum = campaign.detail(slug)["raised_amount"]
		pid = self.make_donation(slug=slug, amount=25000)
		self.assertEqual(campaign.detail(slug)["raised_amount"], sebelum)  # Pending belum dihitung
		self.pay(pid)
		self.assertEqual(campaign.detail(slug)["raised_amount"], sebelum + 25000)  # angka persis, bukan ringkasan teks

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

	def test_hapus_akun_kosongkan_doa_jadwal_dan_pengamin(self):
		import json

		self.new_donor()
		pid = self.make_donation(message="Doa saya, hubungi 0812xxxx", amount=7000)
		self.pay(pid)
		dname = frappe.db.get_value("Donation", {"gateway_order_id": pid}, "name")
		owner = frappe.session.user
		frappe.set_user("Guest")
		doa.amin(pid, 2)
		frappe.set_user(owner)
		today = nowdate()
		sch = {"frequency": "DAILY", "startDate": today, "hourLocal": 8, "amount": 3000, "target": {"type": "campaign", "slug": "sedekah"},
			"isAnonymous": False, "reminders": {"bell": True, "wa": True, "email": False}, "status": "ACTIVE", "pauses": [], "genFrom": today}
		sid = recurring.save_schedule(json.dumps(sch))["id"]
		auth.delete_account("HAPUS")
		self.assertIsNone(frappe.db.get_value("Donation", dname, "message"))
		self.assertEqual(frappe.db.get_value("Donation", dname, "amount"), 7000)  # catatan keuangan tetap
		self.assertEqual(frappe.db.get_value("Jadwal Rutin", sid, "status"), "Dibatalkan")
		self.assertTrue(frappe.db.get_value("Jadwal Rutin", sid, "cancelled_at"))
		self.assertEqual(frappe.db.count("Doa Amin", {"donation": dname, "actor_name": ["is", "set"]}), 0)

	def test_avatar(self):
		import io
		from types import SimpleNamespace

		self.new_donor()
		preset = "/avatars/a01.webp"
		self.assertEqual(auth.set_avatar(preset=preset)["avatarUrl"], preset)
		for bad in ("https://evil.example/x.webp", "/avatars/a18.webp", "/avatars/../x.webp", "javascript:alert(1)", "", None):
			with self.assertRaises(frappe.ValidationError):
				auth.set_avatar(preset=bad)

		def kirim(data):
			frappe.local.request = SimpleNamespace(files={"file": SimpleNamespace(stream=io.BytesIO(data))}, host="uji.localhost", headers={})

		try:
			kirim(b"MZ\x90\x00 bukan gambar")
			with self.assertRaises(frappe.ValidationError):
				auth.set_avatar()
			kirim(b"\x89PNG\r\n\x1a\n" + b"0" * (2 * 1024 * 1024))
			with self.assertRaises(frappe.ValidationError):  # >2 MB
				auth.set_avatar()
			kirim(b"RIFF\x10\x00\x00\x00WEBPVP8 " + b"0" * 8)
			url = auth.set_avatar()["avatarUrl"]
			self.assertRegex(url, r"^/files/avatar-[\w-]+\.webp$")
			self.assertEqual(frappe.db.get_value("Donor", {"user": frappe.session.user}, "avatar_url"), url)
			self.assertTrue(frappe.db.exists("File", {"file_url": url}))
			frappe.local.request.files = {}
			auth.set_avatar(preset=preset)  # ganti: berkas lama ikut dihapus
			self.assertFalse(frappe.db.exists("File", {"file_url": url}))
		finally:
			frappe.local.request = None

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
		self.assertNotIn("Tes Donor", str(doa.list_doa(take=5)))  # nama lengkap tidak keluar di API publik
		self.assertIn("T**", doa.list_doa(take=5)[0]["donor_name"])
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
			recurring.create("daily", 7, 2999)
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

	def test_rutin_save_schedule_sinkron_ui(self):
		import json

		self.new_donor()
		today = nowdate()
		sch = {"frequency": "DAILY", "startDate": today, "hourLocal": 8, "amount": 3000, "target": {"type": "campaign", "slug": "zakatcamp-maal-000000001"},
			"isAnonymous": True, "reminders": {"bell": True, "wa": True, "email": False}, "status": "ACTIVE", "pauses": [], "genFrom": today}
		r = recurring.save_schedule(json.dumps(sch))
		self.assertEqual((r["freq"], r["amount"], r["status"], r["target"]["type"]), ("daily", 3000, "Aktif", "campaign"))
		self.assertEqual(r["target"]["slug"], "zakat-maal")
		with self.assertRaises(frappe.ValidationError):
			recurring.save_schedule(json.dumps(sch))  # jadwal kedua ditolak
		# jeda lalu lanjut dengan riwayat; ubah nominal
		p = recurring.save_schedule(json.dumps({**sch, "status": "PAUSED", "pausedAt": today}), id=r["id"])
		self.assertEqual((p["status"], str(p["paused_at"])), ("Dijeda", today))
		u = recurring.save_schedule(json.dumps({**sch, "amount": 7000, "pauses": [{"from": today, "to": today}]}), id=r["id"])
		self.assertEqual((u["status"], u["amount"], len(u["pauses"])), ("Aktif", 7000, 1))
		for bad in ({**sch, "amount": 2999}, {**sch, "frequency": "YEARLY"}, {**sch, "hourLocal": 24}, {**sch, "startDate": "bukan-tanggal"}, {**sch, "pauses": [{"from": "x", "to": today}]}):
			with self.assertRaises(frappe.ValidationError):
				recurring.save_schedule(json.dumps(bad), id=r["id"])
		# donatur lain tidak boleh mengubah
		self.new_donor()
		with self.assertRaises(frappe.PermissionError):
			recurring.save_schedule(json.dumps(sch), id=r["id"])
		# bayar tanggal tertentu: hari ini bukan susulan, kemarin susulan, di luar jendela / masa depan ditolak
		frappe.set_user("Administrator")
		self.new_donor()
		n = recurring.save_schedule(json.dumps({**sch, "startDate": add_days(today, -20), "genFrom": add_days(today, -20)}))
		e1 = recurring.execute(n["id"], targetDate=today)
		e2 = recurring.execute(n["id"], targetDate=add_days(today, -2))
		self.assertNotEqual(e1["donation_id"], e2["donation_id"])
		for bad_t in (add_days(today, 1), add_days(today, -8)):
			with self.assertRaises(frappe.ValidationError):
				recurring.execute(n["id"], targetDate=bad_t)
		ex = {str(x["date"]): x["is_makeup"] for x in recurring.me()["schedules"][0]["executions"]}
		self.assertEqual(ex, {today: False, add_days(today, -2): True})
		self.pay(e2["donation_id"])
		paid = [x for x in recurring.me()["schedules"][0]["executions"] if x["status"] == "Dibayar"]
		self.assertEqual([(str(x["date"]), x["is_makeup"]) for x in paid], [(add_days(today, -2), True)])

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

	def test_legal_placeholder_draf_dan_setujui(self):
		s = frappe.get_single("Pengaturan Donasi")
		s.org_name, s.org_email, s.legal_approved = "Lembaga <Uji>", "kontak@uji.example", 0
		s.save(ignore_permissions=True)
		r = content.legal("kebijakan-privasi", "id")
		self.assertIn("DRAF", r["note"])
		self.assertIn("Lembaga &lt;Uji&gt;", r["html"] + content.legal("syarat-ketentuan", "id")["html"])  # di-escape
		self.assertIn("kontak@uji.example", r["html"])
		self.assertNotIn("DT Peduli", r["html"])
		self.assertNotIn("dtp.id", r["html"])
		self.assertIn("[alamat belum diisi]", content.legal("hapus-akun", "id")["html"] + "[alamat belum diisi]")
		s.legal_approved = 1
		s.save(ignore_permissions=True)
		self.assertNotIn("note", content.legal("kebijakan-privasi", "en"))

	def test_import_snapshot_idempoten(self):
		before = {t: frappe.db.count(t) for t in ("Kampanye Donasi", "Mitra", "Penyaluran", "Artikel", "Wilayah", "Ayat Quran Jar", "Halaman Legal")}
		import_snapshot.run()
		self.assertEqual(before, {t: frappe.db.count(t) for t in before})
		self.assertEqual(before["Kampanye Donasi"], 63)
