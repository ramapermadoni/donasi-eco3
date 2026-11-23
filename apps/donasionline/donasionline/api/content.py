"""Konten publik: penyaluran, laporan, video, popup menu, artikel, wilayah, legal, banner, Quran Jar."""
import json

import frappe

from donasionline.api._util import clean, date_label, date_label_long, feed_item

SORTS = {"terbaru": "tanggal desc", "terlama": "tanggal asc", "a-z": "title asc", "z-a": "title desc"}


@frappe.whitelist(allow_guest=True)
def penyaluran_list(limit=5, offset=0, sort="terbaru", category=None, location=None, program=None):
	flt = {k: v for k, v in {"category": category, "location": location, "program": program}.items() if v and v != "Semua"}
	total = frappe.db.count("Penyaluran", flt)
	rows = frappe.get_all("Penyaluran", flt, ["slug", "title", "subtitle", "tanggal", "category", "image_url", "location", "program", "description"], order_by=SORTS.get(sort, SORTS["terbaru"]), limit=min(int(limit), 50), start=int(offset))
	rows = [feed_item({**r, "description": clean(r.get("description"))}) for r in rows]
	return {"items": rows, "total": total, "hasMore": int(offset) + len(rows) < total}


@frappe.whitelist(allow_guest=True)
def penyaluran_meta(locale="id"):
	g = lambda f: sorted(x for x in frappe.get_all("Penyaluran", pluck=f, distinct=True) if x)
	cats = g("category")
	return {"locations": g("location"), "programs": g("program"), "categories": cats, "categoryLabels": {c: c for c in cats}}


@frappe.whitelist(allow_guest=True)
def laporan_list():
	return [{"id": r.name, "judul": r.judul, "url_laporan": r.url_laporan, "url_donatur": r.url_donatur} for r in frappe.get_all("Laporan Donasi", ["name", "judul", "url_laporan", "url_donatur"], order_by="creation desc")]


@frappe.whitelist(allow_guest=True)
def video_latest():
	r = frappe.get_all("Video Donasi", {"is_latest": 1}, ["name", "src", "poster"], limit=1) or frappe.get_all("Video Donasi", ["name", "src", "poster"], order_by="sort_order asc", limit=1)
	return {"video": {"id": r[0].name, "videoUrl": r[0].src, "thumbnailUrl": r[0].poster} if r else None}


@frappe.whitelist(allow_guest=True)
def video_list():
	return [{"id": r.name, "src": r.src, "poster": r.poster, "likes": r.likes, "comments": r.comments, "campaignSlug": frappe.db.get_value("Kampanye Donasi", r.kampanye, "slug") if r.kampanye else None, "campaignTitle": (frappe.db.get_value("Kampanye Donasi", r.kampanye, "title") if r.kampanye else None), "caption": r.caption} for r in frappe.get_all("Video Donasi", ["*"], order_by="sort_order asc")]


@frappe.whitelist(allow_guest=True)
def popup_menu():
	s = frappe.get_single("Pengaturan Beranda")
	return {"enabled": bool(s.popup_enabled), "heading": s.popup_heading, "items": [{"id": i.name, "title": i.title, "link": i.link, "icon": i.icon} for i in s.popup_items]}


@frappe.whitelist(allow_guest=True)
def artikel_list(limit=12, offset=0):
	total = frappe.db.count("Artikel")
	rows = frappe.get_all("Artikel", fields=["slug", "title", "excerpt", "category", "image_url as image", "tanggal as date", "author"], order_by="tanggal desc", limit=min(int(limit), 50), start=int(offset))
	return {"total": total, "items": rows}


@frappe.whitelist(allow_guest=True)
def artikel_detail(slug):
	name = frappe.db.get_value("Artikel", {"slug": slug})
	if not name:
		frappe.throw("Artikel tidak ditemukan", frappe.DoesNotExistError)
	a = frappe.get_doc("Artikel", name)
	wanted = [x for x in (a.related or "").split("\n") if x]
	cols = ["slug", "title", "image_url as image"]
	rel = [r for r in (frappe.get_all("Artikel", {"slug": x}, cols, limit=1) for x in wanted) if r]
	rel = [r[0] for r in rel][:3] or frappe.get_all("Artikel", {"slug": ["!=", a.slug]}, cols, order_by="tanggal desc", limit=3)
	return {"slug": a.slug, "title": a.title, "excerpt": a.excerpt, "category": a.category, "image": a.image_url, "date": a.tanggal, "dateLabel": date_label_long(a.tanggal),
		"author": a.author, "body": clean(a.body_html), "related": wanted, "relatedItems": rel}


@frappe.whitelist(allow_guest=True)
def penyaluran_detail(slug):
	name = frappe.db.get_value("Penyaluran", {"slug": slug})
	if not name:
		frappe.throw("Penyaluran tidak ditemukan", frappe.DoesNotExistError)
	p = frappe.get_doc("Penyaluran", name)
	return {"slug": p.slug, "title": p.title, "subtitle": p.subtitle, "date": date_label(p.tanggal), "category": p.category, "image": p.image_url,
		"location": p.location, "program": p.program, "description": clean(p.description)}


