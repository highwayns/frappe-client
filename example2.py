#-*- coding: utf-8 -*-

from frappeclient import FrappeClient as Client
import os

files = {
	'CRM': [
		'Customer',
		'Address',
		'Contact',
		'Customer Group',
		'Territory',
		'Sales Person',
		'Terms and Conditions',
		'Target Detail',
		'Sales Partner',
		'Opportunity',
		'Lead'
	],
	'Manufacturing': [
		'Production Order',
		'Workstation',
		'Operation',
		'BOM'
	],
	'Selling': [
		'Quotation',
		'Sales Order',
		'Sales Taxes and Charges',
		'Installation Note',
		'Product Bundle',
	],
	'Stock': [
		'Purchase Receipt',
		'Bin',
		'Item',
		'Delivery Note',
		'Material Request',
		'Item Variant',
		'Item Attribute Value',
		'Serial No',
		'Warehouse',
		'Stock Entry',
		'Price List',
		'Item Price',
		'Batch',
		'Landed Cost Voucher'
	],
	'Setup': [
		'UOM',
		'Print Heading',
		'Currency Exchange',
		'Authorization Rule',
		'Authorization Control'
	],
	'Support': [
		'Issue',
		'Warranty Claim',
		'Maintenance Visit'
	],
	'HR': [
		'Employee',
		'Job Applicant',
		'Offer Letter',
		'Salary Structure',
		'Leave Application',
		'Expense Claim',
		'Expense Claim Type',
		'Appraisal',
		'Salary Slip',
		'Holiday',
		'Attendance',
		'Leave Type',
		'Job Opening',
		'Designation',
		'Department',
		'Earning Type',
		'Deduction Type',
		'Branch'
	]
}

def get_path(*args):
	path = os.path.abspath(os.path.join(
		os.path.dirname(__file__), 'ERPNext',
		*args
	))
	if not os.path.exists(path):
		os.makedirs(path)

	return path
import requests

def download_invoice_pdf(base_url, api_key, api_secret, doctype, docname, print_format):
    headers = {
        "Authorization": f"token {api_key}:{api_secret}"
    }
    url = f"{base_url}/api/method/frappe.utils.print_format.download_pdf"
    params = {
        "doctype": doctype,
        "name": docname,
        "format": print_format
    }
    response = requests.get(url, headers=headers, params=params)
    with open(f"{docname}.pdf", "wb") as f:
        f.write(response.content)
    print("✅ PDF 下载完成")


def download():
	c = Client('http://site1.localhost:8000', 'Administrator', 'admin')

	for k,v in list(files.items()):
		for dt in v:
			for s, ext, method in (('Schemes', 'pdf', 'get_pdf'), ('Upload Templates', 'csv', 'get_upload_template')):
				base_path = get_path(k, s)
				with open(os.path.join(base_path, '.'.join([dt, ext])), 'wb') as handler:
					fn = getattr(c, method)
					if ext == 'pdf':
						content = fn('DocType', dt, 'Standard')
					else:
						try:
							content = fn(dt)
						except Exception as e:
							print('Failed to Download: ' + dt)
							continue

					handler.write(content.getvalue())
				print('Downloaded: `{0}` of {1}'.format(ext, dt))

if __name__ == '__main__':
#	download()
# 示例调用
	download_invoice_pdf(
		base_url="http://site1.localhost:8000",
		api_key="94c9529d08c0366",
		api_secret="062d009546bdc82",
		doctype="Sales Invoice",
		docname="SINV-0001",
		print_format="Standard"
	)

