#!/bin/bash
# Quick Deployment Script - Run this to deploy everything

set -e

echo "🚀 AWS Interview Prep - Quick Deployment"
echo "========================================"
echo ""

# Configuration
REGION="eu-central-1"
BUCKET_PREFIX="aws-interview-prep-$(whoami)-"
# Use S3_BUCKET_NAME if set; otherwise reuse existing bucket with our prefix or create new
if [ -n "${S3_BUCKET_NAME:-}" ]; then
  BUCKET_NAME="$S3_BUCKET_NAME"
  echo "Using bucket from S3_BUCKET_NAME: $BUCKET_NAME"
else
  EXISTING=$(aws s3api list-buckets --query "Buckets[?starts_with(Name, \`$BUCKET_PREFIX\`)].Name" --output text 2>/dev/null | awk '{print $1}' | head -1)
  if [ -n "$EXISTING" ]; then
    BUCKET_NAME="$EXISTING"
    echo "Reusing existing bucket: $BUCKET_NAME"
  else
    BUCKET_NAME="${BUCKET_PREFIX}$(date +%s)"
    echo "Creating new bucket: $BUCKET_NAME"
  fi
fi
FUNCTION_NAME="aws-interview-prep-api"
STAGE="prod"

# Check prerequisites
echo "📋 Checking prerequisites..."
if ! command -v aws &> /dev/null; then
    echo "❌ AWS CLI not found. Please install: https://aws.amazon.com/cli/"
    exit 1
fi

if ! aws sts get-caller-identity &> /dev/null; then
    echo "❌ AWS credentials not configured. Run: aws configure"
    exit 1
fi

echo "✓ AWS CLI configured"
aws configure set region $REGION
echo "✓ Region set to: $REGION"
echo ""

# Step 1: Create Lambda package
echo "📦 Step 1: Creating Lambda deployment package..."
cd lambda
mkdir -p deployment/deploy
cp lambda_function.py bedrock_service.py aws_context.py models.py deployment/deploy/

echo "Installing dependencies..."
python3 -m pip install boto3 pydantic botocore -t deployment/deploy/ --quiet 2>&1 | grep -v "already satisfied" || pip3 install boto3 pydantic botocore -t deployment/deploy/ --quiet 2>&1 | grep -v "already satisfied" || echo "Note: Dependencies will be installed by Lambda runtime"

cd deployment/deploy
zip -r ../../lambda-deployment.zip . -q
cd ../../..
echo "✓ Lambda package created: lambda/lambda-deployment.zip"
echo ""

# Step 2: Create/Update Lambda Function
echo "⚙️  Step 2: Deploying Lambda function..."
ROLE_NAME="aws-interview-prep-lambda-role"

# Check if role exists, create if not
if ! aws iam get-role --role-name $ROLE_NAME &>/dev/null; then
    echo "Creating IAM role..."
    aws iam create-role \
        --role-name $ROLE_NAME \
        --assume-role-policy-document '{
            "Version": "2012-10-17",
            "Statement": [{
                "Effect": "Allow",
                "Principal": {"Service": "lambda.amazonaws.com"},
                "Action": "sts:AssumeRole"
            }]
        }' > /dev/null
    
    sleep 3
    
    # Attach Bedrock policy
    aws iam put-role-policy \
        --role-name $ROLE_NAME \
        --policy-name BedrockAccess \
        --policy-document file://infrastructure/lambda-role.json
    
    # Attach basic Lambda execution policy
    aws iam attach-role-policy \
        --role-name $ROLE_NAME \
        --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole
    
    echo "✓ IAM role created"
fi

ROLE_ARN=$(aws iam get-role --role-name $ROLE_NAME --query 'Role.Arn' --output text)

# Create or update Lambda
if aws lambda get-function --function-name $FUNCTION_NAME --region $REGION &>/dev/null; then
    echo "Updating Lambda function..."
    aws lambda update-function-code \
        --function-name $FUNCTION_NAME \
        --zip-file fileb://lambda/lambda-deployment.zip \
        --region $REGION > /dev/null
    
    # Wait for update to complete
    echo "Waiting for Lambda update to complete..."
    aws lambda wait function-updated \
        --function-name $FUNCTION_NAME \
        --region $REGION 2>/dev/null || sleep 5
    
    aws lambda update-function-configuration \
        --function-name $FUNCTION_NAME \
        --timeout 300 \
        --memory-size 512 \
        --environment "Variables={BEDROCK_MODEL_ID=anthropic.claude-3-sonnet-20240229-v1:0}" \
        --region $REGION > /dev/null 2>&1 || echo "Configuration update skipped (may already be set)"
