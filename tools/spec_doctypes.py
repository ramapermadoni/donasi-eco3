"""Sumber tunggal DocType platform (W5/W6). Menghasilkan JSON DocType + ERD Mermaid.

Jalankan dari root proyek:  python3 tools/spec_doctypes.py
Notasi field: "fieldname|Tipe|Label|opsi" ; akhiran: * wajib, ^ unik, ~ read-only, # tampil di list.
Tipe "Link:Doctype", "Select:a/b/c", "Table:Child".
"""
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE = os.path.join(ROOT, "apps/donasionline/donasionline/donasi_online/doctype")
ROLES = ["System Manager", "Petugas Donasi"]
READ_ROLES = ["Akuntan Donasi"]

def F(s):
	flags = ""
	while s and s[-1] in "*^~#":
		flags, s = s[-1] + flags, s[:-1]
	p = s.split("|")
	name, typ = p[0], p[1]
	label = p[2] if len(p) > 2 and p[2] else name.replace("_", " ").title()
	opt = p[3] if len(p) > 3 else None
	d = {"fieldname": name, "label": label}
	if typ.startswith("Link:"):
		d["fieldtype"], d["options"] = "Link", typ[5:]
	elif typ.startswith("Table:"):
		d["fieldtype"], d["options"] = "Table", typ[6:]
	elif typ.startswith("Select:"):
		d["fieldtype"], d["options"] = "Select", typ[7:].replace("/", "\n")
	else:
		d["fieldtype"] = typ
		if opt:
			d["options"] = opt
	if "*" in flags: d["reqd"] = 1
	if "^" in flags: d["unique"] = 1
	if "~" in flags: d["read_only"] = 1
	if "#" in flags: d["in_list_view"] = 1
	return d

# (nama, autoname, {kunci: nilai}, [field...])  kunci: single, child, title, modul_catatan
DT = []
def dt(name, autoname, fields, **kw):
	DT.append(dict(name=name, autoname=autoname, fields=[F(x) for x in fields], **kw))

# ---------- Master konten ----------
dt("Mitra", "field:slug", [
	"slug|Data|Slug|*^#", "mitra_name|Data|Nama Mitra|*#", "mitra_type|Data|Tipe|#", "avatar_url|Data|Avatar (URL)",
	"instagram|Data", "verified|Check|Terverifikasi", "campaign_count|Int|Jumlah Kampanye|~", "total_raised|Currency|Total Terkumpul|~",
], title="mitra_name")
dt("Banner", "format:BNR-{#####}", ["src|Data|Gambar (URL)|*", "href|Data|Tautan", "alt|Data", "sort_order|Int", "enabled|Check"], title="alt")
dt("Wilayah", "format:WIL-{#####}", ["wilayah_name|Data|Nama|*#", "province|Data|Provinsi|#"], title="wilayah_name")
dt("Halaman Legal", "format:{slug}-{lang}", [
	"slug|Data|Slug|*", "lang|Select:id/en|Bahasa|*", "title|Data|Judul|*#", "subtitle|Data", "updated_label|Data", "body_html|Text Editor|Isi (HTML, disanitasi)",
], title="title")
dt("Ayat Quran Jar", "format:QJ-{#####}", [
	"mood|Select:bahagia/marah/sedih/gelisah/bersyukur/sendiri|Perasaan|*#", "payload|Code|Data ayat (JSON)|JSON",
])
dt("Penyaluran", "field:slug", [
	"slug|Data|Slug|*^", "title|Small Text|Judul|*", "subtitle|Small Text", "tanggal|Date|Tanggal|#", "category|Data|Kategori|#", "image_url|Data|Gambar (URL)",
	"location|Data|Lokasi", "program|Data|Program", "description|Text Editor|Deskripsi (HTML, disanitasi)", "kampanye|Link:Kampanye Donasi|Kampanye",
])
dt("Artikel", "field:slug", [
	"slug|Data|Slug|*^", "title|Small Text|Judul|*", "excerpt|Small Text", "category|Data|Kategori", "image_url|Data|Gambar (URL)", "tanggal|Date|Tanggal|#",
	"author|Data|Penulis", "body_html|Text Editor|Isi (HTML, disanitasi)", "related|Small Text|Slug terkait (satu per baris)",
])
dt("Video Donasi", "format:VID-{#####}", [
	"src|Data|Sumber (mp4)|*", "poster|Data", "likes|Data", "comments|Data", "kampanye|Link:Kampanye Donasi|Kampanye", "caption|Small Text", "is_latest|Check|Terbaru", "sort_order|Int",
], title="caption")
dt("Laporan Donasi", "format:LAP-{#####}", ["judul|Data|Judul|*#", "url_laporan|Data|URL Laporan", "url_donatur|Data|URL Donatur"], title="judul")
dt("Harga Emas", None, ["price_per_gram|Currency|Harga per gram|*", "source|Data|Sumber", "updated_label|Data", "fetched_at|Datetime", "stale|Check"], single=True)
dt("Item Menu Popup Beranda", None, ["title|Data|Judul|*#", "link|Data|Tautan|*", "icon|Data|Ikon"], child=True)
dt("Pengaturan Beranda", None, ["popup_enabled|Check|Menu popup aktif", "popup_heading|Data|Judul menu", "popup_items|Table:Item Menu Popup Beranda|Item menu"], single=True)

