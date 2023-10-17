// Copyright (c) 2023, Hardik Gadesha and contributors
// For license information, please see license.txt

frappe.ui.form.on('Appointment', {
	refresh: function (frm) {
		frm.add_custom_button(__("Update Appointment"), function () {
			frappe.call({
				method: "appointedd_integration.api.update_appointedd_bookings",
				args : {
					'booking_id' : frm.doc.appointment_id,
					'start' : frm.doc.scheduled_time,
					'end' : frm.doc.end_time
				},
				freeze: true,
				freeze_message: __("Updating Booking......"),
				callback (r) {
					console.log(r.message)
				}
			});
		});
	}
});