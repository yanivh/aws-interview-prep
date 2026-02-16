#!/bin/bash
# Complete Deployment Script
# Run this script to deploy everything

set -e

REGION="eu-central-1"
BUCKET_NAME="${S3_BUCKET_NAME:-aws-interview-prep-$(date +%s)}"
FUNCTION_NAME="aws-interview-prep-api"

echo "=========================================="
echo "AWS Interview Prep - Deployment Script"
echo "=========================================="
echo ""

# Check AWS CLI
if ! command -v aws &> /dev/null; then
    echo "ERROR: AWS CLI not found. Please install AWS CLI first."
    exit 1
fi

# Check AWS credentials
if ! aws sts get-caller-identity &> /dev/null; then
    echo "ERROR: AWS credentials not configured. Run 'aws configure' first."
    exit 1
fi

# Set region
aws configure set region $REGION
echo "✓ AWS Region set to: $REGION"
echo ""

# Step 1: Create Lambda package
echo "Step 1: Creating Lambda deployment package..."
cd lambda/deployment
chmod +x package.sh
if [ -f package.sh ]; then
    ./package.sh || {
        echo "Creating package manually..."
        cd ..
        mkdir -p deployment/deploy
        cp lambda_function.py bedrock_service.py aws_context.py models.py deployment/deploy/
        pip install -r requirements.txt -t deployment/deploy/ --quiet
        cd deployment/deploy
        zip -r ../../lambda-deployment.zip . -q
        cd ../../..
    }
else
    echo "Package script not found, creating manually..."
    cd ../..
    mkdir -p lambda/deployment/deploy
    cp lambda/*.py lambda/deployment/deploy/ 2>/dev/null || true
    pip install boto3 pydantic botocore -t lambda/deployment/deploy/ --quiet 2>&1 | grep -v "already satisfied" || true
    cd lambda/deployment/deploy
    zip -r ../../lambda-deployment.zip . -q 2>/dev/null || zip -r ../../lambda-deployment.zip . 
    cd ../../..
fi

if [ ! -f lambda/lambda-deployment.zip ]; then
    echo "ERROR: Failed to create Lambda package"
    exit 1
fi

echo "✓ Lambda package created"
echo ""

# Step 2: Deploy Lambda
echo "Step 2: Deploying Lambda function..."
cd scripts
chmod +x deploy-lambda.sh

# Check if function exists
if aws lambda get-function --function-name $FUNCTION_NAME --region $REGION &>/dev/null; then
    echo "Updating existing Lambda function..."
    aws lambda update-function-code \
        --function-name $FUNCTION_NAME \
        --zip-file fileb://../lambda/lambda-deployment.zip \
        --region $REGION > /dev/null
else
    echo "Creating new Lambda function..."
    # This will be handled by deploy-lambda.sh
    ./deploy-lambda.sh || {
        echo "Manual Lambda deployment needed. See DEPLOYMENT_GUIDE.md"
    }
fi

echo "✓ Lambda function deployed"
echo ""

# Step 3: Deploy API Gateway
echo "Step 3: Deploying API Gateway..."
chmod +x deploy-api-gateway.sh
./deploy-api-gateway.sh || {
    echo "API Gateway deployment needs manual setup. See DEPLOYMENT_GUIDE.md"
    API_ENDPOINT=""
}

# Try to get API endpoint
API_ID=$(aws apigateway get-rest-apis --region $REGION --query "items[?name=='aws-interview-prep-api'].id" --output text 2>/dev/null || echo "")
if [ -n "$API_ID" ]; then
    API_ENDPOINT="https://$API_ID.execute-api.$REGION.amazonaws.com/prod"
    echo "✓ API Gateway deployed: $API_ENDPOINT"
else
    echo "⚠ API Gateway endpoint not found. You'll need to set it manually."
    API_ENDPOINT=""
fi
echo ""

# Step 4: Update frontend config
if [ -n "$API_ENDPOINT" ]; then
    echo "Step 4: Updating frontend configuration..."
    cd ../frontend
    # Update config.js with API endpoint
    if [ -f config.js ]; then
        sed -i.bak "s|API_ENDPOINT:.*|API_ENDPOINT: '$API_ENDPOINT',|" config.js
        echo "✓ Frontend config updated with API endpoint"
    fi
    cd ..
fi
echo ""

# Step 5: Deploy Frontend
echo "Step 5: Deploying frontend to S3..."
cd scripts
export S3_BUCKET_NAME=$BUCKET_NAME
chmod +x deploy-frontend.sh
./deploy-frontend.sh || {
    echo "Frontend deployment needs manual setup. See DEPLOYMENT_GUIDE.md"
    FRONTEND_URL=""
}

# Get frontend URL
FRONTEND_URL="http://$BUCKET_NAME.s3-website.$REGION.amazonaws.com"
echo ""
echo "=========================================="
echo "Deployment Complete!"
echo "=========================================="
echo ""
echo "Your application is available at:"
echo "  $FRONTEND_URL"
echo ""
if [ -n "$API_ENDPOINT" ]; then
    echo "API Endpoint:"
    echo "  $API_ENDPOINT"
    echo ""
fi
echo "Next steps:"
echo "1. Verify the website works: $FRONTEND_URL"
echo "2. Test question generation"
echo "3. (Optional) Set up CloudFront for HTTPS"
echo ""
