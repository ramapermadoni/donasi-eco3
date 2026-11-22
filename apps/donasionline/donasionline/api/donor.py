"""/api/donor/*"""
import frappe
from frappe import _

from donasionline.api._util import current_donor


@frappe.whitelist()
def stats():
	d = current_donor()
	r = frappe.db.sql(
		"select count(*), coalesce(sum(amount),0), min(paid_at) from `tabDonation` where donor=%s and status='Paid'", d.name
	)[0]
	return {"totalCount": r[0], "totalAmount": float(r[1]), "firstDonatedAt": r[2], "donorSince": d.donor_since}


@frappe.whitelist()
def donations():
	d = current_donor()
	rows = frappe.get_all(
		"Donation",
		{"donor": d.name},
		["gateway_order_id", "amount", "currency", "idr_equivalent", "status", "kampanye", "campaign_title", "paid_at", "creation", "payment_method"],
		order_by="creation desc",
		limit=200,
	)
	return [
		{
			"id": r.gateway_order_id, "amount": r.amount, "currency": r.currency or "IDR", "idr_equivalent": r.idr_equivalent or r.amount,
			"status": (r.status or "").lower(), "campaign": {"title": r.campaign_title}, "paid_at": r.paid_at, "created_at": r.creation,
			"payment_channel": r.payment_method,
		}
		for r in rows
	]


@frappe.whitelist()
def my_doa():
	d = current_donor()
	rows = frappe.get_all("Donation", {"donor": d.name, "message": ["is", "set"], "status": "Paid"}, ["name", "gateway_order_id", "message", "amin_count"], order_by="paid_at desc", limit=50)
	out = []
	for r in rows:
		names = frappe.get_all("Doa Amin", {"donation": r.name}, pluck="actor_name", distinct=True)
		out.append({"id": r.gateway_order_id, "message": r.message, "amin_count": r.amin_count or 0, "aminers": [n for n in names if n]})
	return {"doas": out}


@frappe.whitelist(methods=["POST", "PATCH"])
def update_profile(full_name, email=None):
	d = current_donor()
	full_name = (full_name or "").strip()
	if len(full_name) < 2:
		frappe.throw(_("Nama minimal 2 huruf"), frappe.ValidationError)
	d.full_name = full_name
	d.email = (email or "").strip() or None
	d.save(ignore_permissions=True)
	return {"ok": True, "user": {"name": d.full_name, "email": d.email}}
