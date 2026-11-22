"""Mode gabung: melayani UI Vue hasil build (public/ui) langsung dari Frappe.

- File nyata di public/ui (index.html, ui-assets/*, logo, dst.) dilayani apa adanya.
- Rute SPA (daftar di SPA_ROOTS, ditambah /<slug mitra>) dijawab dengan index.html; routing selanjutnya oleh Vue.
- Rute milik Frappe (/desk, /api, /login, /assets, ...) tidak pernah diambil alih.
"""
import mimetypes
import os

import frappe
from werkzeug.wrappers import Response

from frappe.website.page_renderers.base_renderer import BaseRenderer

# Segmen pertama rute SPA (ui/src/router.js). Ubah di sini bila rute UI bertambah.
SPA_ROOTS = {
	"jalankebaikan", "akun", "auth", "penyaluran", "berita", "artikel", "laporan", "teman", "doa", "video",
	"shadaqa-rutin", "jejak-kebaikan", "public", "syarat-ketentuan", "kebijakan-privasi", "hapus-akun",
	"qurban", "donasi", "campaigns", "mitra", "zakat", "wakaf", "kalkulatorzakat", "en",
}


def ui_dir():
	return frappe.get_app_path("donasionline", "public", "ui")


def _enabled():
	if not os.path.exists(os.path.join(ui_dir(), "index.html")):
		return False
	try:
		return bool(frappe.db.get_single_value("Pengaturan Donasi", "serve_ui"))
	except Exception:
		return False


def _safe_file(rel):
	"""Path file di public/ui, atau None (tolak traversal)."""
	root = os.path.realpath(ui_dir())
	full = os.path.realpath(os.path.join(root, rel))
	if rel and os.path.commonpath([root, full]) == root and os.path.isfile(full):
		return full
	return None


class UiRenderer(BaseRenderer):
	def __init__(self, path=None, http_status_code=None):
		super().__init__(path, http_status_code)
		# path asli permintaan (argumen `path` sudah dipetakan resolver Frappe)
		req = frappe.local.request
		self.req_path = (req.path if req else "").strip("/")
		self.method = req.method if req else "GET"

	def _kind(self):
		if self.method not in ("GET", "HEAD") or not _enabled():
			return None
		rel = self.req_path
		if rel == "index.html":
			return None
		if rel and _safe_file(rel):
			return "file"
		first = rel.split("/")[0]
		if rel == "" or first in SPA_ROOTS:
			return "spa"
		if "/" not in rel and frappe.db.exists("Mitra", {"slug": rel}):
			return "spa"
		return None

	def can_render(self):
		return self._kind() is not None

	def render(self):
		kind = self._kind()
		if kind == "file":
			full = _safe_file(self.req_path)
			ctype = mimetypes.guess_type(full)[0] or "application/octet-stream"
			headers = {"Cache-Control": "public, max-age=31536000, immutable" if self.req_path.startswith("ui-assets/") else "public, max-age=3600"}
		else:
			full = os.path.join(ui_dir(), "index.html")
			ctype = "text/html; charset=utf-8"
			headers = {"Cache-Control": "no-cache"}
		with open(full, "rb") as f:
			data = f.read()
		return Response(data, status=200, mimetype=ctype.split(";")[0], headers={**headers, "Content-Type": ctype})