# ---------- Pembayaran ----------
dt("Instruksi Pembayaran", None, ["group_title|Data|Judul grup|*#", "steps|Small Text|Langkah (satu per baris; token {va_number} {amount})"], child=True)
dt("Metode Pembayaran", "field:code", [
	"code|Data|Kode|*^#", "method_name|Data|Nama|*#", "method_type|Select:qris/virtual_account/ewallet/retail/manual_transfer/credit_card|Tipe|*#",
	"fee_flat|Currency|Biaya tetap", "fee_percent|Percent|Biaya persen", "min_amount|Currency|Minimum|*", "max_amount|Currency|Maksimum", "icon_url|Data|Ikon (URL)",
	"enabled|Check|Aktif", "sort_order|Int|Urutan", "instructions|Table:Instruksi Pembayaran|Cara bayar",
], title="method_name")
dt("Permintaan Pembayaran", "format:PAY-{#####}", [
	"donation|Link:Donation|Donasi|*#", "order_id|Data|Order ID|*^", "payment_method|Link:Metode Pembayaran|Metode|#", "payment_type|Data", "gateway|Data",
	"status|Select:pending/paid/failed/expired|Status|#", "snap_token|Data", "redirect_url|Data", "qr_string|Small Text", "qr_code_url|Data", "va_bank|Data", "va_number|Data",
	"expires_at|Datetime|Kedaluwarsa", "simulated|Check|Simulasi (tanpa gateway)|~", "raw_response|Code|Respons gateway|JSON",
])

# ---------- Donor, OTP, Doa ----------
dt("Donor", "format:DNR-{#####}", [
	"user|Link:User|Pengguna", "full_name|Data|Nama|*#", "phone|Data|Telepon (digit, 62…)|*^#", "email|Data", "avatar_url|Data|Avatar (URL)", "birthdate|Date",
	"city|Data", "job|Data", "goal|Data", "source|Data", "donor_since|Date", "total_amount|Currency|Total donasi|~", "total_count|Int|Jumlah donasi|~", "points_spent|Int|Poin dipakai|~",
], title="full_name")
dt("Permintaan OTP", "format:OTP-{#####}", [
	"phone|Data|Telepon|*#", "purpose|Select:login/register|Tujuan", "code_hash|Data|Hash kode|~", "expires_at|Datetime|Kedaluwarsa", "attempts|Int|Percobaan", "used|Check|Terpakai",
])
dt("Doa Amin", "format:AMN-{#####}", [
	"donation|Link:Donation|Donasi (doa)|*#", "actor|Data|Pelaku (donor atau hash IP)|*", "actor_name|Data|Nama pengamin", "delta|Int|Jumlah|*", "read_at|Datetime|Dibaca pemilik",
])

# ---------- Survei ----------
dt("Butir Skala Survei", None, ["emoji|Data|Emoji|*", "label|Data|Label|*"], child=True)
dt("Survei Kepuasan", "format:SRV-{#####}", [
	"enabled|Check|Aktif", "lang|Select:id/en|Bahasa", "title|Data|Judul|*#", "image_url|Data", "question_text|Data|Pertanyaan|*",
	"comment_enabled|Check|Komentar aktif", "comment_prompt|Data", "scale|Table:Butir Skala Survei|Skala",
], title="title")
dt("Jawaban Survei", "format:SRA-{#####}", [
	"survey|Link:Survei Kepuasan|Survei|*", "rating|Int|Nilai|*#", "comment|Small Text", "donation|Link:Donation|Donasi",
])

