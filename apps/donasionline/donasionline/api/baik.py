"""/api/baik/* (Jalan Kebaikan). Klaim memakai voucher pool sponsor.
Akuntansi voucher/pool (E18) DIBLOKIR sampai F22: klaim TIDAK membuat Donation maupun jurnal."""
import frappe
from frappe import _
from frappe.rate_limiter import rate_limit
from frappe.utils import add_to_date, now_datetime

from donasionline.api._util import current_donor


def _expire(donor=None):
	frappe.db.sql("update `tabSesi Kebaikan` set status='Kedaluwarsa' where status='Aktif' and reserved_until < %s", now_datetime())


@frappe.whitelist(methods=["POST"])
@rate_limit(limit=30, seconds=60)
def start(missionSlug):
	donor = current_donor()
	_expire()
	if not frappe.db.exists("Misi Kebaikan", missionSlug):
		frappe.throw(_("Misi tidak ditemukan"), frappe.DoesNotExistError)
	m = frappe.get_doc("Misi Kebaikan", missionSlug)
	if not m.enabled:
		frappe.throw(_("Misi nonaktif"), frappe.ValidationError)
	if frappe.db.exists("Sesi Kebaikan", {"mission": m.name, "donor": donor.name, "status": "Aktif"}):
		frappe.throw(_("Misi sedang berjalan"), frappe.ValidationError)
	# reservasi voucher dari pool (atomik: kurangi saldo hanya bila cukup)
	if m.sponsor_pool and m.voucher_amount:
		n = frappe.db.sql("update `tabPool Sponsor Kebaikan` set pool_available = pool_available - %s where name=%s and pool_available >= %s", (m.voucher_amount, m.sponsor_pool, m.voucher_amount))
		if not frappe.db.sql("select row_count()")[0][0]:
			frappe.throw(_("Pool voucher habis"), frappe.ValidationError)
	now = now_datetime()
	max_s = m.max_duration_sec or 600
	s = frappe.get_doc({"doctype": "Sesi Kebaikan", "mission": m.name, "donor": donor.name, "started_at": now, "reserved_until": add_to_date(now, seconds=max_s), "status": "Aktif", "voucher_amount": m.voucher_amount, "pool": m.sponsor_pool}).insert(ignore_permissions=True)
	return {"sessionId": s.name, "serverNow": now, "startedAt": now, "reservedUntil": s.reserved_until, "maxDurationSec": max_s, "minDurationSec": m.min_duration_sec}


def _own(session):
	donor = current_donor()
	s = frappe.get_doc("Sesi Kebaikan", session)
	if s.donor != donor.name:
		frappe.throw(_("Sesi bukan milik Anda"), frappe.PermissionError)
	return s


def _refund(s):
	if s.pool and s.voucher_amount:
		frappe.db.sql("update `tabPool Sponsor Kebaikan` set pool_available = pool_available + %s where name=%s", (s.voucher_amount, s.pool))


@frappe.whitelist(methods=["POST"])
def claim(sessionId, count=1):
	s = _own(sessionId)
	if s.status != "Aktif":
		frappe.throw(_("Sesi tidak aktif"), frappe.ValidationError)
	m = frappe.get_doc("Misi Kebaikan", s.mission)
	now = now_datetime()
	if s.reserved_until < now:
		frappe.db.set_value("Sesi Kebaikan", s.name, "status", "Kedaluwarsa")
		_refund(s)
		return {"code": "EXPIRED", "error": "Sesi kedaluwarsa"}
	if m.mission_type == "TAP_COUNTER" and int(count) < (m.target_count or 1):
		frappe.throw(_("Target belum tercapai"), frappe.ValidationError)
	if m.min_duration_sec and (now - s.started_at).total_seconds() < m.min_duration_sec:
		frappe.throw(_("Terlalu cepat"), frappe.ValidationError)
	frappe.db.set_value("Sesi Kebaikan", s.name, "status", "Diklaim")
	pool = frappe.get_doc("Pool Sponsor Kebaikan", s.pool) if s.pool else None
	return {"voucherAmount": s.voucher_amount, "campaignTitle": frappe.db.get_value("Kampanye Donasi", m.kampanye, "title") if m.kampanye else None, "sponsorName": (pool.sponsor_name if pool else None) or "Hamba Allah"}


@frappe.whitelist(methods=["POST"])
def release(sessionId):
	s = _own(sessionId)
	if s.status == "Aktif":
		frappe.db.set_value("Sesi Kebaikan", s.name, "status", "Dilepas")
		_refund(s)
	return {"ok": True}


@frappe.whitelist(allow_guest=True)
def missions():
	out = []
	for m in frappe.get_all("Misi Kebaikan", {"enabled": 1}, ["*"]):
		left = None
		if m.sponsor_pool and m.voucher_amount:
			left = int(frappe.db.get_value("Pool Sponsor Kebaikan", m.sponsor_pool, "pool_available") // m.voucher_amount)
		out.append({"slug": m.slug, "type": m.mission_type, "title": m.title, "icon": m.icon, "instruction": m.instruction, "meaning": m.meaning, "dzikirName": m.dzikir_name, "arabicText": m.arabic_text, "latinText": m.latin_text, "targetCount": m.target_count, "targetDurationSec": m.target_duration_sec, "voucherAmount": m.voucher_amount, "voucherLeft": left})
	return out
