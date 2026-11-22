"""Utilitas bersama API platform (W6)."""
import hashlib
import re
import secrets

import frappe
from frappe import _
from frappe.utils.html_utils import clean_html

GENERAL_ID = "clt00testsedekah000001234"  # id kampanye umum yang dikirim UI (FAKTA: donate.js)
MIN_DONATION = 3000  # FAKTA: minimum server asli Rp3.000 (HANDOVER bag. 5)


def digits(p):
	return re.sub(r"\D", "", str(p or ""))


def norm_phone(p):
	"""Digit saja; 0xxxx -> 62xxxx. Panjang 9-15."""
	d = digits(p)
	if d.startswith("0"):
		d = "62" + d[1:]
	if not 9 <= len(d) <= 15:
		frappe.throw(_("Nomor telepon tidak valid"), frappe.ValidationError)
	return d


def clean(html):
	return clean_html(html or "")


def mask_name(name):
	out = []
	for w in str(name or "").split():
		out.append(w if len(w) <= 2 else w[0] + "*" * min(3, len(w) - 1))
	return " ".join(out) or "H***"


def new_public_id():
	return secrets.token_urlsafe(15)


def current_donor(required=True):
	user = frappe.session.user
	if user == "Guest":
		if required:
			frappe.throw(_("Silakan masuk"), frappe.AuthenticationError)
		return None
	name = frappe.db.get_value("Donor", {"user": user})
	if not name and required:
		frappe.throw(_("Akun donor tidak ditemukan"), frappe.PermissionError)
	return frappe.get_doc("Donor", name) if name else None


def login_as(user):
	lm = getattr(frappe.local, "login_manager", None)
	if lm:
		lm.login_as(user)
	else:  # pemanggilan langsung (tes)
		frappe.set_user(user)


def hash_code(phone, code):
	key = frappe.local.conf.get("encryption_key") or frappe.local.site
	return hashlib.sha256(f"{key}:{phone}:{code}".encode()).hexdigest()


def client_actor():
	ip = getattr(frappe.local, "request_ip", None) or "0.0.0.0"
	return "ip:" + hashlib.sha256(f"{ip}".encode()).hexdigest()[:16]


LEGACY_IDS = {  # id tetap kampanye sistem dari sedekah.id (FAKTA handover 03 bag. 9)
	"zakatcamp-penghasilan-01": "zakat-penghasilan", "zakatcamp-maal-000000001": "zakat-maal", "zakatcamp-emas-000000001": "zakat-emas",
	"zakatcamp-investasi-0001": "zakat-investasi", "zakatcamp-perniagaan-001": "zakat-perniagaan", "wakafcamp-umum-000000001": "wakaf-umum",
	"zakatcamp-fidyah-0000001": "fidyah",
}


def campaign_by_key(key):
	"""Terima kode kampanye atau slug; id umum UI dipetakan ke slug 'sedekah'."""
	if not key:
		key = "sedekah"
	if key == GENERAL_ID:
		key = "sedekah"
	key = LEGACY_IDS.get(key, key)
	name = frappe.db.get_value("Kampanye Donasi", key) or frappe.db.get_value("Kampanye Donasi", {"slug": key})
	return name


def raised(campaign):
	r = frappe.db.sql(
		"select coalesce(sum(amount),0) from `tabDonation` where kampanye=%s and status='Paid'", campaign
	)
	return float(r[0][0])


_BULAN = ["Jan", "Feb", "Mar", "Apr", "Mei", "Jun", "Jul", "Agu", "Sep", "Okt", "Nov", "Des"]


def date_label(d):
	"""'10 Sep 2026' (bentuk date_label yang dipakai UI)."""
	from frappe.utils import getdate

	if not d:
		return ""
	d = getdate(d)
	return f"{d.day} {_BULAN[d.month - 1]} {d.year}"


def feed_item(r):
	"""Bentuk item penyaluran untuk UI: id, slug, title, subtitle, date_label, image_url (+ field lain)."""
	r = dict(r)
	r["id"] = r.get("slug")
	r["image_url"] = r.get("image_url") or r.get("image")
	r["date_label"] = date_label(r.get("tanggal") or r.get("date"))
	return r
