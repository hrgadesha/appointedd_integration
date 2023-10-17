// Copyright (c) 2023, Hardik Gadesha and contributors
// For license information, please see license.txt

frappe.ui.form.on('Appointedd Integration Settings', {
	sync_appointedd_service_categories: function (frm) {
		frappe.call({
			method: "appointedd_integration.api.get_appointedd_service_categories",
			freeze: true,
			freeze_message: __("Syncing Service Categories......"),
		});
	},
	sync_appointedd_services: function (frm) {
		frappe.call({
			method: "appointedd_integration.api.get_appointedd_services",
			freeze: true,
			freeze_message: __("Syncing Service......"),
		});
	},
	sync_appointedd_resource_groups: function (frm) {
		frappe.call({
			method: "appointedd_integration.api.get_appointedd_resources_groups",
			freeze: true,
			freeze_message: __("Syncing Resources Groups......"),
		});
	},
	sync_appointedd_resource: function (frm) {
		frappe.call({
			method: "appointedd_integration.api.get_appointedd_resources",
			freeze: true,
			freeze_message: __("Syncing Resources......"),
		});
	}
});