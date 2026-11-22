import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import now_datetime


class Donation(Document):
	def validate(self):
		if self.amount is not None and float(self.amount) <= 0:
			frappe.throw(_("Jumlah donasi harus > 0"))

	def amount_amil_or_zero(self):
		return float(self.amil_amount or 0)

	@frappe.whitelist()
	def mark_paid(self):
		"""Pending -> Paid, lalu E2/E3 bila posting aktif (status hanya maju)."""
		from donasionline import journals

		if self.status not in ("Pending", "Paid"):
			frappe.throw(_("Status {0} tidak bisa dibayar").format(self.status))
		if self.status == "Pending":
			self.db_set({"status": "Paid", "paid_at": self.paid_at or now_datetime()})
			self.reload()
		if self.status == "Paid":
			self._after_paid()
		try:
			journals.post_receipt(self.name)
			journals.post_amil(self.name)
		except journals.PostingBlocked as e:
			frappe.msgprint(str(e), indicator="orange", alert=True)

	def _after_paid(self):
		"""Agregat donor/mitra dan streak Rutin; idempoten (dihitung ulang dari Donation Paid)."""
		from donasionline.api import recurring

		if self.donor:
			r = frappe.db.sql("select count(*), coalesce(sum(amount),0) from `tabDonation` where donor=%s and status='Paid'", self.donor)[0]
			frappe.db.set_value("Donor", self.donor, {"total_count": r[0], "total_amount": r[1]})
		if self.mitra:
			r = frappe.db.sql("select count(distinct kampanye), coalesce(sum(amount),0) from `tabDonation` where mitra=%s and status='Paid'", self.mitra)[0]
			frappe.db.set_value("Mitra", self.mitra, {"campaign_count": r[0], "total_raised": r[1]})
		recurring.on_donation_paid(self)
