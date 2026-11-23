"""/api/recurring/* (Shadaqa Rutin). Spec: docs di donasi-eco3/docs/superpowers/specs (engine UI: src/rutin.js). Minimum Rp5.000 (FAKTA UI)."""
import frappe
from frappe import _
from frappe.utils import add_days, add_months, getdate, nowdate

from donasionline.api._util import current_donor

MIN_AMOUNT = 5000


def _next(d, freq):
	d = getdate(d)
	return add_days(d, 1) if freq == "daily" else add_days(d, 7) if freq == "weekly" else add_months(d, 1)


def _mine(sid):
	donor = current_donor()
	s = frappe.get_doc("Jadwal Rutin", sid)
	if s.donor != donor.name:
		frappe.throw(_("Bukan jadwal Anda"), frappe.PermissionError)
	return s


def _json(s):
	return {"id": s.name, "freq": s.freq, "hour": s.hour, "amount": s.amount, "method": s.payment_method, "remind_wa": bool(s.remind_wa), "remind_email": bool(s.remind_email), "start_date": s.start_date, "next_run": s.next_run, "paused": s.status != "Aktif", "status": s.status, "streak": s.streak or 0, "is_anonymous": bool(s.is_anonymous), "prayer_note": s.prayer_note}


@frappe.whitelist()
def me():
	d = current_donor()
	rows = frappe.get_all("Jadwal Rutin", {"donor": d.name, "status": ["!=", "Dibatalkan"]}, pluck="name")
	return {"schedules": [_json(frappe.get_doc("Jadwal Rutin", n)) for n in rows]}


@frappe.whitelist(methods=["POST"])
def create(freq, hour, amount, method=None, remind_wa=0, remind_email=0, start_date=None, is_anonymous=0, prayer_note=None):
	d = current_donor()
	if freq not in ("daily", "weekly", "monthly"):
		frappe.throw(_("Frekuensi tidak valid"), frappe.ValidationError)
	if int(amount) < MIN_AMOUNT:
		frappe.throw(_("Minimal Rp5.000"), frappe.ValidationError)
	if not 0 <= int(hour) <= 23:
		frappe.throw(_("Jam 0-23"), frappe.ValidationError)
	if remind_email and not d.email:
		frappe.throw(_("Pengingat email butuh alamat email"), frappe.ValidationError)
	if method and not frappe.db.exists("Metode Pembayaran", method):
		frappe.throw(_("Metode tidak dikenal"), frappe.ValidationError)
	start = getdate(start_date or nowdate())
	s = frappe.get_doc({"doctype": "Jadwal Rutin", "donor": d.name, "freq": freq, "hour": int(hour), "amount": int(amount), "payment_method": method, "remind_wa": int(bool(int(remind_wa))), "remind_email": int(bool(int(remind_email))), "start_date": start, "next_run": start, "status": "Aktif", "is_anonymous": int(bool(int(is_anonymous))), "prayer_note": prayer_note, "kampanye": frappe.db.get_value("Kampanye Donasi", {"slug": "sedekah"})}).insert(ignore_permissions=True)
	return _json(s)


@frappe.whitelist()
def streak():
	d = current_donor()
	rows = frappe.get_all("Jadwal Rutin", {"donor": d.name, "status": ["!=", "Dibatalkan"]}, ["name", "streak"])
	return {"streak": max([r.streak or 0 for r in rows] or [0])}


def _spawn(s, target_date, makeup=False, note=None, anon=None):
	"""Buat Donation Pending untuk satu eksekusi; idempoten per (jadwal, tanggal)."""
	target = getdate(target_date)
	for e in s.executions:
		if getdate(e.target_date) == target:
			return e.donation
	camp = s.kampanye or frappe.db.get_value("Kampanye Donasi", {"slug": "sedekah"})
	from donasionline.api.donation import create as dcreate
	donor = frappe.get_doc("Donor", s.donor)
	r = dcreate(campaign_id=camp, amount=s.amount, donor_name=donor.full_name, donor_phone=donor.phone, is_anonymous=int(anon if anon is not None else s.is_anonymous), message=note or s.prayer_note, type="recurring")
	don = frappe.db.get_value("Donation", {"gateway_order_id": r["donation_id"]})
	frappe.db.set_value("Donation", don, "recurring_schedule", s.name)
	s.append("executions", {"target_date": target, "is_makeup": int(makeup), "donation": don, "status": "Dibuat"})
	s.save(ignore_permissions=True)
	return don


