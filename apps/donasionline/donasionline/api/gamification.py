"""/api/donor/gamification*. ASUMSI: rumus poin = total donasi Paid / idr_per_point (rumus server asli TIDAK diketahui; dapat diatur)."""
import frappe
from frappe import _
from frappe.rate_limiter import rate_limit

from donasionline.api._util import current_donor


def points(donor):
	s = frappe.get_single("Pengaturan Gamifikasi")
	per = float(s.idr_per_point or 1) or 1
	total = frappe.db.sql("select coalesce(sum(amount),0) from `tabDonation` where donor=%s and status='Paid'", donor.name)[0][0]
	return max(0, int(float(total) // per) - int(donor.points_spent or 0))


def _levels():
	return frappe.get_all("Level Gamifikasi", ["level_name as name", "threshold", "badge_url as badgeUrl"], order_by="threshold asc")


@frappe.whitelist()
def get():
	d = current_donor()
	s = frappe.get_single("Pengaturan Gamifikasi")
	pts = points(d)
	lv = _levels()
	idx = max([i for i, l in enumerate(lv) if l.threshold <= pts] or [0]) if lv else 0
	cur = lv[idx] if lv else None
	nxt = lv[idx + 1] if lv and idx + 1 < len(lv) else None
	prog = 100 if not nxt else int(100 * (pts - cur.threshold) / max(1, nxt.threshold - cur.threshold))
	rewards = frappe.get_all("Hadiah Gamifikasi", ["name as id", "reward_name as name", "description", "image_url as imageUrl", "category", "point_cost as pointCost", "out_of_stock as outOfStock"])
	for r in rewards:
		r["affordable"] = pts >= r.pointCost and not r.outOfStock
	return {
		"enabled": bool(s.enabled), "claimEnabled": bool(s.claim_enabled), "points": pts,
		"level": {"currentName": cur.name if cur else None, "currentBadge": cur.badgeUrl if cur else None, "currentIndex": idx, "nextName": nxt.name if nxt else None, "nextBadge": nxt.badgeUrl if nxt else None, "nextThreshold": nxt.threshold if nxt else None, "progress": prog},
		"levels": lv, "rewards": rewards,
	}


@frappe.whitelist(methods=["POST"])
@rate_limit(limit=10, seconds=60)
def claim_reward(rewardId, recipientName, phone, address):
	d = current_donor()
	s = frappe.get_single("Pengaturan Gamifikasi")
	if not (s.enabled and s.claim_enabled):
		frappe.throw(_("Penukaran belum dibuka"), frappe.ValidationError)
	r = frappe.get_doc("Hadiah Gamifikasi", rewardId)
	if r.out_of_stock:
		frappe.throw(_("Stok habis"), frappe.ValidationError)
	frappe.db.sql("select name from `tabDonor` where name=%s for update", d.name)  # serialkan potong poin
	d.reload()
	if points(d) < r.point_cost:
		frappe.throw(_("Poin tidak cukup"), frappe.ValidationError)
	for v, label in ((recipientName, "Nama"), (phone, "Telepon"), (address, "Alamat")):
		if not (v or "").strip():
			frappe.throw(_("{0} wajib diisi").format(label), frappe.ValidationError)
	frappe.get_doc({"doctype": "Klaim Hadiah", "reward": r.name, "donor": d.name, "recipient_name": recipientName.strip(), "phone": phone.strip(), "address": address.strip(), "points_spent": r.point_cost, "status": "Diajukan"}).insert(ignore_permissions=True)
	frappe.db.set_value("Donor", d.name, "points_spent", int(d.points_spent or 0) + r.point_cost)
	return {"ok": True}
