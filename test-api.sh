#!/bin/bash
# Test script for generate-question API endpoint

set -e

API_ENDPOINT="https://s7ow2cvh6i.execute-api.eu-central-1.amazonaws.com/prod"
REGION="eu-central-1"

echo "🧪 Testing Generate Question API"
echo "================================"
echo ""

# Test 1: OPTIONS preflight
echo "Test 1: OPTIONS preflight request..."
OPTIONS_RESPONSE=$(curl -s -o /tmp/options-response.txt -w "%{http_code}" -X OPTIONS \
  "${API_ENDPOINT}/generate-question" \
  -H "Origin: http://aws-interview-prep-yanivhamo-1771254018.s3-website.eu-central-1.amazonaws.com" \
  -H "Access-Control-Request-Method: POST" \
  -H "Access-Control-Request-Headers: Content-Type")

if [ "$OPTIONS_RESPONSE" = "200" ]; then
    echo "✅ OPTIONS request: PASSED (Status: $OPTIONS_RESPONSE)"
    CORS_HEADERS=$(cat /tmp/options-response.txt | grep -i "access-control" || echo "")
    if [ -n "$CORS_HEADERS" ]; then
        echo "   CORS headers present"
    fi
else
    echo "❌ OPTIONS request: FAILED (Status: $OPTIONS_RESPONSE)"
    cat /tmp/options-response.txt
    exit 1
fi
echo ""

# Test 2: POST request
echo "Test 2: POST generate-question request..."
POST_RESPONSE=$(curl -s -o /tmp/post-response.json -w "%{http_code}" -X POST \
  "${API_ENDPOINT}/generate-question" \
  -H "Content-Type: application/json" \
  -H "Origin: http://aws-interview-prep-yanivhamo-1771254018.s3-website.eu-central-1.amazonaws.com" \
  -d '{
    "topic": "linux",
    "subtopic": "processes",
    "difficulty": "intermediate"
  }')

echo "HTTP Status: $POST_RESPONSE"
echo ""

if [ "$POST_RESPONSE" = "200" ]; then
    echo "✅ POST request: PASSED (Status: $POST_RESPONSE)"
    echo ""
    echo "Response body:"
    cat /tmp/post-response.json | python3 -m json.tool 2>/dev/null || cat /tmp/post-response.json
    echo ""
    
    # Validate response structure
    if python3 << 'PYTHON_EOF'
import json
import sys

try:
    with open('/tmp/post-response.json', 'r') as f:
        data = json.load(f)
    
    # Check if it's wrapped in body
    if 'body' in data and isinstance(data['body'], str):
        data = json.loads(data['body'])
    
    # Validate required fields
    if 'question' in data and 'answer' in data:
        print("✅ Response structure: VALID")
        print(f"   Question: {data['question'][:100]}...")
        print(f"   Answer has summary: {'summary' in data.get('answer', {})}")
        sys.exit(0)
    else:
        print("❌ Response structure: INVALID")
        print(f"   Missing fields. Got: {list(data.keys())}")
        sys.exit(1)
except Exception as e:
    print(f"❌ Response parsing: FAILED - {e}")
    sys.exit(1)
PYTHON_EOF
    then
        echo "✅ All tests PASSED!"
        exit 0
    else
        echo "❌ Response validation FAILED"
        exit 1
    fi
else
    echo "❌ POST request: FAILED (Status: $POST_RESPONSE)"
    echo ""
    echo "Response body:"
    cat /tmp/post-response.json
    echo ""
    exit 1
fi
