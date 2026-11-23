"""/api/donations (buat) dan /api/donasi/:id (status). id publik = gateway_order_id acak (sulit ditebak), bukan nama DON-xxxxx."""
import re

import frappe
from frappe import _
from frappe.rate_limiter import rate_limit
from frappe.utils import add_to_date, now_datetime

from donasionline.api._util import MIN_DONATION, campaign_by_key, new_public_id, norm_phone

REF_RE = re.compile(r"^[a-z0-9-]{3,30}$")


def by_public_id(pid):
	name = frappe.db.get_value("Donation", {"gateway_order_id": pid})
	if not name:
		frappe.throw(_("Donasi tidak ditemukan"), frappe.DoesNotExistError)
	return frappe.get_doc("Donation", name)


def _wakaf_dibuka(c):
	"""Gerbang F4, per kampanye. Dikelola lembaga: lembaga terdaftar nazhir BWI (centang + nomor).
	Titipan: kampanye terikat ke Mitra bernomor nazhir BWI. Kedua mode dapat berjalan bersamaan pada kampanye berbeda."""
	if not (c.wakaf_mode or "").startswith("Dikelola"):  # kosong/tak dikenal = Titipan (mode operasi saat ini)
		return bool(c.mitra and (frappe.db.get_value("Mitra", c.mitra, "nazhir_no_bwi") or "").strip())
	s = frappe.get_cached_doc("Pengaturan Donasi")
	return bool(s.nazhir_terdaftar and (s.nazhir_no_bwi or "").strip())


@frappe.whitelist(allow_guest=True, methods=["POST"])
@rate_limit(limit=20, seconds=60)
def create(campaign_id=None, amount=None, donor_name=None, donor_phone=None, is_anonymous=0, message=None, ref=None, currency="IDR",
	type="one_time", utm_source=None, utm_medium=None, utm_campaign=None, utm_content=None, utm_term=None, event_slug=None, **_ignored):
	if currency != "IDR":
		frappe.throw(_("Hanya IDR"), frappe.ValidationError)
	amount = int(float(amount or 0))
	if amount < MIN_DONATION:
		frappe.throw(_("Minimal donasi Rp{0}").format(f"{MIN_DONATION:,}".replace(",", ".")), frappe.ValidationError)
	camp = campaign_by_key(campaign_id)
	if not camp:
		frappe.throw(_("Kampanye tidak ditemukan"), frappe.DoesNotExistError)
	c = frappe.get_doc("Kampanye Donasi", camp)
	if not c.is_active or c.status == "draft":
		frappe.throw(_("Kampanye tidak aktif"), frappe.ValidationError)
	if c.fund_type == "wakaf" and not _wakaf_dibuka(c):
		frappe.throw(_("Wakaf belum dibuka: belum ada nazhir terdaftar yang menerimanya."), frappe.ValidationError)
	mitra = None
	if ref and REF_RE.match(ref):
		mitra = frappe.db.get_value("Mitra", {"slug": ref})  # abaikan bila tak dikenal (aturan handover 04 bag. 2)
	lim = lambda v: (v or None) and str(v)[:100]
	donor = frappe.db.get_value("Donor", {"user": frappe.session.user}) if frappe.session.user != "Guest" else None
	doc = frappe.get_doc(
		{
			"doctype": "Donation", "gateway_order_id": new_public_id(), "status": "Pending", "donor": donor,
			"donor_name": (donor_name or "").strip()[:140] or "Hamba Allah", "donor_phone": norm_phone(donor_phone) if donor_phone else None,
			"is_anonymous": 1 if str(is_anonymous).lower() in ("1", "true") else 0, "message": (message or "").strip()[:500] or None,
			"fund_type": c.fund_type, "program": c.program, "kampanye": c.name, "campaign_title": c.title or c.nama_kampanye,
			"amount": amount, "currency": "IDR", "idr_equivalent": amount, "donation_type": "one_time" if type != "recurring" else "recurring",
			"mitra": mitra, "ref": ref if mitra else None, "utm_source": lim(utm_source), "utm_medium": lim(utm_medium), "utm_campaign": lim(utm_campaign),
			"utm_content": lim(utm_content), "utm_term": lim(utm_term), "event_slug": lim(event_slug),
			"referrer_captured_at": now_datetime() if mitra or utm_source else None,
			"expired_at": add_to_date(now_datetime(), hours=24),
		}
	)
	doc.insert(ignore_permissions=True)
	return {"donation_id": doc.gateway_order_id}


def _poll_midtrans(d, p):
	"""Tanya Midtrans paling sering 1x/10 detik per donasi."""
	key = f"mt_poll:{d.name}"
	if frappe.cache.get_value(key):
		return
	frappe.cache.set_value(key, 1, expires_in_sec=10)
	from donasionline import gateway
	from donasionline.api.payment import _apply_status

	res = gateway.fetch_status(p.order_id)
	if res and res[0]:
		_apply_status(frappe.get_doc("Permintaan Pembayaran", p.name), res[0], res[1])
		frappe.db.commit()


@frappe.whitelist(allow_guest=True)
def status(id):
	d = by_public_id(id)
	pr = frappe.get_all("Permintaan Pembayaran", {"donation": d.name}, ["*"], order_by="creation desc", limit=1)
	if d.status == "Pending" and pr and pr[0].gateway == "midtrans" and pr[0].status == "pending":
		_poll_midtrans(d, pr[0])  # cadangan webhook (mis. dev lokal tanpa URL publik)
		d.reload()
		pr = frappe.get_all("Permintaan Pembayaran", {"donation": d.name}, ["*"], order_by="creation desc", limit=1)
	if d.status == "Pending" and d.expired_at and d.expired_at < now_datetime():
		frappe.db.set_value("Donation", d.name, "status", "Expired")
		frappe.db.commit()  # GET tidak otomatis commit
		d.status = "Expired"
	meta = {}
	if pr:
		p = pr[0]
		meta = {
			"payment_method": p.payment_method, "payment_type": p.payment_type, "qrString": p.qr_string, "qr_code_url": p.qr_code_url,
			"va_numbers": [{"bank": p.va_bank, "va_number": p.va_number}] if p.va_number else [], "vaNumber": p.va_number,
			"redirect_url": p.redirect_url, "snap_token": p.snap_token,
		}
	return {
		"id": d.gateway_order_id, "status": (d.status or "").lower(), "amount": d.amount, "expired_at": d.expired_at,
		"donor_name": d.donor_name, "is_anonymous": bool(d.is_anonymous), "campaign": {"title": d.campaign_title, "slug": frappe.db.get_value("Kampanye Donasi", d.kampanye, "slug")},
		"metadata": meta,
	}
