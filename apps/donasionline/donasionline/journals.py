"""Mesin jurnal E2-E5 (docs/psak/05 D0, E2-E5). USULAN/PROVISIONAL; posting mati bawaan.

Semua angka Decimal; A dibulatkan half-up ke rupiah utuh; tiap JE seimbang per Dana.
"""

from decimal import ROUND_HALF_UP, Decimal

import frappe
from frappe import _
from frappe.utils import getdate

BLOCKED_FUND_TYPES = ("wakaf", "fidyah", "qurban")  # F4/E7/E13
CLEARING = {"Midtrans": "1-1110", "Winpay": "1-1120", "Lainnya": "1-1130"}
BANK = "1-1101"
ACC_RECEIPT = {
	"zakat": {"Pribadi": "4-1100", "Perusahaan": "4-1200"},
	"infak_bebas": "4-2100",
	"infak_terikat": "4-2200",
}
DANA_OF = {"zakat": "ZAKAT", "infak_bebas": "INFAK-TT", "infak_terikat": "INFAK-T"}
ACC_AMIL_EXPENSE = {"zakat": "5-1100", "infak_bebas": "5-2100"}
ACC_AMIL_INCOME = {"zakat": "4-3100", "infak_bebas": "4-3200"}
ACC_FEE = "5-3200"


class PostingBlocked(frappe.ValidationError):
	pass


def D(v):
	return Decimal(str(v or 0))


def rupiah(v):
	return D(v).quantize(Decimal(1), rounding=ROUND_HALF_UP)


def settings():
	return frappe.get_single("Pengaturan Donasi")


def hak_amil(fund_type, amount, s=None):
	s = s or settings()
	pct = {"zakat": D(s.h_zakat), "infak_bebas": D(s.h_infak)}.get(fund_type, Decimal(0))
	return rupiah(D(amount) * pct / 100)


def _acc(company, number):
	name = frappe.db.get_value("Account", {"company": company, "account_number": number}, "name")
	if not name:
		frappe.throw(_("Akun {0} tidak ditemukan").format(number))
	return name


def check_gate(don, s=None):
	"""Gerbang H.1. Melempar PostingBlocked bila tidak boleh diposting."""
	s = s or settings()
	if not s.posting_enabled:
		raise PostingBlocked(_("Posting jurnal otomatis belum diaktifkan (Pengaturan Donasi)."))
	if not (s.peran_platform or "").startswith("A"):
		raise PostingBlocked(_("Hanya model A (amil/PUB berizin) yang didukung jurnal otomatis."))
	if don.fund_type in BLOCKED_FUND_TYPES:
		raise PostingBlocked(_("Jenis dana {0} diblokir sampai diputuskan.").format(don.fund_type))
	if don.fund_type not in DANA_OF:
		raise PostingBlocked(_("Jenis dana belum diisi/tidak dikenal."))
	if not don.program:
		raise PostingBlocked(_("Program (Cost Center) wajib."))
	if don.fund_type == "infak_terikat" and not don.kampanye:
		raise PostingBlocked(_("Infak terikat wajib punya Kampanye."))
	if D(don.amount) <= 0:
		raise PostingBlocked(_("Jumlah donasi harus > 0."))


def _line(company, number, debit, credit, dana, cost_center=None, kampanye=None):
	row = {
		"account": _acc(company, number),
		"debit_in_account_currency": float(debit),
		"credit_in_account_currency": float(credit),
		"dana": dana,
	}
	if cost_center:
		row["cost_center"] = cost_center
	if kampanye:
		row["kampanye"] = kampanye
	return row


def make_je(ref, company, posting_date, lines, user_remark, bank_ref=None):
	"""Idempoten: bila donation_ref sudah ada, kembalikan JE yang ada (tanpa menggandakan)."""
	assert ref, "donation_ref tidak boleh kosong"
	existing = frappe.db.get_value("Journal Entry", {"donation_ref": ref, "docstatus": 1})
	if existing:
		return existing
	touches_bank = any(
		frappe.db.get_value("Account", l["account"], "account_type") == "Bank" for l in lines
	)
	doc = frappe.new_doc("Journal Entry")
	doc.update(
		{
			"voucher_type": "Bank Entry" if touches_bank else "Journal Entry",
			"company": company,
			"posting_date": getdate(posting_date),
			"donation_ref": ref,
			"user_remark": user_remark,
		}
	)
	if touches_bank:
		doc.cheque_no = bank_ref or ref
		doc.cheque_date = getdate(posting_date)
	for l in lines:
		doc.append("accounts", l)
	try:
		doc.insert(ignore_permissions=True)
		doc.submit()
	except frappe.UniqueValidationError:
		frappe.db.rollback()
		return frappe.db.get_value("Journal Entry", {"donation_ref": ref})
	return doc.name


def _lock(name):
	don = frappe.get_doc("Donation", name)
	frappe.db.sql("select name from `tabDonation` where name=%s for update", name)
	don.reload()
	return don


