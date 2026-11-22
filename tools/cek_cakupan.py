"""Reviewer cakupan (otomatis): setiap endpoint di handover 02 dan setiap Doctype di handover 03 harus punya padanan atau alasan ditunda.
Jalankan: python3 tools/cek_cakupan.py [--tulis]   (butuh akses ke folder handover; jalur bisa diubah lewat HANDOVER=...)"""
import importlib.util
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT + "/tools")
HAND = os.environ.get("HANDOVER", "/Users/ramapermadoni/Project/donasi-eco3/docs/handover-frappe")
spec = importlib.util.spec_from_file_location("catalog", ROOT + "/apps/donasionline/donasionline/api/catalog.py")
cat = importlib.util.module_from_spec(spec); spec.loader.exec_module(cat)
import spec_doctypes as S


def norm(p):
	return re.sub(r":\w+|<\w+>", ":x", p).rstrip("/")

def handover_endpoints():
	txt = open(HAND + "/02-katalog-endpoint.md", encoding="utf-8").read()
	out = []
	for m in re.finditer(r"^\| `(/api/[^`]+)` \| ([A-Z]+(?: \([A-Z]+\))?)", txt, re.M):
		out.append((m[2].split()[0], m[1]))
	# bagian 4 tidak punya kolom method; bagian 5 tabel 3 kolom
	for m in re.finditer(r"^\| `(/api/(?:baik|recurring)[^`]+)` \| ([A-Z]+)", txt, re.M):
		pass
	return sorted(set(out))

COVER_ALIAS = {  # path handover -> path katalog
	"/api/campaigns/feed": "/api/campaigns/feed",
}

def covered(http, path):
	n = norm(path)
	for h, p, *_ in cat.ENDPOINTS:
		if norm(p) == n:
			return True
	for h, p, _ in cat.DEFERRED:
		if norm(p).startswith(n.split("...")[0]) or n.startswith(norm(p).split("...")[0]):
			return True
	return False

DT03 = {  # Doctype usulan handover 03 -> Doctype dibangun
	"Campaign": "Kampanye Donasi", "Campaign Update": "Penyaluran (Link kampanye)", "Donation": "Donation", "Payment Request": "Permintaan Pembayaran",
	"Payment Method": "Metode Pembayaran", "Donor": "Donor", "Mitra": "Mitra", "Doa Amin": "Doa Amin", "Penyaluran": "Penyaluran", "Artikel": "Artikel",
	"Video": "Video Donasi", "Laporan": "Laporan Donasi", "Satisfaction Survey": "Survei Kepuasan", "Survey Scale Item": "Butir Skala Survei",
	"Survey Response": "Jawaban Survei", "Gold Price": "Harga Emas", "Recurring Schedule": "Jadwal Rutin", "Recurring Execution": "Eksekusi Rutin",
	"Baik Mission": "Misi Kebaikan", "Baik Sponsor Pool": "Pool Sponsor Kebaikan", "Baik Session": "Sesi Kebaikan", "Gamification Level": "Level Gamifikasi",
	"Gamification Reward": "Hadiah Gamifikasi", "Reward Claim": "Klaim Hadiah", "Home Popup Menu": "Pengaturan Beranda + Item Menu Popup Beranda", "Banner": "Banner",
	"Quran Jar Mood / Verse": "Ayat Quran Jar (mood = Select; label/warna mood tetap di UI)", "Region (Wilayah)": "Wilayah", "Legal Page": "Halaman Legal",
}

def main():
	bad = []
	for http, p in handover_endpoints():
		if not covered(http, p):
			bad.append((http, p))
	built = {d["name"] for d in S.DT} | {"Kampanye Donasi", "Donation", "Dana", "Pengaturan Donasi"}
	missing_dt = []
	for k, v in DT03.items():
		for part in re.split(r" \+ |\(", v)[0].split(" + "):
			if part.strip() and part.strip() not in built:
				missing_dt.append((k, part))
	print("endpoint handover:", len(handover_endpoints()), "| tak tercakup:", bad)
	print("doctype handover:", len(DT03), "| tak ada:", missing_dt)
	return bad, missing_dt

if __name__ == "__main__":
	b, m = main()
	sys.exit(1 if b or m else 0)
