"""/api/gold-price"""
import frappe
from frappe.utils import now_datetime

FALLBACK_GOLD = 2300000  # FAKTA: zakatCalc.js


@frappe.whitelist(allow_guest=True)
def gold_price():
	s = frappe.get_single("Harga Emas")
	price = float(s.price_per_gram or 0)
	return {"pricePerGram": price or FALLBACK_GOLD, "source": s.source or "fallback", "updatedAt": s.updated_label, "fetchedAt": s.fetched_at, "stale": bool(s.stale or not price)}
