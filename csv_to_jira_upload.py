import csv
import requests
from requests.auth import HTTPBasicAuth
from datetime import datetime

# Jira connection details
JIRA_BASE_URL = "https://razorgroupgmbh.atlassian.net"
JIRA_USERNAME = ""
JIRA_API_TOKEN = ""
PROJECT_KEY = "ME"
CONFIG_FILE = r"C:\Users\HridayChhabria\AppData\Local\Microsoft\WindowsApps\Scripts\BulkCreate-configuration-202410081034.txt"
CSV_FILE = r"C:\Users\HridayChhabria\AppData\Local\Microsoft\WindowsApps\Scripts\jira_upload_test_2.csv"

# Parse the configuration file to get field mappings
import json

with open(CONFIG_FILE, "r") as config_file:
    config = json.load(config_file)

field_mappings = config.get("config.field.mappings", {})
delimiter = config.get("config.delimiter", ",")  # Default to comma

# Define the create_issue function
def create_issue(issue_data):
    url = f"https://razorgroupgmbh.atlassian.net/rest/api/3/issue"
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json"
    }

    response = requests.post(url, data=json.dumps(issue_data), headers=headers, auth=HTTPBasicAuth(JIRA_USERNAME, JIRA_API_TOKEN))
    if response.status_code == 201:
        print(f"Issue created: {response.json()['key']}")
    else:
        print(f"Failed to create issue: {response.status_code}")
        print(response.text)

# Read data from CSV and create issues
with open(CSV_FILE, newline='', encoding='utf-8') as csvfile:
    reader = csv.DictReader(csvfile, delimiter=delimiter)
    for row in reader:
        # Ensure the summary is read from the CSV properly
        summary_value = row.get("Summary")
        if summary_value is None or not summary_value.strip():
            summary_value = "Default Summary"

        issue_fields = {
            "fields": {
                "project": {
                    "key": PROJECT_KEY
                },
                "issuetype": {
                    "name": "Task"
                },
                "summary": summary_value
            }
        }

        # Map fields from CSV to Jira issue fields based on config
        for csv_field, jira_field_mapping in field_mappings.items():
            jira_field = jira_field_mapping.get("jira.field")
            existing_field_id = jira_field_mapping.get("existing.custom.field")
            
            if jira_field and csv_field in row and row[csv_field].strip():
                # Handle description as Atlassian Document Format
                if jira_field == "description":
                    issue_fields["fields"][jira_field] = {
                        "type": "doc",
                        "version": 1,
                        "content": [
                            {
                                "type": "paragraph",
                                "content": [
                                    {
                                        "type": "text",
                                        "text": row[csv_field]
                                    }
                                ]
                            }
                        ]
                    }
                # Handle priority as string and set a default value if empty
                elif jira_field == "priority":
                    priority_value = row[csv_field].strip().title()
                    if priority_value:
                        issue_fields["fields"][jira_field] = {"name": priority_value}
                    else:
                        issue_fields["fields"][jira_field] = {"name": "Medium"}  # Default priority
                else:
                    issue_fields["fields"][jira_field] = row[csv_field]
            elif existing_field_id and csv_field in row:
                # Handle date fields in the correct format
                if existing_field_id == "10642":  # Date of BB Loss
                    try:
                        date_obj = datetime.strptime(row[csv_field].strip(), "%d/%m/%Y")
                        issue_fields["fields"][f"customfield_{existing_field_id}"] = date_obj.strftime("%Y-%m-%d")
                    except ValueError:
                        print(f"Invalid date format for Date of BB Loss: {row[csv_field]}")
                else:
                    issue_fields["fields"][f"customfield_{existing_field_id}"] = row[csv_field]

        create_issue(issue_fields)
