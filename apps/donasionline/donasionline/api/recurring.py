"""/api/recurring/* (Shadaqa Rutin). Spec: docs di donasi-eco3/docs/superpowers/specs (engine UI: src/rutin.js). Minimum Rp5.000 (FAKTA UI)."""
import json
import re

import frappe
from frappe import _
from frappe.utils import add_days, add_months, getdate, nowdate

from donasionline.api._util import campaign_by_key, current_donor

MIN_AMOUNT = 3000  # = MIN_AMOUNT mesin UI (rutin.js) = minimal donasi
GRACE_DAYS = 7  # jendela genapi (rutin.js)


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
	return {"id": s.name, "freq": s.freq, "hour": s.hour, "amount": s.amount, "method": s.payment_method, "remind_wa": bool(s.remind_wa), "remind_email": bool(s.remind_email), "start_date": s.start_date, "next_run": s.next_run, "paused": s.status != "Aktif", "status": s.status, "streak": s.streak or 0, "is_anonymous": bool(s.is_anonymous), "prayer_note": s.prayer_note,
		"target": _target(s), "gen_from": s.gen_from, "paused_at": s.paused_at, "cancelled_at": s.cancelled_at, "pauses": _pauses(s.pauses), "created_at": getdate(s.creation),
		"executions": [{"date": e.target_date, "status": e.status, "is_makeup": bool(e.is_makeup), "donation": frappe.db.get_value("Donation", e.donation, "gateway_order_id") if e.donation else None} for e in s.executions]}


def _target(s):
	if not s.kampanye:
		return {"type": "pilihan"}
	slug, title = frappe.db.get_value("Kampanye Donasi", s.kampanye, ["slug", "title"])
	return {"type": "pilihan"} if slug == "sedekah" else {"type": "campaign", "slug": slug, "title": title}


def _pauses(raw):
	try:
		v = json.loads(raw or "[]")
		return v if isinstance(v, list) else []
	except ValueError:
		return []


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
		frappe.throw(_("Minimal Rp3.000"), frappe.ValidationError)
	if not 0 <= int(hour) <= 23:
		frappe.throw(_("Jam 0-23"), frappe.ValidationError)
	if remind_email and not d.email:
		frappe.throw(_("Pengingat email butuh alamat email"), frappe.ValidationError)
	if method and not frappe.db.exists("Metode Pembayaran", method):
		frappe.throw(_("Metode tidak dikenal"), frappe.ValidationError)
	start = getdate(start_date or nowdate())
	s = frappe.get_doc({"doctype": "Jadwal Rutin", "donor": d.name, "freq": freq, "hour": int(hour), "amount": int(amount), "payment_method": method, "remind_wa": int(bool(int(remind_wa))), "remind_email": int(bool(int(remind_email))), "start_date": start, "next_run": start, "status": "Aktif", "is_anonymous": int(bool(int(is_anonymous))), "prayer_note": prayer_note, "kampanye": frappe.db.get_value("Kampanye Donasi", {"slug": "sedekah"})}).insert(ignore_permissions=True)
	return _json(s)


ISO = re.compile(r"^\d{4}-\d{2}-\d{2}$")
STATUS_IN = {"ACTIVE": "Aktif", "PAUSED": "Dijeda", "CANCELLED": "Dibatalkan"}


def _iso(v, nullable=True):
	if v in (None, ""):
		if nullable:
			return None
		frappe.throw(_("Tanggal wajib"), frappe.ValidationError)
	if not (isinstance(v, str) and ISO.match(v)):
		frappe.throw(_("Format tanggal tidak valid"), frappe.ValidationError)
	return str(getdate(v))


