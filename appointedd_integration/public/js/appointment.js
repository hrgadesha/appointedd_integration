// Copyright (c) 2023, Hardik Gadesha and contributors
// For license information, please see license.txt

frappe.ui.form.on('Appointment', {
	refresh: function (frm) {
		frm.add_custom_button(__("Cancel Appointment"), function () {
			frappe.call({
				method: "appointedd_integration.api.cancel_appointedd_booking",
				args : {
					'booking_id' : frm.doc.appointment_id
				},
				freeze: true,
				freeze_message: __("Cancelling Booking......"),
				callback (r) {
					if(r.message){
						frappe.throw(r.message.message)
					}
					else{
						frm.set_value('status', "Closed");
						frm.save();
					}
				}
			});
		});
	}
});