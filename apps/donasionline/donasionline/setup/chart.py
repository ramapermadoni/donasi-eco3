"""Bagan akun USULAN (docs/psak/05, bagian B). Provisional: tunggu F1-F29."""

# (nomor, nama, account_type, root_type bila akar, nomor induk, is_group)
G = True
ROWS = [
	# --- Aset (B1) ---
	("1-0000", "ASET", None, "Asset", None, G),
	("1-1000", "Aset Lancar", None, None, "1-0000", G),
	("1-1100", "Kas dan Setara Kas", None, None, "1-1000", G),
	("1-1101", "Bank Operasional", "Bank", None, "1-1100", False),
	("1-1110", "Clearing Gateway - Midtrans", "Bank", None, "1-1100", False),
	("1-1120", "Clearing Gateway - Winpay", "Bank", None, "1-1100", False),
	("1-1130", "Clearing Kanal Lain", "Bank", None, "1-1100", False),
	("1-1190", "Kas Valas", "Cash", None, "1-1100", False),
	("1-1150", "Kas Pihak Ketiga", None, None, "1-1000", G),
	("1-1102", "Bank Titipan", "Bank", None, "1-1150", False),
	("1-1115", "Clearing Titipan", "Bank", None, "1-1150", False),
	("1-1200", "Piutang Penyaluran Zakat", None, None, "1-1000", False),
	("1-1210", "Piutang Penyaluran Infak dan Sedekah", None, None, "1-1000", False),
	("1-1220", "Al-Qardh Al-Hasan", None, None, "1-1000", False),
	("1-1300", "Aset Zakat dan Infak Nonkas", None, None, "1-1000", G),
	("1-1400", "Piutang Antar-Dana", "Current Asset", None, "1-1000", False),
	("1-2000", "Aset Tidak Lancar", None, None, "1-0000", G),
	("1-2100", "Aset Tetap", None, None, "1-2000", G),
	("1-2110", "Aset Tetap Umum", "Fixed Asset", None, "1-2100", False),  # tambahan teknis (modul Asset)
	("1-2150", "Akumulasi Penyusutan Aset Tetap", "Accumulated Depreciation", None, "1-2000", False),
	("1-2200", "Aset Takberwujud", None, None, "1-2000", False),
	("1-2300", "Aset Kelolaan", None, None, "1-2000", G),
	("1-2350", "Akumulasi Penyusutan Aset Kelolaan", "Accumulated Depreciation", None, "1-2000", False),
	# --- Liabilitas (B2) ---
	("2-0000", "LIABILITAS", None, "Liability", None, G),
	("2-1000", "Liabilitas Jangka Pendek", None, None, "2-0000", G),
	("2-1100", "Liabilitas Penyaluran Zakat", None, None, "2-1000", False),
	("2-1200", "Liabilitas Penyaluran Infak dan Sedekah", None, None, "2-1000", False),
	("2-1300", "Titipan Zakat Penghasilan di Muka", None, None, "2-1000", False),
	("2-1310", "Titipan Qurban", None, None, "2-1000", False),
	("2-1320", "Utang Refund Donatur", None, None, "2-1000", False),
	("2-1330", "Titipan Wakaf Uang", None, None, "2-1000", False),
	("2-1340", "Titipan Biaya Kanal Ditanggung Donatur", None, None, "2-1000", False),
	("2-1350", "Selisih Bayar Donatur", None, None, "2-1000", False),
	("2-1360", "Titipan Sponsor Pool Jalan Kebaikan", None, None, "2-1000", False),
	("2-1400", "Utang Pajak dan Utang Lain", None, None, "2-1000", False),
	("2-1500", "Utang Antar-Dana", None, None, "2-1000", False),
	("2-2000", "Liabilitas Jangka Panjang", None, None, "2-0000", G),
	("2-2100", "Liabilitas Imbalan Kerja", None, None, "2-2000", False),
	# --- Aset neto (B3) ---
	("3-0000", "ASET NETO", None, "Equity", None, G),
	("3-1000", "Saldo Dana", "Equity", None, "3-0000", False),
	("3-2000", "Saldo Awal dan Penyesuaian Dana", "Equity", None, "3-0000", False),
	# --- Penghasilan (B4) ---
	("4-0000", "PENGHASILAN", None, "Income", None, G),
	("4-1000", "Penerimaan Zakat", None, None, "4-0000", G),
	("4-1100", "Penerimaan Zakat - Muzaki Pribadi", "Income Account", None, "4-1000", False),
	("4-1200", "Penerimaan Zakat - Muzaki Perusahaan", "Income Account", None, "4-1000", False),
	("4-1900", "Dampak Pengukuran Ulang Aset Zakat", "Income Account", None, "4-1000", False),
	("4-2000", "Penerimaan Infak dan Sedekah", None, None, "4-0000", G),
	("4-2100", "Infak dan Sedekah Tanpa Pembatasan", "Income Account", None, "4-2000", False),
	("4-2200", "Infak dan Sedekah Dengan Pembatasan", "Income Account", None, "4-2000", False),
	("4-2900", "Hasil Pengelolaan Aset Infak dan Sedekah", "Income Account", None, "4-2000", False),
	("4-2950", "Dampak Pengukuran Ulang Aset Infak dan Sedekah", "Income Account", None, "4-2000", False),
	("4-3000", "Penghasilan Dana Amil", None, None, "4-0000", G),
	("4-3100", "Bagian Amil dari Penerimaan Zakat", "Income Account", None, "4-3000", False),
	("4-3200", "Bagian Amil dari Penerimaan Infak dan Sedekah", "Income Account", None, "4-3000", False),
	("4-3900", "Penghasilan Lain Dana Amil", "Income Account", None, "4-3000", False),
	("4-4000", "Penerimaan Dana Nonhalal", "Income Account", None, "4-0000", False),
	("4-5000", "Penerimaan Wakaf", "Income Account", None, "4-0000", False),
	# --- Beban (B5) ---
	("5-0000", "BEBAN", None, "Expense", None, G),
	("5-1000", "Penyaluran Zakat", None, None, "5-0000", G),
	("5-1100", "Penyaluran Zakat - Amil", "Expense Account", None, "5-1000", False),
	("5-1110", "Penyaluran Zakat - Fakir", "Expense Account", None, "5-1000", False),
	("5-1120", "Penyaluran Zakat - Miskin", "Expense Account", None, "5-1000", False),
	("5-1130", "Penyaluran Zakat - Riqab", "Expense Account", None, "5-1000", False),
	("5-1140", "Penyaluran Zakat - Gharim", "Expense Account", None, "5-1000", False),
	("5-1150", "Penyaluran Zakat - Muallaf", "Expense Account", None, "5-1000", False),
	("5-1160", "Penyaluran Zakat - Sabilillah", "Expense Account", None, "5-1000", False),
	("5-1170", "Penyaluran Zakat - Ibnu Sabil", "Expense Account", None, "5-1000", False),
	("5-1190", "Selisih Realisasi dan Kerugian Aset Zakat", "Expense Account", None, "5-1000", False),
	("5-2000", "Penyaluran Infak dan Sedekah", None, None, "5-0000", G),
	("5-2100", "Penyaluran Infak TT - Kepada Amil", "Expense Account", None, "5-2000", False),
	("5-2110", "Penyaluran Infak TT - Kepada Penerima Manfaat", "Expense Account", None, "5-2000", False),
	("5-2200", "Penyaluran Infak T - Kepada Amil", "Expense Account", None, "5-2000", False),
	("5-2210", "Penyaluran Infak T - Kepada Penerima Manfaat", "Expense Account", None, "5-2000", False),
	("5-2300", "Beban Penyusutan Aset Kelolaan", "Expense Account", None, "5-2000", False),
	("5-2400", "Penghapusan Al-Qardh Al-Hasan", "Expense Account", None, "5-2000", False),
	("5-2900", "Selisih Realisasi dan Kerugian Aset Infak", "Expense Account", None, "5-2000", False),
	("5-3000", "Beban Dana Amil", None, None, "5-0000", G),
	("5-3100", "Beban Pegawai", "Expense Account", None, "5-3000", False),
	("5-3200", "Beban Biaya Kanal Pembayaran", "Expense Account", None, "5-3000", False),
	("5-3300", "Beban Pemasaran Penghimpunan", "Expense Account", None, "5-3000", False),
	("5-3400", "Beban Penyusutan Aset Tetap Amil", "Depreciation", None, "5-3000", False),
	("5-3500", "Beban Operasional Lain", "Expense Account", None, "5-3000", False),
	("5-3600", "Beban Administrasi Bank dan Transfer", "Expense Account", None, "5-3000", False),
	("5-3900", "Kerugian Aset karena Kelalaian Amil", "Expense Account", None, "5-3000", False),
	("5-4000", "Penyaluran Dana Nonhalal", "Expense Account", None, "5-0000", False),
	("5-5000", "Penyaluran dan Beban Wakaf", "Expense Account", None, "5-0000", False),
]

