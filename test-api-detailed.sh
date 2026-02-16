#!/bin/bash
# Detailed API Gateway test

API_ENDPOINT="https://s7ow2cvh6i.execute-api.eu-central-1.amazonaws.com/prod/generate-question"

echo "Testing API Gateway with detailed output..."
echo ""

# Make request and capture full response
curl -v -X POST "${API_ENDPOINT}" \
  -H "Content-Type: application/json" \
  -H "Origin: http://aws-interview-prep-yanivhamo-1771254018.s3-website.eu-central-1.amazonaws.com" \
  -d '{
    "topic": "linux",
    "subtopic": "processes",
    "difficulty": "intermediate"
  }' \
  -o /tmp/api-response.json \
  -w "\n\nHTTP Status: %{http_code}\n" \
  2>&1 | tee /tmp/api-verbose.log

echo ""
echo "Response body:"
cat /tmp/api-response.json | python3 -m json.tool 2>/dev/null || cat /tmp/api-response.json
echo ""

# Check for specific error patterns
if grep -q "Internal server error" /tmp/api-response.json; then
    echo "❌ Got Internal Server Error"
    echo ""
    echo "Checking verbose log for details:"
    grep -i "x-amzn\|error\|exception" /tmp/api-verbose.log | head -10
    exit 1
elif grep -q "question" /tmp/api-response.json; then
    echo "✅ Success! Response contains question"
    exit 0
else
    echo "❓ Unexpected response"
    exit 1
fi
