import frappe
import requests
from frappe import _
from frappe.client import get_password
import json
import pytz
from datetime import datetime

@frappe.whitelist()
def get_appointedd_api_key():
	api_key = get_password("Appointedd Integration Settings", "Appointedd Integration Settings", "api_key")
	return api_key

@frappe.whitelist()
def get_appointedd_service_categories():
	try:
		api_key = get_appointedd_api_key()
		url = "https://api.appointedd.com/v1/services/categories"

		headers = {
			'X-API-KEY': str(api_key),
			'Accept': 'application/json'
		}

		response = requests.request("GET", url, headers=headers)

		categories = json.loads(response.text)
		insert_appointedd_categories(categories)

	except Exception as error:
		frappe.log_error("Get Appointedd Service Categories Error", str(error))

@frappe.whitelist()
def get_appointedd_services():
	try:
		api_key = get_appointedd_api_key()
		url = "https://api.appointedd.com/v1/services"

		headers = {
			'X-API-KEY': str(api_key),
			'Accept': 'application/json'
		}

		response = requests.request("GET", url, headers=headers)

		services = json.loads(response.text)
		insert_appointedd_services(services)

	except Exception as error:
		frappe.log_error("Get Appointedd Services Error", str(error))

@frappe.whitelist()
def get_appointedd_resources_groups():
	try:
		api_key = get_appointedd_api_key()
		url = "https://api.appointedd.com/v1/resources/groups"

		headers = {
			'X-API-KEY': str(api_key),
			'Accept': 'application/json'
		}

		response = requests.request("GET", url, headers=headers)

		resource_groups = json.loads(response.text)
		insert_appointedd_resource_groups(resource_groups)

	except Exception as error:
		frappe.log_error("Get Appointedd Resource Groups Error", str(error))

@frappe.whitelist()
def get_appointedd_resources():
	try:
		api_key = get_appointedd_api_key()
		url = "https://api.appointedd.com/v1/resources"

		headers = {
			'X-API-KEY': str(api_key),
			'Accept': 'application/json'
		}

		response = requests.request("GET", url, headers=headers)

		resources = json.loads(response.text)
		insert_appointedd_resources(resources)

	except Exception as error:
		frappe.log_error("Get Appointedd Resources Error", str(error))

@frappe.whitelist()
def get_appointedd_bookings():
	try:
		api_key = get_appointedd_api_key()
		url = "https://api.appointedd.com/v1/bookings"

		headers = {
			'X-API-KEY': str(api_key),
			'Accept': 'application/json'
		}

		response = requests.request("GET", url, headers=headers)

		bookings = json.loads(response.text)
		insert_appointedd_bookings(bookings)

	except Exception as error:
		frappe.log_error("Get Appointedd Bookings Error", str(error))

def insert_appointedd_categories(categories):
	for cat in categories.get("data"):
		if not frappe.db.exists('Appointedd Service Category', cat.get("name")):
			service_category = frappe.new_doc('Appointedd Service Category')
			service_category.appointedd_service_category = cat.get("name")
			service_category.appointedd_service_category_id = cat.get("id")
			service_category.flags.ignore_permissions = True
			service_category.flags.ignore_mandatory = True
			service_category.insert()

def insert_appointedd_services(services):
	for service in services.get("data"):
		if not frappe.db.exists('Appointedd Service', service.get("name")):
			service_doc = frappe.new_doc('Appointedd Service')
			service_doc.appointedd_service_category = frappe.db.get_value('Appointedd Service Category', 
				{'appointedd_service_category_id' : service.get("category_id")}, 'name')
			service_doc.appointedd_service = service.get("name")
			service_doc.appointedd_service_id = service.get("id")
			service_doc.description = service.get("description")
			service_doc.booking_type = service.get("booking")["type"]
			service_doc.set("appointedd_service_table", service.get("booking")["durations"])
			service_doc.flags.ignore_permissions = True
			service_doc.flags.ignore_mandatory = True
			service_doc.insert()

def insert_appointedd_resource_groups(resource_groups):
	for res_group in resource_groups.get("data"):
		if not frappe.db.exists('Appointedd Resource Groups', res_group.get("name")):
			res_group_doc = frappe.new_doc('Appointedd Resource Groups')
			res_group_doc.appointedd_resource_group = res_group.get("name")
			res_group_doc.appointedd_resource_group_id = res_group.get("id")
			res_group_doc.flags.ignore_permissions = True
			res_group_doc.flags.ignore_mandatory = True
			res_group_doc.insert()

def insert_appointedd_resources(resources):
	for resource in resources.get("data"):
		services_names = frappe.db.get_all("Appointedd Service", 
			filters={"appointedd_service_id": ["in", resource.get("services")]}, 
			fields=["name as appointedd_service"])
		resource_groups = frappe.db.get_all("Appointedd Resource Groups", 
			filters={"appointedd_resource_group_id": ["in", resource.get("resource_group_ids")]}, 
			fields=["name as appointedd_resource_group"])

		if not frappe.db.exists('Appointedd Resource', resource.get("profile")["name"]):
			resource_doc = frappe.new_doc('Appointedd Resource')
			resource_doc.appointedd_resource = resource.get("profile")["name"]
			resource_doc.appointedd_resource_id = resource.get("id")
			resource_doc.email = resource.get("profile")["email"]
			resource_doc.phone = resource.get("profile")["phone"]
			resource_doc.house_no = resource.get("profile")["address"]["house_no"]
			resource_doc.address_1 = resource.get("profile")["address"]["address_1"]
			resource_doc.address_2 = resource.get("profile")["address"]["address_2"]
			resource_doc.city = resource.get("profile")["address"]["city"]
			resource_doc.postcode = resource.get("profile")["address"]["postcode"]
			resource_doc.set("appointedd_resource_services", services_names)
			resource_doc.set("appointedd_resource_groups_table", resource_groups)
			resource_doc.flags.ignore_permissions = True
			resource_doc.flags.ignore_mandatory = True
			resource_doc.insert()

