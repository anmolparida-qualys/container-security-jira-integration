# Container Security → Jira Integration

Automate the creation and management of Jira tickets for vulnerable container images using Qualys APIs — without deploying a separate connector container.

This solution fetches container image vulnerability data using QQL filters, and automatically generates Jira issues for critical findings. Once a Jira issue is created for a vulnerability (QID), the image is *tagged* to prevent duplicate tickets.

---

## 🚀 Features

- 🔎 **Identify high-severity vulnerabilities** (e.g., severity 4 & 5) using Qualys Container Security QQL queries
- 📩 **Create Jira issues automatically** for each unique vulnerability found
- 🔁 **Avoid duplicates** via tagging
- 🐳 Can run as a **containerized automation** or script-based integration

---

## 📦 Repository Contents
├── app/
├── .dockerignore
├── .gitignore
├── Dockerfile
├── README.md
└── requirements.txt



- **app/** – Core Python application and logic  
- **Dockerfile** – Defines container build for running the integration  
- **requirements.txt** – Python dependencies

---

## 🛠️ Prerequisites

Before using this integration, you need:

1. **Qualys Container Security API credentials**
2. **Jira Cloud/Server API token and account**
3. A Jira project where issues will be opened

---

## ⚙️ Configuration

Create a `configurations.py` (or environment variables) with the following:

```json
{
  "jira_domain": "https://yourcompany.atlassian.net",
  "jira_email": "your_email@example.com",
  "jira_api_token": "your_jira_api_token_here",
  "qualys_api_gateway_url": "https://gateway.qg1.apps.qualys.ca",
  "qualys_access_token": "your_qualys_api_token_here",
  "qualys_qql": "vulnerabilities:(severity:5 or severity:4) and not imagesInUse:[now-7d ... now]",
  "qualys_tag": "JiraTicketCreated"
}
```
💡 The Qualys QQL query filters vulnerabilities based on severity and excludes already processed images.

🐳 Running with Docker

Build the image:
```shell
docker build -t container-security-jira-integration .
```

Run with environment variables:
```shell
docker run \
  -e JIRA_DOMAIN="https://yourcompany.atlassian.net" \
  -e JIRA_EMAIL="your_email@example.com" \
  -e JIRA_API_TOKEN="your_jira_api_token" \
  -e QUALYS_API_GATEWAY_URL="https://gateway.qg1.apps.qualys.ca" \
  -e QUALYS_ACCESS_TOKEN="your_qualys_api_token" \
  -e QUALYS_QQL="vulnerabilities:(severity:5 or severity:4) and not imagesInUse:[now-7d ... now]" \
  -e QUALYS_TAG="qualys-tag" \
  container-security-jira-integration
```


This will start the integration and begin processing vulnerability results.

🧪 Usage Examples

Depending on your environment, you could schedule this as:

✔ A Cron job

✔ A GitHub Action / CI workflow

✔ A Kubernetes CronJob

##### Each run will:
- Query Qualys for vulnerabilities 
- Create Jira tickets for unique items
- Tag images to avoid duplicates