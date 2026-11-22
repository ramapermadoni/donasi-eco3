"""Impor snapshot konten UI (docs W6). Idempoten (lewati yang sudah ada). TIDAK mengimpor doa.json/teman.json (teks pengguna nyata) dan qurban.js (karangan).

Pakai: bench --site <site> execute donasionline.setup.import_snapshot.run
Catatan: gambar/video tetap URL hotlink (sedekah.id) sampai pemilik mengizinkan unduh ke File Frappe (risiko handover 06).
"""
import json
import os
import re
from datetime import datetime

import frappe

SNAP = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "snapshot")
BULAN = {"jan": 1, "feb": 2, "mar": 3, "apr": 4, "mei": 5, "jun": 6, "jul": 7, "agu": 8, "agt": 8, "sep": 9, "okt": 10, "nov": 11, "des": 12}
BRAND = re.compile(r"(?<![/.\w-])[Ss]edekah\.id")


def load(name):
	with open(os.path.join(SNAP, name), encoding="utf-8") as f:
		return json.load(f)


def brand(s):
	return BRAND.sub("donasi", s) if isinstance(s, str) else s


def parse_date(s):
	if not s:
		return None
	m = re.match(r"(\d{4})-(\d{2})-(\d{2})", s)
	if m:
		return f"{m[1]}-{m[2]}-{m[3]}"
	m = re.match(r"(\d{1,2})\s+([A-Za-z]+)\s+(\d{4})", s)
	if m and m[2][:3].lower() in BULAN:
		return f"{m[3]}-{BULAN[m[2][:3].lower()]:02d}-{int(m[1]):02d}"
	return None


def make(doctype, key, data):
	"""Sisipkan bila belum ada. key = filter unik."""
	if frappe.db.exists(doctype, key):
		return False
	frappe.get_doc({"doctype": doctype, **data}).insert(ignore_permissions=True, ignore_if_duplicate=True)
	return True


def fund_type_of(slug):
	if "zakat" in slug or slug == "fidyah":
		return "zakat" if "zakat" in slug else "fidyah"
	if "wakaf" in slug:
		return "wakaf"
	if "qurban" in slug:
		return "qurban"
	return "infak_bebas"  # PROVISIONAL: pengelola harus menetapkan infak_terikat per kampanye (F, E7)


def campaigns(program):
	d = load("sedekah.json")
	en = load("campaigns-en.json")
	kabar = load("kabar.json")
	pilihan = ["peduli-banjir-aceh", "bantu-pakpandi-bertahan", "petani-ubi-cilembu", "tpq-al-ihsan-bogor", "tebar-10000-mushaf", "dukung-mimpi-yaziz", "rtq-lubuk-linggau", "bantu-khalisa-sembuh", "bantu-gilang-sembuh"]
	n = 0
	for c in d["campaigns"]:
		s = c["slug"]
		det = d["details"].get(s, {})
		feat = d["featured"] if d["featured"]["slug"] == s else None
		ok = make("Kampanye Donasi", s, {
			"kode_kampanye": s, "nama_kampanye": c["title"], "slug": s, "title": c["title"], "image_url": c["image"], "fund_type": fund_type_of(s), "program": program,
			"target_amount": det.get("target"), "description": brand(det.get("description")), "organizer_name": (det.get("organizer") or {}).get("name"),
			"organizer_avatar": (det.get("organizer") or {}).get("avatar"), "is_featured": 1 if feat else 0, "featured_excerpt": feat["excerpt"] if feat else None,
			"home_rank": pilihan.index(s) + 1 if s in pilihan else None, "status": "aktif", "is_active": 1, "title_en": (en.get(s) or {}).get("title"),
		})
		n += ok
	# kampanye umum + sistem (tak tampil di daftar)
	sysc = [("sedekah", "Sedekah", "infak_bebas", ""), ("zakat-penghasilan", "Zakat Penghasilan", "zakat", "zakat"), ("zakat-maal", "Zakat Maal", "zakat", "zakat"), ("zakat-emas", "Zakat Emas & Perak", "zakat", "zakat"),
		("zakat-investasi", "Zakat Investasi", "zakat", "zakat"), ("zakat-perniagaan", "Zakat Perniagaan", "zakat", "zakat"), ("wakaf-umum", "Wakaf Umum", "wakaf", "wakaf"), ("fidyah", "Fidyah", "fidyah", "fidyah")]
	for slug, title, ft, kind in sysc:
		n += make("Kampanye Donasi", slug, {"kode_kampanye": slug, "nama_kampanye": title, "slug": slug, "title": title, "fund_type": ft, "program": program, "is_system": 1, "system_kind": kind, "status": "aktif", "is_active": 1})
	return n


