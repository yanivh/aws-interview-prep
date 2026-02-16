#!/bin/bash
# Lambda Deployment Script

set -e

REGION="eu-central-1"
FUNCTION_NAME="aws-interview-prep-api"
ROLE_NAME="aws-interview-prep-lambda-role"
ZIP_FILE="lambda-deployment.zip"

echo "Deploying Lambda function to $REGION..."

# Check if function exists
if aws lambda get-function --function-name $FUNCTION_NAME --region $REGION &>/dev/null; then
    echo "Updating existing function..."
    aws lambda update-function-code \
        --function-name $FUNCTION_NAME \
        --zip-file fileb://$ZIP_FILE \
        --region $REGION
    
    echo "Updating function configuration..."
    aws lambda update-function-configuration \
        --function-name $FUNCTION_NAME \
        --timeout 300 \
        --memory-size 512 \
        --environment Variables="{
            AWS_REGION=$REGION,
            BEDROCK_MODEL_ID=anthropic.claude-3-sonnet-20240229-v1:0,
            BEDROCK_AGENT_ID=${BEDROCK_AGENT_ID:-}
        }" \
        --region $REGION
else
    echo "Creating new function..."
    
    # Create IAM role if it doesn't exist
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
            }' \
            --region $REGION
        
        # Attach policies
        aws iam put-role-policy \
            --role-name $ROLE_NAME \
            --policy-name BedrockAccess \
            --policy-document file://../infrastructure/lambda-role.json \
            --region $REGION
        
        # Wait for role to be available
        sleep 5
    fi
    
    ROLE_ARN=$(aws iam get-role --role-name $ROLE_NAME --query 'Role.Arn' --output text)
    
    aws lambda create-function \
        --function-name $FUNCTION_NAME \
        --runtime python3.11 \
        --role $ROLE_ARN \
        --handler lambda_function.lambda_handler \
        --zip-file fileb://$ZIP_FILE \
        --timeout 300 \
        --memory-size 512 \
        --environment Variables="{
            AWS_REGION=$REGION,
            BEDROCK_MODEL_ID=anthropic.claude-3-sonnet-20240229-v1:0,
            BEDROCK_AGENT_ID=${BEDROCK_AGENT_ID:-}
        }" \
        --region $REGION
fi

echo "Lambda function deployed successfully!"
