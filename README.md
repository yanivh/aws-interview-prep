# AWS Interview Prep Website

A serverless web application to help prepare for AWS Systems Engineer interviews, organized by distinct topics (Linux, Networking, Operational Excellence, Scripting), using AWS Bedrock LLM for question generation and enhanced answer evaluation.

## Architecture

- **Frontend**: Static HTML/CSS/JavaScript hosted on S3
- **Backend**: AWS Lambda functions (Python) with API Gateway
- **LLM**: AWS Bedrock (Claude, Llama, or other available models)
- **Region**: eu-central-1 (Frankfurt)

## Features

1. **Topic-Based Organization**: Linux, Networking, Operational Excellence, Scripting
2. **Difficulty Levels**: Newbie, Intermediate, Pro
3. **Learning Plan**: Structured 8-week curriculum
4. **Question Generation**: Two-step refinement process for high-quality questions
5. **Visual Answer Formatting**: Structured answers with icons, badges, tables, and code blocks
6. **Progress Tracking**: localStorage-based progress tracking
7. **Practice Mode**: Timed practice sessions with answer evaluation
8. **Flashcard Mode**: Quick review of key concepts

## Prerequisites

- AWS Account with appropriate permissions
- AWS CLI configured with credentials
- AWS Bedrock access enabled in eu-central-1
- Python 3.9+ (for Lambda functions)
- boto3, pydantic (see requirements.txt)

## Setup Instructions

### 1. Configure AWS Region

Set default region to eu-central-1:
```bash
aws configure set region eu-central-1
```

### 2. Enable Bedrock Access

Enable Bedrock access in AWS Console:
- Go to AWS Bedrock Console
- Request access to models (e.g., Claude 3 Sonnet)
- Note: Some models may require approval

### 3. Create Bedrock Agent (Optional)

For enhanced answer evaluation:
```bash
# Create agent via AWS Console or CLI
# Note the Agent ID and Alias ID
export BEDROCK_AGENT_ID="your-agent-id"
export BEDROCK_AGENT_ALIAS_ID="TSTALIASID"
```

### 4. Deploy Lambda Function

```bash
cd lambda/deployment
chmod +x package.sh
./package.sh

cd ../../scripts
chmod +x deploy-lambda.sh
export BEDROCK_AGENT_ID="your-agent-id"  # Optional
./deploy-lambda.sh
```

### 5. Deploy API Gateway

```bash
cd scripts
chmod +x deploy-api-gateway.sh
./deploy-api-gateway.sh
```

Note the API Gateway endpoint URL and update `frontend/config.js`:
```javascript
API_ENDPOINT: 'https://your-api-id.execute-api.eu-central-1.amazonaws.com/prod'
```

### 6. Deploy Frontend to S3

```bash
cd scripts
chmod +x deploy-frontend.sh
export S3_BUCKET_NAME="your-bucket-name"
./deploy-frontend.sh
```

### 7. (Optional) Set up CloudFront

1. Create CloudFront distribution pointing to S3 bucket
2. Note the distribution ID
3. Update `deploy-frontend.sh` with distribution ID
4. Re-run deployment script

## Configuration

### Environment Variables

**Lambda Function:**
- `AWS_REGION`: eu-central-1
- `BEDROCK_MODEL_ID`: (optional) Default `anthropic.claude-3-7-sonnet-20250219-v1:0` (Claude 3.7 Sonnet with extended thinking for better questions and explanations). Other reasoning models: Sonnet 4, Opus 4. Enable model in [Bedrock Model Access](https://docs.aws.amazon.com/bedrock/latest/userguide/inference-reasoning.html).
- `BEDROCK_AGENT_ID`: (optional) Your Bedrock Agent ID

**Frontend:**
- Update `frontend/config.js` with API Gateway endpoint

### IAM Roles

Lambda function requires IAM role with:
- Bedrock `InvokeModel` permission
- Bedrock `InvokeAgent` permission (if using agents)
- CloudWatch Logs permissions

See `infrastructure/lambda-role.json` for policy.

## Project Structure

```
interview-prep/
├── lambda/              # Lambda function code
│   ├── lambda_function.py
│   ├── bedrock_service.py
│   ├── aws_context.py
│   ├── models.py
│   └── requirements.txt
├── frontend/            # Static frontend files
│   ├── index.html
│   ├── styles.css
│   ├── app.js
│   └── components/
├── infrastructure/      # Infrastructure configs
│   ├── lambda-role.json
│   ├── s3-bucket-policy.json
│   ├── api-gateway.yaml
│   └── api-gateway-cors.json
└── scripts/             # Deployment scripts
    ├── deploy-lambda.sh
    ├── deploy-api-gateway.sh
    └── deploy-frontend.sh
```

## API Endpoints

- `POST /generate-question` - Generate interview question
- `POST /evaluate-answer` - Evaluate user answer
- `GET /topics` - List available topics
- `GET /flashcard` - Generate flashcard
- `GET /learning-plan` - Get learning plan
- `GET /progress` - Get user progress (optional)
- `POST /progress` - Update user progress (optional)

## Topics Covered

1. **Linux**: Processes, Memory, Disk, Package Management, Boot Process, Daemons, Load Average, Shells, Security Hardening, Troubleshooting
2. **Networking**: TLS, Certificate Validation, Load Balancing, Troubleshooting
3. **Operational Excellence**: Performance, Automation, Incidents, Scale
4. **Scripting**: Log Parsing, System Maintenance, Monitoring, Text Manipulation, User Management

## Development

### Local Testing

For local Lambda testing, use AWS SAM or test framework:
```bash
pip install -r lambda/requirements.txt
python -m pytest tests/  # If tests exist
```

### Frontend Development

Serve locally:
```bash
cd frontend
python -m http.server 8000
# Or use any static file server
```

## Troubleshooting

### Bedrock Access Issues
- Verify Bedrock access is enabled in eu-central-1
- Check model availability in your region
- Verify IAM permissions

### API Gateway CORS Issues
- Check CORS configuration in API Gateway
- Verify allowed origins match S3 bucket URL
- Check browser console for CORS errors

### Lambda Timeout
- Increase timeout for question generation (up to 5 minutes)
- Check CloudWatch logs for errors

## License

MIT

## Support

For issues or questions, please check AWS documentation or CloudWatch logs.
