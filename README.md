
# Qualys Container Security → Jira Integration

This project automates the creation of **Jira issues for container image vulnerabilities** detected by **Qualys Container Security**.  
After Jira tickets are created, the processed images are **tagged in Qualys** to prevent duplicate ticket creation.

The solution supports **three execution modes**:
1. Run directly from the command line (Python)
2. Run as a Docker container
3. Run as an AWS ECS Fargate task using CloudFormation

---

## 📌 Use Cases

### Vulnerability Automation
- Fetch container images using **Qualys QQL**
- Retrieve image-level vulnerabilities (QIDs)
- Create **one Jira ticket per QID**
- Automatically tag images in Qualys after processing

### Security Operations
- Ad-hoc security scans
- CI/CD security enforcement
- Serverless execution using ECS Fargate

---

## 🔐 Configuration Model

- **No hardcoded values**
- **Environment variables only**
- **Secrets injected via env vars or AWS Secrets Manager**

---

## Required Environment Variables

| Variable | Description |
|--------|------------|
| `JIRA_DOMAIN` | Jira domain (e.g. `company.atlassian.net`) |
| `JIRA_EMAIL` | Jira user email |
| `JIRA_API_TOKEN` | Jira API token |
| `QUALYS_API_GATEWAY_URL` | Qualys API base URL |
| `QUALYS_ACCESS_TOKEN` | Qualys access token |
| `QUALYS_QQL` | Qualys QQL filter |
| `QUALYS_TAG` | Qualys tag applied after Jira creation |

---

# 1️⃣ Run from Command Line (Python)

### Create and activate virtual environment

```bash
python3 -m venv venv
source venv/bin/activate
````

### Install dependencies

```bash
pip install -r requirements.txt
```

### Export environment variables

```bash
export JIRA_DOMAIN="company.atlassian.net"
export JIRA_EMAIL="user@company.com"
export JIRA_API_TOKEN="xxxxx"
export QUALYS_API_GATEWAY_URL="https://gateway.qg2.apps.qualys.com"
export QUALYS_ACCESS_TOKEN="xxxxx"
export QUALYS_QQL="severity:5"
export QUALYS_TAG="jira-created"
```

### Run the script

```bash
python3 main.py
```

---

# 2️⃣ Run Using Docker

### Build Docker image

```bash
docker build -t qualys-jira-integration .
```

### Run Docker container with env vars

```bash
docker run --rm \
  -e JIRA_DOMAIN \
  -e JIRA_EMAIL \
  -e JIRA_API_TOKEN \
  -e QUALYS_API_GATEWAY_URL \
  -e QUALYS_ACCESS_TOKEN \
  -e QUALYS_QQL \
  -e QUALYS_TAG \
  qualys-jira-integration
```

> You may also use an `.env` file:
>
> ```bash
> docker run --env-file .env qualys-jira-integration
> ```

---

# 3️⃣ Run on AWS ECS Fargate (CloudFormation)

## Architecture Overview

* Docker image stored in **Amazon ECR**
* Executed as **ECS Fargate task**
* Secrets stored in **AWS Secrets Manager**
* Logs captured in **CloudWatch Logs**

---

## Build and Push Image to ECR (Mac)

```bash
aws ecr get-login-password --region ap-south-1 \
| docker login --username AWS --password-stdin <account-id>.dkr.ecr.ap-south-1.amazonaws.com
```

```bash
docker buildx create --use
docker buildx build \
  --platform linux/amd64 \
  -t <account-id>.dkr.ecr.ap-south-1.amazonaws.com/container-security/jira-integration:v1 \
  --push .
```

---

## Secrets Manager Setup

Create **plaintext secrets** (not JSON):

* `jira-api-token`
* `qualys-access-token`

Each secret must contain **only the raw token value**, without quotes.

---

## Deploy ECS Stack

```bash
aws cloudformation deploy \
  --template-file ecs-stack.yaml \
  --stack-name qualys-jira-integration \
  --capabilities CAPABILITY_NAMED_IAM
```

---

## Run ECS Task

1. Open **AWS ECS Console**
2. Select the cluster
3. Click **Run new task**
4. Launch type: **FARGATE**
5. Select the latest task definition
6. Run task

---

## 📜 Logging

* Logs are available in **CloudWatch Logs**
* Log group: `/ecs/qualys-kcs-jira`
* All stdout/stderr is captured automatically

---

## 🔎 Troubleshooting

| Issue                  | Resolution                                                |
| ---------------------- | --------------------------------------------------------- |
| Image pull error       | Verify ECR tag and execution role permissions             |
| Secrets access denied  | Ensure execution role has `secretsmanager:GetSecretValue` |
| Task exits immediately | Check CloudWatch logs                                     |
| No images returned     | Validate QQL syntax                                       |

---

## ✅ Summary

| Mode        | Usage                         |
| ----------- | ----------------------------- |
| Python CLI  | Local development & debugging |
| Docker      | CI/CD & repeatable runs       |
| ECS Fargate | Production automation         |

---