else
    echo "Creating Lambda function..."
    aws lambda create-function \
        --function-name $FUNCTION_NAME \
        --runtime python3.11 \
        --role $ROLE_ARN \
        --handler lambda_function.lambda_handler \
        --zip-file fileb://lambda/lambda-deployment.zip \
        --timeout 300 \
        --memory-size 512 \
        --environment "Variables={BEDROCK_MODEL_ID=anthropic.claude-3-sonnet-20240229-v1:0}" \
        --region $REGION > /dev/null
fi

LAMBDA_ARN=$(aws lambda get-function --function-name $FUNCTION_NAME --region $REGION --query 'Configuration.FunctionArn' --output text)
echo "✓ Lambda function deployed: $FUNCTION_NAME"
echo ""

# Step 3: Create API Gateway
echo "🌐 Step 3: Creating API Gateway..."
API_NAME="aws-interview-prep-api"

# Check if API exists
API_ID=$(aws apigateway get-rest-apis --region $REGION --query "items[?name=='$API_NAME'].id" --output text 2>/dev/null || echo "")

if [ -z "$API_ID" ]; then
    echo "Creating new API Gateway..."
    API_ID=$(aws apigateway create-rest-api \
        --name $API_NAME \
        --description "AWS Interview Prep API" \
        --region $REGION \
        --query 'id' \
        --output text)
    
    sleep 2
    
    # Get root resource
    ROOT_ID=$(aws apigateway get-resources \
        --rest-api-id $API_ID \
        --region $REGION \
        --query 'items[?path==`/`].id' \
        --output text)
    
    # Helper function to create endpoint
    create_endpoint() {
        local PATH_PART=$1
        local METHOD=$2
        
        # Check if resource already exists
        local RESOURCE_ID=$(aws apigateway get-resources \
            --rest-api-id $API_ID \
            --region $REGION \
            --query "items[?pathPart=='$PATH_PART'].id" \
            --output text 2>/dev/null || echo "")
        
        if [ -z "$RESOURCE_ID" ]; then
            # Create resource
            RESOURCE_ID=$(aws apigateway create-resource \
                --rest-api-id $API_ID \
                --parent-id $ROOT_ID \
                --path-part $PATH_PART \
                --region $REGION \
                --query 'id' \
                --output text 2>/dev/null || echo "")
        fi
        
        if [ -z "$RESOURCE_ID" ]; then
            echo "Warning: Failed to create/get resource for $PATH_PART"
            return
        fi
        
        # Create method (ignore if exists)
        aws apigateway put-method \
            --rest-api-id $API_ID \
            --resource-id $RESOURCE_ID \
            --http-method $METHOD \
            --authorization-type NONE \
            --region $REGION 2>/dev/null || true
        
        # Set integration
        aws apigateway put-integration \
            --rest-api-id $API_ID \
            --resource-id $RESOURCE_ID \
            --http-method $METHOD \
            --type AWS_PROXY \
            --integration-http-method POST \
            --uri "arn:aws:apigateway:$REGION:lambda:path/2015-03-31/functions/$LAMBDA_ARN/invocations" \
            --region $REGION 2>/dev/null || true
        
        # CORS
        aws apigateway put-method-response \
            --rest-api-id $API_ID \
            --resource-id $RESOURCE_ID \
            --http-method $METHOD \
            --status-code 200 \
            --response-parameters "method.response.header.Access-Control-Allow-Origin=true" \
            --region $REGION 2>/dev/null || true
        
        aws apigateway put-integration-response \
            --rest-api-id $API_ID \
            --resource-id $RESOURCE_ID \
            --http-method $METHOD \
            --status-code 200 \
            --response-parameters '{"method.response.header.Access-Control-Allow-Origin":"'"'"'*'"'"'"}' \
            --region $REGION 2>/dev/null || true
    }
    
    # Create all endpoints
    create_endpoint "generate-question" "POST"
    create_endpoint "evaluate-answer" "POST"
    create_endpoint "topics" "GET"
    create_endpoint "flashcard" "GET"
    create_endpoint "learning-plan" "GET"
    create_endpoint "progress" "GET"
    create_endpoint "progress" "POST"
    
    # Deploy
    aws apigateway create-deployment \
        --rest-api-id $API_ID \
        --stage-name $STAGE \
        --region $REGION > /dev/null
    
    echo "✓ API Gateway created"
