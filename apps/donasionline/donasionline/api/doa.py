"""/api/doa*. Doa = Donation.message (paid). Amin dibatasi 10 per pelaku per doa (FAKTA komentar DoaPage.vue; dasar server TAK-TERVERIFIKASI)."""
import frappe
from frappe import _
from frappe.rate_limiter import rate_limit
from frappe.utils import now_datetime

from donasionline.api._util import client_actor, current_donor, mask_name
from donasionline.api.donation import by_public_id

MAX_AMIN = 10


def _row(r):
	name = "Hamba Allah" if r.is_anonymous else mask_name(r.donor_name)  # API publik: nama selalu disamarkan
	return {"id": r.gateway_order_id, "message": r.message, "amin_count": r.amin_count or 0, "is_anonymous": bool(r.is_anonymous), "donor_name": name, "currency": r.currency or "IDR", "amount": r.amount, "paid_at": r.paid_at}


FIELDS = ["gateway_order_id", "message", "amin_count", "is_anonymous", "donor_name", "currency", "amount", "paid_at"]
BASE = {"status": "Paid", "message": ["is", "set"]}


@frappe.whitelist(allow_guest=True)
def list_doa(take=9, skip=0):
	return [_row(r) for r in frappe.get_all("Donation", BASE, FIELDS, order_by="paid_at desc", limit=min(int(take), 30), start=int(skip))]


@frappe.whitelist(allow_guest=True)
def for_amin(limit=12):
	import random

	rows = frappe.get_all("Donation", BASE, FIELDS, order_by="paid_at desc", limit=500)
	random.shuffle(rows)
	return [_row(r) for r in rows[: min(int(limit), 30)]]


@frappe.whitelist(allow_guest=True, methods=["POST"])
@rate_limit(limit=60, seconds=60)
def amin(doa, delta=1):
	d = by_public_id(doa)
	if d.status != "Paid" or not d.message:
		frappe.throw(_("Doa tidak ditemukan"), frappe.DoesNotExistError)
	delta = max(1, min(int(delta), MAX_AMIN))
	donor = current_donor(required=False)
	actor = donor.name if donor else client_actor()
	have = frappe.db.sql("select coalesce(sum(delta),0) from `tabDoa Amin` where donation=%s and actor=%s", (d.name, actor))[0][0]
	delta = min(delta, MAX_AMIN - int(have))
	if delta <= 0:
		return {"ok": True, "capped": True}
	frappe.get_doc({"doctype": "Doa Amin", "donation": d.name, "actor": actor, "actor_name": mask_name(donor.full_name) if donor else None, "delta": delta}).insert(ignore_permissions=True)
	frappe.db.sql("update `tabDonation` set amin_count = coalesce(amin_count,0) + %s where name=%s", (delta, d.name))
	return {"ok": True}
