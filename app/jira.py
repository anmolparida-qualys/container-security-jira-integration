import json
import configurations

# configurations.py >> config loader
jira_domain = configurations.variables["jira_domain"]
jira_email = configurations.variables["jira_email"]
jira_api_token = configurations.variables["jira_api_token"]

import requests
from requests.auth import HTTPBasicAuth


def check_jira_credentials():
    print("Validating Jira Credentials")
    url = f"{jira_domain}/rest/api/3/myself"

    try:
        response = requests.get(
            url,
            auth=HTTPBasicAuth(jira_email, jira_api_token),
            headers={"Accept": "application/json"}
        )

        if response.status_code != 200:
            print(f"Invalid Jira credentials. Status code: {response.status_code}")
            print(response.text)
            print(f'Please check the values ["jira_domain","jira_email","jira_api_token"]')
        else:
            return True

    except requests.exceptions.RequestException as e:
        print(f"Error connecting to Jira: {e}")
        print(f'Please check the values ["jira_domain","jira_email","jira_api_token"]')
        return False


def create_jira_issue(summary, description_json) -> None:
    json_string = json.dumps(description_json, indent=4)
    payload = {
        "fields": {
            "project": {
                "key": "KAN"
            },
            "summary": summary,
            "issuetype": {
                "name": "Task"
            },
            "labels": [
                "my-label"
            ],
            "description": {
                "type": "doc",
                "version": 1,
                "content": [
                    {
                        "type": "codeBlock",
                        "attrs": {"language": "json"},
                        "content": [
                            {
                                "type": "text",
                                "text": json_string
                            }
                        ]
                    }
                ]
            }
        }
    }

    # Make API request
    response = requests.post(
        url=f"{jira_domain}/rest/api/3/issue",
        headers={
            "Accept": "application/json",
            "Content-Type": "application/json"
        },
        auth=(jira_email, jira_api_token),
        data=json.dumps(payload)
    )

    if response.status_code == 201:
        print(f"JIRA issue [{response.json()["key"]}] created successfully for >> {summary}")
    else:
        print("Failed to create JIRA issue:", response.status_code)
        print(response.text)
