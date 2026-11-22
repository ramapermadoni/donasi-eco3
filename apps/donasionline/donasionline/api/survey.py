"""/api/satisfaction-survey. Server memilih pertanyaan ACAK; id donasi apa pun tetap 200 (FAKTA survey-spec bag. 2)."""
import frappe
from frappe import _
from frappe.rate_limiter import rate_limit


@frappe.whitelist(allow_guest=True)
def get(donation=None, lang="id"):
	import random

	names = frappe.get_all("Survei Kepuasan", {"enabled": 1, "lang": lang if lang in ("id", "en") else "id"}, pluck="name")
	if not names:
		return {"enabled": False}
	s = frappe.get_doc("Survei Kepuasan", random.choice(names))
	return {
		"enabled": True, "surveyId": s.name, "title": s.title, "imageUrl": s.image_url, "scale": [{"emoji": i.emoji, "label": i.label} for i in s.scale],
		"commentEnabled": bool(s.comment_enabled), "commentPrompt": s.comment_prompt, "question": {"id": s.name, "text": s.question_text},
	}


@frappe.whitelist(allow_guest=True, methods=["POST"])
@rate_limit(limit=10, seconds=60)
def submit(surveyId, rating, comment=None, donationId=None, questionId=None):
	if not frappe.db.exists("Survei Kepuasan", surveyId):
		frappe.throw(_("Survei tidak ditemukan"), frappe.DoesNotExistError)
	n = len(frappe.get_doc("Survei Kepuasan", surveyId).scale)
	rating = int(rating)
	if not 1 <= rating <= max(n, 1):
		frappe.throw(_("Nilai di luar skala"), frappe.ValidationError)
	dn = frappe.db.get_value("Donation", {"gateway_order_id": donationId}) if donationId else None
	frappe.get_doc({"doctype": "Jawaban Survei", "survey": surveyId, "rating": rating, "comment": (comment or "")[:1000] or None, "donation": dn}).insert(ignore_permissions=True)
	return {"ok": True}