def run():
	frappe.flags.in_import = True
	co = frappe.get_single("Pengaturan Donasi").company
	program = frappe.db.get_value("Cost Center", {"company": co, "cost_center_name": "Umum"})
	cnt = {}
	cnt["Mitra"] = sum(make("Mitra", m["slug"], {"slug": m["slug"], "mitra_name": m["name"], "mitra_type": m["type"], "avatar_url": m.get("img"), "instagram": m.get("ig"), "verified": 1}) for m in load("mitra.json"))
	cnt["Kampanye Donasi"] = campaigns(program)
	inst = load("instruksi.json")
	pm = 0
	for i, m in enumerate(load("payment.json")):
		t = {"qris": "qris", "virtual_account": "virtual_account", "ewallet": "ewallet"}.get(m["type"], "virtual_account")
		steps = inst.get(m["code"]) or (inst.get("mandiri_va") if m["code"] == "other_va" else [])
		pm += make("Metode Pembayaran", m["code"], {"code": m["code"], "method_name": m["name"], "method_type": t, "fee_flat": m["feeFlat"], "fee_percent": m["feePercent"], "min_amount": max(m["minAmount"], 3000), "max_amount": m["maxAmount"], "icon_url": m.get("iconUrl"), "enabled": 1, "sort_order": i, "instructions": [{"group_title": x["title"], "steps": "\n".join(x["steps"])} for x in steps]})
	cnt["Metode Pembayaran"] = pm
	cnt["Wilayah"] = 0
	if not frappe.db.count("Wilayah"):
		for w in load("wilayah.json"):
			frappe.get_doc({"doctype": "Wilayah", "wilayah_name": w["name"], "province": w["province"]}).insert(ignore_permissions=True)
			cnt["Wilayah"] += 1
	cnt["Banner"] = 0
	if not frappe.db.count("Banner"):
		for i, b in enumerate(load("sedekah.json")["banners"]):
			frappe.get_doc({"doctype": "Banner", "src": b["src"], "href": b["href"].replace("https://sedekah.id", ""), "alt": b["alt"], "sort_order": i, "enabled": 1}).insert(ignore_permissions=True)
			cnt["Banner"] += 1
	lv = load("gamification.json")
	cnt["Level"] = sum(make("Level Gamifikasi", l["name"], {"level_name": l["name"], "threshold": l["threshold"], "badge_url": l["badgeUrl"]}) for l in lv["levels"])
	if not frappe.db.count("Hadiah Gamifikasi"):
		for r in lv["rewards"]:
			frappe.get_doc({"doctype": "Hadiah Gamifikasi", "reward_name": r["name"], "description": r["description"], "image_url": r["imageUrl"], "category": r["category"], "point_cost": r["pointCost"], "out_of_stock": 1 if r["outOfStock"] else 0}).insert(ignore_permissions=True)
	g = frappe.get_single("Pengaturan Gamifikasi")
	if not g.idr_per_point:
		g.update({"enabled": 1, "claim_enabled": 0, "idr_per_point": 1})  # klaim mati bawaan (rumus poin = ASUMSI)
		g.save(ignore_permissions=True)
	ms = load("missions.json")
	pools = []
	if not frappe.db.count("Pool Sponsor Kebaikan"):
		for sp in ms["sponsor"]:
			p = frappe.get_doc({"doctype": "Pool Sponsor Kebaikan", "title": sp["title"], "voucher_amount": sp["voucherAmount"], "icon": sp.get("icon"), "pool_type": sp.get("type"), "pool_available": sp["poolAvailable"], "sponsor_name": "Hamba Allah"}).insert(ignore_permissions=True)
			pools.append(p.name)
	else:
		pools = frappe.get_all("Pool Sponsor Kebaikan", pluck="name", order_by="creation")
	for i, m in enumerate(ms["missions"]):
		make("Misi Kebaikan", m["slug"], {"slug": m["slug"], "mission_type": m["type"], "title": m["title"], "icon": m.get("icon"), "instruction": m.get("instruction"), "meaning": m.get("meaning"), "dzikir_name": m.get("dzikirName"), "arabic_text": m.get("arabicText"), "latin_text": m.get("latinText"), "target_count": m.get("targetCount"), "target_duration_sec": m.get("targetDurationSec"), "voucher_amount": m.get("voucherAmount"), "min_duration_sec": m.get("minDurationSec"), "max_duration_sec": m.get("maxDurationSec") or 600, "sponsor_pool": pools[i] if i < len(pools) else None, "enabled": 1})
	cnt["Video"] = 0
	if not frappe.db.count("Video Donasi"):
		for i, v in enumerate(load("videos.json")):
			slug = v.get("campaignSlug")
			frappe.get_doc({"doctype": "Video Donasi", "src": v["src"], "poster": v.get("poster"), "likes": v.get("likes"), "comments": v.get("comments"), "kampanye": slug if slug and frappe.db.exists("Kampanye Donasi", slug) else None, "caption": brand(v.get("caption")), "is_latest": 1 if i == 0 else 0, "sort_order": i}).insert(ignore_permissions=True)
			cnt["Video"] += 1
	pen = load("penyaluran.json")["items"]
	cnt["Penyaluran"] = sum(make("Penyaluran", p["slug"], {"slug": p["slug"], "title": p["title"], "subtitle": p.get("subtitle"), "tanggal": parse_date(p.get("date")), "category": p.get("category"), "image_url": p.get("image"), "location": p.get("location"), "program": p.get("program"), "description": brand(p.get("description"))}) for p in pen)
	art = load("artikel.json")["items"]
	cnt["Artikel"] = sum(make("Artikel", a["slug"], {"slug": a["slug"], "title": a["title"], "excerpt": a.get("excerpt"), "category": a.get("category"), "image_url": a.get("image"), "tanggal": parse_date(a.get("date")), "author": a.get("author"), "body_html": brand(a.get("body")), "related": "\n".join(a.get("related") or [])}) for a in art)
	cnt["Legal"] = 0
	for lang, f in (("id", "legal.json"), ("en", "legal.en.json")):
		for slug, p in load(f).items():
			cnt["Legal"] += make("Halaman Legal", f"{slug}-{lang}", {"slug": slug, "lang": lang, "title": brand(p["title"]), "subtitle": brand(p.get("subtitle")), "updated_label": p.get("updated"), "body_html": brand(p.get("html"))})
	cnt["Quran Jar"] = 0
	if not frappe.db.count("Ayat Quran Jar"):
		for mood, verses in load("quranjar.json")["verses"].items():
			for v in verses:
				frappe.get_doc({"doctype": "Ayat Quran Jar", "mood": mood, "payload": json.dumps(v, ensure_ascii=False)}).insert(ignore_permissions=True)
				cnt["Quran Jar"] += 1
	cnt["Survei"] = _surveys()
	frappe.db.commit()
	return cnt


def _surveys():
	if frappe.db.count("Survei Kepuasan"):
		return 0
	scale = [("😞", "Sangat Tidak Puas"), ("😕", "Kurang Puas"), ("😐", "Biasa Saja"), ("🙂", "Puas"), ("😍", "Sangat Puas")]  # ASUMSI: label skala asli tidak tercatat
	n = 0
	for lang, items in (("id", [("Tentang donasi", "Seberapa puas Anda dengan donasi ini?"), ("Pengalaman Berdonasi", "Bagaimana pengalaman berdonasi Anda hari ini?"), ("Mengenal Sahabat", "Seberapa mudah Anda menemukan kampanye yang Anda cari?")]),):
		for title, q in items:
			frappe.get_doc({"doctype": "Survei Kepuasan", "enabled": 1, "lang": lang, "title": title, "question_text": q, "comment_enabled": 1, "comment_prompt": "Ada masukan?", "scale": [{"emoji": e, "label": l} for e, l in scale]}).insert(ignore_permissions=True)
			n += 1
	return n