# ---------- Shadaqa Rutin ----------
dt("Eksekusi Rutin", None, ["target_date|Date|Tanggal target|*#", "is_makeup|Check|Susulan", "donation|Link:Donation", "status|Select:Dibuat/Dibayar/Terlewat|Status"], child=True)
dt("Jadwal Rutin", "format:RTN-{#####}", [
	"donor|Link:Donor|Donor|*#", "freq|Select:daily/weekly/monthly|Frekuensi|*#", "hour|Int|Jam (0-23)|*", "amount|Currency|Nominal|*", "payment_method|Link:Metode Pembayaran|Metode",
	"remind_wa|Check|Ingatkan via WA", "remind_email|Check|Ingatkan via email", "start_date|Date|Mulai|*", "next_run|Date|Eksekusi berikut|~", "paused|Check|Dijeda",
	"status|Select:Aktif/Dijeda/Dibatalkan|Status|#", "streak|Int|Streak|~", "is_anonymous|Check", "prayer_note|Small Text|Catatan doa", "kampanye|Link:Kampanye Donasi|Kampanye",
	"executions|Table:Eksekusi Rutin|Riwayat",
], title="donor")
dt("Log Pengingat Rutin", "format:RLG-{#####}", ["schedule|Link:Jadwal Rutin|Jadwal|*#", "channel|Select:wa/email|Kanal", "sent_at|Datetime", "status|Select:Terkirim/Gagal/Dilewati|Status"])

# ---------- Jalan Kebaikan, Gamifikasi ----------
dt("Pool Sponsor Kebaikan", "format:POOL-{#####}", [
	"title|Data|Judul|*#", "kampanye|Link:Kampanye Donasi|Kampanye", "voucher_amount|Currency|Nominal voucher|*", "icon|Data", "pool_type|Data|Tipe", "pool_available|Currency|Sisa pool|*", "sponsor_name|Data|Nama sponsor",
], title="title")
dt("Misi Kebaikan", "field:slug", [
	"slug|Data|Slug|*^", "mission_type|Select:TAP_COUNTER/TIMER/CONFIRM/SHARE|Tipe|*#", "title|Data|Judul|*#", "icon|Data", "instruction|Small Text", "meaning|Small Text",
	"dzikir_name|Data", "arabic_text|Small Text", "latin_text|Small Text", "target_count|Int", "target_duration_sec|Int", "share_text|Small Text", "share_url|Data",
	"voucher_amount|Currency", "min_duration_sec|Int", "max_duration_sec|Int", "kampanye|Link:Kampanye Donasi", "sponsor_pool|Link:Pool Sponsor Kebaikan|Pool", "enabled|Check|Aktif",
], title="title")
dt("Sesi Kebaikan", "format:SES-{#####}", [
	"mission|Link:Misi Kebaikan|Misi|*#", "donor|Link:Donor|Donor|*", "started_at|Datetime|*", "reserved_until|Datetime", "status|Select:Aktif/Diklaim/Dilepas/Kedaluwarsa|Status|#", "voucher_amount|Currency", "pool|Link:Pool Sponsor Kebaikan",
])
dt("Level Gamifikasi", "field:level_name", ["level_name|Data|Nama|*^#", "threshold|Int|Ambang poin|*#", "badge_url|Data"], title="level_name")
dt("Hadiah Gamifikasi", "format:HDH-{#####}", ["reward_name|Data|Nama|*#", "description|Small Text", "image_url|Data", "category|Data", "point_cost|Int|Biaya poin|*#", "out_of_stock|Check|Stok habis"], title="reward_name")
dt("Klaim Hadiah", "format:KLM-{#####}", [
	"reward|Link:Hadiah Gamifikasi|Hadiah|*#", "donor|Link:Donor|Donor|*", "recipient_name|Data|Penerima|*", "phone|Data|*", "address|Small Text|Alamat|*",
	"points_spent|Int|Poin|~", "status|Select:Diajukan/Dikirim/Selesai/Dibatalkan|Status|#",
])
dt("Pengaturan Gamifikasi", None, ["enabled|Check|Aktif", "claim_enabled|Check|Klaim aktif", "idr_per_point|Currency|Rupiah per 1 poin"], single=True)

# ---------- Perluasan DocType yang sudah ada (field ditambahkan, tidak menimpa) ----------
EXTEND = {
	"Kampanye Donasi": [
		"slug|Data|Slug|^", "title|Small Text|Judul", "image_url|Data|Gambar (URL)", "target_amount|Currency|Target", "description|Text Editor|Deskripsi (HTML, disanitasi)",
		"organizer_name|Data", "organizer_avatar|Data", "category|Data|Kategori", "is_featured|Check", "featured_excerpt|Small Text", "home_rank|Int", "is_system|Check|Kampanye sistem",
		"system_kind|Select:/zakat/wakaf/fidyah|Jenis sistem", "mitra|Link:Mitra", "status|Select:draft/aktif/selesai|Status|#",
		"title_en|Data", "description_en|Text Editor", "event_slug|Data",
	],
	"Donation": [
		"campaign_title|Data", "currency|Data|Mata uang", "donor|Link:Donor", "donor_phone|Data|Telepon donor", "is_anonymous|Check", "message|Small Text|Doa",
		"donation_type|Select:one_time/recurring|Jenis", "idr_equivalent|Currency", "payment_method|Link:Metode Pembayaran", "expired_at|Datetime", "mitra|Link:Mitra",
		"ref|Data", "utm_source|Data", "utm_medium|Data", "utm_campaign|Data", "utm_content|Data", "utm_term|Data", "referrer_captured_at|Datetime", "event_slug|Data",
		"baik_session|Link:Sesi Kebaikan", "recurring_schedule|Link:Jadwal Rutin", "amin_count|Int|Jumlah amin|~",
	],
}


