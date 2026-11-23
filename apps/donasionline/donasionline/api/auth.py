"""Auth/OTP/donor. Mengganti /api/auth/*. FAKTA: bentuk dari auth.js; ASUMSI: aturan server (OTP 6 digit, 5 menit, 5 percobaan)."""
import re
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
	# donasi: lepas dari donor, kosongkan nama/telepon dan ucapan doa (bisa memuat data pribadi)
	own = frappe.get_all("Donation", {"donor": d.name}, pluck="name")
	frappe.db.sql("update `tabDonation` set donor=NULL, donor_name='Hamba Allah', donor_phone=NULL, message=NULL where donor=%s", d.name)
	# nama pengamin pada doa-doa itu, dan amin yang pernah diberikan akun ini
	for dn in own:
		frappe.db.set_value("Doa Amin", {"donation": dn}, "actor_name", None)
	frappe.db.sql("update `tabDoa Amin` set actor_name=NULL where actor=%s", d.name)
	# jadwal rutin: hentikan permanen (tidak ada pengingat/penagihan lagi)
	for sch in frappe.get_all("Jadwal Rutin", {"donor": d.name, "status": ["!=", "Dibatalkan"]}, pluck="name"):
		s = frappe.get_doc("Jadwal Rutin", sch)
		s.status, s.paused, s.cancelled_at, s.prayer_note = "Dibatalkan", 0, frappe.utils.today(), None
		s.save(ignore_permissions=True)
	_hapus_file_avatar(d.avatar_url)
	user = d.user
	d.update({"full_name": "Akun dihapus", "phone": f"del-{d.name}", "email": None, "avatar_url": None, "birthdate": None, "city": None, "job": None, "goal": None, "source": None, "user": None})
	d.save(ignore_permissions=True)
	frappe.db.set_value("User", user, "enabled", 0)
	frappe.set_user("Guest")
	return {"ok": True}


PRESET_RE = re.compile(r"^/avatars/a(0[1-9]|1[0-7])\.webp$")  # salinan lokal di ui/public/avatars
AVATAR_MAX = 2 * 1024 * 1024
AVATAR_TYPES = {b"\xff\xd8\xff": "jpg", b"\x89PNG": "png"}


def _hapus_file_avatar(url):
	"""Hapus berkas avatar unggahan lama (hanya yang kita simpan sendiri: /files/avatar-...)."""
	if url and url.startswith("/files/avatar-"):
		fn = frappe.db.get_value("File", {"file_url": url})
		if fn:
			frappe.delete_doc("File", fn, ignore_permissions=True, force=True)


def _sniff(data):
	"""Jenis gambar dari isi berkas (bukan dari nama/header kiriman)."""
	for sig, ext in AVATAR_TYPES.items():
		if data.startswith(sig):
			return ext
	if data[:4] == b"RIFF" and data[8:12] == b"WEBP":
		return "webp"
	return None


@frappe.whitelist(methods=["POST"])
def set_avatar(preset=None):
	"""Ganti foto profil: `preset` (URL bawaan yang diizinkan) atau berkas unggahan `file` (JPG/PNG/WebP, maks 2 MB)."""
	d = current_donor()
	f = frappe.request.files.get("file") if getattr(frappe, "request", None) else None
	if f:
		data = f.stream.read(AVATAR_MAX + 1)
		if len(data) > AVATAR_MAX:
			frappe.throw(_("Ukuran foto maksimal 2 MB"), frappe.ValidationError)
		ext = _sniff(data)
		if not ext:
			frappe.throw(_("Format foto harus JPG, PNG, atau WebP"), frappe.ValidationError)
		name = f"avatar-{secrets.token_urlsafe(12)}.{ext}"
		doc = frappe.get_doc({"doctype": "File", "file_name": name, "content": data, "is_private": 0}).insert(ignore_permissions=True)
		url = doc.file_url
	elif preset and PRESET_RE.match(preset):
		url = preset
	else:
		frappe.throw(_("Foto tidak valid"), frappe.ValidationError)
	old = d.avatar_url
	d.avatar_url = url
	d.save(ignore_permissions=True)
	if old != url:
		_hapus_file_avatar(old)
	return {"ok": True, "avatarUrl": url}


@frappe.whitelist(allow_guest=True)
def google_status():
	return {"enabled": False}
