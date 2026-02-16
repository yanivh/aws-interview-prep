#!/bin/bash
# Test Lambda function directly

echo "Testing Lambda function directly..."
echo ""

# Create test event
cat > /tmp/test-event.json << 'EOF'
{
  "httpMethod": "POST",
  "path": "/generate-question",
  "body": "{\"topic\":\"linux\",\"subtopic\":\"processes\",\"difficulty\":\"intermediate\"}",
  "headers": {
    "Content-Type": "application/json"
  }
}
EOF

# Invoke Lambda
aws lambda invoke \
  --function-name aws-interview-prep-api \
  --region eu-central-1 \
  --payload file:///tmp/test-event.json \
  /tmp/lambda-response.json \
  2>&1

echo ""
echo "Lambda Response:"
cat /tmp/lambda-response.json | python3 -m json.tool 2>/dev/null || cat /tmp/lambda-response.json
echo ""

# Check for errors in response
if python3 << 'PYEOF'
import json
with open('/tmp/lambda-response.json', 'r') as f:
    data = json.load(f)
    if 'errorMessage' in data:
        print(f"❌ Lambda Error: {data.get('errorMessage')}")
        if 'stackTrace' in data:
            print("\nStack Trace:")
            for line in data['stackTrace'][:10]:
                print(f"  {line}")
        exit(1)
    elif 'statusCode' in data:
        body = json.loads(data.get('body', '{}'))
        if data.get('statusCode') == 200:
            print("✅ Lambda returned 200")
            if 'question' in body:
                print(f"✅ Question: {body['question'][:100]}...")
                exit(0)
            else:
                print(f"❌ Missing question in response. Got: {list(body.keys())}")
                exit(1)
        else:
            print(f"❌ Lambda returned status {data.get('statusCode')}")
            print(f"Body: {body}")
            exit(1)
    else:
        print(f"❌ Unexpected response format: {list(data.keys())}")
        exit(1)
PYEOF
then
    echo "✅ Lambda test PASSED"
    exit 0
else
    echo "❌ Lambda test FAILED"
    exit 1
fi