def scrub(n):
	return re.sub(r"[^a-z0-9]+", "_", n.lower()).strip("_")

def perms(single=False):
	out = []
	for r in ROLES:
		out.append({"role": r, "read": 1, "write": 1, "create": 0 if single else 1, "delete": 0 if single else 1, "report": 1, "export": 1, "print": 1})
	for r in READ_ROLES:
		out.append({"role": r, "read": 1, "report": 1, "export": 1})
	return out

def write_dt(d):
	folder = os.path.join(BASE, scrub(d["name"]))
	os.makedirs(folder, exist_ok=True)
	open(os.path.join(folder, "__init__.py"), "a").close()
	doc = {
		"doctype": "DocType", "name": d["name"], "module": "Donasi Online", "custom": 0, "engine": "InnoDB",
		"field_order": [f["fieldname"] for f in d["fields"]], "fields": d["fields"],
		"sort_field": "creation", "sort_order": "DESC", "states": [], "links": [],
		"modified": "2026-11-22 12:00:00.000000", "creation": "2026-11-22 12:00:00.000000",
	}
	if d.get("child"):
		doc["istable"] = 1
		doc["editable_grid"] = 1
	else:
		doc["permissions"] = perms(d.get("single"))
		if d["autoname"]:
			doc["autoname"] = d["autoname"]
		if d.get("title"):
			doc["title_field"] = d["title"]
	if d.get("single"):
		doc["issingle"] = 1
	json.dump(doc, open(os.path.join(folder, scrub(d["name"]) + ".json"), "w"), indent=1, ensure_ascii=False)
	pyf = os.path.join(folder, scrub(d["name"]) + ".py")
	if not os.path.exists(pyf):
		cls = d["name"].replace(" ", "").replace("-", "")
		open(pyf, "w").write(f"from frappe.model.document import Document\n\n\nclass {cls}(Document):\n\tpass\n")

def extend(name, fields):
	f = os.path.join(BASE, scrub(name), scrub(name) + ".json")
	doc = json.load(open(f))
	have = {x["fieldname"] for x in doc["fields"]}
	new = [F(x) for x in fields]
	new = [x for x in new if x["fieldname"] not in have]
	# sisipkan sebelum kolom tanpa tipe tetap: cukup tambahkan di akhir
	doc["fields"] += new
	doc["field_order"] = [x["fieldname"] for x in doc["fields"]]
	json.dump(doc, open(f, "w"), indent=1, ensure_ascii=False)
	return len(new)

def erd():
	"""ERD Mermaid dari relasi Link/Table di spesifikasi + DocType yang sudah ada."""
	lines = ["erDiagram"]
	known = {d["name"] for d in DT} | set(EXTEND) | {"Dana", "Pengaturan Donasi", "Journal Entry", "Cost Center", "User"}
	rel = []
	all_fields = {d["name"]: d["fields"] for d in DT}
	for n in list(EXTEND) + ["Dana", "Pengaturan Donasi"]:
		f = os.path.join(BASE, scrub(n), scrub(n) + ".json")
		all_fields[n] = json.load(open(f))["fields"]
	for n, fl in all_fields.items():
		for f in fl:
			if f["fieldtype"] in ("Link", "Table") and f.get("options") in known:
				kind = "||--o{" if f["fieldtype"] == "Table" else "}o--||"
				a, b = (n, f["options"]) if f["fieldtype"] == "Table" else (n, f["options"])
				rel.append((a, b, kind, f["fieldname"]))
	q = lambda s: '"' + s + '"'
	for a, b, kind, fn in sorted(set(rel)):
		lines.append(f"\t{q(a)} {kind} {q(b)} : {fn}")
	return "\n".join(lines)

if __name__ == "__main__":
	for d in DT:
		write_dt(d)
	added = {n: extend(n, f) for n, f in EXTEND.items()}
	print("DocType baru:", len(DT), "| field ditambahkan:", added)
	if "--erd" in sys.argv:
		print(erd())
