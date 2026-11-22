"""Konten publik: penyaluran, laporan, video, popup menu, artikel, wilayah, legal, banner, Quran Jar."""
import json

import frappe

from donasionline.api._util import clean, feed_item

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
	return [{"id": r.name, "src": r.src, "poster": r.poster, "likes": r.likes, "comments": r.comments, "campaignSlug": frappe.db.get_value("Kampanye Donasi", r.kampanye, "slug") if r.kampanye else None, "caption": r.caption} for r in frappe.get_all("Video Donasi", ["*"], order_by="sort_order asc")]


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
	if not frappe.db.exists("Artikel", slug):
		frappe.throw("Artikel tidak ditemukan", frappe.DoesNotExistError)
	a = frappe.get_doc("Artikel", slug)
	return {"slug": a.slug, "title": a.title, "excerpt": a.excerpt, "image": a.image_url, "date": a.tanggal, "author": a.author, "body": clean(a.body_html), "related": [x for x in (a.related or "").split("\n") if x]}


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
	return {"title": d.title, "subtitle": d.subtitle, "updated": d.updated_label, "html": clean(d.body_html)}


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