else
    echo "API Gateway already exists, creating new deployment..."
    aws apigateway create-deployment \
        --rest-api-id $API_ID \
        --stage-name $STAGE \
        --region $REGION > /dev/null
fi

API_ENDPOINT="https://$API_ID.execute-api.$REGION.amazonaws.com/$STAGE"
echo "✓ API Gateway endpoint: $API_ENDPOINT"

# Grant API Gateway permission
aws lambda add-permission \
    --function-name $FUNCTION_NAME \
    --statement-id apigateway-invoke-$(date +%s) \
    --action lambda:InvokeFunction \
    --principal apigateway.amazonaws.com \
    --source-arn "arn:aws:execute-api:$REGION:*:$API_ID/*/*" \
    --region $REGION 2>/dev/null || echo "Permission may already exist"
echo ""

# Step 4: Update frontend config
echo "📝 Step 4: Updating frontend configuration..."
sed -i.bak "s|API_ENDPOINT:.*|API_ENDPOINT: '$API_ENDPOINT',|" frontend/config.js
echo "✓ Frontend config updated"
echo ""

# Step 5: Deploy Frontend to S3
echo "☁️  Step 5: Deploying frontend to S3..."
if ! aws s3 ls "s3://$BUCKET_NAME" &>/dev/null; then
    echo "Creating S3 bucket..."
    aws s3 mb "s3://$BUCKET_NAME" --region $REGION
    
    # Disable Block Public Access (required for static website hosting)
    echo "Configuring bucket for public access..."
    aws s3api put-public-access-block \
        --bucket $BUCKET_NAME \
        --public-access-block-configuration "BlockPublicAcls=false,IgnorePublicAcls=false,BlockPublicPolicy=false,RestrictPublicBuckets=false" \
        --region $REGION 2>/dev/null || echo "Note: May need manual configuration of Block Public Access"
    
    # Enable static website hosting
    aws s3 website "s3://$BUCKET_NAME" \
        --index-document index.html \
        --error-document index.html \
        --region $REGION
    
    # Set bucket policy
    cat > /tmp/bucket-policy.json <<EOF
{
  "Version": "2012-10-17",
  "Statement": [{
    "Sid": "PublicReadGetObject",
    "Effect": "Allow",
    "Principal": "*",
    "Action": "s3:GetObject",
    "Resource": "arn:aws:s3:::$BUCKET_NAME/*"
  }]
}
EOF
    aws s3api put-bucket-policy \
        --bucket $BUCKET_NAME \
        --policy file:///tmp/bucket-policy.json \
        --region $REGION 2>/dev/null || echo "Warning: Bucket policy may need manual configuration"
    
    echo "✓ S3 bucket created and configured"
fi

# Upload files
aws s3 sync frontend/ "s3://$BUCKET_NAME" \
    --exclude "*.md" \
    --exclude ".git/*" \
    --delete \
    --region $REGION > /dev/null

# Set content types
aws s3 cp "s3://$BUCKET_NAME/index.html" "s3://$BUCKET_NAME/index.html" \
    --content-type "text/html" \
    --metadata-directive REPLACE \
    --region $REGION > /dev/null

aws s3 cp "s3://$BUCKET_NAME/styles.css" "s3://$BUCKET_NAME/styles.css" \
    --content-type "text/css" \
    --metadata-directive REPLACE \
    --region $REGION > /dev/null

FRONTEND_URL="http://$BUCKET_NAME.s3-website.$REGION.amazonaws.com"
echo "✓ Frontend deployed"
echo ""

# Cleanup
rm -f /tmp/bucket-policy.json frontend/config.js.bak 2>/dev/null || true

echo "========================================"
echo "✅ Deployment Complete!"
echo "========================================"
echo ""
echo "🌐 Your Application URL:"
echo "   $FRONTEND_URL"
echo ""
echo "🔗 API Endpoint:"
echo "   $API_ENDPOINT"
echo ""
echo "📋 Next Steps:"
echo "   1. Open the URL in your browser: $FRONTEND_URL"
echo "   2. Test question generation"
echo "   3. (Optional) Set up CloudFront for HTTPS"
echo ""
echo "💡 Note: Save these URLs for future reference!"
echo ""
