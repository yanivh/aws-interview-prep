#!/bin/bash
# API Gateway Deployment Script

set -e

REGION="eu-central-1"
API_NAME="aws-interview-prep-api"
STAGE="prod"
LAMBDA_FUNCTION_NAME="aws-interview-prep-api"

echo "Deploying API Gateway to $REGION..."

# Get Lambda function ARN
LAMBDA_ARN=$(aws lambda get-function \
    --function-name $LAMBDA_FUNCTION_NAME \
    --region $REGION \
    --query 'Configuration.FunctionArn' \
    --output text)

echo "Lambda ARN: $LAMBDA_ARN"

# Check if API exists
API_ID=$(aws apigateway get-rest-apis \
    --region $REGION \
    --query "items[?name=='$API_NAME'].id" \
    --output text)

if [ -z "$API_ID" ]; then
    echo "Creating new API Gateway..."
    API_ID=$(aws apigateway create-rest-api \
        --name $API_NAME \
        --description "AWS Interview Prep API" \
        --region $REGION \
        --query 'id' \
        --output text)
    
    echo "API created with ID: $API_ID"
    
    # Get root resource ID
    ROOT_RESOURCE_ID=$(aws apigateway get-resources \
        --rest-api-id $API_ID \
        --region $REGION \
        --query 'items[?path==`/`].id' \
        --output text)
    
    # Create resources and methods
    create_endpoint $API_ID $ROOT_RESOURCE_ID "generate-question" "POST"
    create_endpoint $API_ID $ROOT_RESOURCE_ID "evaluate-answer" "POST"
    create_endpoint $API_ID $ROOT_RESOURCE_ID "topics" "GET"
    create_endpoint $API_ID $ROOT_RESOURCE_ID "flashcard" "GET"
    create_endpoint $API_ID $ROOT_RESOURCE_ID "learning-plan" "GET"
    create_endpoint $API_ID $ROOT_RESOURCE_ID "progress" "GET"
    create_endpoint $API_ID $ROOT_RESOURCE_ID "progress" "POST"
    
    # Deploy API
    aws apigateway create-deployment \
        --rest-api-id $API_ID \
        --stage-name $STAGE \
        --region $REGION
    
    echo "API Gateway deployed!"
    echo "Endpoint: https://$API_ID.execute-api.$REGION.amazonaws.com/$STAGE"
else
    echo "API Gateway already exists with ID: $API_ID"
    echo "Creating new deployment..."
    aws apigateway create-deployment \
        --rest-api-id $API_ID \
        --stage-name $STAGE \
        --region $REGION
fi

# Grant API Gateway permission to invoke Lambda
echo "Granting API Gateway permission to invoke Lambda..."
aws lambda add-permission \
    --function-name $LAMBDA_FUNCTION_NAME \
    --statement-id apigateway-invoke \
    --action lambda:InvokeFunction \
    --principal apigateway.amazonaws.com \
    --source-arn "arn:aws:execute-api:$REGION:*:$API_ID/*/*" \
    --region $REGION || echo "Permission may already exist"

echo "API Gateway deployment complete!"
echo "Update frontend/config.js with endpoint: https://$API_ID.execute-api.$REGION.amazonaws.com/$STAGE"

function create_endpoint() {
    local API_ID=$1
    local PARENT_ID=$2
    local PATH=$3
    local METHOD=$4
    
    # Create resource
    RESOURCE_ID=$(aws apigateway create-resource \
        --rest-api-id $API_ID \
        --parent-id $PARENT_ID \
        --path-part $PATH \
        --region $REGION \
        --query 'id' \
        --output text)
    
    # Create method
    aws apigateway put-method \
        --rest-api-id $API_ID \
        --resource-id $RESOURCE_ID \
        --http-method $METHOD \
        --authorization-type NONE \
        --region $REGION
    
    # Set up Lambda integration
    aws apigateway put-integration \
        --rest-api-id $API_ID \
        --resource-id $RESOURCE_ID \
        --http-method $METHOD \
        --type AWS_PROXY \
        --integration-http-method POST \
        --uri "arn:aws:apigateway:$REGION:lambda:path/2015-03-31/functions/$LAMBDA_ARN/invocations" \
        --region $REGION
    
    # Enable CORS
    aws apigateway put-method-response \
        --rest-api-id $API_ID \
        --resource-id $RESOURCE_ID \
        --http-method $METHOD \
        --status-code 200 \
        --response-parameters "method.response.header.Access-Control-Allow-Origin=true" \
        --region $REGION
    
    aws apigateway put-integration-response \
        --rest-api-id $API_ID \
        --resource-id $RESOURCE_ID \
        --http-method $METHOD \
        --status-code 200 \
        --response-parameters '{"method.response.header.Access-Control-Allow-Origin":"'"'"'*'"'"'"}' \
        --region $REGION
}