@frappe.whitelist(methods=["POST"])
def save_schedule(data, id=None):
	"""Simpan jadwal bentuk mesin UI (rutin.js): frequency/startDate/hourLocal/amount/target/isAnonymous/reminders/status/pauses/genFrom.
	Server memvalidasi semua; id kosong/tak dikenal = buat baru (satu jadwal aktif per donor, sesuai UI)."""
	d = current_donor()
	x = json.loads(data) if isinstance(data, str) else data
	if not isinstance(x, dict):
		frappe.throw(_("Data tidak valid"), frappe.ValidationError)
	freq = {"DAILY": "daily", "WEEKLY": "weekly", "MONTHLY": "monthly"}.get(x.get("frequency"))
	status = STATUS_IN.get(x.get("status") or "ACTIVE")
	amount, hour = int(x.get("amount") or 0), int(x.get("hourLocal", 8))
	if not freq or not status:
		frappe.throw(_("Frekuensi/status tidak valid"), frappe.ValidationError)
	if amount < MIN_AMOUNT:
		frappe.throw(_("Minimal Rp3.000"), frappe.ValidationError)
	if not 0 <= hour <= 23:
		frappe.throw(_("Jam 0-23"), frappe.ValidationError)
	rem = x.get("reminders") or {}
	if rem.get("email") and not d.email:
		frappe.throw(_("Pengingat email butuh alamat email"), frappe.ValidationError)
	pauses = [{"from": _iso(p.get("from"), False), "to": _iso(p.get("to"), False)} for p in (x.get("pauses") or [])[:200]]
	tgt = x.get("target") or {}
	camp = (campaign_by_key(tgt.get("slug")) if tgt.get("type") == "campaign" else None) or frappe.db.get_value("Kampanye Donasi", {"slug": "sedekah"})
	start = _iso(x.get("startDate"), False)
	vals = {
		"freq": freq, "hour": hour, "amount": amount, "start_date": start, "status": status, "paused": 1 if status == "Dijeda" else 0,
		"remind_wa": int(bool(rem.get("wa"))), "remind_email": int(bool(rem.get("email"))), "is_anonymous": int(bool(x.get("isAnonymous"))),
		"kampanye": camp, "gen_from": _iso(x.get("genFrom")), "paused_at": _iso(x.get("pausedAt")), "cancelled_at": _iso(x.get("cancelledAt")),
		"pauses": json.dumps(pauses),
	}
	if id and frappe.db.exists("Jadwal Rutin", id):
		s = _mine(id)
		s.update(vals)
		if s.status == "Aktif" and (not s.next_run or getdate(s.next_run) < getdate(start)):
			s.next_run = start
		s.save(ignore_permissions=True)
	else:
		active = frappe.db.exists("Jadwal Rutin", {"donor": d.name, "status": ["!=", "Dibatalkan"]})
		if active and status != "Dibatalkan":
			frappe.throw(_("Anda sudah punya jadwal rutin"), frappe.ValidationError)
		s = frappe.get_doc({"doctype": "Jadwal Rutin", "donor": d.name, "next_run": start, **vals}).insert(ignore_permissions=True)
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
def execute(id, prayerNote=None, isAnonymousThisTime=None, targetDate=None):
	s = _mine(id)
	if s.status != "Aktif":
		frappe.throw(_("Jadwal tidak aktif"), frappe.ValidationError)
	makeup = False
	if targetDate:
		t, today = getdate(targetDate), getdate(nowdate())
		if t > today or (today - t).days > GRACE_DAYS:
			frappe.throw(_("Tanggal di luar jendela pembayaran"), frappe.ValidationError)
		makeup = t < today
	don = _spawn(s, targetDate or s.next_run or nowdate(), makeup, prayerNote, isAnonymousThisTime)
	return {"donation_id": frappe.db.get_value("Donation", don, "gateway_order_id")}


@frappe.whitelist(methods=["POST"])
def execute_makeup(id, targetDate):
	s = _mine(id)
	if getdate(targetDate) >= getdate(nowdate()):
		frappe.throw(_("Susulan hanya untuk tanggal terlewat"), frappe.ValidationError)
	if (getdate(nowdate()) - getdate(targetDate)).days > GRACE_DAYS:
		frappe.throw(_("Tanggal di luar jendela pembayaran"), frappe.ValidationError)
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
