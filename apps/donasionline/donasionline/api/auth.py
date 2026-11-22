"""Auth/OTP/donor. Mengganti /api/auth/*. FAKTA: bentuk dari auth.js; ASUMSI: aturan server (OTP 6 digit, 5 menit, 5 percobaan)."""
import secrets

import frappe
from frappe import _
from frappe.rate_limiter import rate_limit
from frappe.utils import add_to_date, now_datetime, today

from donasionline.api._util import current_donor, hash_code, login_as, norm_phone

OTP_TTL_MIN = 5
OTP_MAX_ATTEMPTS = 5


def _send_otp(phone):
	code = f"{secrets.randbelow(10**6):06d}"
	doc = frappe.get_doc(
		{
			"doctype": "Permintaan OTP",
			"phone": phone,
			"purpose": "login",
			"code_hash": hash_code(phone, code),
			"expires_at": add_to_date(now_datetime(), minutes=OTP_TTL_MIN),
		}
	).insert(ignore_permissions=True)
	from donasionline import notify

	notify.send_otp(phone, code)
	return code if frappe.local.conf.get("donasionline_otp_dev_echo") else None


def _csrf():
	return frappe.sessions.get_csrf_token()


def _user_json(d):
	return {"id": d.name, "name": d.full_name, "phone": d.phone, "email": d.email, "avatarUrl": d.avatar_url}


@frappe.whitelist(allow_guest=True)
def me():
	d = current_donor(required=False)
	return {"user": _user_json(d) if d else None, "csrf_token": _csrf() if d else None}


@frappe.whitelist(allow_guest=True, methods=["POST"])
@rate_limit(limit=5, seconds=600)
def request_otp(phone):
	p = norm_phone(phone)
	code = _send_otp(p)
	out = {"ok": True, "phone": p}
	if code:
		out["dev_code"] = code
	return out


@frappe.whitelist(allow_guest=True, methods=["POST"])
@rate_limit(limit=10, seconds=600)
def verify_otp(phone, code):
	p = norm_phone(phone)
	row = frappe.get_all(
		"Permintaan OTP",
		{"phone": p, "used": 0, "expires_at": [">", now_datetime()]},
		["name", "code_hash", "attempts"],
		order_by="creation desc",
		limit=1,
	)
	if not row:
		frappe.throw(_("Kode salah atau kedaluwarsa"), frappe.ValidationError)
	r = row[0]
	if r.attempts >= OTP_MAX_ATTEMPTS:
		frappe.throw(_("Terlalu banyak percobaan. Minta kode baru."), frappe.ValidationError)
	if not secrets.compare_digest(r.code_hash, hash_code(p, str(code))):
		frappe.db.set_value("Permintaan OTP", r.name, "attempts", r.attempts + 1)
		frappe.db.commit()
		frappe.throw(_("Kode salah atau kedaluwarsa"), frappe.ValidationError)
	frappe.db.set_value("Permintaan OTP", r.name, "used", 1)
	donor = frappe.db.get_value("Donor", {"phone": p})
	if not donor:
		return {"ok": True, "needs_register": True, "phone": p}
	d = frappe.get_doc("Donor", donor)
	login_as(d.user)
	return {"ok": True, "user": _user_json(d), "csrf_token": _csrf()}


@frappe.whitelist(allow_guest=True, methods=["POST"])
@rate_limit(limit=5, seconds=600)
def register_donor(name, phone, email=None, birthdate=None, city=None, job=None, goal=None, source=None):
	p = norm_phone(phone)
	name = (name or "").strip()
	if len(name) < 2:
		frappe.throw(_("Nama minimal 2 huruf"), frappe.ValidationError)
	if frappe.db.exists("Donor", {"phone": p}):
		frappe.throw(_("Nomor sudah terdaftar. Silakan masuk."), frappe.ValidationError)
	mail = (email or "").strip() or f"{p}@donor.invalid"
	user = frappe.get_doc(
		{"doctype": "User", "email": mail, "first_name": name, "user_type": "Website User", "send_welcome_email": 0, "enabled": 1}
	).insert(ignore_permissions=True)
	frappe.get_doc(
		{
			"doctype": "Donor", "user": user.name, "full_name": name, "phone": p, "email": (email or None),
			"birthdate": birthdate or None, "city": city, "job": job, "goal": goal, "source": source, "donor_since": today(),
		}
	).insert(ignore_permissions=True)
	code = _send_otp(p)
	out = {"ok": True, "phone": p}
	if code:
		out["dev_code"] = code
	return out


@frappe.whitelist(methods=["POST"])
def logout():
	lm = getattr(frappe.local, "login_manager", None)
	if lm:
		lm.logout()
	else:
		frappe.set_user("Guest")
	return {"ok": True}


@frappe.whitelist(methods=["POST"])
def delete_account(confirm=None):
	"""Anonimkan donor + nonaktifkan user; donasi (catatan keuangan) tetap, tanpa PII. Konfirmasi ganda 'HAPUS'."""
	d = current_donor()
	if confirm != "HAPUS":
		frappe.throw(_("Ketik HAPUS untuk konfirmasi"), frappe.ValidationError)
	frappe.db.sql("update `tabDonation` set donor=NULL, donor_name='Hamba Allah', donor_phone=NULL where donor=%s", d.name)
	user = d.user
	d.update({"full_name": "Akun dihapus", "phone": f"del-{d.name}", "email": None, "avatar_url": None, "birthdate": None, "city": None, "job": None, "goal": None, "source": None, "user": None})
	d.save(ignore_permissions=True)
	frappe.db.set_value("User", user, "enabled", 0)
	frappe.set_user("Guest")
	return {"ok": True}


@frappe.whitelist(allow_guest=True)
def google_status():
	return {"enabled": False}
