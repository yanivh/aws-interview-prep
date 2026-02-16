# Troubleshooting Guide

## Current Issue: Model Access Error

### Problem
Both `/generate-question` and `/flashcard` endpoints are returning:
```
AccessDeniedException: Model access is denied due to IAM user or service role is not authorized to perform the required AWS Marketplace actions
```

### Important Update
According to the [AWS Bedrock Console](https://eu-central-1.console.aws.amazon.com/bedrock/home?region=eu-central-1#/modelaccess):
- **Model access page has been retired**
- Serverless foundation models are now **automatically enabled** when first invoked
- **For Anthropic models**: First-time users may need to **submit use case details** before accessing the model
- For Marketplace models: A user with Marketplace permissions must invoke once to enable account-wide

### What We've Verified
1. ✅ Lambda code is using correct model ID: `anthropic.claude-3-sonnet-20240229-v1:0`
2. ✅ Lambda environment variable is set correctly
3. ✅ IAM role has `bedrock:InvokeModel` permission for the model
4. ✅ Model exists and is listed in the region

### Solution Steps

#### Option 1: Submit Use Case Details (Recommended for Anthropic Models)
1. Go to AWS Bedrock Console: https://eu-central-1.console.aws.amazon.com/bedrock/
2. Navigate to **Model catalog** or **Playground**
3. Select **Claude 3 Sonnet**
4. When prompted, **submit use case details** (e.g., "Interview preparation application")
5. Wait for approval (usually instant or a few minutes)

#### Option 2: Invoke Model Directly (Triggers Auto-Enable)
Try invoking the model directly from your AWS account (not Lambda) to trigger auto-enablement:

```bash
# Create test payload
echo '{"anthropic_version":"bedrock-2023-05-31","max_tokens":10,"messages":[{"role":"user","content":"test"}]}' | base64 > test-payload.b64

# Invoke model (this may trigger use case submission prompt)
aws bedrock-runtime invoke-model \
  --model-id anthropic.claude-3-sonnet-20240229-v1:0 \
  --region eu-central-1 \
  --body fileb://test-payload.b64 \
  output.json
```

#### Option 3: Use Claude Haiku (Usually No Approval Needed)
Switch to Claude Haiku which typically doesn't require use case approval:

```bash
aws lambda update-function-configuration \
  --function-name aws-interview-prep-api \
  --region eu-central-1 \
  --environment "Variables={BEDROCK_MODEL_ID=anthropic.claude-3-haiku-20240307-v1:0}"
```

### Testing After Fix
Once access is granted, test the API:
```bash
curl -X POST https://s7ow2cvh6i.execute-api.eu-central-1.amazonaws.com/prod/generate-question \
  -H "Content-Type: application/json" \
  -d '{"topic":"linux","subtopic":"processes","difficulty":"newbie"}'
```

### References
- [AWS Bedrock Model Access](https://eu-central-1.console.aws.amazon.com/bedrock/home?region=eu-central-1#/modelaccess)
- [Bedrock Documentation](https://docs.aws.amazon.com/bedrock/)
