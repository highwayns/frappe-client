# Example
# Import job applications from a CSV File (created via Google Forms) to "Job Application"

import csv
from frappeclient import FrappeClient

NAME = 2
EMAIL = 3
INTRODUCTION = 4
THOUGHTS_ON_COMPANY = 5
LIKES = 6
LINKS = 7
PHONE = 8

def sync():
	print("logging in...")
	client = FrappeClient("http://site1.localhost:8000")
	client.authenticate("94c9529d08c0366", "062d009546bdc82")

	with open("jobs.csv", "r", newline='') as jobsfile:
		reader = csv.reader(jobsfile, dialect='excel')
		for row in reader:
			if row[0]=="Timestamp":
				continue

			print("finding " + row[EMAIL])
			name = client.get_value("Job Applicant", "name", {"email_id": row[EMAIL]})

			if name:
				doc = client.get_doc("Job Applicant", name["name"])
			else:
				doc = {"doctype":"Job Applicant"}

			doc["applicant_name"] = row[NAME]
			doc["email_id"] = row[EMAIL]
			doc["introduction"] = row[INTRODUCTION]
			doc["thoughts_on_company"] = row[THOUGHTS_ON_COMPANY]
			doc["likes"] = row[LIKES]
			doc["links"] = row[LINKS]
			doc["phone_number"] = row[PHONE]
			if doc.get("status") != "Rejected":
				doc["status"] = "Open"

			if name:
				client.update(doc)
				print("Updated " + row[EMAIL])
			else:
				client.insert(doc)
				print("Inserted " + row[EMAIL])

if __name__=="__main__":
	sync()
