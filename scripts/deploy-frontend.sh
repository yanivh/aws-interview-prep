#!/bin/bash
# Frontend Deployment Script for S3

set -e

BUCKET_NAME="${S3_BUCKET_NAME:-aws-interview-prep-frontend}"
REGION="eu-central-1"
DISTRIBUTION_ID="${CLOUDFRONT_DISTRIBUTION_ID:-}"

echo "Deploying frontend to S3 bucket: $BUCKET_NAME"

# Check if bucket exists
if ! aws s3 ls "s3://$BUCKET_NAME" &>/dev/null; then
    echo "Creating S3 bucket..."
    aws s3 mb "s3://$BUCKET_NAME" --region $REGION
    
    # Enable static website hosting
    aws s3 website "s3://$BUCKET_NAME" \
        --index-document index.html \
        --error-document index.html \
        --region $REGION
    
    # Set bucket policy for public read
    aws s3api put-bucket-policy \
        --bucket $BUCKET_NAME \
        --policy file://../infrastructure/s3-bucket-policy.json \
        --region $REGION
    
    echo "Bucket created and configured for static website hosting"
fi

# Upload files
echo "Uploading frontend files..."
aws s3 sync ../frontend/ "s3://$BUCKET_NAME" \
    --exclude "*.md" \
    --exclude ".git/*" \
    --delete \
    --region $REGION

# Set content types
aws s3 cp "s3://$BUCKET_NAME/index.html" "s3://$BUCKET_NAME/index.html" \
    --content-type "text/html" \
    --metadata-directive REPLACE \
    --region $REGION

aws s3 cp "s3://$BUCKET_NAME/styles.css" "s3://$BUCKET_NAME/styles.css" \
    --content-type "text/css" \
    --metadata-directive REPLACE \
    --region $REGION

# Set cache control for static assets
aws s3 sync ../frontend/components/ "s3://$BUCKET_NAME/components/" \
    --cache-control "max-age=31536000" \
    --region $REGION

echo "Frontend deployed successfully!"
echo "Website URL: http://$BUCKET_NAME.s3-website.$REGION.amazonaws.com"

# Invalidate CloudFront if distribution ID is provided
if [ -n "$DISTRIBUTION_ID" ]; then
    echo "Invalidating CloudFront distribution..."
    aws cloudfront create-invalidation \
        --distribution-id $DISTRIBUTION_ID \
        --paths "/*" \
        --region $REGION
    echo "CloudFront cache invalidated"
fi
