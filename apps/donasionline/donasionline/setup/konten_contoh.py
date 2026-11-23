"""Konten contoh (snapshot dari situs asal): tandai, ringkas, bersihkan.

  bench --site <site> execute donasionline.setup.konten_contoh.ringkasan
  bench --site <site> execute donasionline.setup.konten_contoh.bersihkan                       # simulasi (tidak mengubah apa pun)
  bench --site <site> execute donasionline.setup.konten_contoh.bersihkan --kwargs "{'dry_run': 0}"   # benar-benar membersihkan

Aturan bersihkan:
- Hanya baris is_sample=1. Konten yang Anda buat sendiri tidak disentuh.
- Kampanye contoh yang SUDAH punya donasi/jadwal rutin tidak dihapus (catatan keuangan): dinonaktifkan (tak tampil, tak bisa dibayar).
- Mitra contoh yang masih dirujuk kampanye/donasi dipertahankan dan dilaporkan.
- Kampanye sistem (zakat, wakaf umum, fidyah, sedekah) bukan contoh dan tidak disentuh.
- Setelah sukses: Pengaturan Donasi.konten_contoh_dibersihkan=1 (UI beralih membaca konten dari server; impor snapshot tidak membuat ulang).
"""
import json
import os

import frappe

from donasionline.setup import import_snapshot as imp

# Kampanye inti yang dipakai sistem (donasi bawaan, Shadaqa Rutin, zakat, wakaf umum, fidyah): TIDAK PERNAH dianggap contoh.
RESERVED = ("sedekah", "zakat-penghasilan", "zakat-maal", "zakat-emas", "zakat-investasi", "zakat-perniagaan", "wakaf-umum", "fidyah")

DOCTYPES = ("Penyaluran", "Artikel", "Video Donasi", "Banner", "Kampanye Donasi", "Mitra")  # urutan hapus: penunjuk dulu


def lindungi():
	"""Pastikan kampanye inti tidak bertanda contoh (idempoten)."""
	frappe.db.sql("update `tabKampanye Donasi` set is_sample=0 where is_sample=1 and name in %s", (RESERVED,))


def tandai():
	"""Beri tanda is_sample pada baris lama yang berasal dari snapshot (dipakai patch; idempoten)."""
	snap = imp.load("sedekah.json")
	keys = {
		"Kampanye Donasi": ("slug", {c["slug"] for c in snap["campaigns"]}),
		"Mitra": ("slug", {m["slug"] for m in imp.load("mitra.json")}),
		"Penyaluran": ("slug", {p["slug"] for p in imp.load("penyaluran.json")["items"]}),
		"Artikel": ("slug", {a["slug"] for a in imp.load("artikel.json")["items"]}),
		"Video Donasi": ("src", {v["src"] for v in imp.load("videos.json")}),
		"Banner": ("src", {b["src"] for b in snap["banners"]}),
	}
	n = 0
	for dt, (field, vals) in keys.items():
		for name, val, ya, sistem in frappe.db.sql(
			f"select name, `{field}`, is_sample, {'is_system' if dt == 'Kampanye Donasi' else '0'} from `tab{dt}`"
		):
			if val in vals and not ya and not sistem:
				frappe.db.set_value(dt, name, "is_sample", 1, update_modified=False)
				n += 1
	lindungi()
	return n


def _dipakai_kampanye(name):
	return bool(frappe.db.count("Donation", {"kampanye": name}) or frappe.db.count("Jadwal Rutin", {"kampanye": name}))


def ringkasan():
	lindungi()
	out = {}
	for dt in DOCTYPES:
		out[dt] = {"contoh": frappe.db.count(dt, {"is_sample": 1}), "milik_sendiri": frappe.db.count(dt, {"is_sample": 0}) - (frappe.db.count(dt, {"is_system": 1}) if dt == "Kampanye Donasi" else 0)}
	out["kampanye_contoh_ber_donasi"] = sum(1 for n in frappe.get_all("Kampanye Donasi", {"is_sample": 1}, pluck="name") if _dipakai_kampanye(n))
	out["sudah_dibersihkan"] = imp.cleaned()
	print(json.dumps(out, indent=1, ensure_ascii=False))
	return out


def bersihkan(dry_run=1, commit=1):
	dry = str(dry_run).lower() not in ("0", "false", "no")
	lindungi()
	hasil = {"dry_run": dry, "dihapus": {}, "dinonaktifkan": [], "dipertahankan": []}
	for dt in DOCTYPES:
		hapus = 0
		for name in frappe.get_all(dt, {"is_sample": 1}, pluck="name"):
			if dt == "Kampanye Donasi" and _dipakai_kampanye(name):
				hasil["dinonaktifkan"].append(name)
				if not dry:
					frappe.db.set_value(dt, name, {"is_active": 0, "is_featured": 0, "status": "draft"})
				continue
			if dt == "Mitra" and (frappe.db.count("Kampanye Donasi", {"mitra": name}) or frappe.db.count("Donation", {"mitra": name})):
				hasil["dipertahankan"].append(name)
				continue
			hapus += 1
			if not dry:
				frappe.delete_doc(dt, name, ignore_permissions=True, force=True)
		hasil["dihapus"][dt] = hapus
	if not dry:
		frappe.db.set_single_value("Pengaturan Donasi", "konten_contoh_dibersihkan", 1)
		if str(commit).lower() not in ("0", "false", "no"):
			frappe.db.commit()
	print(json.dumps(hasil, indent=1, ensure_ascii=False))
	return hasil
