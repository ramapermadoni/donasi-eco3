app_name = "donasionline"
app_title = "Donasi Online"
app_publisher = "Donasi Online"
app_description = "Akuntansi dana ZIS (PSAK 409/109, 401/101) di ERPNext"
app_email = "noreply@example.com"
app_license = "mit"
required_apps = ["erpnext"]

after_install = "donasionline.setup.install.after_install"

doc_events = {
	"Journal Entry": {
		"before_submit": "donasionline.guards.validate_dana_balance",
	},
}

scheduler_events = {
	"daily": [
		"donasionline.api.recurring.run_due",
		"donasionline.api.recurring.purge_logs",
	],
}
