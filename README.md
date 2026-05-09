# App Suitability Assessment Tool

A mobile-first serverless web app that assesses whether a mobile app is suitable for a child. The user enters an app name; Claude evaluates it against a set of criteria defined in a prompt file stored in S3.

## Architecture

```
Browser → CloudFront → S3 (frontend: HTML/CSS/JS)
                     → API Gateway → Lambda (Python) → Anthropic API
                                                      → SSM (API key)
                                                      → S3 (SKILL.md prompt)
```

All traffic goes through a single CloudFront domain. The `/api/*` path routes to API Gateway; everything else serves static files from S3.

## Prerequisites

- AWS CLI configured (`aws configure`)
- SAM CLI (`sam --version`)
- Python 3.13+
- An Anthropic API key

## First-time setup

**1. Store your Anthropic API key in SSM**

```powershell
aws ssm put-parameter `
  --name "/app/anthropic-api-key" `
  --value "sk-ant-YOUR-KEY-HERE" `
  --type SecureString `
  --region ap-southeast-2
```

**2. Build and deploy**

```powershell
cd C:\Users\simon\Projects\App-suitability-assessment-tool
sam build
sam deploy --guided
```

Accept the defaults on the first guided deploy. SAM will write the chosen values back to `samconfig.toml`. Note the stack outputs — you'll need the bucket names in the next steps.

**3. Upload the assessment prompt**

```powershell
aws s3 cp prompts/SKILL.md s3://<PromptsBucketName>/SKILL.md --region ap-southeast-2
```

**4. Upload the frontend**

```powershell
aws s3 sync frontend/ s3://<FrontendBucketName>/ --region ap-southeast-2
```

**5. Open the app**

The CloudFront URL is in the stack outputs (`CloudFrontUrl`). Note that CloudFront distributions can take 5–10 minutes to deploy on first creation.

## Updating the assessment criteria

Edit `prompts/SKILL.md` locally, then upload it to S3:

```powershell
aws s3 cp prompts/SKILL.md s3://<PromptsBucketName>/SKILL.md --region ap-southeast-2
```

The Lambda reads `SKILL.md` on cold start and caches it for the lifetime of the container. Changes take effect on the next cold start — typically within minutes under normal traffic.

## Project structure

```
App-suitability-assessment-tool/
├── template.yaml          SAM/CloudFormation template
├── samconfig.toml         Deployment configuration
├── backend/
│   ├── app.py             Lambda handler
│   └── requirements.txt
├── frontend/
│   ├── index.html
│   ├── css/styles.css
│   └── js/app.js
└── prompts/
    └── SKILL.md           Assessment prompt (upload to S3; edit here to update)
```

## Redeployment

After any change to `backend/` or `template.yaml`:

```powershell
sam build && sam deploy
```

Frontend-only changes don't require a SAM deploy — just re-sync to S3:

```powershell
aws s3 sync frontend/ s3://<FrontendBucketName>/ --region ap-southeast-2
```
