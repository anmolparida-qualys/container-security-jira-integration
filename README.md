Jira ticket for image vulnerability management: 

Use Case: 

Customers don’t want to go with creating the container based connector for creating the JIRA ticket creation, customer is not comfortable to spin up the docker instance in their environment.  

 

Initial Proposed solution: 

So, we are proposing below approach 

We would be initially filtering the images using a QQL token like, 

 vulnerabilities:(severity:5 or severity:4) and imagesInUse:`[now-7d ... now]` 

Based on the filtered listed images, we would be creating a JIRA ticket for each vulnerability and post creations of the respective JIRA tickets we would be tagging the respective image as “Jira_ticket”. 

This tagging will help to identify as to for how many images the JIRA tickets have been created. 

While closing the ticket, we will close the JIRA ticket based on the QQL token as below, 

vulnerabilities:(severity:5 or severity:4) and not imagesInUse:`[now-7d ... now]` and tags.name: Jira_ticket 


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