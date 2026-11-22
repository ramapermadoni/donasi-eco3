"""Kontrol keuangan buatan sendiri (docs/psak/05 D0). USULAN/PROVISIONAL.

ERPNext TIDAK menegakkan keseimbangan debit-kredit per nilai dimensi Dana.
Hook ini menolak Journal Entry yang tidak seimbang per Dana.
"""

from decimal import Decimal

import frappe
from frappe import _

DANA_FIELD = "dana"


def _d(v):
	return Decimal(str(v or 0))


def dana_imbalances(accounts):
	"""Kembalikan {dana: debit-kredit} untuk baris yang tidak nol. Dana kosong ditulis '(kosong)'."""
	totals = {}
	for row in accounts:
		key = row.get(DANA_FIELD) or "(kosong)"
		totals[key] = totals.get(key, Decimal(0)) + _d(row.get("debit_in_account_currency") or row.get("debit")) - _d(
			row.get("credit_in_account_currency") or row.get("credit")
		)
	return {k: v for k, v in totals.items() if v != 0}


def validate_dana_balance(doc, method=None):
	"""before_submit Journal Entry: jumlah debit - kredit per Dana harus nol."""
	if doc.get("skip_dana_balance"):
		return
	bad = dana_imbalances(doc.accounts)
	if bad:
		detail = ", ".join(f"{k}: {v:,.2f}" for k, v in sorted(bad.items()))
		frappe.throw(
			_("Journal Entry tidak seimbang per Dana ({0}). Setiap Dana harus seimbang sendiri.").format(detail),
			title=_("Keseimbangan per Dana"),
		)
