
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

## 📄 Config File: `config.json` 

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
