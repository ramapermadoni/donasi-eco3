// Tombol Sembunyikan/Tampilkan per baris (memanggil donasionline.api.doa.sembunyikan / tampilkan).
frappe.query_reports["Moderasi Doa"] = {
	filters: [{ fieldname: "status", label: __("Status"), fieldtype: "Select", options: "\nTampil\nTersembunyi", default: "" }],
	formatter(value, row, column, data, default_formatter) {
		if (column.fieldname === "aksi" && data) {
			const sembunyi = data.status === "Tersembunyi";
			return `<button class="btn btn-xs ${sembunyi ? "btn-default" : "btn-danger"} doa-aksi" data-id="${frappe.utils.escape_html(data.id)}" data-act="${sembunyi ? "tampilkan" : "sembunyikan"}">${sembunyi ? __("Tampilkan") : __("Sembunyikan")}</button>`;
		}
		return default_formatter(value, row, column, data);
	},
	onload(report) {
		report.page.main.off("click.doa").on("click.doa", ".doa-aksi", function () {
			const id = this.dataset.id, act = this.dataset.act;
			const kirim = (alasan) => frappe.call({ method: "donasionline.api.doa." + act, args: { donation_id: id, alasan }, freeze: true }).then(() => report.refresh());
			if (act === "sembunyikan") frappe.prompt({ fieldname: "alasan", label: __("Alasan (wajib)"), fieldtype: "Small Text", reqd: 1 }, (v) => kirim(v.alasan), __("Sembunyikan doa dari publik"), __("Sembunyikan"));
			else kirim();
		});
	},
};