def insert_appointedd_bookings(bookings):
	time_zone = frappe.defaults.get_defaults().get("time_zone")
	for booking in bookings.get("data"):
		customer = get_customer_data(booking.get("customers"))
		services_name = frappe.db.get_value("Appointedd Service", {"appointedd_service_id": booking.get("service")}, "name")
		resource_name = frappe.db.get_value("Appointedd Resource", {"appointedd_resource_id": booking.get("resource")}, "name")
		start_time_utc = datetime.strptime(booking.get("start"), "%Y-%m-%dT%H:%M:%S.%f%z")
		end_time_utc = datetime.strptime(booking.get("end"), "%Y-%m-%dT%H:%M:%S.%f%z")
		indian_timezone = pytz.timezone(time_zone)
		ist_start_time = start_time_utc.astimezone(indian_timezone)
		ist_end_time = end_time_utc.astimezone(indian_timezone)
		formatted_start_time = ist_start_time.strftime("%Y-%m-%d %H:%M:%S")
		formatted_end_time = ist_end_time.strftime("%Y-%m-%d %H:%M:%S")

		if not frappe.db.exists('Appointment', {"appointment_id" : booking.get("id")}):
			resource_doc = frappe.new_doc('Appointment')
			resource_doc.appointment_id = booking.get("id")
			resource_doc.appointedd_resource = resource_name
			resource_doc.appointedd_service = services_name
			resource_doc.scheduled_time = formatted_start_time
			resource_doc.end_time = formatted_end_time
			resource_doc.price = booking.get("price")
			resource_doc.customer_name = customer.customer_name if customer else None
			resource_doc.customer_phone_number = customer.mobile_no if customer else None
			resource_doc.customer_email = customer.email_id if customer else None
			resource_doc.appointment_with = "Customer" if customer else None
			resource_doc.party = customer.name if customer else None
			resource_doc.flags.ignore_permissions = True
			resource_doc.flags.ignore_mandatory = True
			resource_doc.insert()

def get_customer_data(customers):
	for customer in customers:
		if customer.get("id") and not frappe.db.exists("Customer", {"appointedd_customer_id" : customer.get("id")}):
			customer_id = customer.get("id")
			api_key = get_appointedd_api_key()
			url = "https://api.appointedd.com/v1/customers/{}".format(customer_id)

			headers = {
				'X-API-KEY': str(api_key),
				'Accept': 'application/json'
			}

			try:
				response = requests.get(url, headers=headers)
				response.raise_for_status()  # Check for HTTP errors

				customer_data = json.loads(response.text)
				customer = create_customer(customer_data)
				return customer

			except requests.exceptions.RequestException as e:
				frappe.log_error("Error in Get Customer API request", str(e))

		else:
			if customer.get("id"):
				customer = frappe.get_doc("Customer", {"appointedd_customer_id" : customer.get("id")})
				return customer

def create_customer(customer_data):
	customer_doc = frappe.new_doc('Customer')
	customer_doc.customer_name = customer_data.get("data")["profile"]["firstname"] + " " + customer_data.get("data")["profile"]["lastname"]
	customer_doc.customer_type = "Company"
	customer_doc.appointedd_customer_id = customer_data.get("data")["id"]
	customer_doc.mobile_no = customer_data.get("data")["profile"]["mobile"]
	customer_doc.email_id = customer_data.get("data")["profile"]["email"]
	customer_doc.flags.ignore_permissions = True
	customer_doc.flags.ignore_mandatory = True
	customer_doc.insert()

	return customer_doc

@frappe.whitelist()
def update_appointedd_bookings(booking_id = "65279e22615c41000eee7974", start = "13-10-2023 12:15:00", end = "13-10-2023 12:45:00"):
	time_zone = frappe.defaults.get_defaults().get("time_zone")
	try:
		parsed_start_datetime = datetime.strptime(start, "%d-%m-%Y %H:%M:%S")
		iso_start_format = parsed_start_datetime.isoformat()
		return(iso_start_format)
		# api_key = get_appointedd_api_key()
		# url = "https://api.appointedd.com/v1/bookings/".format(booking_id)

		# payload = json.dumps({
		# 	"ignore_service_assignment": False,
		# 	"ignore_service_schedule": False,
		# 	"send_notifications": True,
		# 	"data": {
		# 		"modified_source": "api",
		# 		"parts": [
		# 			{
		# 				"start": "2023-10-13T12:30:00.000+05:30",
		# 				"end": "2023-10-13T13:00:00.000+05:30"
		# 			}
		# 		]
		# 	},
		# 	"timezone": time_zone
		# })

		# headers = {
		# 	'X-API-KEY': str(api_key),
		# 	'Accept': 'application/json',
		# 	'Content-Type': 'application/json'
		# }

		# response = requests.request("PUT", url, headers=headers, data=payload)

		# bookings = json.loads(response.text)
		# insert_appointedd_bookings(bookings)

	except Exception as error:
		frappe.log_error("Get Appointedd Bookings Error", str(error))