def balance(company, clearing_no, dana):
	"""Saldo debit-kredit akun clearing pada satu Dana (GL, tidak dibatalkan)."""
	acc = _acc(company, clearing_no)
	r = frappe.db.sql(
		"select coalesce(sum(debit-credit),0) from `tabGL Entry` where account=%s and dana=%s and is_cancelled=0",
		(acc, dana),
	)
	return D(r[0][0])


# --- E2 ---
def post_receipt(name):
	don = _lock(name)
	check_gate(don)
	if don.status != "Paid":
		raise PostingBlocked(_("Donasi belum Paid."))
	if don.je_receipt:
		return don.je_receipt
	s = settings()
	co = s.company
	g = rupiah(don.amount)
	dana = DANA_OF[don.fund_type]
	acc_no = ACC_RECEIPT[don.fund_type]
	if isinstance(acc_no, dict):
		acc_no = acc_no[don.donor_type or "Pribadi"]
	lines = [
		_line(co, CLEARING[don.gateway or "Midtrans"], g, 0, dana, kampanye=don.kampanye),
		_line(co, acc_no, 0, g, dana, cost_center=don.program, kampanye=don.kampanye),
	]
	je = make_je(f"{don.name}:RECEIPT", co, don.paid_at, lines, f"Penerimaan {don.name}")
	don.db_set("je_receipt", je)
	return je


# --- E3 ---
def post_amil(name):
	don = _lock(name)
	check_gate(don)
	if not don.je_receipt:
		raise PostingBlocked(_("Penerimaan (E2) belum diposting."))
	if don.je_amil:
		return don.je_amil
	s = settings()
	co = s.company
	a = hak_amil(don.fund_type, don.amount, s)
	don.db_set("amil_amount", float(a))
	if a <= 0:
		return None
	dana = DANA_OF[don.fund_type]
	clr = CLEARING[don.gateway or "Midtrans"]
	lines = [
		_line(co, ACC_AMIL_EXPENSE[don.fund_type], a, 0, dana, cost_center=don.program, kampanye=don.kampanye),
		_line(co, ACC_AMIL_INCOME[don.fund_type], 0, a, "AMIL", cost_center=don.program),
		_line(co, clr, a, 0, "AMIL"),
		_line(co, clr, 0, a, dana, kampanye=don.kampanye),
	]
	je = make_je(f"{don.name}:AMIL", co, don.paid_at, lines, f"Hak amil {don.name}")
	don.db_set("je_amil", je)
	return je


# --- E4 ---
def post_fee(name, fee):
	"""Fee dibebankan ke Dana Amil; ditahan bila saldo clearing AMIL kurang (tidak pernah negatif)."""
	don = _lock(name)
	check_gate(don)
	s = settings()
	co = s.company
	f = rupiah(fee)
	don.db_set("fee", float(f))
	if don.je_fee:
		return don.je_fee
	if f <= 0:
		don.db_set("fee_status", "Belum ada")
		return None
	clr = CLEARING[don.gateway or "Midtrans"]
	if balance(co, clr, "AMIL") < f:
		don.db_set("fee_status", "Ditahan")
		return None
	cc = s.cost_center_operasional
	lines = [
		_line(co, ACC_FEE, f, 0, "AMIL", cost_center=cc),
		_line(co, clr, 0, f, "AMIL"),
	]
	je = make_je(f"{don.name}:FEE", co, don.paid_at, lines, f"Fee gateway {don.name}")
	don.db_set({"je_fee": je, "fee_status": "Diposting"})
	return je


# --- E5 ---
def settle(settlement_id, donation_names, posting_date, gateway="Midtrans"):
	"""Settlement batch: per Dana, Dr Bank / Cr Clearing sebesar saldo batch itu."""
	s = settings()
	co = s.company
	dons = [_lock(n) for n in donation_names]
	totals = {}
	for d in dons:
		check_gate(d)
		if d.settled:
			raise PostingBlocked(_("{0} sudah Settled.").format(d.name))
		if not d.je_receipt or (D(hak_amil(d.fund_type, d.amount, s)) > 0 and not d.je_amil):
			raise PostingBlocked(_("{0}: E2/E3 belum diposting.").format(d.name))
		if d.fee_status == "Ditahan" or (D(d.fee) > 0 and d.fee_status != "Diposting"):
			raise PostingBlocked(_("{0}: fee ditahan/belum diposting.").format(d.name))
		g, a, f = rupiah(d.amount), D(d.amount_amil_or_zero()), D(d.fee)
		src = DANA_OF[d.fund_type]
		totals[src] = totals.get(src, Decimal(0)) + (g - a)
		totals["AMIL"] = totals.get("AMIL", Decimal(0)) + a - f
	clr = CLEARING[gateway]
	lines = []
	for dana, v in totals.items():
		if v == 0:
			continue
		if v < 0:
			raise PostingBlocked(_("Saldo settlement negatif untuk Dana {0}.").format(dana))
		lines.append(_line(co, BANK, v, 0, dana))
		lines.append(_line(co, clr, 0, v, dana))
	je = make_je(f"{settlement_id}:SETTLE", co, posting_date, lines, f"Settlement {settlement_id}", bank_ref=settlement_id)
	for d in dons:
		d.db_set({"settlement_id": settlement_id, "settled": 1})
	return je
