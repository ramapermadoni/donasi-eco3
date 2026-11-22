"""Pengiriman OTP/pengingat. Kanal belum diputuskan (WORK-ORDER W0): bawaan hanya mencatat log, TIDAK mengirim ke luar."""
import frappe


def send_otp(phone, code):
	if frappe.local.conf.get("donasionline_otp_dev_echo"):
		return
	frappe.logger("donasionline").info("OTP dibuat untuk %s (belum ada gateway WA/email dikonfigurasi)", phone[-4:])


def send_reminder(donor, text, channel):
	frappe.logger("donasionline").info("Pengingat %s untuk %s (gateway belum dikonfigurasi)", channel, donor)
	return False