@frappe.whitelist(methods=["POST"])
def execute(id, prayerNote=None, isAnonymousThisTime=None):
	s = _mine(id)
	if s.status != "Aktif":
		frappe.throw(_("Jadwal tidak aktif"), frappe.ValidationError)
	don = _spawn(s, s.next_run or nowdate(), False, prayerNote, isAnonymousThisTime)
	return {"donation_id": frappe.db.get_value("Donation", don, "gateway_order_id")}


@frappe.whitelist(methods=["POST"])
def execute_makeup(id, targetDate):
	s = _mine(id)
	if getdate(targetDate) >= getdate(nowdate()):
		frappe.throw(_("Susulan hanya untuk tanggal terlewat"), frappe.ValidationError)
	don = _spawn(s, targetDate, True)
	return {"donation_id": frappe.db.get_value("Donation", don, "gateway_order_id")}


@frappe.whitelist(methods=["POST"])
def set_state(id, action):
	s = _mine(id)
	new = {"pause": "Dijeda", "resume": "Aktif", "cancel": "Dibatalkan"}.get(action)
	if not new or s.status == "Dibatalkan":
		frappe.throw(_("Aksi tidak valid"), frappe.ValidationError)
	s.status = new
	s.paused = 1 if new == "Dijeda" else 0
	s.save(ignore_permissions=True)
	return _json(s)


@frappe.whitelist(methods=["POST", "PATCH"])
def update(id, is_anonymous=None):
	s = _mine(id)
	if is_anonymous is not None:
		s.is_anonymous = int(bool(int(is_anonymous)))
	s.save(ignore_permissions=True)
	return _json(s)


def on_donation_paid(doc, method=None):
	"""Streak naik saat donasi jadwal dibayar; majukan next_run (dipanggil dari mark_paid)."""
	if not doc.recurring_schedule:
		return
	s = frappe.get_doc("Jadwal Rutin", doc.recurring_schedule)
	for e in s.executions:
		if e.donation == doc.name and e.status != "Dibayar":
			e.status = "Dibayar"
			s.streak = (s.streak or 0) + 1
			s.next_run = _next(e.target_date, s.freq)
	s.save(ignore_permissions=True)


def _reminder_text(s, donation):
	donor = frappe.get_doc("Donor", s.donor)
	oid = frappe.db.get_value("Donation", donation, "gateway_order_id")
	url = f"{frappe.utils.get_url()}/donasi/{oid}"
	nominal = f"Rp{int(s.amount):,}".replace(",", ".")
	return f"Assalamu'alaikum {donor.full_name}, waktunya shadaqa rutin {nominal}. Selesaikan di: {url}"


def run_due():
	"""Scheduler per jam: buat Donation Pending bagi jadwal jatuh tempo (jam jadwal sudah lewat) dan kirim pengingat SEKALI per eksekusi baru.
	Kegagalan satu jadwal/kanal dicatat di Log Pengingat Rutin dan tidak menghentikan yang lain."""
	from frappe.utils import now_datetime

	from donasionline import notify

	now = now_datetime()
	today = getdate(now)
	for name in frappe.get_all("Jadwal Rutin", {"status": "Aktif", "next_run": ["<=", today]}, pluck="name"):
		s = frappe.get_doc("Jadwal Rutin", name)
		if getdate(s.next_run) == today and (s.hour or 0) > now.hour:
			continue  # belum jam-nya
		before = len(s.executions)
		try:
			don = _spawn(s, s.next_run)
		except Exception:
			frappe.log_error(title=f"Jadwal Rutin {name}: gagal membuat donasi")
			continue
		if len(s.executions) == before:
			continue  # eksekusi sudah ada: pengingat sudah pernah dikirim
		for ch, on in (("wa", s.remind_wa), ("email", s.remind_email)):
			if not on:
				continue
			try:
				ok = notify.send_reminder(s.donor, _reminder_text(s, don), ch)
				status = "Terkirim" if ok else "Dilewati"
			except Exception as e:
				frappe.logger("donasionline").error("Pengingat %s jadwal %s gagal: %s", ch, name, type(e).__name__)
				status = "Gagal"
			frappe.get_doc({"doctype": "Log Pengingat Rutin", "schedule": s.name, "channel": ch, "sent_at": now, "status": status}).insert(ignore_permissions=True)
		frappe.db.commit()


def purge_logs():
	"""Retensi (usulan W0): Reminder Log 24 bulan, OTP 90 hari."""
	from frappe.utils import add_months, add_days, nowdate
	frappe.db.delete("Log Pengingat Rutin", {"creation": ["<", add_months(nowdate(), -24)]})
	frappe.db.delete("Permintaan OTP", {"creation": ["<", add_days(nowdate(), -90)]})
