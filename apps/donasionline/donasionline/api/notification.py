"""/api/notifications: amin atas doa milik donor (turunan Doa Amin; FAKTA bell-spec)."""
import frappe
from frappe.utils import now_datetime

from donasionline.api._util import current_donor


@frappe.whitelist(allow_guest=True)
def list_notifications():
	d = current_donor(required=False)
	if not d:
		return {"unread": 0, "items": []}
	rows = frappe.db.sql(
		"""select dn.gateway_order_id doa_id, dn.message, count(*) n, sum(a.delta) total
		from `tabDoa Amin` a join `tabDonation` dn on dn.name=a.donation
		where dn.donor=%s and a.read_at is null group by dn.name order by max(a.creation) desc limit 20""",
		d.name, as_dict=True,
	)
	items = []
	for r in rows:
		names = frappe.db.sql(
			"select distinct a.actor_name from `tabDoa Amin` a join `tabDonation` dn on dn.name=a.donation where dn.gateway_order_id=%s and a.read_at is null and a.actor_name is not null limit 5",
			r.doa_id,
		)
		items.append({"doa_id": r.doa_id, "aminers": [x[0] for x in names], "total_aminers": int(r.total or 0), "message": r.message})
	return {"unread": len(items), "items": items}


@frappe.whitelist(methods=["POST"])
def mark_read():
	d = current_donor()
	frappe.db.sql(
		"update `tabDoa Amin` a join `tabDonation` dn on dn.name=a.donation set a.read_at=%s where dn.donor=%s and a.read_at is null",
		(now_datetime(), d.name),
	)
	return {"ok": True}
