# Quick Deployment Guide

Follow these steps to deploy the application and get your link.

## Prerequisites Check

```bash
# Verify AWS CLI is working
aws --version
aws configure get region

# Should show: eu-central-1
# If not, set it:
aws configure set region eu-central-1
```

## Step 1: Create Lambda Deployment Package

```bash
cd lambda/deployment
chmod +x package.sh
./package.sh
cd ../..
```

## Step 2: Deploy Lambda Function

```bash
cd scripts
chmod +x deploy-lambda.sh

# Optional: Set Bedrock Agent ID if you created one
export BEDROCK_AGENT_ID="your-agent-id"

./deploy-lambda.sh
```

**Note the Lambda function ARN from the output.**

## Step 3: Deploy API Gateway

```bash
chmod +x deploy-api-gateway.sh
./deploy-api-gateway.sh
```

**IMPORTANT: Note the API Gateway endpoint URL from the output.**
It will look like: `https://abc123xyz.execute-api.eu-central-1.amazonaws.com/prod`

## Step 4: Update Frontend Config

Edit `frontend/config.js` and update the API_ENDPOINT:

```javascript
API_ENDPOINT: 'https://YOUR_API_ID.execute-api.eu-central-1.amazonaws.com/prod'
```

## Step 5: Deploy Frontend to S3

```bash
# Choose a unique bucket name (must be globally unique)
export S3_BUCKET_NAME="aws-interview-prep-$(date +%s)"

chmod +x deploy-frontend.sh
./deploy-frontend.sh
```

**Note the website URL from the output.**
It will look like: `http://YOUR_BUCKET_NAME.s3-website.eu-central-1.amazonaws.com`

## Step 6: (Optional) Set up CloudFront

1. Go to CloudFront Console
2. Create distribution pointing to your S3 bucket
3. Use the CloudFront URL instead of S3 URL

## Your Application Link

After deployment, your application will be available at:

**S3 Website URL:**
```
http://YOUR_BUCKET_NAME.s3-website.eu-central-1.amazonaws.com
```

**Or CloudFront URL (if configured):**
```
https://YOUR_DISTRIBUTION_ID.cloudfront.net
```

## Troubleshooting

### If Lambda deployment fails:
- Check IAM permissions
- Verify Bedrock access is enabled in eu-central-1
- Check CloudWatch logs for errors

### If API Gateway fails:
- Ensure Lambda function exists first
- Check IAM permissions for API Gateway
- Verify CORS configuration

### If S3 deployment fails:
- Ensure bucket name is globally unique
- Check S3 bucket policy permissions
- Verify static website hosting is enabled

## Quick Test

After deployment, test the API:

```bash
curl -X POST https://YOUR_API_ID.execute-api.eu-central-1.amazonaws.com/prod/generate-question \
  -H "Content-Type: application/json" \
  -d '{"topic":"linux","subtopic":"processes","difficulty":"newbie"}'
```

## Next Steps

1. Update `frontend/config.js` with your API endpoint
2. Re-deploy frontend: `./deploy-frontend.sh`
3. Access your website at the S3 or CloudFront URL
