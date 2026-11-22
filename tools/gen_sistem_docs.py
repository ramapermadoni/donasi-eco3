"""Menghasilkan docs/sistem/04-erd-doctype.md dan 05-matriks-keterlacakan.md dari spesifikasi (agar tak pernah menyimpang dari kode)."""
import importlib.util, json, os, re, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT + "/tools")
import spec_doctypes as S
import cek_cakupan as C

cat = C.cat
OUT = ROOT + "/docs/sistem"

def fields_of(name):
	for d in S.DT:
		if d["name"] == name:
			return d["fields"]
	f = json.load(open(os.path.join(S.BASE, S.scrub(name), S.scrub(name) + ".json")))
	return f["fields"]

def doctypes_table():
	rows = []
	for d in S.DT:
		kind = "single" if d.get("single") else "child" if d.get("child") else "master/transaksi"
		links = sorted({f["options"] for f in d["fields"] if f["fieldtype"] in ("Link", "Table")})
		rows.append((d["name"], kind, len(d["fields"]), ", ".join(links) or "-"))
	for n in ("Kampanye Donasi", "Donation", "Dana", "Pengaturan Donasi"):
		fl = fields_of(n)
		links = sorted({f["options"] for f in fl if f.get("fieldtype") in ("Link", "Table")})
		kind = "single" if n == "Pengaturan Donasi" else "master" if n in ("Dana", "Kampanye Donasi") else "transaksi"
		rows.append((n, kind + " (keuangan, W3/W4; diperluas W6)" if n != "Dana" else kind + " (keuangan, W3)", len(fl), ", ".join(links) or "-"))
	return rows

def used_by():
	"""Doctype -> method yang menyentuhnya (dibaca dari teks sumber api/*.py)."""
	import glob
	names = [r[0] for r in doctypes_table()]
	m = {n: set() for n in names}
	for f in glob.glob(ROOT + "/apps/donasionline/donasionline/api/*.py"):
		src = open(f).read()
		mod = os.path.basename(f)[:-3]
		for fn in re.finditer(r"^def (\w+)\(", src, re.M):
			start = fn.end()
			nxt = re.search(r"^def |^@frappe", src[start:], re.M)
			body = src[start:start + (nxt.start() if nxt else len(src))]
			for n in names:
				if f'"{n}"' in body:
					m[n].add(f"{mod}.{fn[1]}")
	return m

def write_04():
	t = ["# 04. ERD dan DocType (HASIL OTOMATIS)", "",
		"Dihasilkan oleh `tools/gen_sistem_docs.py` dari `tools/spec_doctypes.py` (sumber tunggal) — jangan sunting tangan. Status: **FAKTA** (DocType benar-benar ada dan termigrasi di site uji dan site utama). Nama field dan relasi adalah **USULAN** yang sudah dibangun.", "",
		"## Daftar DocType", "", "| DocType | Jenis | Jumlah field | Relasi keluar (Link/Table) |", "|---|---|---|---|"]
	for r in doctypes_table():
		t.append(f"| {r[0]} | {r[1]} | {r[2]} | {r[3]} |")
	t += ["", "## ERD (Mermaid)", "", "```mermaid", S.erd(), "```", "",
		"Catatan: Journal Entry, Cost Center, dan User adalah DocType ERPNext/Frappe. `Donation.je_receipt/je_amil/je_fee` mengikat jurnal PSAK (W4). Dimensi akuntansi `Dana` dan `Kampanye` berada pada GL Entry, bukan relasi ERD.", ""]
	open(OUT + "/04-erd-doctype.md", "w").write("\n".join(t))

def write_05():
	ub = used_by()
	t = ["# 05. Matriks Keterlacakan (HASIL OTOMATIS)", "",
		"Dihasilkan oleh `tools/gen_sistem_docs.py`. Sumber endpoint: handover `02-katalog-endpoint.md` (FAKTA, dibaca dari berkas); method dan tes: `apps/donasionline/donasionline/api/catalog.py` (FAKTA, ada di kode). Cakupan diperiksa oleh `tools/cek_cakupan.py`.", "",
		"## A. Endpoint -> Method -> Tes", "", "| HTTP | Path lama (sedekah.id) | Method Frappe `donasionline.api.…` | Tamu | Tes | Catatan |", "|---|---|---|---|---|---|"]
	for h, p, m, g, test, note in cat.ENDPOINTS:
		t.append(f"| {h} | `{p}` | `{m}` | {'ya' if g else 'tidak'} | `{test}` | {note} |")
	t += ["", "### Sengaja ditunda", "", "| HTTP | Path | Alasan |", "|---|---|---|"]
	for h, p, why in cat.DEFERRED:
		t.append(f"| {h} | `{p}` | {why} |")
	t += ["", "## B. Doctype handover 03 -> DocType dibangun", "", "| Doctype usulan (handover 03) | Dibangun sebagai |", "|---|---|"]
	for k, v in C.DT03.items():
		t.append(f"| {k} | {v} |")
	t += ["", "## C. DocType -> method yang menyentuhnya", "", "| DocType | Method (terbaca dari kode) |", "|---|---|"]
	for n, s in ub.items():
		t.append(f"| {n} | {', '.join(sorted(s)) or '— (diisi impor/admin atau mesin jurnal)'} |")
	t.append("")
	open(OUT + "/05-matriks-keterlacakan.md", "w").write("\n".join(t))

if __name__ == "__main__":
	b, m = C.main()
	write_04(); write_05()
	print("ditulis ke", OUT)
