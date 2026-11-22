"""/api/campaigns/*"""
import frappe

from donasionline.api._util import campaign_by_key, clean, mask_name, raised

FIELDS = ["name", "slug", "title", "nama_kampanye", "image_url", "target_amount", "category", "is_featured", "home_rank", "is_system"]


def _row(r):
	return {
		"id": r.name, "slug": r.slug, "title": r.title or r.nama_kampanye, "image_url": r.image_url,
		"target_amount": r.target_amount or 0, "raised_amount": raised(r.name),
	}


@frappe.whitelist(allow_guest=True)
def list_campaigns(limit=200, offset=0, category=None):
	filters = {"is_active": 1, "is_system": 0, "status": ["!=", "draft"]}
	if category:
		filters["category"] = category
	rows = frappe.get_all("Kampanye Donasi", filters, FIELDS, order_by="creation desc", limit=1000)
	rows.sort(key=lambda r: (r.home_rank is None, r.home_rank or 0))
	rows = rows[int(offset): int(offset) + min(int(limit), 500)]
	return {"campaigns": [_row(r) for r in rows]}


@frappe.whitelist(allow_guest=True)
def detail(slug):
	name = campaign_by_key(slug)
	if not name:
		frappe.throw("Kampanye tidak ditemukan", frappe.DoesNotExistError)
	d = frappe.get_doc("Kampanye Donasi", name)
	mitra = frappe.db.get_value("Mitra", d.mitra, ["slug", "mitra_name", "mitra_type", "avatar_url", "verified"], as_dict=True) if d.mitra else None
	return {
		**_row(d), "description": clean(d.description), "organizer": {"name": d.organizer_name, "avatar": d.organizer_avatar},
		"category": d.category, "mitra": mitra, "title_en": d.title_en, "description_en": clean(d.description_en),
	}


@frappe.whitelist(allow_guest=True)
def donors(slug, offset=0, limit=20):
	name = campaign_by_key(slug)
	if not name:
		frappe.throw("Kampanye tidak ditemukan", frappe.DoesNotExistError)
	flt = {"kampanye": name, "status": "Paid"}
	total = frappe.db.count("Donation", flt)
	rows = frappe.get_all("Donation", flt, ["donor_name", "amount", "message", "is_anonymous", "paid_at"], order_by="paid_at desc", start=int(offset), limit=min(int(limit), 50))
	return {
		"donors": [
			{"donor_name": "Hamba Allah" if r.is_anonymous else r.donor_name, "amount": r.amount, "message": r.message, "is_anonymous": bool(r.is_anonymous), "paid_at": r.paid_at}
			for r in rows
		],
		"total": total, "hasMore": int(offset) + len(rows) < total,
	}


@frappe.whitelist(allow_guest=True)
def updates(slug):
	"""Kabar terbaru = Penyaluran yang diikat ke kampanye."""
	name = campaign_by_key(slug)
	rows = frappe.get_all("Penyaluran", {"kampanye": name}, ["slug", "title", "subtitle", "tanggal", "image_url"], order_by="tanggal desc", limit=50) if name else []
	return {"items": rows}