@frappe.whitelist(allow_guest=True)
def wilayah(q=None, limit=20):
	flt = {"wilayah_name": ["like", f"%{q}%"]} if q else {}
	return frappe.get_all("Wilayah", flt, ["wilayah_name as name", "province"], order_by="wilayah_name asc", limit=min(int(limit), 100))


@frappe.whitelist(allow_guest=True)
def legal(slug, lang="id"):
	n = frappe.db.get_value("Halaman Legal", {"slug": slug, "lang": lang if lang in ("id", "en") else "id"})
	if not n:
		frappe.throw("Halaman tidak ditemukan", frappe.DoesNotExistError)
	d = frappe.get_doc("Halaman Legal", n)
	from donasionline.setup import legal as L

	s = frappe.get_single("Pengaturan Donasi")
	out = {"title": d.title, "subtitle": d.subtitle, "updated": d.updated_label, "html": L.render(clean(d.body_html), s)}
	if not s.legal_approved:
		out["note"] = (
			"<b>DRAF</b>: halaman ini belum ditinjau penasihat hukum/ahli syariah dan belum berlaku sebagai dokumen resmi."
			if lang != "en" else "<b>DRAFT</b>: this page has not been reviewed by legal counsel / sharia advisers and is not an official document yet."
		)
	return out


@frappe.whitelist(allow_guest=True)
def banners():
	return frappe.get_all("Banner", {"enabled": 1}, ["src", "href", "alt"], order_by="sort_order asc")


@frappe.whitelist(allow_guest=True)
def quran_jar():
	out = {}
	for r in frappe.get_all("Ayat Quran Jar", ["mood", "payload"]):
		out.setdefault(r.mood, []).append(json.loads(r.payload or "{}"))
	return out


@frappe.whitelist(allow_guest=True)
def mitra_list():
	return frappe.get_all("Mitra", fields=["slug", "mitra_name as name", "mitra_type as type", "avatar_url as img", "instagram as ig", "verified", "campaign_count as count", "total_raised"], order_by="mitra_name asc")


@frappe.whitelist(allow_guest=True)
def mitra_detail(slug):
	if not frappe.db.exists("Mitra", slug):
		frappe.throw("Mitra tidak ditemukan", frappe.DoesNotExistError)
	m = frappe.get_doc("Mitra", slug)
	return {"slug": m.slug, "name": m.mitra_name, "type": m.mitra_type, "img": m.avatar_url, "ig": m.instagram, "verified": bool(m.verified)}


def _kompak(v):
	"""Format ringkas seperti di UI: 'Rp 1.7 jt', 'Rp 535 rb', 'Rp 900'."""
	v = float(v or 0)
	if v >= 1_000_000:
		return f"Rp {v / 1_000_000:.1f} jt"
	if v >= 1_000:
		return f"Rp {round(v / 1_000)} rb"
	return f"Rp {int(v)}"


def _bundle():
	"""Konten halaman depan dalam bentuk yang dibaca UI (sama dengan berkas statis ui/src/data): banner, kampanye, mitra, video."""
	from donasionline.api._util import raised

	flt = {"is_active": 1, "is_system": 0, "status": ["!=", "draft"]}
	rows = frappe.get_all("Kampanye Donasi", flt, ["name", "slug", "title", "nama_kampanye", "image_url", "target_amount", "description", "organizer_name", "organizer_avatar", "is_featured", "featured_excerpt", "home_rank"], order_by="creation desc", limit=1000)
	rows.sort(key=lambda r: (r.home_rank is None, r.home_rank or 0))
	campaigns, details, featured = [], {}, {}
	for r in rows:
		got, target = raised(r.name), float(r.target_amount or 0)
		campaigns.append({"slug": r.slug, "image": r.image_url, "title": r.title or r.nama_kampanye, "raised": _kompak(got), "percent": int(got * 100 // target) if target else 0})
		details[r.slug] = {"target": int(target), "organizer": {"name": r.organizer_name, "avatar": r.organizer_avatar}, "description": clean(r.description) or ""}
		if r.is_featured and not featured:
			featured = {"slug": r.slug, "excerpt": r.featured_excerpt or "", "goal": _kompak(target)}
	banners = [{"href": b.href, "src": b.src, "alt": b.alt} for b in frappe.get_all("Banner", {"enabled": 1}, ["href", "src", "alt"], order_by="sort_order asc")]
	mitra = []
	for m in frappe.get_all("Mitra", ["slug", "mitra_name", "mitra_type", "avatar_url", "instagram", "campaign_count", "total_raised"], order_by="mitra_name asc"):
		mitra.append({"slug": m.slug, "name": m.mitra_name, "type": m.mitra_type, "img": m.avatar_url, "count": m.campaign_count or 0, "total": "Rp {:,.0f}".format(m.total_raised or 0).replace(",", "."), "ig": m.instagram, "campaigns": []})
	return {"banners": banners, "campaigns": campaigns, "details": details, "featured": featured, "totalCampaigns": len(campaigns), "mitra": mitra, "videos": video_list()}


@frappe.whitelist(allow_guest=True)
def bundle():
	"""replace=False selama konten contoh belum dibersihkan: UI tetap memakai berkas statis bawaan."""
	if not frappe.db.get_single_value("Pengaturan Donasi", "konten_contoh_dibersihkan"):
		return {"replace": False}
	return {"replace": True, **_bundle()}
