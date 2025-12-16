
## Image Vulnerability Management – Jira Ticket Automation

This repository provides an automated workflow for creating and managing Jira tickets for vulnerable container images **without requiring customers to deploy a container-based connector**. The solution relies on QQL-based filtering to detect high-severity vulnerabilities and automatically openQID based Jira tickets.

---

## 🔎 Use Case
- Identify container images with a specific QQL i.e. with high-severity vulnerabilities  
- Automatically create Jira tickets per vulnerability (QID)  
- Once Jira issue is created for all QIDs tag the image to avoid duplicate ticket creation   


```qql
vulnerabilities:(severity:5 or severity:4) and not imagesInUse:`[now-7d ... now]` and not tags.name: <qualys_tag> 
```

## 📄 Configurations File: `configurations.py` 

```json
{
  "jira_domain": "https://yourcompany.atlassian.net",
  "jira_email": "your_email@example.com",
  "jira_api_token": "your_jira_api_token_here",
  "qualys_api_gateway_url": "example https://gateway.qg1.apps.qualys.ca",
  "qualys_access_token": "your_qualys_api_token_here",
  "qualys_qql": "vulnerabilities:(severity:5 or severity:4) and not imagesInUse:[now-7d ... now]",
  "qualys_tag": "JiraTest1"
}
```


## How to containerize
```shell
docker run -p 8080:8080 \
  -e JIRA_DOMAIN="https://yourcompany.atlassian.net" \
  -e JIRA_EMAIL="your_email@example.com" \
  -e JIRA_API_TOKEN="your_jira_api_token_here" \
  -e QUALYS_API_GATEWAY_URL="https://gateway.qg1.apps.qualys.ca" \
  -e QUALYS_ACCESS_TOKEN="your_qualys_api_token_here" \
  -e QUALYS_QQL="vulnerabilities:(severity:5 or severity:4) and not imagesInUse:[now-7d ... now]" \
  -e QUALYS_TAG="JiraTest1" \
  your-image-name
```