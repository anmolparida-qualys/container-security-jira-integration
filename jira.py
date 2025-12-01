import requests
import json
from config_loader import config

# config.json >> config loader
jira_domain = config["jira_domain"]
jira_email = config["jira_email"]
jira_api_token = config["jira_api_token"]


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