# Dana yang diizinkan per akun P&L / titipan (B4/B5/B2). Akun kas, ekuitas, piutang antar-dana: tanpa batas.
FILTERS = {
	("ZAKAT",): ["4-1100", "4-1200", "4-1900", "5-1100", "5-1110", "5-1120", "5-1130", "5-1140", "5-1150", "5-1160", "5-1170", "5-1190"],
	("INFAK-TT",): ["4-2100", "5-2100", "5-2110"],
	("INFAK-T",): ["4-2200", "5-2200", "5-2210"],
	("INFAK-TT", "INFAK-T"): ["4-2900", "4-2950", "5-2300", "5-2400", "5-2900"],
	("AMIL",): ["4-3100", "4-3200", "4-3900", "5-3100", "5-3200", "5-3300", "5-3400", "5-3500", "5-3600", "5-3900"],
	("NONHALAL",): ["4-4000", "5-4000"],
	("WAKAF",): ["4-5000", "5-5000"],
	("TITIPAN",): ["1-1102", "1-1115", "2-1300", "2-1310", "2-1320", "2-1330", "2-1340", "2-1350", "2-1360"],
}

DANA = [
	("ZAKAT", "Dana Zakat", "Dengan Pembatasan"),
	("INFAK-TT", "Dana Infak dan Sedekah - Tanpa Pembatasan (penghasilan)", "Dengan Pembatasan"),
	("INFAK-T", "Dana Infak dan Sedekah - Dengan Pembatasan (penghasilan)", "Dengan Pembatasan"),
	("AMIL", "Dana Amil", "Tanpa Pembatasan"),
	("NONHALAL", "Dana Nonhalal", "Di luar aset neto (titipan)"),
	("WAKAF", "Dana Wakaf (bersyarat F4)", "Di luar aset neto (titipan)"),
	("TITIPAN", "Titipan Pihak Ketiga", "Di luar aset neto (titipan)"),
]

# Program (Cost Center) contoh: GANTI dengan program nyata lembaga.
PROGRAMS = ["Pendidikan", "Kesehatan", "Kemanusiaan dan Bencana", "Ekonomi Umat", "Umum"]


def tree():
	"""Bentuk dict bersarang untuk create_charts(custom_chart=...)."""
	nodes = {}
	for num, name, atype, root, parent, grp in ROWS:
		d = {"account_number": num}
		if atype:
			d["account_type"] = atype
		if root:
			d["root_type"] = root
		if grp:
			d["is_group"] = 1
		nodes[num] = (name, d, parent)
	out = {}
	for num, (name, d, parent) in nodes.items():
		if parent is None:
			out[name] = d
	def attach(num):
		name, d, parent = nodes[num]
		pname, pd, _ = nodes[parent]
		return pd
	for num, (name, d, parent) in nodes.items():
		if parent is not None:
			attach(num)[name] = d
	return out
